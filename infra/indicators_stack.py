import aws_cdk as cdk
from aws_cdk import (
    aws_events as events,
    aws_events_targets as targets,
    aws_lambda as lambda_,
    aws_s3 as s3,
    aws_s3_deployment as s3_deploy,
    aws_ssm as ssm,
)
from constructs import Construct


class IndicatorsStack(cdk.Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # ── Secrets (SSM Parameter Store) ─────────────────────────────────────
        # SecureString parameters — replace placeholder values before deploying.

        alpha_vantage_key = ssm.StringParameter(
            self,
            "AlphaVantageKey",
            parameter_name="/indicators/ALPHA_VANTAGE_API_KEY",
            string_value="REPLACE_ME",
            tier=ssm.ParameterTier.STANDARD,
        )

        twilio_sid = ssm.StringParameter(
            self,
            "TwilioSid",
            parameter_name="/indicators/TWILIO_ACCOUNT_SID",
            string_value="REPLACE_ME",
            tier=ssm.ParameterTier.STANDARD,
        )

        twilio_token = ssm.StringParameter(
            self,
            "TwilioToken",
            parameter_name="/indicators/TWILIO_AUTH_TOKEN",
            string_value="REPLACE_ME",
            tier=ssm.ParameterTier.STANDARD,
        )

        twilio_from = ssm.StringParameter(
            self,
            "TwilioFrom",
            parameter_name="/indicators/TWILIO_FROM",
            string_value="REPLACE_ME",
            tier=ssm.ParameterTier.STANDARD,
        )

        twilio_to = ssm.StringParameter(
            self,
            "TwilioTo",
            parameter_name="/indicators/TWILIO_TO",
            string_value="REPLACE_ME",
            tier=ssm.ParameterTier.STANDARD,
        )

        # ── S3: report storage + static site ──────────────────────────────────

        bucket = s3.Bucket(
            self,
            "ReportsBucket",
            bucket_name=f"indicators-reports-{self.account}",
            website_index_document="index.html",
            public_read_access=True,
            block_public_access=s3.BlockPublicAccess(
                block_public_acls=False,
                block_public_policy=False,
                ignore_public_acls=False,
                restrict_public_buckets=False,
            ),
            removal_policy=cdk.RemovalPolicy.RETAIN,
        )

        # Sync the static viewer into the bucket on every cdk deploy
        s3_deploy.BucketDeployment(
            self,
            "DeployViewer",
            sources=[s3_deploy.Source.asset("../reports", exclude=["*.json"])],
            destination_bucket=bucket,
        )

        # ── Lambda ────────────────────────────────────────────────────────────
        # CDK bundles deps via pip into a zip at synth time
        # The bundling step runs in a Lambda-compatible container locally.

        scanner_fn = lambda_.Function(
            self,
            "ScannerFunction",
            runtime=lambda_.Runtime.PYTHON_3_12,
            handler="lambda_handler.handler",
            code=lambda_.Code.from_asset(
                "..",
                bundling=cdk.BundlingOptions(
                    image=lambda_.Runtime.PYTHON_3_12.bundling_image,
                    command=[
                        "bash", "-c",
                        " && ".join([
                            "pip install -r requirements.txt -t /asset-output --quiet",
                            "cp -r indicators lambda_handler.py /asset-output",
                        ]),
                    ],
                ),
            ),
            timeout=cdk.Duration.minutes(10),
            memory_size=1024,
            environment={
                "REPORTS_BUCKET": bucket.bucket_name,
                "NOTIFY_VIA": "sms",
                "GAINER_MIN_GAIN_PCT": "500",
                "GAINER_CACHE_FLOOR_PCT": "100",
                "GAINER_PUT_MAX_COST_PCT": "0.05",
                "GAINER_PUT_MAX_IV": "2.00",
                "GAINER_PUT_MIN_OI": "10",
                "GAINER_PUT_MIN_DTE": "60",
                "GAINER_PUT_MAX_DTE": "1000",
                # Secrets are fetched from SSM at runtime (see lambda_handler.py)
                "SSM_PREFIX": "/indicators",
            },
        )

        bucket.grant_put(scanner_fn)
        bucket.grant_read(scanner_fn)

        # Grant Lambda read access to all SSM parameters under /indicators/
        for param in [alpha_vantage_key, twilio_sid, twilio_token, twilio_from, twilio_to]:
            param.grant_read(scanner_fn)

        # ── EventBridge: daily cron ───────────────────────────────────────────
        # 9:31 AM ET on weekdays — one minute after market open

        rule = events.Rule(
            self,
            "DailyScanRule",
            schedule=events.Schedule.cron(
                minute="31",
                hour="9",
                week_day="MON-FRI",
                time_zone=cdk.TimeZone.AMERICA_NEW_YORK,
            ),
        )
        rule.add_target(targets.LambdaFunction(scanner_fn))

        # ── Outputs ───────────────────────────────────────────────────────────

        cdk.CfnOutput(self, "SiteUrl", value=bucket.bucket_website_url)
        cdk.CfnOutput(self, "BucketName", value=bucket.bucket_name)
        cdk.CfnOutput(self, "ScannerFunctionArn", value=scanner_fn.function_arn)
