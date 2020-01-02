from bs4 import BeautifulSoup
import requests
import logging
import hug
import boto3
from hug.middleware import CORSMiddleware


api = hug.API(__name__)
api.http.add_middleware(CORSMiddleware(api))


def get_html_doc(is_test=False):
    if not is_test:
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:65.0) Gecko/20100101 Firefox/65.0"
        }
        html_content = requests.get(
            "https://www.ozbargain.com.au/", headers=headers
        ).content
        return BeautifulSoup(html_content, "html.parser")
    else:
        with open("test_bargains.txt") as file:
            html_content = file.read()
            return BeautifulSoup(html_content, "html.parser")


@hug.post("/bargain")
def bargain(body, response):
    print(body)
    return get_elegible_bargains(body)


@hug.get("/ping")
def ping():
    return "still up!"


@hug.post("/test_bargain")
def test_bargain(body, response):
    print(body)
    return get_elegible_bargains(body, is_test=True)


def get_elegible_bargains(keyword_object, is_test=False):
    if is_test:
        soup = get_html_doc(is_test=True)
    else:
        # get cached copy from s3 bucket
        s3 = boto3.resource("s3")
        obj = s3.Object("bargain-notifier-bucket", "bargain_html")
        html_content = obj.get()["Body"].read().decode("utf-8")
        soup = BeautifulSoup(html_content, "html.parser")
    res = soup.find_all(class_="node node-ozbdeal node-teaser")

    for offer_html in res:
        offer_info = offer_html.find("h2", class_="title")
        for keyword in keyword_object["keywords"]:
            keyword_info = keyword_object["keywords"][keyword]
            link = "https://www.ozbargain.com.au/node/" + offer_info["id"].strip(
                "title"
            )
            offer_title = offer_info["data-title"]
            seen_links = [offer[0] for offer in keyword_info["offers"]]
            if keyword.lower() in offer_title.lower() and link not in seen_links:
                keyword_object["areThereNewDeals"] = True
                print(offer_title)
                keyword_info["offers"].append([link, offer_title])
                if (
                    not keyword_info["isOnFrontPage"]
                    and not keyword_info["hasUserClicked"]
                ) or keyword_info["hasUserClicked"]:
                    keyword_object["numberOfUnclickedKeywords"] += 1
                keyword_info["isOnFrontPage"] = True
                keyword_info["hasUserClicked"] = False

    return keyword_object
