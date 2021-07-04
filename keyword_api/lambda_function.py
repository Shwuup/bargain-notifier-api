import logging
import json
import traceback
import sys
import boto3  # pylint: disable=import-error
import ast

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def convert_to_dynamo_list(l):
    return [{"S": keyword} for keyword in l]


def update_keywords(token, keywords):
    client = boto3.client("dynamodb")
    altered_keyword_list = convert_to_dynamo_list(keywords)
    response = client.update_item(
        TableName="users",
        Key={"token": {"S": token}},
        UpdateExpression="SET keywords = :newKeywords",
        ExpressionAttributeValues={":newKeywords": {"L": altered_keyword_list}},
    )
    logger.info(f"Updated keywords\nresponse: {response}")
    return response


def lambda_handler(event, context):
    try:
        logging.info(f"event: {event}")
        if event["httpMethod"] == "POST":
            body = ast.literal_eval(event["body"])
            token, keywords = body["token"], body["keywords"]
            update_keywords(token, keywords)
            return {"statusCode": 200, "body": "Successfully updated keywords"}

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
