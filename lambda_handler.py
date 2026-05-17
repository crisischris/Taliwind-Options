"""
AWS Lambda entry point for the tailwind-options scanner.

Single invocation that runs the put scanner and writes the JSON report + manifest to S3.
"""
import json
import logging
import os
from datetime import datetime, timezone
from typing import Any

import boto3

logging.getLogger().setLevel(logging.INFO)
_logger = logging.getLogger(__name__)


class _InvocationLogger(logging.LoggerAdapter):
    """Prefixes every log line with the Lambda request ID for CloudWatch querying."""
    def process(self, msg: str, kwargs: dict) -> tuple[str, dict]:
        return "[%s] %s" % (self.extra["inv_id"], msg), kwargs


def handler(event: dict, context: Any) -> dict:
    log = _InvocationLogger(_logger, {"inv_id": context.aws_request_id})
    log.info("Invocation received: %s", json.dumps(event))

    bucket_name = os.environ["REPORTS_BUCKET"]
    s3 = boto3.client("s3")
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M")

    try:
        from indicators.call_universe import get_tickers
        from indicators.sources.gainer_puts import GainerPutScanner
        from indicators.sources.trend_calls import TrendCallScanner

        log.info("Running daily gainer put scan")
        put_signals = [s for s in GainerPutScanner().check() if s.triggered]

        log.info("Fetching call universe tickers")
        universe_tickers = get_tickers(s3=s3, bucket=bucket_name)
        log.info("Running trend call scan (%d universe tickers)", len(universe_tickers))
        call_signals = [s for s in TrendCallScanner(universe=universe_tickers).check() if s.triggered]

        if not put_signals and not call_signals:
            log.info("No qualifying signals found — no report written")
            return {"statusCode": 200, "body": "no signals"}

        _write_report_to_s3(put_signals, call_signals, s3, bucket_name, timestamp, log)
        log.info("Done — %d put signals, %d call signals written to S3", len(put_signals), len(call_signals))
        return {"statusCode": 200, "body": f"{len(put_signals)} puts, {len(call_signals)} calls written to S3"}

    except Exception:
        log.exception("Scanner failed")
        return {"statusCode": 500, "body": "error"}


def _write_report_to_s3(
    put_signals: list,
    call_signals: list,
    s3: Any,
    bucket_name: str,
    timestamp: str,
    log: logging.LoggerAdapter,
) -> None:
    from indicators.report import _build_calls_report, _build_puts_report

    if put_signals:
        puts_id = f"put-scan-{timestamp}"
        puts_data = _build_puts_report(put_signals, puts_id, timestamp)
        s3.put_object(
            Bucket=bucket_name,
            Key=f"puts/{puts_id}.json",
            Body=json.dumps(puts_data, indent=2),
            ContentType="application/json",
        )
        log.info("Puts report written to s3://%s/puts/%s.json", bucket_name, puts_id)
        _write_manifest_to_s3(s3, bucket_name, "puts/manifest.json", puts_id, puts_data["summary"], timestamp, log)

    if call_signals:
        calls_id = f"call-scan-{timestamp}"
        calls_data = _build_calls_report(call_signals, calls_id, timestamp)
        s3.put_object(
            Bucket=bucket_name,
            Key=f"calls/{calls_id}.json",
            Body=json.dumps(calls_data, indent=2),
            ContentType="application/json",
        )
        log.info("Calls report written to s3://%s/calls/%s.json", bucket_name, calls_id)
        _write_manifest_to_s3(s3, bucket_name, "calls/manifest.json", calls_id, calls_data["summary"], timestamp, log)


def _write_manifest_to_s3(
    s3: Any,
    bucket_name: str,
    key: str,
    report_id: str,
    summary: dict,
    timestamp: str,
    log: logging.LoggerAdapter,
) -> None:
    try:
        existing = json.loads(s3.get_object(Bucket=bucket_name, Key=key)["Body"].read())
    except Exception:
        existing = []
    existing = [e for e in existing if e.get("id") != report_id]
    existing.insert(0, {"id": report_id, "generated_at": timestamp, **summary})
    s3.put_object(
        Bucket=bucket_name,
        Key=key,
        Body=json.dumps(existing, indent=2),
        ContentType="application/json",
        CacheControl="no-store",
    )
    log.info("%s updated (%d entries)", key, len(existing))
