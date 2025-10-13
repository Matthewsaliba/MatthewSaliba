from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_apigateway as apigateway,
    aws_dynamodb as dynamodb,
    aws_iam as iam,
    Duration
)
from constructs import Construct

class CrawlerApiStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # DynamoDB table for target websites
        table = dynamodb.Table(
            self, "CrawlerTargets",
            partition_key={"name": "url", "type": dynamodb.AttributeType.STRING},
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST
        )

        # Lambda for CRUD operations
        fn = _lambda.Function(
            self, "TargetApiHandler",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="handler.lambda_handler",
            code=_lambda.Code.from_asset("lambda_22128867/api_handler"),
            timeout=Duration.seconds(10),
            environment={
                "TABLE_NAME": table.table_name
            }
        )

        # Grant Lambda access to the DynamoDB table
        table.grant_read_write_data(fn)

        # API Gateway
        api = apigateway.LambdaRestApi(
            self, "CrawlerTargetApi",
            handler=fn,
            proxy=False
        )

        targets = api.root.add_resource("targets")
        targets.add_method("GET")     
        targets.add_method("POST")    

        target = targets.add_resource("{url}")
        target.add_method("GET")      
        target.add_method("DELETE")  
        target.add_method("PUT")
