import json
import boto3


def get_dic_from_s3(fileName):
    s3 = boto3.resource("s3")
    obj = s3.Object("cached-deals", fileName)
    deals = json.loads(obj.get()["Body"].read().decode("utf-8"))
    return deals


def check_for_offers(dic, payload):
    for link, title in dic.items():
        for keyword_info in payload["keywords"]:
            keyword = keyword_info["keyword"]
            offers = [offer["url"] for offer in keyword["offers"]]
            if (
                keyword in title.lower()
                and link not in payload["seenDeals"]
                and link not in offers
            ):
                payload["areThereNewDeals"] = True
                keyword_info["offers"].append({"url": link, "title": title})
                if (
                    not keyword_info["isOnFrontPage"]
                    and not keyword_info["hasUserClicked"]
                ) or keyword_info["hasUserClicked"]:
                    payload["numberOfUnclickedKeywords"] += 1
                keyword_info["isOnFrontPage"] = True
                keyword_info["hasUserClicked"] = False


def get_elegible_bargains(payload):
    front_page_deals = get_dic_from_s3("frontPageDeals")
    new_deals = get_dic_from_s3("newDeals")
    check_for_offers(front_page_deals, payload)
    if not payload["isFrontPageOnly"]:
        check_for_offers(new_deals, payload)
    for url in list(payload["seenDeals"].keys()):
        if url not in front_page_deals and url not in new_deals:
            del payload["seenDeals"][url]
    return payload


def lambda_handler(event, context):
    body = json.loads(event["body"])
    bargains = get_elegible_bargains(body)
    return json.dumps(bargains)
