from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_apigateway as apigateway,
    aws_dynamodb as dynamodb,
    aws_iam as iam,
    Duration
)
from aws_cdk.aws_lambda_event_sources import DynamoEventSource
from constructs import Construct

class CrawlerApiStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # DynamoDB table for target websites
        table = dynamodb.Table(
            self, "CrawlerTargets",
            partition_key={"name": "url", "type": dynamodb.AttributeType.STRING},
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            stream=dynamodb.StreamViewType.NEW_AND_OLD_IMAGES
        )
        


        monitoring_handler_fn = _lambda.Function(
            self, "MonitoringHandler",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="monitoring_handler.lambda_handler",
            code=_lambda.Code.from_asset("lambda_22128867"),
            timeout=Duration.seconds(30),
            environment={
                "DASHBOARD_NAME": "APIDashboard"
            }
        )

        monitoring_handler_fn.add_event_source(DynamoEventSource(
    table,
    starting_position=_lambda.StartingPosition.LATEST
))

        monitoring_handler_fn.add_to_role_policy(iam.PolicyStatement(
    actions=[
        "cloudwatch:PutMetricAlarm",
        "cloudwatch:DeleteAlarms",
        "cloudwatch:PutDashboard",
        "cloudwatch:GetDashboard"
    ],
    resources=["*"]
))


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
