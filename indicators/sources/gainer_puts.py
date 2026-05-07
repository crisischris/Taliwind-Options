from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date, timedelta

import yfinance as yf

from .. import cache
from ..config import config
from ..universe import get_universe
from .base import Indicator, Signal

logger = logging.getLogger(__name__)


@dataclass
class GainerPutScanner(Indicator):
    """
    Scans the S&P 500 + NASDAQ 100 universe for tickers with extreme 1-year gains,
    then surfaces cheap OTM puts on those tickers as potential reversion plays.
    """

    universe: list[str] = field(default_factory=get_universe)

    def check(self) -> list[Signal]:
        signals: list[Signal] = []

        gainers = self._find_gainers()
        if not gainers:
            logger.info("No tickers found with >= %.0f%% gain over past year", config.gainer_min_gain_pct)
            return signals

        logger.info("Found %d gainer(s): %s", len(gainers), [t for t, _ in gainers])

        for ticker, gain_pct in gainers:
            try:
                current_price = self._fetch_price(ticker)
                if not current_price:
                    continue
                signals.extend(self._scan_puts(ticker, gain_pct, current_price))
            except Exception as e:
                logger.error("Error scanning puts for %s: %s", ticker, e)

        return signals

    def _find_gainers(self) -> list[tuple[str, float]]:
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
        threshold = config.gainer_min_gain_pct / 100.0

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
        signals: list[Signal] = []
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
            return signals

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

            mask = (
                (~puts["inTheMoney"]) &
                (puts["ask"] > 0) &
                (puts["ask"] / current_price <= config.gainer_put_max_cost_pct) &
                (puts["impliedVolatility"] <= config.gainer_put_max_iv) &
                (puts["openInterest"] >= config.gainer_put_min_oi)
            )
            cheap_puts = puts[mask]

            for _, row in cheap_puts.iterrows():
                signals.append(Signal(
                    triggered=True,
                    title=f"Put Opportunity: {ticker}",
                    subtitle=f"{ticker} (+{gain_pct:.0f}% YTD)",
                    message=(
                        f"${row['ask']:.2f} ask | "
                        f"${row['strike']:.0f} strike | "
                        f"IV {row['impliedVolatility']:.0%} | "
                        f"Exp {expiry}"
                    ),
                    data={
                        "ticker": ticker,
                        "gain_pct": gain_pct,
                        "current_price": current_price,
                        "strike": row["strike"],
                        "expiry": expiry,
                        "ask": row["ask"],
                        "bid": row["bid"],
                        "iv": row["impliedVolatility"],
                        "open_interest": row["openInterest"],
                        "volume": row.get("volume"),
                        "contract": row["contractSymbol"],
                    },
                ))

        return signals
