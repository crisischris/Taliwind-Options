from __future__ import annotations

import json
import logging
from datetime import date
from typing import Any

import yfinance as yf

from . import cache

logger = logging.getLogger(__name__)

_S3_KEY_TPL = "cache/ark-holdings/{date}.json"

_ARK_ETFS = ["ARKK", "ARKX"]


def get_tickers(s3: Any = None, bucket: str | None = None) -> list[str]:
    """Return deduplicated sorted list of tickers held across ARK ETFs.

    Check order: file cache → S3 → Yahoo Finance. Writes back to file cache and S3.
    """
    cached = cache.get("ark_holdings")
    if cached is not None:
        logger.info("ARK holdings: file cache hit (%d tickers)", len(cached))
        return cached

    if s3 and bucket:
        s3_key = _S3_KEY_TPL.format(date=date.today().isoformat())
        try:
            obj = s3.get_object(Bucket=bucket, Key=s3_key)
            tickers = json.loads(obj["Body"].read())
            logger.info("ARK holdings: S3 cache hit (%d tickers)", len(tickers))
            cache.set("ark_holdings", tickers)
            return tickers
        except Exception as e:
            logger.info("ARK holdings: S3 miss or read failed (%s) — fetching from Yahoo Finance", e)

    tickers = _fetch_from_yf()

    if tickers:
        cache.set("ark_holdings", tickers)
        if s3 and bucket:
            try:
                s3_key = _S3_KEY_TPL.format(date=date.today().isoformat())
                s3.put_object(
                    Bucket=bucket,
                    Key=s3_key,
                    Body=json.dumps(tickers),
                    ContentType="application/json",
                )
                logger.info("ARK holdings cached to S3 (%d tickers)", len(tickers))
            except Exception as e:
                logger.warning("ARK holdings: S3 write failed: %s", e)

    return tickers


def _fetch_from_yf() -> list[str]:
    tickers: set[str] = set()
    for etf in _ARK_ETFS:
        try:
            holdings = yf.Ticker(etf).funds_data.top_holdings
            count = 0
            for sym in holdings.index:
                sym = str(sym).strip()
                if sym and sym not in ("-", "nan", "None"):
                    tickers.add(sym)
                    count += 1
            logger.info("%s: %d tickers fetched via Yahoo Finance", etf, count)
        except Exception as e:
            logger.error("Failed to fetch %s holdings: %s", etf, e)
    return sorted(tickers)
