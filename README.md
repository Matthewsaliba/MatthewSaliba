User Guide: Website Canary Monitoring System using AWS CDK & Lambda
Overview

This is an AWS CDK (Cloud Development Kit) serverless monitoring project that deploys Lambda functions as synthetic canaries to monitor the availability and responsiveness of specified URLs every 5 minutes. It performs a number of checks and measures, records metrics, and generates a CloudWatch Alarm that sends an SMS alert via SNS if any monitored pages fail to load. 

 Architectural Components:

1. AWS Lambda (Python)
 
Performs HTTP checks against defined URLs. 

To edit urls add the url to this bit of the code 

       urls = [
            "https://www.smh.com.au/",
            "https://www.bbc.com/",
            "https://www.nytimes.com/"
        ]
found in the stack.py file 

Records and publishes metrics to CloudWatch:
Latency
PageLoadSuccess
TimeToInteractive
 
If a page fails to load, it publishes alerts to SNS.

2. Alarms

If a site doesn't load (status code ≥ 400), an SMS is sent to +61405128866.

Triggered by a CloudWatch Alarm when PageLoadSuccess < 1.

3. Amazon CloudWatch
 
Stores custom monitoring metrics.

Triggers alarms on thresholds exceeded.

4. Amazon SNS
 
Sends SMS alerts when an alarm is triggered.

5. Amazon EventBridge (CloudWatch Events)
 
Schedules the Lambda to run every 5 mins.

6.  Deploying the Stack

First, assume you have AWS CDK installed.

(If not run this : 

npm install -g aws-cdk)

Now run :

cdk deploy to deploy the lambda function    

(Make sure you have AWS credentials configured (aws configure).)

 What it Monitors:

It checks the following URLS: https://www.smh.com, https://www.bbc.com/, https://www.nytimes.com/




