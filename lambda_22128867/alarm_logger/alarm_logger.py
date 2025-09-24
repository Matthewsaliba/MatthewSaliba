import os
import boto3
import json
from datetime import datetime

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])

def lambda_handler(event, context):
    print("Received event:", json.dumps(event))


    detail = event.get("detail", {})
    alarm_name = detail.get("alarmName", "UnknownAlarm")
    state = detail.get("state", {}).get("value", "UNKNOWN")


    table.put_item(Item={
        "alarmName": alarm_name,
        "timestamp": datetime.utcnow().isoformat(),
        "newState": state,
        "rawEvent": json.dumps(event)
    })

    return {"statusCode": 200, "body": "Logged"}
