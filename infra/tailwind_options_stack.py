import json
import pathlib

import aws_cdk as cdk
from aws_cdk import (
    aws_certificatemanager as acm,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_cloudwatch as cloudwatch,
    aws_cloudwatch_actions as cloudwatch_actions,
    aws_iam as iam,
    aws_lambda as lambda_,
    aws_route53 as route53,
    aws_route53_targets as targets,
    aws_s3 as s3,
    aws_s3_deployment as s3_deploy,
    aws_scheduler as scheduler,
    aws_sns as sns,
    aws_sns_subscriptions as subscriptions,
)
from constructs import Construct
from stage_config import StageConfig

_SCHEDULE = json.loads(
    (pathlib.Path(__file__).parent / "../frontend/src/config/scanSchedule.json").read_text()
)


class TailwindOptionsStack(cdk.Stack):
    def __init__(self, scope: Construct, id: str, config: StageConfig, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # ── S3: report storage + static site ──────────────────────────────────

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

        # ── CloudFront + custom domain: prod only ─────────────────────────────

        site_url = bucket.bucket_website_url
        distribution = None

        if config.domain_name:
            hosted_zone = route53.HostedZone.from_lookup(
                self, "HostedZone",
                domain_name=config.domain_name,
            )

            certificate = acm.Certificate(
                self, "Certificate",
                domain_name=config.domain_name,
                subject_alternative_names=[f"www.{config.domain_name}"],
                validation=acm.CertificateValidation.from_dns(hosted_zone),
            )

            # Redirect www → apex at the edge
            www_redirect_fn = cloudfront.Function(
                self, "WwwRedirect",
                code=cloudfront.FunctionCode.from_inline(
                    "function handler(event){"
                    "var h=event.request.headers.host.value;"
                    f"if(h.startsWith('www.')){{return{{statusCode:301,"
                    f"statusDescription:'Moved Permanently',"
                    f"headers:{{location:{{value:'https://{config.domain_name}'+event.request.uri}}}}}};}}"
                    "return event.request;}"
                ),
            )

            s3_origin = origins.HttpOrigin(
                bucket.bucket_website_domain_name,
                protocol_policy=cloudfront.OriginProtocolPolicy.HTTP_ONLY,
            )

            distribution = cloudfront.Distribution(
                self, "Distribution",
                domain_names=[config.domain_name, f"www.{config.domain_name}"],
                certificate=certificate,
                default_root_object="index.html",
                default_behavior=cloudfront.BehaviorOptions(
                    origin=s3_origin,
                    viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                    cache_policy=cloudfront.CachePolicy.CACHING_DISABLED,
                    function_associations=[cloudfront.FunctionAssociation(
                        function=www_redirect_fn,
                        event_type=cloudfront.FunctionEventType.VIEWER_REQUEST,
                    )],
                ),
                additional_behaviors={
                    # Content-hashed filenames — safe to cache aggressively
                    "/assets/*": cloudfront.BehaviorOptions(
                        origin=s3_origin,
                        viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                        cache_policy=cloudfront.CachePolicy.CACHING_OPTIMIZED,
                    ),
                },
                # Return index.html for unknown paths so React hash routing works
                error_responses=[
                    cloudfront.ErrorResponse(
                        http_status=403,
                        response_page_path="/index.html",
                        response_http_status=200,
                    ),
                    cloudfront.ErrorResponse(
                        http_status=404,
                        response_page_path="/index.html",
                        response_http_status=200,
                    ),
                ],
            )

            route53.ARecord(
                self, "ApexARecord",
                zone=hosted_zone,
                target=route53.RecordTarget.from_alias(targets.CloudFrontTarget(distribution)),
            )

            route53.ARecord(
                self, "WwwARecord",
                zone=hosted_zone,
                record_name="www",
                target=route53.RecordTarget.from_alias(targets.CloudFrontTarget(distribution)),
            )

            site_url = f"https://{config.domain_name}"

        # ── Monitoring: prod only ─────────────────────────────────────────────

        if config.enable_monitoring:
            alert_topic = sns.Topic(self, "AlertTopic", topic_name="tailwind-options-alerts")
            alert_topic.add_subscription(subscriptions.EmailSubscription(config.alert_email))
            alert_topic.add_subscription(subscriptions.SmsSubscription(config.alert_phone))

            alarm_action = cloudwatch_actions.SnsAction(alert_topic)

            cloudwatch.Alarm(
                self, "LambdaErrorAlarm",
                alarm_name="tailwind-options-lambda-errors",
                alarm_description="Lambda scanner threw an error",
                metric=scanner_fn.metric_errors(period=cdk.Duration.minutes(5), statistic="Sum"),
                threshold=1,
                evaluation_periods=1,
                comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
                treat_missing_data=cloudwatch.TreatMissingData.NOT_BREACHING,
            ).add_alarm_action(alarm_action)

            cloudwatch.Alarm(
                self, "LambdaDurationAlarm",
                alarm_name="tailwind-options-lambda-duration",
                alarm_description="Lambda scanner avg duration > 8 min (timeout is 10 min)",
                metric=scanner_fn.metric_duration(period=cdk.Duration.minutes(5), statistic="Average"),
                threshold=480_000,  # 8 minutes in milliseconds
                evaluation_periods=1,
                comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
                treat_missing_data=cloudwatch.TreatMissingData.NOT_BREACHING,
            ).add_alarm_action(alarm_action)

            cloudwatch.Alarm(
                self, "MissedScanAlarm",
                alarm_name="tailwind-options-missed-scan",
                alarm_description="Scanner did not run — no invocations in 13 hours",
                metric=scanner_fn.metric_invocations(period=cdk.Duration.hours(13), statistic="Sum"),
                threshold=1,
                evaluation_periods=1,
                comparison_operator=cloudwatch.ComparisonOperator.LESS_THAN_THRESHOLD,
                treat_missing_data=cloudwatch.TreatMissingData.BREACHING,
            ).add_alarm_action(alarm_action)

            if distribution:
                cloudwatch.Alarm(
                    self, "CloudFront5xxAlarm",
                    alarm_name="tailwind-options-cloudfront-5xx",
                    alarm_description="CloudFront 5xx error rate > 5%",
                    metric=cloudwatch.Metric(
                        namespace="AWS/CloudFront",
                        metric_name="5xxErrorRate",
                        dimensions_map={
                            "DistributionId": distribution.distribution_id,
                            "Region": "Global",
                        },
                        statistic="Average",
                        period=cdk.Duration.minutes(5),
                    ),
                    threshold=5,
                    evaluation_periods=2,
                    comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
                    treat_missing_data=cloudwatch.TreatMissingData.NOT_BREACHING,
                ).add_alarm_action(alarm_action)

        # ── Outputs ───────────────────────────────────────────────────────────

        cdk.CfnOutput(self, "Stage",               value=config.stage)
        cdk.CfnOutput(self, "SiteUrl",             value=site_url)
        cdk.CfnOutput(self, "BucketName",          value=bucket.bucket_name)
        cdk.CfnOutput(self, "ScannerFunctionArn",  value=scanner_fn.function_arn)
        cdk.CfnOutput(self, "ScannerFunctionName", value=scanner_fn.function_name)
