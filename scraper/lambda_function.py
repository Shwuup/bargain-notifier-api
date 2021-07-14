import logging
import boto3
import sys
import json
import traceback
from bs4 import BeautifulSoup
import requests
from dynamodb_iterator import *

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def highlighted_deals_exists(soup):
    span = soup.find("span")
    return True if span.text == "Highlighted Deals" else False


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
    if highlighted_deals_exists(soup):
        deals_span = soup.select("span")[1]
        res = deals_span.find_all_next(class_="node node-ozbdeal node-teaser")
    else:
        res = soup.find_all(class_="node node-ozbdeal node-teaser")
    return res


def get_last_seen_deal_id():
    client = boto3.client("dynamodb")
    response = client.get_item(TableName="latest_url", Key={"id": {"N": "1"}})
    node = response["Item"]["bargainId"]["S"]
    return node


def update_last_seen_deal(last_seen_id):
    client = boto3.client("dynamodb")
    response = client.update_item(
        TableName="latest_url",
        Key={"id": {"N": "1"}},
        UpdateExpression="SET bargainId = :newBargainId",
        ExpressionAttributeValues={":newBargainId": {"S": last_seen_id}},
    )
    logger.info(f"Updated latest id\nresponse: {response}")
    return response


def check_for_new_deals(last_seen_id, elems):
    bargains = []
    new_last_seen_id = 0
    for elem in elems:
        h2 = elem.find("h2", class_="title")
        title = h2["data-title"]
        bargain_id = elem["id"].strip("node")
        if bargain_id == last_seen_id:
            break
        else:
            bargains.append(
                {
                    "url": "https://www.ozbargain.com.au/node/" + bargain_id,
                    "title": title,
                }
            )
    if len(bargains) > 0:
        new_last_seen_id = bargains[0]["url"].strip(
            "https://www.ozbargain.com.au/node/"
        )
    return bargains, new_last_seen_id


def process_notifications():
    last_seen_deal_id = get_last_seen_deal_id()
    new_deals, new_last_seen_id = check_for_new_deals(
        last_seen_deal_id, find_all_deal_elems(get_test_html())
    )
    dynamo_db_scan_iterator = DynamoDBScanIterator()
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
                arn = user["ARN"]["S"]
                notify_user(arn, deals_to_send)
            deals_to_send = []
    if len(new_deals) > 0:
        update_last_seen_deal(new_last_seen_id)


def notify_user(arn, deals):
    client = boto3.client("sns")
    logging.info(f"notified: {arn}")
    return client.publish(
        TargetArn=arn, MessageStructure="string", Message=json.dumps(deals)
    )


def lambda_handler(event, context):
    try:
        logging.info(f"event: {event}")
        if event["httpMethod"] == "POST":
            process_notifications()
            return {
                "statusCode": 200,
                "body": "Successfully notified users",
            }

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
