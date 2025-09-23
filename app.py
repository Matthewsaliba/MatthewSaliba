import aws_cdk as cdk
from week2work.pipeline_stack import PipelineStack


app = cdk.App()

PipelineStack(app, "MultiStagePipelineStack", env=cdk.Environment(region="ap-southeast-2"))

app.synth()
