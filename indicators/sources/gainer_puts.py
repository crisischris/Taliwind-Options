from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from datetime import date, timedelta

import yfinance as yf

from .. import cache
from ..config import config
from ..universe import get_universe
from .base import Indicator, Signal

logger = logging.getLogger(__name__)

_RISK_FREE_RATE = 0.05
_TERM_BOUNDARY_DAYS = 180  # 6 months — short below, long at or above


def _norm_cdf(x: float) -> float:
    return (1.0 + math.erf(x / math.sqrt(2.0))) / 2.0


def _prob_itm_put(S: float, K: float, T: float, sigma: float) -> float:
    """Black-Scholes risk-neutral probability that a put expires ITM (N(-d2))."""
    if T <= 0 or sigma <= 0 or S <= 0 or K <= 0:
        return 0.0
    d2 = (math.log(S / K) + (_RISK_FREE_RATE - 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    return _norm_cdf(-d2)


@dataclass
class GainerPutScanner(Indicator):
    """
    Scans the S&P 500 + NASDAQ 100 universe for tickers with extreme 1-year gains,
    then surfaces cheap OTM puts on those tickers as potential reversion plays.
    """

    universe: list[str] = field(default_factory=get_universe)

    def check(self) -> list[Signal]:
        # Warm cache for all tickers above the floor so filter changes don't require re-scraping
        all_gainers = self._find_gainers(config.gainer_cache_floor_pct)
        if not all_gainers:
            logger.info("No tickers found with >= %.0f%% gain over past year", config.gainer_cache_floor_pct)
            return []

        report_gainers = [(t, g) for t, g in all_gainers if g >= config.gainer_min_gain_pct]
        logger.info(
            "Cache floor: %d ticker(s) >= %.0f%% | Report threshold: %d ticker(s) >= %.0f%%",
            len(all_gainers), config.gainer_cache_floor_pct,
            len(report_gainers), config.gainer_min_gain_pct,
        )

        signals: list[Signal] = []
        for ticker, gain_pct in all_gainers:
            try:
                current_price = self._fetch_price(ticker)
                if not current_price:
                    continue
                puts = self._scan_puts(ticker, gain_pct, current_price)
                if gain_pct >= config.gainer_min_gain_pct:
                    signals.extend(puts)
            except Exception as e:
                logger.error("Error scanning puts for %s: %s", ticker, e)

        return signals

    def _find_gainers(self, threshold_pct: float) -> list[tuple[str, float]]:
        cached = cache.get("history_1y")
        if cached is not None:
            logger.info("Using cached 1-year history")
            closes = cached
        else:
            logger.info("Fetching 1-year history for %d tickers...", len(self.universe))
            try:
                data = yf.download(
                    self.universe,
                    period="1y",
                    auto_adjust=True,
                    progress=False,
                    threads=True,
                )
            except Exception as e:
                logger.error("Bulk history download failed: %s", e)
                return []

            closes = data["Close"] if "Close" in data.columns else data.xs("Close", axis=1, level=0)
            cache.set("history_1y", closes)

        gainers: list[tuple[str, float]] = []
        threshold = threshold_pct / 100.0

        for ticker in closes.columns:
            series = closes[ticker].dropna()
            if len(series) < 2:
                continue
            start_price = series.iloc[0]
            end_price = series.iloc[-1]
            if start_price <= 0:
                continue
            gain = (end_price - start_price) / start_price
            if gain >= threshold:
                gainers.append((ticker, gain * 100))

        return sorted(gainers, key=lambda x: x[1], reverse=True)

    def _fetch_price(self, ticker: str) -> float | None:
        key = f"price_{ticker}"
        cached = cache.get(key)
        if cached is not None:
            return cached
        price = yf.Ticker(ticker).fast_info.last_price
        if price:
            cache.set(key, float(price))
        return float(price) if price else None

    def _scan_puts(self, ticker: str, gain_pct: float, current_price: float) -> list[Signal]:
        today = date.today()
        min_exp = today + timedelta(days=config.gainer_put_min_dte)
        max_exp = today + timedelta(days=config.gainer_put_max_dte)

        exp_key = f"expirations_{ticker}"
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
            logger.debug("%s: no expirations in %d–%d DTE window", ticker, config.gainer_put_min_dte, config.gainer_put_max_dte)
            return []

        # Collect all qualifying candidates across every expiration
        candidates: list[dict] = []
        for expiry in expirations:
            chain_key = f"puts_{ticker}_{expiry}"
            puts = cache.get(chain_key)
            if puts is None:
                try:
                    puts = t.option_chain(expiry).puts
                    cache.set(chain_key, puts)
                except Exception as e:
                    logger.error("%s: failed to fetch options for %s: %s", ticker, expiry, e)
                    continue

            # Use lastPrice as fallback when ask is 0 (yfinance returns 0 after hours)
            effective_ask = puts["ask"].where(puts["ask"] > 0, puts["lastPrice"])
            # Liquidity: OI threshold, or any volume today, or any historical trade (lastPrice > 0)
            # The last condition catches long-dated / LEAP puts that are quote-able but thinly traded
            liquid = (
                (puts["openInterest"] >= config.gainer_put_min_oi) |
                (puts["volume"] > 0) |
                (puts["lastPrice"] > 0)
            )

            mask = (
                (~puts["inTheMoney"]) &
                (effective_ask > 0) &
                (effective_ask / current_price <= config.gainer_put_max_cost_pct) &
                (puts["impliedVolatility"] <= config.gainer_put_max_iv) &
                liquid
            )
            for _, row in puts[mask].iterrows():
                ask = row["ask"] if row["ask"] > 0 else row["lastPrice"]
                breakeven = row["strike"] - ask
                breakeven_drop_pct = (current_price - breakeven) / current_price * 100
                return_multiple = row["strike"] / ask
                dte = (date.fromisoformat(expiry) - today).days
                T = dte / 365.0
                prob_itm = _prob_itm_put(current_price, row["strike"], T, row["impliedVolatility"])
                score = return_multiple * prob_itm
                term = "short" if dte < _TERM_BOUNDARY_DAYS else "long"
                candidates.append({
                    "ticker": ticker,
                    "gain_pct": gain_pct,
                    "current_price": current_price,
                    "strike": row["strike"],
                    "expiry": expiry,
                    "ask": ask,
                    "bid": row["bid"],
                    "iv": row["impliedVolatility"],
                    "open_interest": row["openInterest"],
                    "volume": row.get("volume"),
                    "contract": row["contractSymbol"],
                    "breakeven_drop_pct": breakeven_drop_pct,
                    "return_multiple": return_multiple,
                    "prob_itm": prob_itm,
                    "score": score,
                    "dte": dte,
                    "term": term,
                })

        # Sort and cap separately per term so each bucket gets its best 10
        _sort_key = lambda c: (-c["score"], c["ask"])
        short = sorted([c for c in candidates if c["term"] == "short"], key=_sort_key)[:10]
        long = sorted([c for c in candidates if c["term"] == "long"], key=_sort_key)[:10]

        # Moonshot bucket: top 5 by pure return_multiple, excluding anything already surfaced above
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
                title=f"Put Opportunity: {ticker}",
                subtitle=f"{ticker} (+{gain_pct:.0f}% YTD)",
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
