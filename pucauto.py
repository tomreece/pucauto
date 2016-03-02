#!/usr/bin/env python

from __future__ import print_function

import json
import time
import six
import pprint
from selenium import webdriver
from datetime import datetime
from bs4 import BeautifulSoup


with open("config.json") as config:
    CONFIG = json.load(config)


DRIVER = webdriver.Firefox()


START_TIME = datetime.now()
LAST_ADD_ON_CHECK = START_TIME


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
    pucauto.com                                              v0.4.3
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

    Returns True if the card was sent, False otherwise.
    """

    if CONFIG.get("debug"):
        print(u"  DEBUG: Skipping send of '{}'".format(card["name"]))
        return False

    # Go to the /trades/sendcard/******* page first to secure the trade
    DRIVER.get(card["href"])

    try:
        DRIVER.find_element_by_id("confirm-trade-button")
    except Exception:
        if not add_on:
            reason = DRIVER.find_element_by_tag_name("h3").text
            # Indented for readability because this is part of a bundle and there
            # are header/footer messages
            print(u"  Failed to send {}. Reason: {}".format(card["name"], reason))
        return False

    # Then go to the /trades/confirm/******* page to confirm the trade
    DRIVER.get(card["href"].replace("sendcard", "confirm"))

    if add_on:
        print(u"Added on {} to an unshipped trade for {} PucaPoints!".format(card["name"], card["value"]))
    else:
        # Indented for readability because this is part of a bundle and there
        # are header/footer messages
        print(u"  Sent {} for {} PucaPoints!".format(card["name"], card["value"]))

    return True


def find_and_send_add_ons():
    """Build a list of members that have unshipped cards and then send them any
    new cards that they may want. Card value is ignored because they are already
    being shipped to. So it's fine to add any and all cards on.
    """

    DRIVER.get("https://pucatrade.com/trades/active")
    DRIVER.find_element_by_css_selector("div.dataTables_filter input").send_keys('Unshipped')
    # Wait a bit for the DOM to update after filtering
    time.sleep(5)

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
    partial - When True, only loads rows above min_value, thus speeding up
              this function
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
        "1984581": {
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
            "name": "Philip J. Fry",
            "points": 9001,
            "value": 2406
        },
        ...
    }
    """

    trades = {}

    for row in soup.find_all("tr", id=lambda x: x and x.startswith("uc_")):
        member_points = int(row.find("td", class_="points").text)
        if member_points < CONFIG["min_value"]:
            # This member doesn't have enough points so move on to next row
            continue
        member_link = row.find("td", class_="member").find("a", href=lambda x: x and x.startswith("/profiles"))
        member_name = member_link.text.strip()
        member_id = member_link["href"].replace("/profiles/show/", "")
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
            trades[member_id]["value"] += card_value
        else:
            # First time seeing this member so set up the data structure
            trades[member_id] = {
                "cards": [card],
                "name": member_name,
                "points": member_points,
                "value": card_value
            }

    return trades


def find_highest_value_bundle(trades):
    """Find the highest value bundle in the trades dictionary.

    Args:
    trades - The result dictionary from build_trades_dict

    Returns the highest value bundle, which is a tuple of the (k, v) from
    trades.
    """

    if len(trades) == 0:
        return None

    highest_value_bundle = max(six.iteritems(trades), key=lambda x: x[1]["value"])

    if highest_value_bundle[1]["value"] >= CONFIG["min_value"]:
        return highest_value_bundle
    else:
        return None


def complete_trades(highest_value_bundle):
    """Sort the cards by highest value first and then send them all.

    Args:
    highest_value_bundle - The result tuple from find_highest_value_bundle
    """

    if not highest_value_bundle:
        # No valid bundle was found, give up and restart the main loop
        return

    cards = highest_value_bundle[1]["cards"]
    # Sort the cards by highest value to make the most valuable trades first.
    sorted_cards = sorted(cards, key=lambda k: k["value"], reverse=True)

    member_name = highest_value_bundle[1]["name"]
    member_points = highest_value_bundle[1]["points"]
    bundle_value = highest_value_bundle[1]["value"]
    print(u"Found {} card(s) worth {} points to trade to {} who has {} points...".format(
        len(sorted_cards), bundle_value, member_name, member_points))

    success_count = 0
    success_value = 0
    for card in sorted_cards:
        if send_card(card):
            success_value += card["value"]
            success_count += 1

    print("Successfully sent {} out of {} cards worth {} points!".format(
        success_count, len(sorted_cards), success_value))



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
    print("Logging in...")
    log_in()
    goto_trades()
    wait_for_load()

    # Explicit waits to be extra sure auto matching is on because if it's not
    # then bad things happen, like Pucauto sending out cards you don't have.
    # TODO: We could get smarter here and find a way to double check auto
    #   matching really is on, but I don't have a clever solution for it yet, so
    #   this is a band-aid safety measure.
    time.sleep(5)
    print("Turning on auto matching...")
    turn_on_auto_matching()
    time.sleep(5)

    wait_for_load()
    sort_by_member_points()
    wait_for_load()
    print("Finding trades...")
    while check_runtime():
        find_trades()
    DRIVER.close()
