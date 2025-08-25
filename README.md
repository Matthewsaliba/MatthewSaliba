# WSU_DevOps_2025
This is a repo for the 2025 batch of DevOp Course. 


This Lambda Function checks the availabilty, latency and staus code of a url and sends cloudwatch metrics. If the page fails to load a SNS alert will be sent.


This lambda function was tested by deploying a working url to test if the function displays metrics, and a broken url to test if the function will display that the website is unavaliable and the SNS alert is sent.*