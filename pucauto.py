from __future__ import print_function


import json
import time
from selenium import webdriver
from datetime import datetime
from bs4 import BeautifulSoup


with open("config.json") as config:
    CONFIG = json.load(config)


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
    www.pucauto.com                                          v0.3.2

    """)


def wait_for_load():
    """Holy crap I had no idea users could have so many cards on their Haves list and cause PucaTrade to crawl.
    This function solves that by waiting for their loading spinner to dissappear."""

    time.sleep(1)
    while True:
        try:
            loading_spinner = DRIVER.find_element_by_id("fancybox-loading")
        except Exception:
            break


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
        if new_scroll_y == old_scroll_y or new_scroll_y < old_scroll_y:
            break
        else:
            old_scroll_y = new_scroll_y


def build_trades_dict(soup):
    """Iterate through the rows in the table on the /trades page and build up a dictionary. Returns a dictionary like:

    {
        "Philip J Fry": {
            "cards": [
                {
                    "name": "Voice of Resurgence",
                    "value": 2350,
                    "href": https://pucatrade.com/trades/sendcard/38458273
                },
                {
                    "name": "Advent of the Wurm",
                    "value": 56,
                    "href": https://pucatrade.com/trades/sendcard/63524523
                },
                ...
            ],
            "points": 9001
        },
        "Doctor John Zoidberg": {
            "cards": [
                {
                    "name": "Thoughtseize",
                    "value": 2050,
                    "href": https://pucatrade.com/trades/sendcard/46234234
                },
                ...
            ],
            "points": 100
        },
        ...
    }
    """

    trades = {}

    for row in soup.find_all("tr", id=lambda x: x and x.startswith('uc_')):
        member_name = row.find("td", class_="member").find("a", href=lambda x: x and x.startswith("/profiles")).text
        member_points = int(row.find("td", class_="points").text)
        card_name = row.find("a", class_="cl").text
        card_value = int(row.find("td", class_="value").text)
        card_href = "https://pucatrade.com" + row.find("a", class_="fancybox-send").get("href")
        card = {
            "name": card_name,
            "value": card_value,
            "href": card_href
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
        for idx, card in enumerate(sorted_cards):
            # Going directly to URLs instead of interacting with elements on the real page because huge trades lists
            # are super slow.

            # Go to the https://pucatrade.com/trades/sendcard/******* page first to secure the trade.
            DRIVER.get(card.get("href"))

            # Then we can go to the https://pucatrade.com/trades/confirm/******* page to confirm the trade.
            DRIVER.get(card.get("href").replace("sendcard", "confirm"))

            print("Sent {} for {} PucaPoints!".format(card.get("name"), card.get("value")))


def find_trades():
    """The special sauce. Read the docstrings for the individual functions to figure out how this works."""

    load_full_trade_list()
    soup = BeautifulSoup(DRIVER.page_source, 'html.parser')
    trades = build_trades_dict(soup)
    valid_trades = filter_trades_dict(trades)
    complete_trades(valid_trades)


if __name__ == "__main__":
    """Start Pucauto."""

    print_pucauto()
    print("Logging in...")
    log_in()
    goto_trades()
    wait_for_load()
    print("Turning on auto matching...")
    turn_on_auto_matching()
    wait_for_load()
    print("Finding trades...")
    while check_runtime():
        goto_trades()
        wait_for_load()
        find_trades()
    DRIVER.close()
