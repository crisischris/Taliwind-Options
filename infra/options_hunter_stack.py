import aws_cdk as cdk
from aws_cdk import (
    aws_events as events,
    aws_events_targets as targets,
    aws_lambda as lambda_,
    aws_s3 as s3,
    aws_s3_deployment as s3_deploy,
)
from constructs import Construct


class OptionsHunterStack(cdk.Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # ── S3: report storage + static site ──────────────────────────────────

        bucket = s3.Bucket(
            self,
            "ReportsBucket",
            bucket_name="options-hunter-reports",
            website_index_document="index.html",
            public_read_access=True,
            block_public_access=s3.BlockPublicAccess(
                block_public_acls=False,
                block_public_policy=False,
                ignore_public_acls=False,
                restrict_public_buckets=False,
            ),
            versioned=True,
            removal_policy=cdk.RemovalPolicy.RETAIN,
        )

        s3_deploy.BucketDeployment(
            self,
            "DeployViewer",
            sources=[s3_deploy.Source.asset("frontend/dist")],
            destination_bucket=bucket,
            prune=False,  # never delete existing files — runtime JSON reports must persist
        )

        # ── Lambda ────────────────────────────────────────────────────────────

        scanner_fn = lambda_.Function(
            self,
            "ScannerFunction",
            runtime=lambda_.Runtime.PYTHON_3_12,
            handler="lambda_handler.handler",
            code=lambda_.Code.from_asset(
                ".",
                bundling=cdk.BundlingOptions(
                    image=lambda_.Runtime.PYTHON_3_12.bundling_image,
                    command=[
                        "bash", "-c",
                        " && ".join([
                            "mkdir -p /asset-output/.tmp",
                            "TMPDIR=/asset-output/.tmp pip install python-dotenv httpx 'yfinance>=0.2' lxml -t /asset-output --quiet",
                            "rm -rf /asset-output/.tmp",
                            "cp -r indicators lambda_handler.py /asset-output",
                        ]),
                    ],
                ),
            ),
            timeout=cdk.Duration.minutes(10),
            memory_size=1024,
            environment={
                "REPORTS_BUCKET": bucket.bucket_name,
                "GAINER_MIN_GAIN_PCT": "500",
                "GAINER_PUT_MAX_COST_PCT": "0.05",
                "GAINER_PUT_MAX_IV": "2.00",
                "GAINER_PUT_MIN_OI": "10",
                "GAINER_PUT_MIN_DTE": "60",
                "GAINER_PUT_MAX_DTE": "1000",
            },
        )

        bucket.grant_put(scanner_fn)
        bucket.grant_read(scanner_fn)

        # ── EventBridge: twice-daily cron ────────────────────────────────────
        # 14:35 UTC = 9:35 AM EST / 10:35 AM EDT  (near open)
        # 17:00 UTC = 12:00 PM EST / 1:00 PM EDT  (midday)

        for rule_id, hour, minute in [
            ("OpenScanRule",  "14", "35"),
            ("MidayScanRule", "17", "0"),
        ]:
            events.Rule(
                self,
                rule_id,
                schedule=events.Schedule.cron(
                    minute=minute,
                    hour=hour,
                    week_day="MON-FRI",
                ),
                targets=[targets.LambdaFunction(scanner_fn)],
            )

        # ── Outputs ───────────────────────────────────────────────────────────

        cdk.CfnOutput(self, "SiteUrl", value=bucket.bucket_website_url)
        cdk.CfnOutput(self, "BucketName", value=bucket.bucket_name)
        cdk.CfnOutput(self, "ScannerFunctionArn", value=scanner_fn.function_arn)
