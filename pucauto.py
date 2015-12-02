from __future__ import print_function


import json
import time
import six
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
    pucauto.com                                              v0.4.0
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


def commit_to_send_card(card, add_on=False):
    """Commit to send a card.

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
        print("Failed to send {}. Reason: {}".format(card.get("name"), reason))
        return

    # Then go to the /trades/confirm/******* page to confirm the trade
    DRIVER.get(card.get("href").replace("sendcard", "confirm"))

    if add_on:
        print("Added on {} to an unshipped trade for {} PucaPoints!".format(card.get("name"), card.get("value")))
    else:
        print("Sent {} for {} PucaPoints!".format(card.get("name"), card.get("value")))


def find_and_send_add_ons():
    """Build a list of members that have unshipped cards and then send them any
    new cards that they may want. Card value is ignored because they are already
    being shipped to. So it's fine to add any and all cards on.

    Returns True if any add on trades were found, False otherwise.
    """

    found_add_ons = False

    DRIVER.get("https://pucatrade.com/trades/active")
    DRIVER.find_element_by_css_selector("div.dataTables_filter input").send_keys('Unshipped\r')
    soup = BeautifulSoup(DRIVER.page_source, "html.parser")

    unshipped = set()
    for a in soup.find_all("a", class_="trader"):
        unshipped.add(a.get("href"))

    goto_trades()
    wait_for_load()
    load_full_trade_list()
    soup = BeautifulSoup(DRIVER.page_source, "html.parser")

    # Find all rows containing traders from the unshipped set we found earlier
    rows = [r.find_parent("tr") for r in soup.find_all("a", href=lambda x: x and x in unshipped)]

    if rows:
        found_add_ons = True

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
        commit_to_send_card(card, True)

    return found_add_ons


def load_full_trade_list():
    """Scroll to the bottom of the page until we can't scroll any further.
    PucaTrade's /trades page implements an infinite scroll table. Without this
    function, we would only see a portion of the cards available for trade.
    """

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

    print("Found {} card(s) to trade...".format(len(sorted_cards)))

    for card in sorted_cards:
        commit_to_send_card(card)


def find_trades():
    """The special sauce. Read the docstrings for the individual functions to
    figure out how this works."""

    if find_and_send_add_ons():
        # If we found some add ons, we need to redo the work of loading the
        # trades list for a fresh state
        goto_trades()
        wait_for_load()
        load_full_trade_list()
    soup = BeautifulSoup(DRIVER.page_source, "html.parser")
    trades = build_trades_dict(soup)
    highest_value_bundle = find_highest_value_bundle(trades)
    complete_trades(highest_value_bundle)
    # Slow down to not hit PucaTrade refresh limit
    time.sleep(10)


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
        find_trades()
    DRIVER.close()
