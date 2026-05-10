import os
import aws_cdk as cdk
from indicators_stack import IndicatorsStack

app = cdk.App()

IndicatorsStack(
    app,
    "IndicatorsStack",
    env=cdk.Environment(
        account=os.environ.get("CDK_DEFAULT_ACCOUNT"),
        region=os.environ.get("CDK_DEFAULT_REGION", "us-east-1"),
    ),
)

app.synth()
