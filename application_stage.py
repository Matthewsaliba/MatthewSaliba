from aws_cdk import Stage, Environment
from constructs import Construct
from application_stack import ApplicationStack


class ApplicationStage(Stage):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id,
                         env=Environment(region="ap-southeast-2"),  
                         **kwargs)

        ApplicationStack(self, "AppStack")
