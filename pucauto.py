from __future__ import print_function


import json
import time
import six
from selenium import webdriver
from datetime import datetime
from bs4 import BeautifulSoup

from lib import logger

with open("config.json") as config:
    CONFIG = json.load(config)

LOGGER = logger.get_default_logger(__name__)
DRIVER = webdriver.Firefox()


START_TIME = datetime.now()
LAST_ADD_ON_CHECK = START_TIME


def print_pucauto():
    """Print logo and version number."""
    # avoid writing the banner to anyplace but the console...
    print("""
     _______  __   __  _______  _______  __   __  _______  _______
    |       ||  | |  ||       ||   _   ||  | |  ||       ||       |
    |    _  ||  | |  ||       ||  |_|  ||  | |  ||_     _||   _   |
    |   |_| ||  |_|  ||       ||       ||  |_|  |  |   |  |  | |  |
    |    ___||       ||      _||       ||       |  |   |  |  |_|  |
    |   |    |       ||     |_ |   _   ||       |  |   |  |       |
    |___|    |_______||_______||__| |__||_______|  |___|  |_______|
    pucauto.com                                              v0.4.1
    github.com/tomreece/pucauto
    @pucautobot on Twitter

    """)


def wait_for_load():
    """Wait for PucaTrade's loading spinner to dissappear."""

    time.sleep(1)
    while True:
        try:
            loading_spinner = DRIVER.find_element_by_id("fancybox-loading")
        except Exception:
            break


def log_in():
    """Navigate to pucatrade.com and log in using credentials from CONFIG."""

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


def sort_by_member_points():
    """Click the Member Points table header to sort by member points (desc)."""

    DRIVER.find_element_by_css_selector("th[title='user_points']").click()


def check_runtime():
    """Return True if the main execution loop should continue.

    Selenium and Firefox eat up more and more memory after long periods of
    running so this will stop Pucauto after a certain amount of time. If Pucauto
    was started with the startup.sh script it will automatically restart itself
    again. I typically run my instance for 2 hours between restarts on my 2GB
    RAM cloud server.
    """

    hours_to_run = CONFIG.get("hours_to_run")
    if hours_to_run:
        return (datetime.now() - START_TIME).total_seconds() / 60 / 60 < hours_to_run
    else:
        return True


def should_check_add_ons():
    """Return True if we should check for add on trades."""

    minutes_between_add_ons_check = CONFIG.get("minutes_between_add_ons_check")
    if minutes_between_add_ons_check:
        return (datetime.now() - LAST_ADD_ON_CHECK).total_seconds() / 60 >= minutes_between_add_ons_check
    else:
        return True


def send_card(card, add_on=False):
    """Send a card.

    Args:
    card   - A dictionary with href, name, and value keys
    add_on - True if this card is an add on, False if it's part of a bundle
    """

    # Go to the /trades/sendcard/******* page first to secure the trade
    DRIVER.get(card.get("href"))

    try:
        DRIVER.find_element_by_id("confirm-trade-button")
    except Exception:
        reason = DRIVER.find_element_by_tag_name("h3").text
        LOGGER.info("Failed to send {}. Reason: {}".format(card.get("name"), reason))
        return

    # Then go to the /trades/confirm/******* page to confirm the trade
    DRIVER.get(card.get("href").replace("sendcard", "confirm"))

    if add_on:
        LOGGER.info("Added on {} to an unshipped trade for {} PucaPoints!".format(card.get("name"), card.get("value")))
    else:
        LOGGER.info("Sent {} for {} PucaPoints!".format(card.get("name"), card.get("value")))


def find_and_send_add_ons():
    """Build a list of members that have unshipped cards and then send them any
    new cards that they may want. Card value is ignored because they are already
    being shipped to. So it's fine to add any and all cards on.
    """

    DRIVER.get("https://pucatrade.com/trades/active")
    DRIVER.find_element_by_css_selector("div.dataTables_filter input").send_keys('Unshipped')
    soup = BeautifulSoup(DRIVER.page_source, "html.parser")

    unshipped = set()
    for a in soup.find_all("a", class_="trader"):
        unshipped.add(a.get("href"))

    goto_trades()
    wait_for_load()
    load_trade_list()
    soup = BeautifulSoup(DRIVER.page_source, "html.parser")

    # Find all rows containing traders from the unshipped set we found earlier
    rows = [r.find_parent("tr") for r in soup.find_all("a", href=lambda x: x and x in unshipped)]

    cards = []

    for row in rows:
        card_name = row.find("a", class_="cl").text
        card_value = int(row.find("td", class_="value").text)
        card_href = "https://pucatrade.com" + row.find("a", class_="fancybox-send").get("href")
        card = {
            "name": card_name,
            "value": card_value,
            "href": card_href
        }
        cards.append(card)

    # Sort by highest value to send those cards first
    sorted_cards = sorted(cards, key=lambda k: k["value"], reverse=True)
    for card in sorted_cards:
        send_card(card, True)


def load_trade_list(partial=False):
    """Scroll to the bottom of the page until we can't scroll any further.
    PucaTrade's /trades page implements an infinite scroll table. Without this
    function, we would only see a portion of the cards available for trade.

    Args:
    partial - Set to True to only load rows above min_value. This increases
              speed for trades with large trade lists.
    """

    old_scroll_y = 0
    while True:
        if partial:
            try:
                lowest_visible_points = int(
                    DRIVER.find_element_by_css_selector(".cards-show tbody tr:last-of-type td.points").text)
            except:
                # We reached the bottom
                lowest_visible_points = -1
            if lowest_visible_points < CONFIG["min_value"]:
                # Stop loading because there are no more members with points above min_value
                break

        DRIVER.execute_script("window.scrollBy(0, 5000);")
        wait_for_load()
        new_scroll_y = DRIVER.execute_script("return window.scrollY;")

        if new_scroll_y == old_scroll_y or new_scroll_y < old_scroll_y:
            break
        else:
            old_scroll_y = new_scroll_y


def build_trades_dict(soup):
    """Iterate through the rows in the table on the /trades page and build up a
    dictionary.

    Args:
    soup - A BeautifulSoup instance of the page DOM

    Returns a dictionary like:

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

    for row in soup.find_all("tr", id=lambda x: x and x.startswith("uc_")):
        member_link = row.find("td", class_="member").find("a", href=lambda x: x and x.startswith("/profiles"))
        member_name = member_link.text.strip()
        member_id = member_link["href"].replace("/profiles/show/", "")
        member_points = int(row.find("td", class_="points").text)
        card_name = row.find("a", class_="cl").text
        card_value = int(row.find("td", class_="value").text)
        card_href = "https://pucatrade.com" + row.find("a", class_="fancybox-send").get("href")
        card = {
            "name": card_name,
            "value": card_value,
            "href": card_href
        }
        if trades.get(member_id):
            # Seen this member before in another row so just add another card
            trades[member_id]["cards"].append(card)
        else:
            # First time seeing this member so set up the data structure
            trades[member_id] = {
                "cards": [card],
                "name": member_name,
                "points": member_points
            }

    return trades


def find_highest_value_bundle(trades):
    """Iterate through the trades dictionary and find the highest value bundle
    above the CONFIG min_value.

    Args:
    trades - The result dictionary from build_trades_dict

    Returns the highest value bundle, which is a dictionary, specifically the
    value of a key from the trades dictionary.
    """

    min_value = CONFIG.get("min_value")
    highest_value_bundle = None

    for member, v in six.iteritems(trades):
        this_bundle_value = 0
        for card in v.get("cards"):
            this_bundle_value += card.get("value")

        # If no min_value set,
        # or this bundle's value is above the min_value
        #    and this member has enough points
        if not min_value or (this_bundle_value >= min_value and v.get("points") >= min_value):
            if not highest_value_bundle or highest_value_bundle["value"] < this_bundle_value:
                v["value"] = this_bundle_value
                highest_value_bundle = v

    return highest_value_bundle


def complete_trades(highest_value_bundle):
    """Iterate through the cards in the bundle and complete the trades.

    Args:
    highest_value_bundle - The result dictionary from find_highest_value_bundle
    """

    if not highest_value_bundle:
        # No valid bundle was found, give up and restart the main loop
        return

    cards = highest_value_bundle.get("cards")
    # Sort the cards by highest value to make the most valuable trades first.
    sorted_cards = sorted(cards, key=lambda k: k["value"], reverse=True)

    LOGGER.info("Found {} card(s) to trade...".format(len(sorted_cards)))

    for card in sorted_cards:
        send_card(card)


def find_trades():
    """The special sauce. Read the docstrings for the individual functions to
    figure out how this works."""

    global LAST_ADD_ON_CHECK

    if CONFIG.get("find_add_ons") and should_check_add_ons():
        find_and_send_add_ons()
        LAST_ADD_ON_CHECK = datetime.now()
    goto_trades()
    wait_for_load()
    load_trade_list(True)
    soup = BeautifulSoup(DRIVER.page_source, "html.parser")
    trades = build_trades_dict(soup)
    highest_value_bundle = find_highest_value_bundle(trades)
    complete_trades(highest_value_bundle)
    # Slow down to not hit PucaTrade refresh limit
    time.sleep(5)


if __name__ == "__main__":
    """Start Pucauto."""

    print_pucauto()
    LOGGER.info("Logging in...")
    log_in()
    goto_trades()
    wait_for_load()
    LOGGER.info("Turning on auto matching...")
    turn_on_auto_matching()
    wait_for_load()
    sort_by_member_points()
    wait_for_load()
    LOGGER.info("Finding trades...")
    while check_runtime():
        find_trades()
    DRIVER.close()
