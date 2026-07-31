from __future__ import annotations

import logging
import re
from io import StringIO

import httpx
import pandas as pd

from . import cache

logger = logging.getLogger(__name__)

_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; tailwind-options-bot/1.0)"}

# US common-stock tickers: letters only, with an optional single-letter share-class
# suffix (e.g. BRK-B). Rejects foreign listings pulled in by Wikipedia table drift
# (e.g. 005930-KS, 6383-T, ABBN-SW) that Yahoo Finance 404s on every run.
_US_TICKER_RE = re.compile(r"^[A-Z]+(-[A-Z])?$")


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
    names: dict[str, str] = {}

    try:
        sp500 = _read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")[0]
        symbols = sp500["Symbol"].str.replace(".", "-", regex=False).tolist()
        tickers += symbols
        for sym, name in zip(symbols, sp500["Security"].tolist()):
            names[sym] = name
        logger.info("Loaded %d S&P 500 tickers", len(symbols))
    except Exception as e:
        logger.error("Failed to fetch S&P 500 universe: %s", e)

    try:
        nasdaq = _read_html("https://en.wikipedia.org/wiki/Nasdaq-100")[5]
        nasdaq_tickers = nasdaq["Ticker"].tolist()
        tickers += nasdaq_tickers
        for sym, name in zip(nasdaq_tickers, nasdaq["Company"].tolist()):
            if sym not in names:
                names[sym] = name
        logger.info("Loaded %d NASDAQ 100 tickers", len(nasdaq_tickers))
    except Exception as e:
        logger.error("Failed to fetch NASDAQ 100 universe: %s", e)

    deduped = list(dict.fromkeys(tickers))
    result = [t for t in deduped if _US_TICKER_RE.fullmatch(t)]
    if len(result) < len(deduped):
        logger.info("Dropped %d non-US-listed ticker(s)", len(deduped) - len(result))
    cache.set("universe", result)
    # Merge Wikipedia names on top of any ETF names already in cache (ETF names are the floor)
    existing = cache.get("company_names") or {}
    cache.set("company_names", {**existing, **names})
    logger.info("Universe: %d unique tickers total", len(result))
    return result


def get_company_names() -> dict[str, str]:
    cached = cache.get("company_names")
    if cached is not None:
        return cached
    get_universe()  # populates company_names with S&P 500 + NASDAQ 100 names
    return cache.get("company_names") or {}
