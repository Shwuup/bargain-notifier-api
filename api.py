from bs4 import BeautifulSoup
import requests
import logging
import hug
import boto3
from hug.middleware import CORSMiddleware
import json


api = hug.API(__name__)
api.http.add_middleware(CORSMiddleware(api))


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


def get_cached_deals():
    s3 = boto3.resource("s3")
    obj = s3.Object("bargain-notifier-bucket", "dic")
    deals = json.loads(obj.get()["Body"].read().decode("utf-8"))
    return deals


def get_elegible_bargains(payload):
    cached_deals = get_cached_deals()
    new_seen_deals = {}
    for link, title in cached_deals.items():
        for keyword in payload["keywords"]:
            keyword_info = payload["keywords"][keyword]
            if keyword in title.lower() and link not in payload["seenDeals"]:
                payload["areThereNewDeals"] = True
                print(title)
                keyword_info["offers"][link] = title
                if (
                    not keyword_info["isOnFrontPage"]
                    and not keyword_info["hasUserClicked"]
                ) or keyword_info["hasUserClicked"]:
                    payload["numberOfUnclickedKeywords"] += 1
                keyword_info["isOnFrontPage"] = True
                keyword_info["hasUserClicked"] = False
    for url in payload["seenDeals"].keys():
        if url not in cached_deals:
            del payload["seenDeals"][url]

    return payload

