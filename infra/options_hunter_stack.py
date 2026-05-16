import json
import pathlib

import aws_cdk as cdk
from aws_cdk import (
    aws_iam as iam,
)
from aws_cdk import (
    aws_lambda as lambda_,
)
from aws_cdk import (
    aws_s3 as s3,
)
from aws_cdk import (
    aws_s3_deployment as s3_deploy,
)
from aws_cdk import (
    aws_scheduler as scheduler,
)
from constructs import Construct
from stage_config import StageConfig

_SCHEDULE = json.loads(
    (pathlib.Path(__file__).parent / "../frontend/src/config/scanSchedule.json").read_text()
)


class OptionsHunterStack(cdk.Stack):
    def __init__(self, scope: Construct, id: str, config: StageConfig, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # ── S3: report storage + static site ──────────────────────────────────
        # NOTE: prod was previously deployed as bucket "options-hunter-reports"
        # (stack "OptionsHunterStack"). The new prod bucket is
        # "options-hunter-reports-prod". On first prod deploy, copy any reports
        # you want to keep from the old bucket before tearing down the old stack.

        bucket = s3.Bucket(
            self,
            "ReportsBucket",
            bucket_name=config.bucket_name,
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
            function_name=config.function_name,
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
                "STAGE": config.stage,
                "REPORTS_BUCKET": bucket.bucket_name,
                "GAINER_MIN_GAIN_PCT": "500",
                "GAINER_CACHE_FLOOR_PCT": "100",
                "GAINER_PUT_MAX_COST_PCT": "0.05",
                "GAINER_PUT_MAX_IV": "2.00",
                "GAINER_PUT_MIN_OI": "10",
                "GAINER_PUT_MIN_DTE": "60",
                "GAINER_PUT_MAX_DTE": "1000",
            },
        )

        bucket.grant_put(scanner_fn)
        bucket.grant_read(scanner_fn)

        # ── EventBridge Scheduler: prod only ─────────────────────────────────
        # Beta is invoked directly by CI integration tests — no cron needed.

        if config.enable_scheduler:
            scheduler_role = iam.Role(
                self,
                "SchedulerRole",
                assumed_by=iam.ServicePrincipal("scheduler.amazonaws.com"),
            )
            scanner_fn.grant_invoke(scheduler_role)

            scheduler.CfnSchedule(
                self,
                "OpenScanSchedule",
                schedule_expression=f"cron({_SCHEDULE['openScanEt']['minute']} {_SCHEDULE['openScanEt']['hour']} ? * MON-FRI *)",
                schedule_expression_timezone="America/New_York",
                flexible_time_window=scheduler.CfnSchedule.FlexibleTimeWindowProperty(
                    mode="OFF",
                ),
                target=scheduler.CfnSchedule.TargetProperty(
                    arn=scanner_fn.function_arn,
                    role_arn=scheduler_role.role_arn,
                ),
            )

            scheduler.CfnSchedule(
                self,
                "MidayScanSchedule",
                schedule_expression=f"cron({_SCHEDULE['middayScanEt']['minute']} {_SCHEDULE['middayScanEt']['hour']} ? * MON-FRI *)",
                schedule_expression_timezone="America/New_York",
                flexible_time_window=scheduler.CfnSchedule.FlexibleTimeWindowProperty(
                    mode="OFF",
                ),
                target=scheduler.CfnSchedule.TargetProperty(
                    arn=scanner_fn.function_arn,
                    role_arn=scheduler_role.role_arn,
                ),
            )

        # ── Outputs ───────────────────────────────────────────────────────────

        cdk.CfnOutput(self, "Stage",               value=config.stage)
        cdk.CfnOutput(self, "SiteUrl",             value=bucket.bucket_website_url)
        cdk.CfnOutput(self, "BucketName",          value=bucket.bucket_name)
        cdk.CfnOutput(self, "ScannerFunctionArn",  value=scanner_fn.function_arn)
        cdk.CfnOutput(self, "ScannerFunctionName", value=scanner_fn.function_name)
