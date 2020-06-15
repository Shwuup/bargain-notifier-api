import json
import boto3  # pylint: disable=import-error


def get_dic_from_s3(fileName):
    s3 = boto3.resource("s3")
    obj = s3.Object("cached-deals", fileName)
    deals = json.loads(obj.get()["Body"].read().decode("utf-8"))
    return deals


def create_duplicate_dic(payload):
    duplicates = set()
    for keyword in payload["keywords"]:
        for offer in keyword["offers"]:
            duplicates.add(offer["url"])
    return duplicates


def check_for_offers(dic, payload, duplicates):
    for link, title in dic.items():
        for keyword_info in payload["keywords"]:
            keyword = keyword_info["keyword"]
            offers = [offer["url"] for offer in keyword_info["offers"]]
            if (
                keyword in title.lower()
                and link not in payload["seenDeals"]
                and link not in offers
                and link not in duplicates
            ):
                payload["areThereNewDeals"] = True
                keyword_info["offers"].append({"url": link, "title": title})
                duplicates.add(link)
                if (
                    not keyword_info["isOnFrontPage"]
                    and not keyword_info["hasUserClicked"]
                ) or keyword_info["hasUserClicked"]:
                    payload["numberOfUnclickedKeywords"] += 1
                keyword_info["isOnFrontPage"] = True
                keyword_info["hasUserClicked"] = False


def get_elegible_bargains(payload):
    duplicates = create_duplicate_dic(payload)
    front_page_deals = get_dic_from_s3("frontPageDeals")
    new_deals = get_dic_from_s3("newDeals")
    check_for_offers(front_page_deals, payload, duplicates)
    if not payload["isFrontPageOnly"]:
        check_for_offers(new_deals, payload, duplicates)
    for url in list(payload["seenDeals"].keys()):
        if url not in front_page_deals and url not in new_deals:
            del payload["seenDeals"][url]
    return payload


def lambda_handler(event, context):
    body = json.loads(event["body"])
    bargains = get_elegible_bargains(body)
    return json.dumps(bargains)
