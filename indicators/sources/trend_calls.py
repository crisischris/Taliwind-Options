from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from datetime import date, timedelta

import yfinance as yf

from .. import cache
from ..config import config
from .base import Indicator, Signal

logger = logging.getLogger(__name__)

_RISK_FREE_RATE = 0.05
_TERM_BOUNDARY_DAYS = 180


def _norm_cdf(x: float) -> float:
    return (1.0 + math.erf(x / math.sqrt(2.0))) / 2.0


def _prob_itm_call(S: float, K: float, T: float, sigma: float) -> float:
    """Black-Scholes risk-neutral probability that a call expires ITM (N(d2))."""
    if T <= 0 or sigma <= 0 or S <= 0 or K <= 0:
        return 0.0
    d2 = (math.log(S / K) + (_RISK_FREE_RATE - 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
    return _norm_cdf(d2)


@dataclass
class TrendCallScanner(Indicator):
    """
    Scans ARK ETF holdings for tickers with strong recent momentum,
    then surfaces cheap OTM calls as trend-continuation plays.
    """

    universe: list[str] = field(default_factory=list)

    def check(self) -> list[Signal]:
        if not self.universe:
            logger.info("TrendCallScanner: empty universe, skipping")
            return []

        momentum_tickers = self._filter_by_momentum()
        if not momentum_tickers:
            logger.info(
                "No universe tickers passed momentum filter (>= %.0f%% in %d days)",
                config.trend_call_momentum_min_pct,
                config.trend_call_momentum_days,
            )
            return []

        logger.info("%d universe tickers passed momentum filter", len(momentum_tickers))

        signals: list[Signal] = []
        for ticker, momentum_pct in momentum_tickers:
            try:
                current_price = self._fetch_price(ticker)
                if not current_price:
                    continue
                signals.extend(self._scan_calls(ticker, momentum_pct, current_price))
            except Exception as e:
                logger.error("Error scanning calls for %s: %s", ticker, e)

        return signals

    def _filter_by_momentum(self) -> list[tuple[str, float]]:
        key = f"call_universe_momentum_{config.trend_call_momentum_days}d"
        cached = cache.get(key)
        if cached is not None:
            logger.info("Using cached call universe momentum data")
            return cached

        logger.info(
            "Fetching %d-day history for %d universe tickers...",
            config.trend_call_momentum_days,
            len(self.universe),
        )
        try:
            data = yf.download(
                self.universe,
                period=f"{config.trend_call_momentum_days}d",
                auto_adjust=True,
                progress=False,
                threads=True,
            )
        except Exception as e:
            logger.error("ARK bulk history download failed: %s", e)
            return []

        closes = data["Close"] if "Close" in data.columns else data.xs("Close", axis=1, level=0)
        threshold = config.trend_call_momentum_min_pct / 100.0
        result: list[tuple[str, float]] = []

        for ticker in closes.columns:
            series = closes[ticker].dropna()
            if len(series) < 2 or series.iloc[0] <= 0:
                continue
            gain = (series.iloc[-1] - series.iloc[0]) / series.iloc[0]
            if gain >= threshold:
                result.append((ticker, round(gain * 100, 2)))

        result.sort(key=lambda x: x[1], reverse=True)
        cache.set(key, result)
        return result

    def _fetch_price(self, ticker: str) -> float | None:
        key = f"price_{ticker}"
        cached = cache.get(key)
        if cached is not None:
            return cached
        price = yf.Ticker(ticker).fast_info.last_price
        if price:
            cache.set(key, float(price))
        return float(price) if price else None

    def _scan_calls(self, ticker: str, momentum_pct: float, current_price: float) -> list[Signal]:
        today = date.today()
        min_exp = today + timedelta(days=config.trend_call_min_dte)
        max_exp = today + timedelta(days=config.trend_call_max_dte)

        exp_key = f"call_expirations_{ticker}"
        expirations = cache.get(exp_key)
        if expirations is None:
            t = yf.Ticker(ticker)
            expirations = [
                exp for exp in t.options
                if min_exp <= date.fromisoformat(exp) <= max_exp
            ]
            cache.set(exp_key, expirations)
        else:
            t = yf.Ticker(ticker)

        if not expirations:
            logger.debug(
                "%s: no expirations in %d–%d DTE window",
                ticker, config.trend_call_min_dte, config.trend_call_max_dte,
            )
            return []

        candidates: list[dict] = []
        for expiry in expirations:
            chain_key = f"calls_{ticker}_{expiry}"
            calls = cache.get(chain_key)
            if calls is None:
                try:
                    calls = t.option_chain(expiry).calls
                    cache.set(chain_key, calls)
                except Exception as e:
                    logger.error("%s: failed to fetch calls for %s: %s", ticker, expiry, e)
                    continue

            effective_ask = calls["ask"].where(calls["ask"] > 0, calls["lastPrice"])
            liquid = (
                (calls["openInterest"] >= config.trend_call_min_oi) |
                (calls["volume"] > 0) |
                (calls["lastPrice"] > 0)
            )
            mask = (
                (~calls["inTheMoney"]) &
                (effective_ask > 0) &
                (effective_ask / current_price <= config.trend_call_max_cost_pct) &
                (calls["impliedVolatility"] <= config.trend_call_max_iv) &
                liquid
            )

            for _, row in calls[mask].iterrows():
                ask = row["ask"] if row["ask"] > 0 else row["lastPrice"]
                breakeven = row["strike"] + ask
                breakeven_rise_pct = (breakeven - current_price) / current_price * 100
                return_multiple = row["strike"] / ask
                dte = (date.fromisoformat(expiry) - today).days
                T = dte / 365.0
                prob_itm = _prob_itm_call(current_price, row["strike"], T, row["impliedVolatility"])
                score = return_multiple * prob_itm
                term = "short" if dte < _TERM_BOUNDARY_DAYS else "long"
                candidates.append({
                    "ticker": ticker,
                    "momentum_pct": momentum_pct,
                    "current_price": current_price,
                    "strike": row["strike"],
                    "expiry": expiry,
                    "ask": ask,
                    "bid": row["bid"],
                    "iv": row["impliedVolatility"],
                    "open_interest": row["openInterest"],
                    "volume": row.get("volume"),
                    "contract": row["contractSymbol"],
                    "breakeven_rise_pct": breakeven_rise_pct,
                    "return_multiple": return_multiple,
                    "prob_itm": prob_itm,
                    "score": score,
                    "dte": dte,
                    "term": term,
                })

        _sort_key = lambda c: (-c["score"], c["ask"])
        short = sorted([c for c in candidates if c["term"] == "short"], key=_sort_key)[:10]
        long = sorted([c for c in candidates if c["term"] == "long"], key=_sort_key)[:10]

        already_shown = {c["contract"] for c in short + long}
        moonshots = [
            {**c, "term": "moonshot"}
            for c in sorted(
                [c for c in candidates if c["contract"] not in already_shown],
                key=lambda c: -c["return_multiple"],
            )[:5]
        ]

        candidates = short + long + moonshots

        return [
            Signal(
                triggered=True,
                title=f"Call Opportunity: {ticker}",
                subtitle=f"{ticker} (+{momentum_pct:.0f}% {config.trend_call_momentum_days}d)",
                message=(
                    f"{c['return_multiple']:.0f}x return | "
                    f"${c['ask']:.2f} ask | "
                    f"${c['strike']:.0f} strike | "
                    f"Exp {c['expiry']}"
                ),
                data=c,
            )
            for c in candidates
        ]
