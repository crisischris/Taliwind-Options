"""
Broken Momentum put scanner.

Finds S&P 500 + NASDAQ 100 names that made a 52-week high in the past 180 days
but are now trading 20%+ below that peak, with distribution volume (down-day
volume exceeding up-day volume over the trailing 20 sessions). Surfaces cheap OTM puts.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Any

from ..constants import BROKEN_MOMENTUM
from ..config import ScannerOpts, config
from ..market_data import get_universe_ohlcv
from ..universe import get_universe
from ._helpers import cache_or_compute, fetch_price
from .base import BaseOptionScanner, Signal

logger = logging.getLogger(__name__)

_VOLUME_WINDOW = 20
_MAX_DAYS_SINCE_HIGH = 180
_MIN_DRAWDOWN = 0.20


@dataclass
class BrokenMomentumScanner(BaseOptionScanner):
    universe: list[str] = field(default_factory=get_universe)

    # ── BaseOptionScanner template methods ───────────────────────────────────

    @property
    def _option_type(self) -> str:
        return "puts"

    @property
    def _exp_cache_prefix(self) -> str:
        return ""

    def _scan_params(self) -> ScannerOpts:
        return config.broken_mom

    def _theme_fields(self, ticker: str, meta: Any) -> dict:
        return {
            "theme_id": BROKEN_MOMENTUM,
            "peak_price": meta["peak_price"],
            "peak_date": meta["peak_date"],
            "drawdown_pct": meta["drawdown_pct"],
            "down_vol_ratio": meta["down_vol_ratio"],
            "move_pct": -meta["drawdown_pct"],
            "move_label": "from peak",
        }

    def _make_subtitle(self, ticker: str, meta: Any) -> str:
        return f"{ticker} ({meta['drawdown_pct']:.0f}% below {meta['peak_date'][:7]} peak)"

    # ── Scanner logic ─────────────────────────────────────────────────────────

    def check(self) -> list[Signal]:
        candidates = self._find_broken_momentum()
        if not candidates:
            logger.info("BrokenMomentumScanner: no qualifying tickers")
            return []

        logger.info("BrokenMomentumScanner: %d qualifying tickers", len(candidates))
        signals: list[Signal] = []
        for ticker, meta in candidates:
            try:
                current_price = fetch_price(ticker)
                if not current_price:
                    continue
                signals.extend(self._scan_options(ticker, meta, current_price))
            except Exception as e:
                logger.error("Error scanning puts for %s: %s", ticker, e)
        return signals

    def _find_broken_momentum(self) -> list[tuple[str, dict]]:
        return cache_or_compute("broken_momentum_candidates", self._compute_broken_momentum)

    def _compute_broken_momentum(self) -> list[tuple[str, dict]]:
        data = get_universe_ohlcv(self.universe, "1y")
        if data is None:
            return []

        closes = data["Close"] if "Close" in data.columns else data.xs("Close", axis=1, level=0)
        volumes = data["Volume"] if "Volume" in data.columns else data.xs("Volume", axis=1, level=0)

        today = date.today()
        cutoff = today - timedelta(days=_MAX_DAYS_SINCE_HIGH)
        result: list[tuple[str, dict]] = []

        for ticker in closes.columns:
            try:
                close_s = closes[ticker].dropna()
                vol_s = volumes[ticker].dropna()
                if len(close_s) < _VOLUME_WINDOW + 10:
                    continue

                high_val = float(close_s.max())
                high_idx = close_s.idxmax()
                high_date = high_idx.date() if hasattr(high_idx, "date") else high_idx
                if high_date < cutoff:
                    continue

                current = float(close_s.iloc[-1])
                drawdown = (high_val - current) / high_val
                if drawdown < _MIN_DRAWDOWN:
                    continue

                recent_c = close_s.iloc[-_VOLUME_WINDOW:]
                recent_v = vol_s.reindex(recent_c.index).dropna()
                if len(recent_v) < 8:
                    continue

                daily_ret = recent_c.pct_change().dropna()
                idx = daily_ret.index.intersection(recent_v.index)
                if len(idx) < 6:
                    continue

                down_vol = float(recent_v.loc[idx[daily_ret.loc[idx] < 0]].mean())
                up_vol = float(recent_v.loc[idx[daily_ret.loc[idx] > 0]].mean())
                if down_vol <= up_vol or up_vol == 0:
                    continue

                result.append((ticker, {
                    "peak_price": round(high_val, 2),
                    "peak_date": str(high_date),
                    "drawdown_pct": round(drawdown * 100, 1),
                    "down_vol_ratio": round(down_vol / up_vol, 2),
                }))
            except Exception as e:
                logger.debug("BrokenMomentum filter error for %s: %s", ticker, e)

        return result
