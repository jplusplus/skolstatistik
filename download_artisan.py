#!/usr/bin/env python3
"""Fetch all data from http://www.jmftal.artisan.se/

The search interface uses sessions cookies that have proven tricky to emulate,
so this scraper is browser based, using Selenium.
"""

from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from urllib.parse import quote
from time import sleep, time
from csv import DictWriter, DictReader
from hashlib import md5
from bs4 import BeautifulSoup

import boto3
import os
import pathlib

from settings import S3_BUCKET


COMPARISONS = [
    "30001", "30002", "30003", "30004",
    "30005", "30006", "30007", "30008",
    "30009", "30010", "30011", "30012",
    "30013", "30014", "30015", "30016",
    "30017", "30018", "30019", "30020",
    "30021", "30017",
    "3",
    "42", "43", "44", "45", "46", "47", "48", "49",
    "31", "32", "33", "34", "35", "36", "37", "38", "39",
]

# Load list of already fetched datasets
downloaded = []
with open("artisan.csv", "r") as file_:
    reader = DictReader(file_)
    downloaded = [(r["school_type"], r["dataset"]) for r in reader]

session = boto3.Session(profile_name="jplusplus")  # profile_name="XXX"
s3_client = session.client("s3")

"""
# Special profile for downloading
# But the server seems to choke on large requests, so not doing that atm
profile = webdriver.FirefoxProfile()
profile.set_preference("browser.download.folderList", 2)  # do not use default
profile.set_preference("browser.download.manager.showWhenStarting", False)
profile.set_preference("browser.download.dir", "./tmp")
mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
profile.set_preference("browser.helperApps.neverAsk.saveToDisk", mime)
"""

driver = webdriver.Firefox()
driver.get("http://www.jmftal.artisan.se/databas.aspx?presel#tab-0")

# Set ”urval” to “alla”, to get all datasets
id_ = "ctl00_ContentPlaceHolder1_ddlStatusYear"
select = Select(driver.find_element_by_id(id_))
select.select_by_visible_text("Alla")
sleep(2)

# loop through school forms
id_ = "ctl00_ContentPlaceHolder1_ddlSkolformer"
select = Select(driver.find_element_by_id(id_))
options = [e.text for e in select.options]
for o in options:
    select.select_by_visible_text(o)
    sleep(3)

    # Select all municipalities (‘whole nation’) is already selected
    xp = "//ul/li[@class='lbxAllSchoolArea nosearch']"
    checkbox = driver.find_element_by_xpath(xp) \
                     .find_element_by_tag_name('input')
    checkbox.click()
    assert checkbox.is_selected()

    # Select all years
    years = driver.find_elements_by_xpath("//ul/li[@class='lbxYears']")
    for year in years[1:]:  # first year already selected
        checkbox = year.find_element_by_tag_name('input')
        checkbox.click()
        assert checkbox.is_selected()

    xp = "//ul/li[@class='lbxCompareTo']/input"
    checkboxes = driver.find_elements_by_xpath(xp)
    for checkbox in checkboxes:
        val = checkbox.get_attribute("value")
        if val == "-99":
            # This one appears in another menu
            continue
        if val in COMPARISONS:
            checkbox.click()
            assert checkbox.is_selected()
        else:
            assert not checkbox.is_selected()

    # Loop through datasets (”variabler”)
    datasets = driver.find_elements_by_xpath("//ul/li[@class='lbxVariables']")
    for dataset in datasets:
        name = dataset.text
        if (o, name) in downloaded:
            print(f"Skipping already downloaded {name} ({o})")
            continue

        print(f"Fetching {name} ({o})")
        data_checkbox = dataset.find_element_by_tag_name('input')
        # select dataset
        data_checkbox.click()
        assert data_checkbox.is_selected()

        id_ = "ctl00_ContentPlaceHolder1_btnCreateTable"
        btn = driver.find_element_by_id(id_)
        btn.click()
        # Wait for search results to load
        WebDriverWait(driver, 30).until(
            expected_conditions.visibility_of_element_located(
                (By.CSS_SELECTOR, ".resultTable")
            )
        )
        sleep(1)
        # There are two possible layouts that seem to be randomly(?) chosen
        # If we are in table2 mode, select table1
        cls_name = driver.find_element_by_class_name("resultTable") \
                         .get_attribute("class")
        if "table2" in cls_name:
            id_ = "ctl00_ContentPlaceHolder1_btnFlipTable"
            btn = driver.find_element_by_id(id_)
            btn.click()
            WebDriverWait(driver, 30).until(
                expected_conditions.visibility_of_element_located(
                    (By.XPATH, "//table[@class='resultTable table1']")
                )
            )
            sleep(1)

        # Collect data
        data = []
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        xp = "//table[@class='resultTable table1']"
        regions = soup.find_all("table", {'class': "resultTable table1"})
        if o != "Specialskola":
            # Special skola is not aggreggated by municipality
            assert len(regions) >= 290 + 1
        # at least all municipalities + nation
        assert len(regions) <= 290 + 1 + len(COMPARISONS)

        for r in regions:
            rows = r.find_all("tr")
            region_name = rows[0].find_all("th")[1].text
            years = [y.text for y in rows[1].find_all("th")]
            dataset_name = rows[2].find("th").text
            try:
                assert dataset_name == name
            except AssertionError:
                print("WARNING Mismatching dataset names:", dataset_name, name)
            values = [v.text for v in rows[2].find_all("td")]
            assert len(values) == len(years)
            item = {
                'region': region_name,
            }
            for y, v in zip(years, values):
                item[y] = v
            data.append(item)

        tmp_file = "./tmp/tmp.csv"
        with open(tmp_file, "w") as file_:
            writer = DictWriter(file_, fieldnames=item.keys())
            writer.writeheader()
            writer.writerows(data)

        s3_key_name = f"artisan/{o}/{name}.csv"
        s3_client.upload_file(
            tmp_file,
            S3_BUCKET,
            s3_key_name,
            ExtraArgs={'ACL': "public-read", 'CacheControl': "no-cache"},
        )

        s3_base = f"https://{S3_BUCKET}.s3.eu-north-1.amazonaws.com/"
        s3_path = s3_base + quote(s3_key_name)
        with open("artisan.csv", "a") as file_:
            writer = DictWriter(file_, fieldnames=[
                "school_type",
                "dataset",
                "path",
                "size",
                "md5",
            ])
            writer.writerow({
                'school_type': o,
                'dataset': name,
                'path': s3_path,
                'size': os.stat(tmp_file).st_size,
                'md5': md5(pathlib.Path(tmp_file).read_bytes()).hexdigest(),
            })

        # Return to search tab
        id_ = "submenu1"
        btn = driver.find_element_by_id(id_) \
                    .find_element_by_tag_name('a')
        btn.click()

        # de-select dataset again
        data_checkbox.click()
        assert not data_checkbox.is_selected()

driver.close()
