import json
from platform import platform
from socket import PACKET_BROADCAST
import boto3  # pylint: disable=import-error
import ast
import logging
import sys
import traceback
from botocore.exceptions import *
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)
user_db = os.environ["USER_DB"]


def create_platform_endpoint(token):
    client = boto3.client("sns")
    endpoint = client.create_platform_endpoint(
        PlatformApplicationArn="arn:aws:sns:ap-southeast-2:407075709236:app/GCM/bargain-notifier-notifications",
        Token=token,
    )
    endpoint_val = endpoint["EndpointArn"]
    logger.info(
        json.dumps({"message": "Created platform endpoint", "ARN": endpoint_val})
    )
    return endpoint_val


def handle_add(token):
    client = boto3.client("dynamodb")
    endpoint = create_platform_endpoint(token)
    response = client.put_item(
        TableName=user_db,
        Item={"token": {"S": token}, "ARN": {"S": endpoint}},
    )
    logger.info(
        json.dumps({"message": "Added token", "token": token, "response": response})
    )
    return response


def get_platform_endpoint(token):
    try:
        client = boto3.client("dynamodb")
        response = client.get_item(TableName=user_db, Key={"token": {"S": token}})
        endpoint = response["Item"]["ARN"]["S"]
        logger.info(
            json.dumps(
                {
                    "message": "Retrieved platform endpoint",
                    "ARN": endpoint,
                    "response": response,
                }
            )
        )
        return endpoint
    except KeyError:
        return


def delete_platform_endpoint(token):
    client = boto3.client("sns")
    platform_endpoint = get_platform_endpoint(token)
    client.delete_endpoint(EndpointArn=platform_endpoint)


def handle_delete(token):
    client = boto3.client("dynamodb")
    delete_platform_endpoint(token)
    response = client.delete_item(TableName=user_db, Key={"token": {"S": token}})
    logger.info(
        json.dumps({"message": "Deleted token", "token": token, "response": response})
    )
    return response


def handle_update(new_token, old_token):
    handle_delete(old_token)
    handle_add(new_token)
    logger.info(json.dumps({"message": "Successfully updated token"}))


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
