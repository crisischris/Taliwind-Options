from __future__ import annotations

import csv
import io
import json
import logging
import urllib.request
from datetime import date
from typing import Any

from . import cache

logger = logging.getLogger(__name__)

_S3_KEY_TPL = "cache/ark-holdings/{date}.json"

_ARK_ETFS = {
    "ARKK": "https://ark-funds.com/wp-content/uploads/funds-etf-csv/ARK_INNOVATION_ETF_ARKK_HOLDINGS.csv",
    "ARKX": "https://ark-funds.com/wp-content/uploads/funds-etf-csv/ARK_SPACE_EXPLORATION_ETF_ARKX_HOLDINGS.csv",
}


def get_tickers(s3: Any = None, bucket: str | None = None) -> list[str]:
    """Return deduplicated sorted list of tickers held across ARK ETFs.

    Check order: file cache → S3 → ARK URLs. Writes back to file cache and S3.
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
            logger.info("ARK holdings: S3 miss or read failed (%s) — fetching from ARK", e)

    tickers = _fetch_from_ark()

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


def _fetch_from_ark() -> list[str]:
    tickers: set[str] = set()
    for name, url in _ARK_ETFS.items():
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                text = resp.read().decode("utf-8")
            reader = csv.DictReader(io.StringIO(text))
            count = 0
            for row in reader:
                ticker = (row.get("ticker") or row.get("Ticker") or "").strip()
                if ticker and ticker != "-":
                    tickers.add(ticker)
                    count += 1
            logger.info("%s: %d tickers fetched from ARK", name, count)
        except Exception as e:
            logger.error("Failed to fetch %s holdings from ARK: %s", name, e)
    return sorted(tickers)
