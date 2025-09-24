from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_sns as sns,
    aws_iam as iam,
)
from constructs import Construct

class ApplicationStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        
        alert_topic = sns.Topic(self, "AlertTopic")

        canary_function = _lambda.Function(
            self, "CanaryFunction",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="canary.lambda_handler",
            code=_lambda.Code.from_asset("lambda_22128867/canary"),
            environment={
                "TARGET_URL": "https://www.bbc.com/",
                "ALERT_TOPIC_ARN": alert_topic.topic_arn
            }
        )

        alert_topic.grant_publish(canary_function)

    