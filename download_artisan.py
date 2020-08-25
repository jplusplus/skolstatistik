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

# loop through school forms
select_id = "ctl00_ContentPlaceHolder1_ddlSkolformer"
select = Select(driver.find_element_by_id(select_id))
options = [e.text for e in select.options]
for o in options:
    select.select_by_visible_text(o)
    sleep(3)

    # loop through data sets
    # loop through years
    # select alla municipalities
    # download
    # store


driver.close()
