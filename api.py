from bs4 import BeautifulSoup
import requests
import logging
import hug

def get_html_doc():
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:65.0) Gecko/20100101 Firefox/65.0"
    }
    html_content = requests.get(
        "https://www.ozbargain.com.au/", headers=headers
    ).content
    return BeautifulSoup(html_content, "html.parser")

@hug.get('/bargain')
def bargain(body):
    return get_elegible_bargains(body['item list'])

def get_elegible_bargains(search_terms):
    soup = get_html_doc()
    res = soup.find_all(class_="node-ozbdeal")
    deals = {}
    offers_message = ""
    for offers in res:
        offer_info = offers.find("h2", class_="title")
        for search_term in search_terms:
            link = "https://www.ozbargain.com.au/node/" + offer_info["id"].strip(
                "title"
            )
            if (
                search_term.lower() in offer_info["data-title"].lower()
            ):
                print(offer_info["data-title"])
                # offers_message += "%s\n%s\n\n" % (offer_info["data-title"], link)
                deals[link] = offer_info["data-title"]
    return deals