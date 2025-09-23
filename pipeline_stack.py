from aws_cdk import (
    Stack,
    pipelines as pipelines,
    aws_codebuild as codebuild,
    SecretValue,
)
from constructs import Construct
from .application_stage import ApplicationStage 


class PipelineStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        pipeline = pipelines.CodePipeline(
            self, "MyPipeline",
            synth=pipelines.ShellStep("Synth",
                input=pipelines.CodePipelineSource.git_hub(
                    "Matthewsaliba/MatthewSaliba",  
                    "main",
                    authentication=SecretValue.secrets_manager("wsu_devops25")
                ),
                commands=[
                    "npm install -g aws-cdk",    
                    "pip install -r requirements.txt",
                    "echo '--- Running python app.py directly to get error message ---'",
                    "echo '--- Listing all files in the root directory ---'",
                    "ls -la",
                    "cdk synth --app 'python app.py'"
                ]
            )
        )

        #  Beta Stage 
        beta = ApplicationStage(self, "Beta")
        beta_stage = pipeline.add_stage(beta)
        beta_stage.add_pre(pipelines.ShellStep("BetaTest", commands=["pytest tests/beta"]))

        # Gamma Stage
        gamma = ApplicationStage(self, "Gamma")
        gamma_stage = pipeline.add_stage(gamma)
        gamma_stage.add_pre(pipelines.ShellStep("GammaTest", commands=["pytest tests/gamma"]))

        # Prod Stage
        prod = ApplicationStage(self, "Prod")
        prod_stage = pipeline.add_stage(prod)
        prod_stage.add_pre(pipelines.ShellStep("ProdTest", commands=["pytest tests/prod"]))
