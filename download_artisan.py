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
from time import sleep


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

# TODO
# Select counties, as extra data points (comparison daat)

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

    # Loop through datasets (”variabler”)
    datasets = driver.find_elements_by_xpath("//ul/li[@class='lbxVariables']")
    for dataset in datasets:
        name = dataset.text
        data_checkbox = dataset.find_element_by_tag_name('input')
        # select dataset
        data_checkbox.click()
        assert data_checkbox.is_selected()

        print(f"Fetching {name}")
        id_ = "ctl00_ContentPlaceHolder1_btnCreateTable"
        btn = driver.find_element_by_id(id_)
        btn.click()
        # Wait for search results to load
        WebDriverWait(driver, 10).until(
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
            WebDriverWait(driver, 10).until(
                expected_conditions.visibility_of_element_located(
                    (By.XPATH, "//table[@class='resultTable table1']")
                )
            )
            sleep(1)

        # Collect data
        data = []
        xp = "//table[@class='resultTable table1']"
        regions = driver.find_elements_by_xpath(xp)
        assert len(regions) == 291  # municipalities + nation
        for r in regions:
            rows = r.find_elements_by_tag_name("tr")
            region_name = rows[0].find_elements_by_tag_name("th")[1].text
            years = [y.text for y in rows[1].find_elements_by_tag_name("th")]
            dataset_name = rows[2].find_element_by_tag_name("th").text
            assert dataset_name == name
            values = [v.text for v in rows[2].find_elements_by_tag_name("td")]
            assert len(values) == len(years)
            item = {
                'region': region_name,
            }
            for y, v in zip(years, values):
                item[y] = v
            print(item)

        # Return to search tab
        id_ = "submenu1"
        btn = driver.find_element_by_id(id_) \
                    .find_element_by_tag_name('a')
        btn.click()

        # de-select dataset again
        data_checkbox.click()
        assert not data_checkbox.is_selected()

driver.close()
