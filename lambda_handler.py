"""
AWS Lambda entry point for the options-hunter scanner.

Single invocation that runs the put scanner and writes the JSON report + manifest to S3.
"""
import json
import logging
import os
from datetime import datetime

import boto3

logging.getLogger().setLevel(logging.INFO)
_logger = logging.getLogger(__name__)


class _InvocationLogger(logging.LoggerAdapter):
    """Prefixes every log line with the Lambda request ID for CloudWatch querying."""
    def process(self, msg, kwargs):
        return "[%s] %s" % (self.extra["inv_id"], msg), kwargs


def handler(event: dict, context) -> dict:
    log = _InvocationLogger(_logger, {"inv_id": context.aws_request_id})
    log.info("Invocation received: %s", json.dumps(event))

    bucket_name = os.environ["REPORTS_BUCKET"]
    s3 = boto3.client("s3")
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")

    try:
        from indicators.sources.gainer_puts import GainerPutScanner

        log.info("Running daily gainer put scan")
        signals = [s for s in GainerPutScanner().check() if s.triggered]

        if not signals:
            log.info("No qualifying puts found — no report written")
            return {"statusCode": 200, "body": "no signals"}

        _write_report_to_s3(signals, s3, bucket_name, timestamp, log)
        log.info("Done — %d signals written to S3", len(signals))
        return {"statusCode": 200, "body": f"{len(signals)} signals written to S3"}

    except Exception:
        log.exception("Scanner failed")
        return {"statusCode": 500, "body": "error"}


def _write_report_to_s3(signals: list, s3, bucket_name: str, timestamp: str, log) -> None:
    from indicators.report import _build_report

    report_id = f"put-scan-{timestamp}"

    data = _build_report(signals, report_id, timestamp)
    s3.put_object(
        Bucket=bucket_name,
        Key=f"{report_id}.json",
        Body=json.dumps(data, indent=2),
        ContentType="application/json",
    )
    log.info("Report written to s3://%s/%s.json", bucket_name, report_id)

    try:
        existing = json.loads(s3.get_object(Bucket=bucket_name, Key="manifest.json")["Body"].read())
    except s3.exceptions.NoSuchKey:
        existing = []

    existing = [e for e in existing if e.get("id") != report_id]
    existing.insert(0, {"id": report_id, "generated_at": timestamp, **data["summary"]})
    s3.put_object(
        Bucket=bucket_name,
        Key="manifest.json",
        Body=json.dumps(existing, indent=2),
        ContentType="application/json",
    )
    log.info("manifest.json updated (%d entries)", len(existing))
