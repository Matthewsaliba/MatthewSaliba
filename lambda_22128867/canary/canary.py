import os
import urllib.request
import time
import boto3
from botocore.exceptions import ClientError

cloudwatch = boto3.client("cloudwatch")
sns = boto3.client("sns")

TARGET_URL = os.environ.get("TARGET_URL")
ALERT_TOPIC_ARN = os.environ.get("ALERT_TOPIC_ARN")

def check_page_load(url, timeout=10):
    """Attempts to load the page and returns (status_code, page_loaded, tti)."""
    try:
        start_tti = time.time()
        response = urllib.request.urlopen(url, timeout=timeout)
        tti = time.time() - start_tti  
        status_code = response.getcode()
        page_loaded = 1 if 200 <= status_code < 400 else 0
    except Exception as e:
        print(f"Page load failed: {e}")
        status_code = 0
        page_loaded = 0
        tti = 0
    return status_code, page_loaded, tti

def put_metrics(url, latency, page_loaded, tti):
    """Sends metrics to CloudWatch."""
    try:
        cloudwatch.put_metric_data(
            Namespace='CustomCanary',
            MetricData=[
                {
                    'MetricName': 'Latency',
                    'Dimensions': [{'Name': 'URL', 'Value': url}],
                    'Value': latency,
                    'Unit': 'Seconds'
                },
                {
                    'MetricName': 'PageLoadSuccess',
                    'Dimensions': [{'Name': 'URL', 'Value': url}],
                    'Value': page_loaded,
                    'Unit': 'Count'
                },
                {
                    'MetricName': 'TimeToInteractive',
                    'Dimensions': [{'Name': 'URL', 'Value': url}],
                    'Value': tti,
                    'Unit': 'Seconds'
                }
            ]
        )
    except ClientError as e:
        print(f"Failed to put metrics: {e}")

def send_alert(topic_arn, url):
    """Sends an alert via SNS."""
    try:
        sns.publish(
            TopicArn=topic_arn,
            Message=f"ALERT: Page {url} could NOT be loaded!",
            Subject="Canary Page Load Failure"
        )
    except ClientError as e:
        print(f"Failed to send SNS alert: {e}")

def lambda_handler(event, context):
    start_time = time.time()
    status_code, page_loaded, tti = check_page_load(TARGET_URL)
    latency = time.time() - start_time

    put_metrics(TARGET_URL, latency, page_loaded, tti)

    if page_loaded == 0:
        send_alert(ALERT_TOPIC_ARN, TARGET_URL)
        raise Exception(f"Page load failed for {TARGET_URL}")

    return {
        'statusCode': status_code,
        'latency': latency,
        'page_loaded': page_loaded,
        'time_to_interactive': tti
    }


