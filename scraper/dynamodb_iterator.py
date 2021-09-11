import boto3


class DynamoDBScanIterator:
    def __init__(self, table, filter_expression="", projection_expression=""):
        self.filter_expression = filter_expression
        self.projection_expression = projection_expression
        self.table = table
        self.client = boto3.client("dynamodb")
        self.current_response = None
        self.next_key = None
        self.done = False
        self.keyword_arguments = self.get_keyword_arguments()

    def get_keyword_arguments(self):
        keyword_arguments = {"TableName": self.table}
        if self.filter_expression != "":
            keyword_arguments["FilterExpression"] = self.filter_expression
        if self.projection_expression != "":
            keyword_arguments["ProjectionExpression"] = self.projection_expression
        return keyword_arguments

    def scan(self, last_evaluated_key):
        if last_evaluated_key is None:
            return self.client.scan(**self.keyword_arguments)
        else:
            # if LastEvaluatedKey is present, shallow copy keyword_arguments but also add ExclusiveStartKey to it
            return self.client.scan(
                **dict(self.keyword_arguments, ExclusiveStartKey=last_evaluated_key)
            )

    def __iter__(self):
        return self

    def __next__(self):
        while not self.done:
            if self.next_key is None:
                self.current_response = self.scan(None)
            else:
                self.current_response = self.scan(self.next_key)
            if "LastEvaluatedKey" in self.current_response:
                self.next_key = self.current_response["LastEvaluatedKey"]
            else:
                self.done = True
            return self.current_response
        raise StopIteration
