"""
Short Squeeze call scanner.

Finds S&P 500 + NASDAQ 100 names with short interest above 15% of float that
are already showing positive 30-day price momentum (squeeze in motion). Surfaces
cheap OTM calls as short-dated asymmetric bets on the squeeze continuing.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

import yfinance as yf

from .. import cache
from ..config import ScannerOpts, config
from ..constants import SHORT_SQUEEZE
from ..market_data import get_universe_ohlcv
from ..universe import get_universe
from ._helpers import cache_or_compute, fetch_price
from .base import BaseOptionScanner, Signal

logger = logging.getLogger(__name__)


@dataclass
class ShortSqueezeCallScanner(BaseOptionScanner):
    universe: list[str] = field(default_factory=get_universe)

    # ── BaseOptionScanner template methods ───────────────────────────────────

    @property
    def _option_type(self) -> str:
        return "calls"

    @property
    def _exp_cache_prefix(self) -> str:
        return "call_"

    def _scan_params(self) -> ScannerOpts:
        return config.squeeze

    def _theme_fields(self, ticker: str, meta: Any) -> dict:
        return {
            "theme_id": SHORT_SQUEEZE,
            "short_float_pct": meta["short_float_pct"],
            "momentum_pct": meta["momentum_pct"],
            "move_pct": meta["move_pct"],
            "move_label": "short float",
        }

    def _make_subtitle(self, ticker: str, meta: Any) -> str:
        return f"{ticker} ({meta['short_float_pct']:.0f}% short float, +{meta['momentum_pct']:.0f}% 30D)"

    # ── Scanner logic ─────────────────────────────────────────────────────────

    def check(self) -> list[Signal]:
        candidates = self._find_squeeze_candidates()
        if not candidates:
            logger.info("ShortSqueezeCallScanner: no qualifying tickers")
            return []

        logger.info("ShortSqueezeCallScanner: %d qualifying tickers", len(candidates))
        signals: list[Signal] = []
        for ticker, meta in candidates:
            try:
                current_price = fetch_price(ticker)
                if not current_price:
                    continue
                signals.extend(self._scan_options(ticker, meta, current_price))
            except Exception as e:
                logger.error("Error scanning calls for %s: %s", ticker, e)
        return signals

    def _find_squeeze_candidates(self) -> list[tuple[str, dict]]:
        return cache_or_compute(
            f"squeeze_candidates_{config.squeeze_momentum_days}d",
            self._compute_squeeze_candidates,
        )

    def _compute_squeeze_candidates(self) -> list[tuple[str, dict]]:
        # Step 1: filter by 30-day momentum using cached OHLCV
        data = get_universe_ohlcv(self.universe, "1y")
        if data is None:
            return []

        closes = data["Close"] if "Close" in data.columns else data.xs("Close", axis=1, level=0)
        lookback = config.squeeze_momentum_days
        threshold = config.squeeze_min_momentum_pct / 100.0

        momentum_tickers: list[str] = []
        for ticker in closes.columns:
            try:
                series = closes[ticker].dropna()
                if len(series) < lookback + 5:
                    continue
                start = float(series.iloc[-lookback])
                end = float(series.iloc[-1])
                if start <= 0:
                    continue
                if (end - start) / start >= threshold:
                    momentum_tickers.append(ticker)
            except Exception:
                pass

        if not momentum_tickers:
            return []

        # Step 2: fetch shortPercentOfFloat only for momentum-passing tickers
        result: list[tuple[str, dict]] = []
        min_short = config.squeeze_min_short_float_pct / 100.0

        for ticker in momentum_tickers:
            try:
                info_key = f"info_{ticker}"
                info = cache.get(info_key)
                if info is None:
                    info = yf.Ticker(ticker).info
                    cache.set(info_key, info)

                short_pct = info.get("shortPercentOfFloat")
                if short_pct is None or short_pct < min_short:
                    continue

                series = closes[ticker].dropna()
                start = float(series.iloc[-lookback])
                end = float(series.iloc[-1])
                momentum_pct = (end - start) / start * 100

                result.append((ticker, {
                    "short_float_pct": round(float(short_pct) * 100, 1),
                    "momentum_pct": round(momentum_pct, 1),
                    "move_pct": round(float(short_pct) * 100, 1),
                }))
            except Exception as e:
                logger.debug("Squeeze filter error for %s: %s", ticker, e)

        return result
