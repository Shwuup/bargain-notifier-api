import json
import boto3

def get_cached_deals():
    s3 = boto3.resource("s3")
    obj = s3.Object("cached-deals", "dic")
    deals = json.loads(obj.get()["Body"].read().decode("utf-8"))
    return deals

def get_elegible_bargains(payload):
    cached_deals = get_cached_deals()
    new_seen_deals = {}
    for link, title in cached_deals.items():
        for keyword_info in payload["keywords"]:
            keyword = keyword_info["keyword"]
            if keyword in title.lower() and link not in payload["seenDeals"]:
                payload["areThereNewDeals"] = True
                keyword_info["offers"].append({"url": link, "title": title})
                # keyword_info["offers"][link] = title
                if (
                    not keyword_info["isOnFrontPage"]
                    and not keyword_info["hasUserClicked"]
                ) or keyword_info["hasUserClicked"]:
                    payload["numberOfUnclickedKeywords"] += 1
                keyword_info["isOnFrontPage"] = True
                keyword_info["hasUserClicked"] = False
    for url in list(payload["seenDeals"].keys()):
        if url not in cached_deals:
            del payload["seenDeals"][url]

    return payload

def lambda_handler(event, context):    
    body = json.loads(event["body"])
    bargains = get_elegible_bargains(body)
    return json.dumps(bargains)
