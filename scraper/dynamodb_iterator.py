import boto3


class DynamoDBScanIterator:
    def __init__(self, user_table):
        self.user_table = user_table
        self.client = boto3.client("dynamodb")
        self.current_response = None
        self.next_key = None
        self.done = False

    def scan(self, last_evaluated_key):
        if last_evaluated_key is None:
            return self.client.scan(
                TableName=self.user_table,
                FilterExpression="attribute_exists(keywords)",
                ProjectionExpression="keywords, endpoint",
            )
        else:
            return self.client.scan(
                TableName=self.user_table,
                FilterExpression="attribute_exists(keywords)",
                ProjectionExpression="keywords, endpoint",
                ExclusiveStartKey=last_evaluated_key,
            )

    def __iter__(self):
        return self

    def __next__(self):
        if self.done:
            raise StopIteration
        else:
            # first response
            if self.next_key is None:
                self.current_response = self.scan(None)
            else:
                self.current_response = self.scan(self.next_key)
            if "LastEvaluatedKey" in self.current_response:
                self.next_key = self.current_response["LastEvaluatedKey"]
            else:
                self.done = True
            return self.current_response
