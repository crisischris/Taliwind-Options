"""
Valuation Gravity put scanner.

Finds S&P 500 + NASDAQ 100 names with price-to-sales > 15x, positive but
decelerating revenue growth (YoY growth positive and below 30%), and operating
margin above -30%. Surfaces cheap OTM puts as slow-burning compression trades.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from ..constants import VALUATION_GRAVITY
from ..config import ScannerOpts, config
from ..market_data import get_universe_info
from ..universe import get_universe
from ._helpers import cache_or_compute, fetch_price
from .base import BaseOptionScanner, Signal

logger = logging.getLogger(__name__)


@dataclass
class ValuationGravityScanner(BaseOptionScanner):
    universe: list[str] = field(default_factory=get_universe)

    # ── BaseOptionScanner template methods ───────────────────────────────────

    @property
    def _option_type(self) -> str:
        return "puts"

    @property
    def _exp_cache_prefix(self) -> str:
        return ""

    def _scan_params(self) -> ScannerOpts:
        return config.val_gravity

    def _theme_fields(self, ticker: str, meta: Any) -> dict:
        return {
            "theme_id": VALUATION_GRAVITY,
            "ps_ratio": meta["ps_ratio"],
            "revenue_growth_pct": meta["revenue_growth_pct"],
            "op_margin_pct": meta["op_margin_pct"],
            "move_pct": meta["move_pct"],
            "move_label": "P/S premium",
        }

    def _make_subtitle(self, ticker: str, meta: Any) -> str:
        return f"{ticker} (P/S {meta['ps_ratio']:.1f}x, +{meta['revenue_growth_pct']:.0f}% rev growth)"

    # ── Scanner logic ─────────────────────────────────────────────────────────

    def check(self) -> list[Signal]:
        candidates = self._find_overvalued()
        if not candidates:
            logger.info("ValuationGravityScanner: no qualifying tickers")
            return []

        logger.info("ValuationGravityScanner: %d qualifying tickers", len(candidates))
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

    def _find_overvalued(self) -> list[tuple[str, dict]]:
        return cache_or_compute("valuation_gravity_candidates", self._compute_overvalued)

    def _compute_overvalued(self) -> list[tuple[str, dict]]:
        info_map = get_universe_info(self.universe)
        result: list[tuple[str, dict]] = []

        for ticker, info in info_map.items():
            try:
                ps = info.get("priceToSalesTrailing12Months")
                rev_growth = info.get("revenueGrowth")
                op_margin = info.get("operatingMargins")

                if ps is None or rev_growth is None or op_margin is None:
                    continue
                if ps <= config.val_gravity_min_ps:
                    continue
                # Positive but slowing growth — not a rocket, not in free-fall
                if not (0 < rev_growth < config.val_gravity_max_revenue_growth):
                    continue
                if op_margin < config.val_gravity_min_op_margin:
                    continue

                result.append((ticker, {
                    "ps_ratio": round(float(ps), 1),
                    "revenue_growth_pct": round(float(rev_growth) * 100, 1),
                    "op_margin_pct": round(float(op_margin) * 100, 1),
                    # move_pct: how far above the P/S threshold as a percentage
                    "move_pct": round((ps / config.val_gravity_min_ps - 1) * 100, 1),
                }))
            except Exception as e:
                logger.debug("ValuationGravity filter error for %s: %s", ticker, e)

        return result
