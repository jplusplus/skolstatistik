#!/usr/bin/env python3
"""Fetch all data from http://www.jmftal.artisan.se/

The search interface uses sessions cookies that have proven tricky to emulate,
so this scraper is browser based, using Selenium.
"""

from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from time import sleep


# These are the available form controls.
# We want to try every possible combination of them

profile = webdriver.FirefoxProfile()

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
        sleep(5)

        # Download
        # id_ = "ctl00_ContentPlaceHolder1_btnCreateExcel"
        # btn = driver.find_element_by_id(id_)
        # btn.click()

        # Return to search tab
        id_ = "submenu1"
        btn = driver.find_element_by_id(id_) \
                    .find_element_by_tag_name('a')
        btn.click()

        # de-select dataset again
        data_checkbox.click()
        assert not data_checkbox.is_selected()

driver.close()
