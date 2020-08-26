#!/usr/bin/env python3
"""Fetch all data from http://www.jmftal.artisan.se/

The search interface uses sessions cookies that have proven tricky to emulate,
so this scraper is browser based, using Selenium.
"""

from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from time import sleep


form_selects = [
    "ctl00_ContentPlaceHolder1_ddlSkolformer",
]
# These are the available form controls.
# We want to try every possible combination of them

driver = webdriver.Firefox()
driver.get("http://www.jmftal.artisan.se/databas.aspx?presel#tab-0")

# Set ”urval” to “alla”, to get all datasets
select_id = "ctl00_ContentPlaceHolder1_ddlStatusYear"
select = Select(driver.find_element_by_id(select_id))
select.select_by_visible_text("Alla")
sleep(2)

# Select all municipalities (‘whole nation’) is already selected
checkbox = driver.find_element_by_xpath("//ul/li[@class='lbxAllSchoolArea nosearch']")
checkbox.click()

first_years = driver.find_element_by_xpath("//ul/li[@class='lbxYears']")
# Deselect preselected first year, to simplify loop later on
first_years.find_element_by_tag_name('input').click()

# loop through school forms
select_id = "ctl00_ContentPlaceHolder1_ddlSkolformer"
select = Select(driver.find_element_by_id(select_id))
options = [e.text for e in select.options]
for o in options:
    select.select_by_visible_text(o)
    sleep(3)

    # Loop through datasets (”variabler”) for this school form
    datasets = driver.find_elements_by_xpath("//ul/li[@class='lbxVariables']")
    for dataset in datasets:
        name = dataset.text
        data_checkbox = dataset.find_element_by_tag_name('input')
        # select dataset
        data_checkbox.click()
        assert data_checkbox.is_selected()

        # We need to recreate this list, because available years differ
        years = driver.find_elements_by_xpath("//ul/li[@class='lbxYears']")
        for year in years:
            # select year
            year_checkbox = year.find_element_by_tag_name('input')
            year_checkbox.click()
            assert year_checkbox.is_selected()
            print(f"Fetching {name} for {year.text}")
            btn_id = "ctl00_ContentPlaceHolder1_btnCreateTable"

            # download
            # store

            # de-select year again
            year_checkbox.click()
            assert not year_checkbox.is_selected()

        # de-select dataset again
        data_checkbox.click()
        assert not data_checkbox.is_selected()

driver.close()
