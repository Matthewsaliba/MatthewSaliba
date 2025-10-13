import boto3
import os
import json
from botocore.exceptions import ClientError

cloudwatch_client = boto3.client('cloudwatch')

DASHBOARD_NAME = os.environ.get("DASHBOARD_NAME", "DefaultCrawlerDashboard")

def lambda_handler(event, context):
    """
    This function is triggered by DynamoDB Streams.
    It creates/deletes CloudWatch resources based on table changes.
    """
    for record in event['Records']:
        try:
            event_name = record['eventName']

            if event_name == 'INSERT':
                new_item_url = record['dynamodb']['NewImage']['url']['S']
                print(f" Creating monitoring for new URL: {new_item_url}")
                create_monitoring(new_item_url)

            elif event_name == 'REMOVE':
                deleted_item_url = record['dynamodb']['OldImage']['url']['S']
                print(f"Deleting monitoring for removed URL: {deleted_item_url}")
                delete_monitoring(deleted_item_url)

        except Exception as e:
            print(f"Error processing record: {record}. Error: {e}")
           
            continue

    return {"status": "OK", "message": "Monitoring updated"}

def create_monitoring(url: str):
    """Creates a CloudWatch alarm and dashboard widget for a given URL."""
    alarm_name = f"Crawl-Failure-{url.replace('://', '-').replace('/', '_')}"

    try:
        
        cloudwatch_client.put_metric_alarm(
            AlarmName=alarm_name,
            AlarmDescription=f'Alarm when crawl fails for {url}',
            MetricName='CrawlFailed',
            Namespace='WebCrawler',
            Statistic='Sum',
            Dimensions=[{'Name': 'Url', 'Value': url}],
            Period=300,
            EvaluationPeriods=1,
            Threshold=1,
            ComparisonOperator='GreaterThanOrEqualToThreshold'
        )


        update_dashboard(url, action='add')

    except ClientError as e:
        print(f"Error creating monitoring for {url}: {e}")

def delete_monitoring(url: str):
    """Deletes the CloudWatch alarm and dashboard widget for a given URL."""
    alarm_name = f"Crawl-Failure-{url.replace('://', '-').replace('/', '_')}"

    try:
     
        cloudwatch_client.delete_alarms(AlarmNames=[alarm_name])

        
        update_dashboard(url, action='remove')

    except ClientError as e:
        print(f"Error deleting monitoring for {url}: {e}")

def update_dashboard(url: str, action: str):
    """Adds or removes a widget for a specific URL from the CloudWatch dashboard."""
    try:
        response = cloudwatch_client.get_dashboard(DashboardName=DASHBOARD_NAME)
        dashboard_body = json.loads(response['DashboardBody'])
        widgets = dashboard_body.get('widgets', [])
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFound':
          
            widgets = []

            dashboard_body = {}
        else:
            raise e

   
    widget_id = f"widget-for-{url.replace('://', '-').replace('/', '_')}"

    if action == 'add':
        print(f"Adding widget for {url} to dashboard {DASHBOARD_NAME}")
        
        new_widget = {
            "type": "metric",
            "properties": {
                "metrics": [
                    [ "WebCrawler", "CrawlFailed", "Url", url ]
                ],
                "view": "singleValue",
                "region": os.environ['AWS_REGION'],
                "title": f"Crawl Failures: {url}",
                "period": 300
            },
            
            "id": widget_id
        }
       
        if not any(w.get('id') == widget_id for w in widgets):
            widgets.append(new_widget)

    elif action == 'remove':
        print(f"Removing widget for {url} from dashboard {DASHBOARD_NAME}")
       
        widgets = [w for w in widgets if w.get('id') != widget_id]


    dashboard_body['widgets'] = widgets
    cloudwatch_client.put_dashboard(
        DashboardName=DASHBOARD_NAME,
        DashboardBody=json.dumps(dashboard_body)
    )