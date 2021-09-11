import logging
import boto3
import sys
import json
import traceback
from bs4 import BeautifulSoup
import requests
import os
from dynamodb_iterator import *
import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)
user_table = os.environ["USER_TABLE"]
seen_deals_table = os.environ["SEEN_DEALS_TABLE"]


def get_html():
    url = "https://www.ozbargain.com.au/"
    page = requests.get(url).content
    return page


def get_test_html():
    with open("test_html_onlyDeals.html", "r", encoding="utf-8") as f:
        html = f.read()
    return html


def find_all_deal_elems(html):
    soup = BeautifulSoup(html, "html.parser")
    res = soup.find_all(class_="node node-ozbdeal node-teaser")
    return res


def check_for_new_deals(seen_deals, elems):
    new_bargains = []
    for elem in elems:
        h2 = elem.find("h2", class_="title")
        title = h2["data-title"]
        bargain_id = elem["id"].strip("node")
        if bargain_id not in seen_deals:
            deal = {
                "url": "https://www.ozbargain.com.au/node/" + bargain_id,
                "title": title,
            }
            new_bargains.append(deal)
    logger.info(json.dumps({"message": "Checked for new deals", "deals": new_bargains}))
    return new_bargains


def get_seen_deals():
    dynamo_db_scan_iterator = DynamoDBScanIterator(seen_deals_table)
    accumulator = []
    for response in dynamo_db_scan_iterator:
        seen_deals = response["Items"]
        seen_deals = [item["id"]["S"] for item in seen_deals]
        for item in seen_deals:
            accumulator.append(item)
    logger.info(
        json.dumps(
            {
                "message": "Retrieved seen deals from SeenDeals table",
                "accumulator": accumulator,
            }
        )
    )
    return accumulator


def put_seen_deals(bargains):
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(seen_deals_table)
    today = datetime.datetime.today()
    exp_date = int((today + datetime.timedelta(days=7)).timestamp())

    with table.batch_writer() as batch:
        for bargain in bargains:
            stripped_id = bargain["url"].strip("https://www.ozbargain.com.au/node/")
            batch.put_item(Item={"id": stripped_id, "expDate": exp_date})


def keyword_scan_iterator():
    projection_expression = "keywords, endpoint"
    filter_expression = "attribute_exists(keywords)"
    dynamo_db_scan_iterator = DynamoDBScanIterator(
        table=user_table,
        filter_expression=filter_expression,
        projection_expression=projection_expression,
    )
    return dynamo_db_scan_iterator


def process_notifications():
    new_deals = check_for_new_deals(
        seen_deals=get_seen_deals(), elems=find_all_deal_elems(get_html())
    )
    if len(new_deals) > 0:
        put_seen_deals(new_deals)
        dynamo_db_scan_iterator = keyword_scan_iterator()
        for response in dynamo_db_scan_iterator:
            notifiees = response["Items"]
            deals_to_send = []
            for user in notifiees:
                keywords = user["keywords"]["L"]
                for keyword in keywords:
                    for deal in new_deals:
                        title = deal["title"]
                        if keyword["S"] in title.lower():
                            deals_to_send.append(deal)
                if len(deals_to_send) > 0:
                    arn = user["endpoint"]["S"]
                    payload = {
                        "deals": deals_to_send,
                        "keywords": process_keywords(keywords),
                    }
                    notify_user(arn, payload)
                deals_to_send = []


def process_keywords(keywords):
    return [keyword["S"] for keyword in keywords]


def notify_user(arn, payload):
    client = boto3.client("sns")
    logging.info(
        json.dumps(
            {"message": "Sending deal notification", "payload": payload, "ARN": arn}
        )
    )
    return client.publish(
        TargetArn=arn, MessageStructure="string", Message=json.dumps(payload)
    )


def lambda_handler(event, context):
    try:
        logging.info(f"event: {event}")
        process_notifications()

    except Exception:
        exception_type, exception_value, exception_traceback = sys.exc_info()
        traceback_string = traceback.format_exception(
            exception_type, exception_value, exception_traceback
        )
        err_msg = json.dumps(
            {
                "errorType": exception_type.__name__,
                "errorMessage": str(exception_value),
                "stackTrace": traceback_string,
            }
        )
        logger.error(err_msg)
