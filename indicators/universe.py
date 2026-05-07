from __future__ import annotations

import logging
from io import StringIO

import httpx
import pandas as pd

from . import cache

logger = logging.getLogger(__name__)

_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; indicators-bot/1.0)"}


def _read_html(url: str) -> list:
    resp = httpx.get(url, headers=_HEADERS, follow_redirects=True, timeout=15)
    resp.raise_for_status()
    return pd.read_html(StringIO(resp.text))


def get_universe() -> list[str]:
    cached = cache.get("universe")
    if cached is not None:
        logger.info("Universe: %d tickers (cached)", len(cached))
        return cached

    tickers: list[str] = []

    try:
        sp500 = _read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")[0]
        tickers += sp500["Symbol"].str.replace(".", "-", regex=False).tolist()
        logger.info("Loaded %d S&P 500 tickers", len(tickers))
    except Exception as e:
        logger.error("Failed to fetch S&P 500 universe: %s", e)

    try:
        nasdaq = _read_html("https://en.wikipedia.org/wiki/Nasdaq-100")[5]
        nasdaq_tickers = nasdaq["Ticker"].tolist()
        tickers += nasdaq_tickers
        logger.info("Loaded %d NASDAQ 100 tickers", len(nasdaq_tickers))
    except Exception as e:
        logger.error("Failed to fetch NASDAQ 100 universe: %s", e)

    result = list(dict.fromkeys(tickers))
    cache.set("universe", result)
    logger.info("Universe: %d unique tickers total", len(result))
    return result
