from apscheduler.schedulers.blocking import BlockingScheduler
from bs4 import BeautifulSoup
import requests
import boto3
import json


sched = BlockingScheduler()


def get_deals(url):
    page = requests.get(url).content
    soup = BeautifulSoup(page, "html.parser")
    res = soup.find_all(class_="node node-ozbdeal node-teaser")
    dic = {}
    for elem in res:
        h2 = elem.find("h2", class_="title")
        link = "https://www.ozbargain.com.au/node/" + elem["id"].strip("node")
        dic[link] = h2["data-title"]
    return dic


def upload():
    deals = get_deals("https://www.ozbargain.com.au/")
    new_deals = get_deals("https://www.ozbargain.com.au/deals")
    deals.update(new_deals)
    s3 = boto3.resource("s3")
    s3.Bucket("bargain-notifier-bucket").put_object(Key="dic", Body=json.dumps(deals))


@sched.scheduled_job("interval", minutes=25)
def timed_job():
    upload()


sched.start()

