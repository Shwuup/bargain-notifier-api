from apscheduler.schedulers.blocking import BlockingScheduler
from bs4 import BeautifulSoup
import requests
import boto3


sched = BlockingScheduler()


def get_html_doc(is_test=False):
    if not is_test:
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:65.0) Gecko/20100101 Firefox/65.0"
        }
        html_content = requests.get(
            "https://www.ozbargain.com.au/", headers=headers
        ).content
        return BeautifulSoup(html_content, "html.parser").prettify()
    else:
        with open("test_bargains.txt") as file:
            html_content = file.read()
            return BeautifulSoup(html_content, "html.parser")


@sched.scheduled_job("interval", minutes=25)
def timed_job():
    doc = get_html_doc()
    # upload to s3 bucket
    s3 = boto3.resource("s3")
    s3.Bucket("bargain-notifier-bucket").put_object(Key="bargain_html", Body=doc)


sched.start()

