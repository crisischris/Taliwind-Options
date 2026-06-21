"""
52-Week Breakout call scanner.

Finds S&P 500 + NASDAQ 100 names within 2% of their 52-week high where today's
volume is at least 1.5× the 20-day average. Surfaces cheap OTM calls as
trend-continuation bets once overhead resistance is cleared.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from ..config import ScannerOpts, config
from ..constants import BREAKOUTS
from ..market_data import get_universe_ohlcv
from ..universe import get_universe
from ._helpers import cache_or_compute, fetch_price
from .base import BaseOptionScanner, Signal

logger = logging.getLogger(__name__)

_VOL_AVG_WINDOW = 20


@dataclass
class BreakoutCallScanner(BaseOptionScanner):
    universe: list[str] = field(default_factory=get_universe)

    # ── BaseOptionScanner template methods ───────────────────────────────────

    @property
    def _option_type(self) -> str:
        return "calls"

    @property
    def _exp_cache_prefix(self) -> str:
        return "call_"

    def _scan_params(self) -> ScannerOpts:
        return config.breakout

    def _theme_fields(self, ticker: str, meta: Any) -> dict:
        return {
            "theme_id": BREAKOUTS,
            "high_52w": meta["high_52w"],
            "pct_from_high": meta["pct_from_high"],
            "vol_ratio": meta["vol_ratio"],
            "move_pct": meta["move_pct"],
            "move_label": "vol ratio",
        }

    def _make_subtitle(self, ticker: str, meta: Any) -> str:
        return f"{ticker} ({meta['pct_from_high']:.1f}% from 52W high, {meta['vol_ratio']:.1f}x vol)"

    # ── Scanner logic ─────────────────────────────────────────────────────────

    def check(self) -> list[Signal]:
        candidates = self._find_breakouts()
        if not candidates:
            logger.info("BreakoutCallScanner: no qualifying tickers")
            return []

        logger.info("BreakoutCallScanner: %d qualifying tickers", len(candidates))
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

    def _find_breakouts(self) -> list[tuple[str, dict]]:
        return cache_or_compute("breakout_candidates", self._compute_breakouts)

    def _compute_breakouts(self) -> list[tuple[str, dict]]:
        data = get_universe_ohlcv(self.universe, "1y")
        if data is None:
            return []

        closes = data["Close"] if "Close" in data.columns else data.xs("Close", axis=1, level=0)
        volumes = data["Volume"] if "Volume" in data.columns else data.xs("Volume", axis=1, level=0)
        result: list[tuple[str, dict]] = []

        for ticker in closes.columns:
            try:
                close_s = closes[ticker].dropna()
                vol_s = volumes[ticker].dropna()
                if len(close_s) < _VOL_AVG_WINDOW + 5:
                    continue

                high_52w = float(close_s.max())
                current = float(close_s.iloc[-1])
                pct_from_high = (high_52w - current) / high_52w
                if pct_from_high > config.breakout_max_pct_from_high:
                    continue

                # Volume confirmation: today's vol vs 20-day average
                recent_vols = vol_s.iloc[-(_VOL_AVG_WINDOW + 1):]
                avg_vol = float(recent_vols.iloc[:-1].mean())
                today_vol = float(recent_vols.iloc[-1])
                if avg_vol <= 0:
                    continue
                vol_ratio = today_vol / avg_vol
                if vol_ratio < config.breakout_min_volume_ratio:
                    continue

                result.append((ticker, {
                    "high_52w": round(high_52w, 2),
                    "pct_from_high": round(pct_from_high * 100, 2),
                    "vol_ratio": round(vol_ratio, 2),
                    # move_pct: % above average volume (e.g., 1.8x avg → 80% above avg)
                    "move_pct": round((vol_ratio - 1) * 100, 1),
                }))
            except Exception as e:
                logger.debug("Breakout filter error for %s: %s", ticker, e)

        return result
