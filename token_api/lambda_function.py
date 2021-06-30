import json
from platform import platform
from socket import PACKET_BROADCAST
import boto3  # pylint: disable=import-error
import ast
import logging
import sys
import traceback
from botocore.exceptions import *

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def create_platform_endpoint(token):
    client = boto3.client("sns")
    endpoint = client.create_platform_endpoint(
        PlatformApplicationArn="arn:aws:sns:ap-southeast-2:407075709236:app/GCM/bargain-notifier-notifications",
        Token=token,
    )
    endpoint_val = endpoint["EndpointArn"]
    logger.info(f"created platform endpoint: {endpoint_val}")
    return endpoint_val


def handle_add(token):
    client = boto3.client("dynamodb")
    endpoint = create_platform_endpoint(token)
    response = client.put_item(
        TableName="users", Item={"token": {"S": token}, "ARN": {"S": endpoint}}
    )
    logger.info(f"Added token\nresponse: {response}")
    return response


def get_platform_endpoint(token):
    try:
        client = boto3.client("dynamodb")
        response = client.get_item(TableName="users", Key={"token": {"S": token}})
        logger.info(f"Got platform endpoint\nresponse: {response}")
        return response["Item"]["ARN"]["S"]
    except KeyError:
        return


def delete_platform_endpoint(token):
    client = boto3.client("sns")
    platform_endpoint = get_platform_endpoint(token)
    client.delete_endpoint(EndpointArn=platform_endpoint)


def handle_delete(token):
    client = boto3.client("dynamodb")
    delete_platform_endpoint(token)
    response = client.delete_item(TableName="users", Key={"token": {"S": token}})
    logger.info(f"Deleted token\nresponse: {response}")
    return response


def handle_update(new_token, old_token):
    handle_delete(old_token)
    handle_add(new_token)
    logger.info(f"Successfully updated token in database")
    return "Successfully updated"


def lambda_handler(event, context):
    try:
        logging.info(f"event: {event}")
        if event["httpMethod"] == "POST":
            token = ast.literal_eval(event["body"])["token"]
            handle_add(token)
            return {"statusCode": 200, "body": "Successfully created token"}
        elif event["httpMethod"] == "PUT":
            token = ast.literal_eval(event["body"])["token"]
            old_token = ast.literal_eval(event["body"])["oldToken"]
            handle_update(token, old_token)
            return {"statusCode": 200, "body": "Successfully updated token"}
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
