#!/usr/bin/env python

# imports
import pandas as pd
from selenium import webdriver
import time
import re

# get table of countries from the given page, extract and clean the list of countries
euros = pd.read_html('https://en.wikipedia.org/wiki/List_of_European_countries_by_area')[0]['State'].tolist()
euros = [e.replace('*', '') for e in euros]

# initialize chromedriver
chromedriver = "/Applications/chromedriver"
driver = webdriver.Chrome(chromedriver)

# open page of sporcle quiz and press button to start play
driver.get('https://www.sporcle.com/games/g/europe')
play = driver.find_element_by_xpath('.//div[@id="button-play"]')
time.sleep(1)
play.click()

# identify the form to input country names, and enter each name in the list of countries
# keep text that "stays" in the form after input, these are either:
# 1) Countries on the list that are not valid answers
# 2) Fragments of countries which are valid but where a partial string is another valid answer
# Ex: "Ukraine" will become "raine" because "Uk" = "United Kingdom"
enter_country = driver.find_element_by_xpath('.//input[@id="gameinput"]')
fragments = []
for e in euros:
    enter_country.send_keys(e)
    unaccepted = enter_country.get_attribute("value")
    if unaccepted:
        fragments.append(unaccepted)
    enter_country.clear()
    time.sleep(1)

# enter each country matching a "fragment" found from above block into the input form
# the quiz may have already been solved completely, so just cycle through doing nothing if so
enter_again = [e for f in fragments for e in euros if f in e]
for a in enter_again:
    try:
        enter_country.send_keys(a)
        enter_country.clear()
        time.sleep(1)
    except:
        continue

# find and print the sporcle message of congratulations for "winning"
congrats = driver.find_element_by_xpath('.//div[@id="snark"]').text
print(re.sub('\([^)]*\)', '', congrats).strip())

# close/quit chromeriver
driver.close()
driver.quit()