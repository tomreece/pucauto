import sys
import time
from selenium import webdriver

try:
    username = sys.argv[1]
    password = sys.argv[2]
except IndexError:
    print 'You need to type: python pucauto.py email@address.com password'
    quit()

driver = webdriver.Firefox()

def wait(sec):
    time.sleep(sec)

def login():
    driver.get("http://www.pucatrade.com")
    home_login_div = driver.find_element_by_id("home-login")
    home_login_div.find_element_by_id("login").send_keys(username)
    home_login_div.find_element_by_id("password").send_keys(password)
    home_login_div.find_element_by_class_name("btn-primary").click()

def goto_trades():
    driver.get("https://pucatrade.com/trades")

def turn_on_auto_matching():
    driver.find_element_by_css_selector("label.niceToggle").click()
    wait(5)

def sort_by_value():
    driver.find_element_by_css_selector("th.hValue").click()
    wait(5)

def find_trade():
    try:
        return driver.find_element_by_class_name("sendCard")
    except Exception:
        return None

def confirm_trade():
    try:
        driver.find_element_by_id("confirm-trade-button").click()
    except Exception:
        pass

def main():
    login()
    goto_trades()
    turn_on_auto_matching()
    sort_by_value()
    while True:
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
