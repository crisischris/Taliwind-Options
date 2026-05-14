"""
AWS Lambda entry point for the options-hunter scanner.

Single invocation that runs the put scanner and writes the JSON report + manifest to S3.
"""
import json
import logging
import os

import boto3

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)


def handler(event: dict, context) -> dict:
    logger.info("Invocation received: %s", json.dumps(event))

    from indicators.sources.gainer_puts import GainerPutScanner

    logger.info("Running daily gainer put scan")
    signals = [s for s in GainerPutScanner().check() if s.triggered]

    if not signals:
        logger.info("No qualifying puts found")
        return {"statusCode": 200, "body": "no signals"}

    _write_report_to_s3(signals)
    return {"statusCode": 200, "body": f"{len(signals)} signals written to S3"}


def _write_report_to_s3(signals: list) -> None:
    from datetime import datetime
    from indicators.report import _build_report, _REPORTS_DIR

    bucket_name = os.environ["REPORTS_BUCKET"]
    s3 = boto3.client("s3")

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    report_id = f"put-scan-{timestamp}"

    # Build the same JSON structure as the local run
    data = _build_report(signals, report_id, timestamp)
    s3.put_object(
        Bucket=bucket_name,
        Key=f"{report_id}.json",
        Body=json.dumps(data, indent=2),
        ContentType="application/json",
    )
    logger.info("Report written to s3://%s/%s.json", bucket_name, report_id)

    # Update manifest.json
    try:
        existing = json.loads(
            s3.get_object(Bucket=bucket_name, Key="manifest.json")["Body"].read()
        )
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
    logger.info("manifest.json updated (%d entries)", len(existing))
