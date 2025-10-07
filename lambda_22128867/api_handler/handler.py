import json
import os
import urllib.parse
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])

def lambda_handler(event, context):
    method = event['httpMethod']
    path = event['path']
    body = json.loads(event['body']) if event.get('body') else {}

    if method == "GET" and path == "/targets":
        return list_targets()

    elif method == "POST" and path == "/targets":
        return create_target(body)

    elif method == "GET" and path.startswith("/targets/"):
        url = urllib.parse.unquote(event['pathParameters']['url'])
        return get_target(url)

    elif method == "PUT" and path.startswith("/targets/"):
        url = urllib.parse.unquote(event['pathParameters']['url'])
        return update_target(url, body)

    elif method == "DELETE" and path.startswith("/targets/"):
        url = urllib.parse.unquote(event['pathParameters']['url'])
        return delete_target(url)

    else:
        return response(400, {"error": "Unsupported method or path"})

def list_targets():
    resp = table.scan()
    return response(200, resp.get("Items", []))

def create_target(data):
    if "url" not in data:
        return response(400, {"error": "Missing 'url'"})
    table.put_item(Item=data)
    return response(201, {"message": "Target added", "target": data})

def get_target(url):
    resp = table.get_item(Key={"url": url})
    item = resp.get("Item")
    if item:
        return response(200, item)
    return response(404, {"error": "Target not found"})

def update_target(url, data):
    data["url"] = url 
    table.put_item(Item=data)
    return response(200, {"message": "Target updated", "target": data})

def delete_target(url):
    table.delete_item(Key={"url": url})
    return response(200, {"message": f"Target '{url}' deleted"})

def response(status, body):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body)
    }
