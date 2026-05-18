from __future__ import annotations

import json
import logging
from io import StringIO
from pathlib import Path

import httpx
import pandas as pd

from . import cache

logger = logging.getLogger(__name__)

_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; tailwind-options-bot/1.0)"}
_STATIC_NAMES_PATH = Path(__file__).parent / "data" / "company_names.json"


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

    result = list(dict.fromkeys(tickers))
    cache.set("universe", result)
    cache.set("company_names", names)
    logger.info("Universe: %d unique tickers total", len(result))
    return result


def _load_static_names() -> dict[str, str]:
    try:
        return json.loads(_STATIC_NAMES_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def get_company_names() -> dict[str, str]:
    cached = cache.get("company_names")
    if cached is not None:
        return cached
    get_universe()  # populates company_names as a side effect
    live = cache.get("company_names") or {}
    if live:
        return live
    # Wikipedia fetch failed — fall back to static snapshot
    static = _load_static_names()
    if static:
        logger.warning("Using static company name fallback (%d names)", len(static))
    return static
