from bs4 import BeautifulSoup
import requests
import logging
import hug
from hug.middleware import CORSMiddleware

api = hug.API(__name__)
api.http.add_middleware(CORSMiddleware(api))


def get_html_doc():
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:65.0) Gecko/20100101 Firefox/65.0"
    }
    html_content = requests.get(
        "https://www.ozbargain.com.au/", headers=headers
    ).content
    return BeautifulSoup(html_content, "html.parser")


@hug.post("/bargain")
def bargain(body, response):
    print(body)
    return get_elegible_bargains(body)


def get_elegible_bargains(keyword_object):
    soup = get_html_doc()
    res = soup.find_all(class_="node-ozbdeal")
    #TODO: need to think about how to tell when it is actually a NEW deal. and where that logic lives;
    for offer_html in res:
        offer_info = offer_html.find("h2", class_="title")
        for keyword in keyword_object["keywords"]:
            link = "https://www.ozbargain.com.au/node/" + offer_info["id"].strip(
                "title"
            )
            offer_title = offer_info["data-title"]
            seen_links = [offer[0] for offer in keyword_object["keywords"][keyword]["offers"]]
            if keyword.lower() in offer_title.lower() and link not in seen_links:
                keyword_object["areThereNewDeals"] = True
                print(offer_title)
                offers = keyword_object["keywords"][keyword]["offers"]
                offers.append([link, offer_title])
                keyword_object["keywords"][keyword] = {"offers":offers, "hasUserClicked": False}
                

    return keyword_object
