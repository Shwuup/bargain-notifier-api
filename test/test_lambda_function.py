import sys

sys.path.insert(0, "../scraper/")
from lambda_function import find_all_deal_elems, check_for_new_deals
from bs4 import BeautifulSoup
import pickle

# 636396 = SodaStream Syrups
def test_check_for_new_deals_highlightSuccess():
    with open("test_html.html", "r", encoding="utf-8") as f:
        html = f.read()
    res = find_all_deal_elems(html)
    actual_deals, actual_last_id = check_for_new_deals("636396", res)
    expected_deals = [
        {
            "url": "https://www.ozbargain.com.au/node/636401",
            "title": "[eBook] Free - Anabolic Kitchen/Strength Training NOT Bodybuilding/Weight Training: A Beginners Guide - Amazon AU/US",
        },
        {
            "url": "https://www.ozbargain.com.au/node/636399",
            "title": 'Fiskars 53cm 21" Soft Grip Bow Saw $5 @ Bunnings',
        },
    ]
    expected_last_id = "636401"
    assert actual_deals == expected_deals
    assert actual_last_id == expected_last_id


def test_check_for_new_deals_zeroCase():
    with open("test_html.html", "r", encoding="utf-8") as f:
        html = f.read()
    res = find_all_deal_elems(html)
    actual_deals, actual_last_id = check_for_new_deals("636401", res)
    expected_deals = []
    expected_last_id = 0
    assert actual_deals == expected_deals
    assert actual_last_id == expected_last_id


# 636407 = Coles Rewards Mastercard
def test_check_for_new_deals_noHighlightSuccess():
    with open("test_html_onlyDeals.html", "r", encoding="utf-8") as f:
        html = f.read()
    res = find_all_deal_elems(html)
    actual_deals, actual_last_id = check_for_new_deals("636407", res)
    expected_deals = [
        {
            "url": "https://www.ozbargain.com.au/node/636412",
            "title": "[Switch, eBay Plus] Switch Joy-Con Pair (5 Styles/Colours) $89.10, Ring Fit Adventure $89.10 Delivered @ Big W eBay",
        },
        {
            "url": "https://www.ozbargain.com.au/node/636411",
            "title": "Harpic Fresh Power Liquid Toilet Cleaner $1.91ea S&S When Buy 8 ($15.30 Total) + Delivery ($0 with Prime/ $39 Spend) @ Amazon AU",
        },
    ]
    expected_last_id = "636412"
    assert actual_deals == expected_deals
    assert actual_last_id == expected_last_id


def test_check_for_new_deals_noHightlightZeroCase():
    with open("test_html.html", "r", encoding="utf-8") as f:
        html = f.read()
    res = find_all_deal_elems(html)
    actual_deals, actual_last_id = check_for_new_deals("636412", res)
    expected_deals = []
    expected_last_id = 0
    assert actual_deals == expected_deals
    assert actual_last_id == expected_last_id


if __name__ == "__main__":
    test_check_for_new_deals_highlightSuccess()
    test_check_for_new_deals_zeroCase()
    test_check_for_new_deals_noHighlightSuccess()
    test_check_for_new_deals_noHightlightZeroCase
