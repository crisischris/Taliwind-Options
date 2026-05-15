import os

import aws_cdk as cdk
from options_hunter_stack import OptionsHunterStack
from stage_config import StageConfig

app = cdk.App()

stage = app.node.try_get_context("stage")
if not stage:
    raise ValueError("Stage is required. Deploy with: cdk deploy -c stage=beta|prod")

config = StageConfig(stage=stage)

OptionsHunterStack(
    app,
    config.stack_name,
    config=config,
    env=cdk.Environment(
        account=os.environ.get("CDK_DEFAULT_ACCOUNT"),
        region=os.environ.get("CDK_DEFAULT_REGION", "us-east-1"),
    ),
)

app.synth()
