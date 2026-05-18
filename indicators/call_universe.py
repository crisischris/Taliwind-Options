from __future__ import annotations

import json
import logging
from datetime import date
from typing import Any

import yfinance as yf

from . import cache

logger = logging.getLogger(__name__)

_S3_KEY_TPL = "cache/call-universe/{date}.json"

_UNIVERSE_ETFS = [
    "ARKK",   # ARK Innovation — AI, genomics, fintech
    "ARKX",   # ARK Space Exploration
    "ARKQ",   # ARK Autonomous Tech & Robotics
    "SMH",    # VanEck Semiconductors — AI hardware layer
    "AIQ",    # Global X AI & Technology
    "BOTZ",   # Global X Robotics & AI
    "ROKT",   # Kensho Final Frontiers — space / deep tech
]


def get_tickers(s3: Any = None, bucket: str | None = None) -> list[str]:
    """Return deduplicated sorted list of tickers held across the call universe ETFs.

    Check order: file cache → S3 → Yahoo Finance. Writes back to file cache and S3.
    S3 format: {"tickers": [...], "names": {...}} — plain-list entries are treated as
    stale (pre-names) and trigger a fresh yfinance fetch.
    """
    cached = cache.get("call_universe")
    if cached is not None:
        logger.info("Call universe: file cache hit (%d tickers)", len(cached))
        return cached

    if s3 and bucket:
        s3_key = _S3_KEY_TPL.format(date=date.today().isoformat())
        try:
            obj = s3.get_object(Bucket=bucket, Key=s3_key)
            payload = json.loads(obj["Body"].read())
            if isinstance(payload, dict):
                tickers = payload["tickers"]
                _merge_etf_names(payload.get("names", {}))
                logger.info("Call universe: S3 cache hit (%d tickers)", len(tickers))
                cache.set("call_universe", tickers)
                return tickers
            logger.info("Call universe: S3 entry is old format — re-fetching to capture names")
        except Exception as e:
            logger.info("Call universe: S3 miss or read failed (%s) — fetching from Yahoo Finance", e)

    tickers, names = _fetch_from_yf()

    if tickers:
        cache.set("call_universe", tickers)
        _merge_etf_names(names)
        if s3 and bucket:
            try:
                s3.put_object(
                    Bucket=bucket,
                    Key=_S3_KEY_TPL.format(date=date.today().isoformat()),
                    Body=json.dumps({"tickers": tickers, "names": names}),
                    ContentType="application/json",
                )
                logger.info("Call universe cached to S3 (%d tickers, %d names)", len(tickers), len(names))
            except Exception as e:
                logger.warning("Call universe: S3 write failed: %s", e)

    return tickers


def _merge_etf_names(etf_names: dict[str, str]) -> None:
    existing = cache.get("company_names") or {}
    cache.set("company_names", {**etf_names, **existing})


def _fetch_from_yf() -> tuple[list[str], dict[str, str]]:
    tickers: set[str] = set()
    names: dict[str, str] = {}
    for etf in _UNIVERSE_ETFS:
        try:
            holdings = yf.Ticker(etf).funds_data.top_holdings
            count = 0
            for sym, row in holdings.iterrows():
                sym = str(sym).strip().replace(".", "-")
                if sym and sym not in ("-", "nan", "None"):
                    tickers.add(sym)
                    count += 1
                    name = str(row.get("Name", "") or "").strip()
                    if name:
                        names[sym] = name
            logger.info("%s: %d tickers fetched via Yahoo Finance", etf, count)
        except Exception as e:
            logger.error("Failed to fetch %s holdings: %s", etf, e)
    return sorted(tickers), names
