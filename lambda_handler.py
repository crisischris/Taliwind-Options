"""
AWS Lambda entry point for the tailwind-options scanner.

Runs one scanner per theme and writes a JSON report + manifest for each theme
that produces signals, partitioned under puts/{theme-id}/ and calls/{theme-id}/.
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
        from tailwind_options.call_universe import get_tickers
        from tailwind_options.constants import (
            AI_MOMENTUM, BREAKOUTS, BROKEN_MOMENTUM, DRAM_MEMORY, MEAN_REVERSION,
            SECTOR_ROTATION, SHORT_SQUEEZE, SPACE, VALUATION_GRAVITY,
        )
        from tailwind_options.report import write_theme_report_to_s3
        from tailwind_options.sources.breakout_calls import BreakoutCallScanner
        from tailwind_options.sources.broken_momentum import BrokenMomentumScanner
        from tailwind_options.sources.dram_memory_calls import DramMemoryCallScanner
        from tailwind_options.sources.gainer_puts import GainerPutScanner
        from tailwind_options.sources.sector_rotation_calls import SectorRotationCallScanner
        from tailwind_options.sources.short_squeeze_calls import ShortSqueezeCallScanner
        from tailwind_options.sources.space_calls import SpaceCallScanner
        from tailwind_options.sources.trend_calls import TrendCallScanner
        from tailwind_options.sources.valuation_gravity import ValuationGravityScanner

        written: list[str] = []

        # ── Put scanners ──────────────────────────────────────────────────────
        put_scanners: list[tuple[str, Any]] = [
            (MEAN_REVERSION,    GainerPutScanner()),
            (BROKEN_MOMENTUM,   BrokenMomentumScanner()),
            (VALUATION_GRAVITY, ValuationGravityScanner()),
        ]
        for theme_id, scanner in put_scanners:
            try:
                signals = [s for s in scanner.check() if s.triggered]
                if signals:
                    write_theme_report_to_s3(signals, s3, bucket_name, timestamp, "puts", theme_id)
                    written.append(f"{len(signals)} {theme_id} puts")
                    log.info("%s: %d signals written", theme_id, len(signals))
                else:
                    log.info("%s: no qualifying signals", theme_id)
            except Exception:
                log.exception("Put scanner %s failed", theme_id)

        # ── Call scanners ─────────────────────────────────────────────────────
        # TrendCallScanner gets the S3-backed universe for efficient caching;
        # all other call scanners are self-contained.
        universe_tickers = get_tickers(s3=s3, bucket=bucket_name)
        call_scanners: list[tuple[str, Any]] = [
            (AI_MOMENTUM,       TrendCallScanner(universe=universe_tickers)),
            (BREAKOUTS,         BreakoutCallScanner()),
            (SHORT_SQUEEZE,     ShortSqueezeCallScanner()),
            (SECTOR_ROTATION,   SectorRotationCallScanner()),
            (DRAM_MEMORY,       DramMemoryCallScanner()),
            (SPACE,             SpaceCallScanner()),
        ]
        for theme_id, scanner in call_scanners:
            try:
                signals = [s for s in scanner.check() if s.triggered]
                if signals:
                    write_theme_report_to_s3(signals, s3, bucket_name, timestamp, "calls", theme_id)
                    written.append(f"{len(signals)} {theme_id} calls")
                    log.info("%s: %d signals written", theme_id, len(signals))
                else:
                    log.info("%s: no qualifying signals", theme_id)
            except Exception:
                log.exception("Call scanner %s failed", theme_id)

        if not written:
            log.info("No qualifying signals found — no reports written")
            return {"statusCode": 200, "body": "no signals"}

        log.info("Done: %s", ", ".join(written))
        return {"statusCode": 200, "body": ", ".join(written) + " written to S3"}

    except Exception:
        log.exception("Scanner failed")
        return {"statusCode": 500, "body": "error"}
