import os
import aws_cdk as cdk
from options_hunter_stack import OptionsHunterStack

app = cdk.App()

OptionsHunterStack(
    app,
    "OptionsHunterStack",
    env=cdk.Environment(
        account=os.environ.get("CDK_DEFAULT_ACCOUNT"),
        region=os.environ.get("CDK_DEFAULT_REGION", "us-east-1"),
    ),
)

app.synth()
