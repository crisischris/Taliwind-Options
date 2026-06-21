"""
Shared market-data fetchers. Cached once per calendar day so every scanner in a
single Lambda invocation shares the same underlying data pull.
"""
from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

import yfinance as yf

from . import cache

logger = logging.getLogger(__name__)


def get_universe_ohlcv(universe: list[str], period: str = "1y"):
    """
    Bulk-download daily OHLCV for *universe* over *period*.

    Returns the raw yf.download DataFrame (multi-level columns for multiple
    tickers). Cached per period — first caller downloads, all subsequent callers
    in the same Lambda invocation get the file-cache hit.
    """
    key = f"ohlcv_{period}"
    cached = cache.get(key)
    if cached is not None:
        logger.info("Using cached %s OHLCV data", period)
        return cached

    logger.info("Downloading %s OHLCV for %d tickers...", period, len(universe))
    try:
        data = yf.download(
            universe,
            period=period,
            auto_adjust=True,
            progress=False,
            threads=True,
        )
    except Exception as e:
        logger.error("Bulk OHLCV download failed (%s): %s", period, e)
        return None

    cache.set(key, data)
    return data


def get_universe_info(universe: list[str], workers: int = 20) -> dict[str, dict]:
    """
    Fetch yf.Ticker.info for every ticker using a thread pool.

    Returns a dict keyed by ticker symbol; tickers that fail are omitted.
    Cached for the calendar day so all scanners share one fetch.
    """
    key = "universe_info"
    cached = cache.get(key)
    if cached is not None:
        logger.info("Using cached universe info (%d tickers)", len(cached))
        return cached

    logger.info("Fetching info for %d tickers...", len(universe))

    def _fetch_one(ticker: str) -> tuple[str, dict | None]:
        try:
            return ticker, yf.Ticker(ticker).info
        except Exception as e:
            logger.debug("%s: info fetch failed: %s", ticker, e)
            return ticker, None

    result: dict[str, dict] = {}
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(_fetch_one, t): t for t in universe}
        for future in as_completed(futures):
            ticker, info = future.result()
            if info:
                result[ticker] = info

    cache.set(key, result)
    logger.info("Cached info for %d/%d tickers", len(result), len(universe))
    return result
