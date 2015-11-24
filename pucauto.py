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


def print_pucauto():
    """Print logo and version number."""

    print("""
     _______  __   __  _______  _______  __   __  _______  _______
    |       ||  | |  ||       ||   _   ||  | |  ||       ||       |
    |    _  ||  | |  ||       ||  |_|  ||  | |  ||_     _||   _   |
    |   |_| ||  |_|  ||       ||       ||  |_|  |  |   |  |  | |  |
    |    ___||       ||      _||       ||       |  |   |  |  |_|  |
    |   |    |       ||     |_ |   _   ||       |  |   |  |       |
    |___|    |_______||_______||__| |__||_______|  |___|  |_______|
    www.pucauto.com                                          v0.3.0

    """)


def wait(sec):
    """Wait an explicit amount of seconds for page loads and interactions."""

    time.sleep(sec)


def log_in():
    """Navigate to pucatrade.com and log in using credentials from config."""

    DRIVER.get("http://www.pucatrade.com")
    home_login_div = DRIVER.find_element_by_id("home-login")
    home_login_div.find_element_by_id("login").send_keys(CONFIG["username"])
    home_login_div.find_element_by_id("password").send_keys(CONFIG["password"])
    home_login_div.find_element_by_class_name("btn-primary").click()


def goto_trades():
    """Go to the /trades page."""

    DRIVER.get("https://pucatrade.com/trades")


def turn_on_auto_matching():
    """Click the toggle on the /trades page to turn on auto matching."""

    DRIVER.find_element_by_css_selector("label.niceToggle").click()


def sort_by_member():
    """Click the Member header in the trades table to sort."""

    DRIVER.find_element_by_css_selector("th.hMember").click()


def confirm_trade(card):
    """Click the confirm trade button in the trade details modal."""

    try:
        DRIVER.find_element_by_id("confirm-trade-button").click()
    except Exception:
        return

    print("Sending {} for {} PucaPoints!".format(card.get("name"), card.get("value")))


def check_runtime():
    """Check to see if the main execution loop should continue. Selenium and Firefox eat up more and more memory
    after long periods of running so this will stop Pucauto after a certain amount of time. If Pucauto was started with
    the startup.sh script it will automatically restart itself again. I typically run my instance for 4 hours between
    restarts on my 2GB RAM cloud server."""

    hours_to_run = CONFIG.get("hours_to_run")
    if hours_to_run:
        return (datetime.now() - START_TIME).total_seconds() / 60 / 60 < hours_to_run
    else:
        return True


def load_full_trade_list():
    """Scroll to the bottom of the page until we can't scroll any further. PucaTrade's /trades page implements an
    infinite scroll table. Without this function, we could only see a portion of the cards available for trade."""

    old_scroll_y = 0
    while True:
        DRIVER.execute_script("window.scrollBy(0, 5000);")
        wait_for_load()
        new_scroll_y = DRIVER.execute_script("return window.scrollY;")
        if new_scroll_y == old_scroll_y:
            break
        else:
            old_scroll_y = new_scroll_y


def build_trades_dict(rows):
    """Iterate through the rows in the table on the /trades page and build up a dictionary. Returns a dictionary like:

    {
        "Philip J Fry": {
            "cards": [
                {
                    "name": "Voice of Resurgence",
                    "value": 2350
                },
                {
                    "name": "Advent of the Wurm",
                    "value": 56
                },
                ...
            ],
            "points": 9001
        },
        "Doctor John Zoidberg": {
            "cards": [
                {
                    "name": "Thoughtseize",
                    "value": 2050
                },
                ...
            ],
            "points": 100
        },
        ...
    }
    """

    trades = {}

    for row in rows:
        try:
            member_name = row.find_element_by_css_selector("td.member a:nth-of-type(3)").text
            member_points = int(row.find_element_by_css_selector("td.points").text)
            card_name = row.find_element_by_css_selector(".cl").text
            card_value = int(row.find_element_by_css_selector(".value").text)
            card = {
                "name": card_name,
                "value": card_value
            }
            if trades.get(member_name):
                # Seen this member before in another row so just add another card
                trades.get(member_name).get("cards").append(card)
            else:
                # First time seeing this member so set up the data structure
                trades[member_name] = {
                    "cards": [card],
                    "points": member_points
                }
        except Exception:
            # Sometimes empty <tr>'s exist at the bottom of the table due to PucaTrade's infinite scroll.
            # This precents from blowing up when it encounters an empty <tr>.
            pass

    return trades


def filter_trades_dict(trades):
    """Iterate through the trades dictionary and build a new dictionary for any single trades or bundles above the
    min_value config."""

    valid_trades = {}

    for member, v in trades.iteritems():
        value = 0
        for card in v.get("cards"):
            value += card.get("value")
        min_value = CONFIG.get("min_value")
        if not min_value or (value >= min_value and v.get("points") >= min_value):
            valid_trades[member] = v

    return valid_trades


def complete_trades(valid_trades):
    """Iterate through the valid_trades dictionary and complete the trades."""

    for member, v in valid_trades.iteritems():
        cards = v.get("cards")
        # Sort the cards by highest value to make the most valuable trades first.
        sorted_cards = sorted(cards, key=lambda k: k['value'], reverse=True)
        for card in sorted_cards:
            try:
                # We have to select row by this sort of complicated XPATH because after a trade has been confirmed
                # the table changes state because the confirmed trade was removed.
                row_xpath = ("//tr[(td[2]//a[contains(., '{}')]) and (td[5]//a[contains(., '{}')])]"
                    .format(card.get("name"), member))
                row = DRIVER.find_element_by_xpath(row_xpath)
                send_button = row.find_element_by_class_name("sendCard")
                send_button.click()
                wait(2)
                confirm_trade(card)
                wait(2)
                DRIVER.find_element_by_css_selector(".fancybox-close").click()
                wait(2)
            except Exception:
                continue


def find_trades():
    """The special sauce. Read the docstrings for the individual functions to figure out how this works."""

    load_full_trade_list()
    rows = DRIVER.find_elements_by_css_selector(".cards-show tbody tr")
    trades = build_trades_dict(rows)
    valid_trades = filter_trades_dict(trades)
    complete_trades(valid_trades)


def wait_for_load():
    """Holy crap I had no idea users could have so many cards on their Haves list and cause PucaTrade to crawl.
    This function solves that by waiting for their loading spinner to dissappear."""

    wait(5)
    while True:
        try:
            loading_spinner = DRIVER.find_element_by_id("fancybox-loading")
        except Exception:
            break


def main():
    """Start Pucauto."""

    print_pucauto()
    print("Logging in...")
    log_in()
    print("Turning on auto matching...")
    goto_trades()
    turn_on_auto_matching()
    wait_for_load()
    print("Sorting by member...")
    sort_by_member()
    wait_for_load()
    print("Finding trades...")
    while check_runtime():
        goto_trades()
        find_trades()

# FIRE IT UP!
main()

# SHUT IT DOWN!
DRIVER.close()
