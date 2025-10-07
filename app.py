import aws_cdk as cdk
from pipeline_stack import PipelineStack
from week2work_stack import CanaryWithSmsStack

app = cdk.App()
from crawler_api_stack import CrawlerApiStack

CrawlerApiStack(app, "CrawlerApiStack", env=cdk.Environment(region="ap-southeast-2"))
PipelineStack(app, "MultiStagePipelineStack", env=cdk.Environment(region="ap-southeast-2"))
CanaryWithSmsStack(app, "CanaryWithSms", env=cdk.Environment(region="ap-southeast-2"))


app.synth()
