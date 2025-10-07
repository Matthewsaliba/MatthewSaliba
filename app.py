import aws_cdk as cdk
from pipeline_stack import PipelineStack


app = cdk.App()
from crawler_api_stack import CrawlerApiStack

CrawlerApiStack(app, "CrawlerApiStack", env=cdk.Environment(region="ap-southeast-2"))
PipelineStack(app, "MultiStagePipelineStack", env=cdk.Environment(region="ap-southeast-2"))


app.synth()
