"""Shared helpers used by all option scanner classes."""
from __future__ import annotations

import logging
import math
from typing import Callable, TypeVar

import pandas as pd
import yfinance as yf

from .. import cache

logger = logging.getLogger(__name__)

T = TypeVar("T")

RISK_FREE_RATE: float = 0.05
TERM_BOUNDARY_DAYS: int = 180


def norm_cdf(x: float) -> float:
    return (1.0 + math.erf(x / math.sqrt(2.0))) / 2.0


def prob_itm_call(S: float, K: float, T: float, sigma: float) -> float:
    """Black-Scholes risk-neutral probability that a call expires ITM (N(d2))."""
    if T <= 0 or sigma <= 0 or S <= 0 or K <= 0:
        return 0.0
    d2 = (math.log(S / K) + (RISK_FREE_RATE - 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
    return norm_cdf(d2)


def prob_itm_put(S: float, K: float, T: float, sigma: float) -> float:
    """Black-Scholes risk-neutral probability that a put expires ITM (N(-d2))."""
    if T <= 0 or sigma <= 0 or S <= 0 or K <= 0:
        return 0.0
    d2 = (math.log(S / K) + (RISK_FREE_RATE - 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
    return norm_cdf(-d2)


def fetch_price(ticker: str) -> float | None:
    """Return the current price for ticker, using the in-process cache."""
    key = f"price_{ticker}"
    cached = cache.get(key)
    if cached is not None:
        return cached
    price = yf.Ticker(ticker).fast_info.last_price
    if price:
        cache.set(key, float(price))
    return float(price) if price else None


def filter_option_chain(
    chain: pd.DataFrame,
    current_price: float,
    min_oi: int,
    max_cost_pct: float,
    max_iv: float,
) -> pd.DataFrame:
    """
    Filter an option chain DataFrame to OTM contracts that pass cost, IV, and
    liquidity thresholds. Returns the matching subset with an added
    'effective_ask' column (ask if non-zero, else lastPrice).
    """
    effective_ask = chain["ask"].where(chain["ask"] > 0, chain["lastPrice"])
    liquid = (
        (chain["openInterest"] >= min_oi) |
        (chain["volume"] > 0) |
        (chain["lastPrice"] > 0)
    )
    mask = (
        (~chain["inTheMoney"]) &
        (effective_ask > 0) &
        (effective_ask / current_price <= max_cost_pct) &
        (chain["impliedVolatility"] <= max_iv) &
        liquid
    )
    result = chain[mask].copy()
    result["effective_ask"] = effective_ask[mask]
    return result


def cache_or_compute(key: str, compute: Callable[[], T]) -> T:
    """Return the cached value for key, or call compute(), cache, and return the result."""
    hit = cache.get(key)
    if hit is not None:
        return hit  # type: ignore[return-value]
    result = compute()
    cache.set(key, result)
    return result


def format_option_message(c: dict) -> str:
    """Consistent one-line summary used as the Signal message for every option."""
    return (
        f"{c['return_multiple']:.0f}x return | "
        f"${c['ask']:.2f} ask | "
        f"${c['strike']:.0f} strike | "
        f"Exp {c['expiry']}"
    )


def filter_by_momentum(
    universe: list[str],
    lookback_days: int,
    min_pct: float,
    cache_key: str,
) -> list[tuple[str, float]]:
    """
    Download `lookback_days` of history for `universe`, return tickers whose
    gain over the period is >= min_pct, sorted descending by gain. Results
    are cached under `cache_key`.
    """
    cached = cache.get(cache_key)
    if cached is not None:
        logger.info("Using cached momentum data (%s)", cache_key)
        return cached

    logger.info("Fetching %d-day history for %d tickers...", lookback_days, len(universe))
    try:
        data = yf.download(
            universe,
            period=f"{lookback_days}d",
            auto_adjust=True,
            progress=False,
            threads=True,
        )
    except Exception as e:
        logger.error("Momentum bulk history download failed: %s", e)
        return []

    closes = data["Close"] if "Close" in data.columns else data.xs("Close", axis=1, level=0)
    threshold = min_pct / 100.0
    result: list[tuple[str, float]] = []

    for ticker in closes.columns:
        series = closes[ticker].dropna()
        if len(series) < 2 or series.iloc[0] <= 0:
            continue
        gain = (series.iloc[-1] - series.iloc[0]) / series.iloc[0]
        if gain >= threshold:
            result.append((ticker, round(gain * 100, 2)))

    result.sort(key=lambda x: x[1], reverse=True)
    cache.set(cache_key, result)
    return result


def bucket_candidates(candidates: list[dict]) -> list[dict]:
    """
    Sort and cap candidates into short-dated, long-dated, and moonshot buckets.
    Expects each candidate dict to have: term, prob_itm, score, ask, contract,
    and return_multiple keys.
    """
    sort_key = lambda c: (-c["score"], c["ask"])
    short = sorted(
        [c for c in candidates if c["term"] == "short" and c["prob_itm"] >= 0.01],
        key=sort_key,
    )[:10]
    long = sorted(
        [c for c in candidates if c["term"] == "long" and c["prob_itm"] >= 0.01],
        key=sort_key,
    )[:10]
    already_shown = {c["contract"] for c in short + long}
    moonshots = [
        {**c, "term": "moonshot"}
        for c in sorted(
            [c for c in candidates if c["contract"] not in already_shown and c["prob_itm"] >= 0.01],
            key=lambda c: -c["return_multiple"],
        )[:5]
    ]
    return short + long + moonshots
