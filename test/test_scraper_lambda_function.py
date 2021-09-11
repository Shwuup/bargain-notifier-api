import sys

sys.path.insert(0, "../scraper/")
from lambda_function import find_all_deal_elems, check_for_new_deals
from bs4 import BeautifulSoup


def test_check_for_new_deals_success():
    with open("test_html_onlyDeals.html", "r", encoding="utf-8") as f:
        html = f.read()
    res = find_all_deal_elems(html)
    seen_deals = [
        "636229",
        "636251",
        "636255",
        "636264",
        "636310",
        "636318",
        "636322",
        "636353",
        "636355",
        "636375",
        "636380",
        "636383",
        "636393",
        "636396",
        "636399",
        "636401",
        "636405",
        "636407",
    ]

    actual_deals = check_for_new_deals(seen_deals, res)
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
    assert actual_deals == expected_deals


def test_check_for_new_deals_zeroCase():
    with open("test_html.html", "r", encoding="utf-8") as f:
        html = f.read()
        seen_deals = [
            "636412",
            "636411",
            "636229",
            "636251",
            "636255",
            "636264",
            "636310",
            "636318",
            "636322",
            "636353",
            "636355",
            "636375",
            "636380",
            "636383",
            "636393",
            "636396",
            "636399",
            "636401",
            "636405",
            "636407",
        ]
    res = find_all_deal_elems(html)
    actual_deals = check_for_new_deals(seen_deals, res)
    expected_deals = []
    assert actual_deals == expected_deals


if __name__ == "__main__":
    test_check_for_new_deals_success()
    test_check_for_new_deals_zeroCase
    print("Tests passed successfully!")
