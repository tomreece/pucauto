from __future__ import print_function

import json
import time
from selenium import webdriver
from datetime import datetime

CONFIG_FILE = open("config.json")
CONFIG = json.load(CONFIG_FILE)
CONFIG_FILE.close()

DRIVER = webdriver.Firefox()

START_TIME = datetime.now()

def wait(sec):
    time.sleep(sec)

def login():
    DRIVER.get("http://www.pucatrade.com")
    home_login_div = DRIVER.find_element_by_id("home-login")
    home_login_div.find_element_by_id("login").send_keys(CONFIG["username"])
    home_login_div.find_element_by_id("password").send_keys(CONFIG["password"])
    home_login_div.find_element_by_class_name("btn-primary").click()

def goto_trades():
    DRIVER.get("https://pucatrade.com/trades")

def turn_on_auto_matching():
    DRIVER.find_element_by_css_selector("label.niceToggle").click()

def sort_by_value():
    DRIVER.find_element_by_css_selector("th.hValue").click()

def find_trade():
    try:
        row = DRIVER.find_element_by_css_selector("tr.first")
        send_button = row.find_element_by_class_name("sendCard")
        value = int(row.find_element_by_class_name("value").text)
        min_value = CONFIG.get("min_value")
        if not min_value or min_value <= value:
            return send_button
        else:
            return None
    except Exception:
        return None

def confirm_trade():
    try:
        card_name = DRIVER.find_element_by_css_selector("div.lightbox-text p:nth-of-type(2) span.bold").text
        print("Committing to send: {}".format(card_name))
        DRIVER.find_element_by_id("confirm-trade-button").click()
    except Exception:
        pass

def check_runtime():
    hours_to_run = CONFIG.get("hours_to_run")
    if hours_to_run:
        return (datetime.now() - START_TIME).total_seconds() / 60 / 60 < hours_to_run
    else:
        return True

def main():
    print("Logging in.")
    login()
    print("Turning on auto matching and sorting by value.")
    goto_trades()
    turn_on_auto_matching()
    wait(5)
    sort_by_value()
    wait(5)
    print("Finding trades...")
    while check_runtime():
        goto_trades()
        trade = find_trade()
        if trade:
            trade.click()
            wait(5)
            confirm_trade()
            wait(5)
        else:
            wait(5)

main()

DRIVER.close()
