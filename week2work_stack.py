from aws_cdk import (
    aws_cloudwatch as cloudwatch,
    aws_cloudwatch_actions as cw_actions,
    aws_lambda as _lambda,
    aws_events as events,
    aws_events_targets as targets,
    aws_sns as sns,
    aws_sns_subscriptions as subs,
    aws_iam as iam,
    aws_dynamodb as dynamodb,
    aws_lambda_event_sources as lambda_event_sources,
    Stack,
    Duration,
)
from constructs import Construct
from urllib.parse import urlparse


class CanaryWithSmsStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

    
        self.alarm_log_table = dynamodb.Table(
            self, "AlarmLogTable",
            partition_key={"name": "alarmName", "type": dynamodb.AttributeType.STRING},
            sort_key={"name": "timestamp", "type": dynamodb.AttributeType.STRING},
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
        )

 
        self.alarm_logger_fn = self.create_alarm_logger_lambda(self.alarm_log_table)

        alert_topic = self.create_alert_topic()

        urls = [
            "https://www.smh.com.au/",
            "https://www.bbc.com/",
            "https://www.nytimes.com/"
        ]

        for url in urls:
            site_id = urlparse(url).netloc.replace('.', '_').replace('-', '_')
            fn = self.create_canary_lambda(alert_topic, url, site_id)
            self.grant_permissions(fn, alert_topic)
            self.create_schedule_rule(fn, site_id)
            self.create_page_load_alarm(alert_topic, url, site_id)

    def create_alert_topic(self):
        topic = sns.Topic(self, "PageLoadAlertTopic")
        topic.add_subscription(subs.SmsSubscription("+61405128866"))
        return topic

    def create_canary_lambda(self, alert_topic, target_url, site_id):
        fn = _lambda.Function(self, f"CanaryFunction_{site_id}",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="canary.lambda_handler",
            code=_lambda.Code.from_asset("lambda/canary"),
            timeout=Duration.seconds(30),
            environment={
                "TARGET_URL": target_url,
                "ALERT_TOPIC_ARN": alert_topic.topic_arn
            }
        )
        return fn

    def grant_permissions(self, fn, alert_topic):
        fn.add_to_role_policy(iam.PolicyStatement(
            actions=["cloudwatch:PutMetricData"],
            resources=["*"],
        ))
        fn.add_to_role_policy(iam.PolicyStatement(
            actions=["sns:Publish"],
            resources=[alert_topic.topic_arn],
        ))
        alert_topic.grant_publish(fn)

    def create_schedule_rule(self, fn, site_id):
        rule = events.Rule(self, f"CanaryScheduleRule_{site_id}",
            schedule=events.Schedule.rate(Duration.minutes(5))
        )
        rule.add_target(targets.LambdaFunction(fn))
        return rule

    def create_page_load_alarm(self, alert_topic, target_url, site_id):
        alarm = cloudwatch.Alarm(self, f"PageLoadSuccessAlarm_{site_id}",
            metric=cloudwatch.Metric(
                namespace="CustomCanary",
                metric_name="PageLoadSuccess",
                dimensions_map={"URL": target_url},
                period=Duration.minutes(5),
                statistic="Sum"
            ),
            threshold=1,
            evaluation_periods=1,
            comparison_operator=cloudwatch.ComparisonOperator.LESS_THAN_THRESHOLD,
            alarm_description=f"Alarm if page {target_url} fails to load in a 5-minute window",
        )


        alarm.add_alarm_action(cw_actions.SnsAction(alert_topic))

        alarm.add_alarm_action(cw_actions.LambdaAction(self.alarm_logger_fn))

        return alarm

    def create_alarm_logger_lambda(self, table):
        fn = _lambda.Function(self, "AlarmLoggerFunction",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="alarm_logger.lambda_handler",
            code=_lambda.Code.from_asset("lambda/alarm_logger"),
            timeout=Duration.seconds(15),
            environment={
                "TABLE_NAME": table.table_name
            }
        )


        table.grant_write_data(fn)

        return fn
