from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

import yfinance as yf

from ..call_universe import get_tickers
from ..config import ScannerOpts, config
from ..constants import AI_MOMENTUM
from ._helpers import fetch_price, filter_by_momentum
from .base import BaseOptionScanner, Signal

logger = logging.getLogger(__name__)


@dataclass
class TrendCallScanner(BaseOptionScanner):
    """
    Scans ARK ETF holdings for tickers with strong recent momentum,
    then surfaces cheap OTM calls as trend-continuation plays.
    """

    # default_factory allows standalone use; lambda_handler overrides with S3-backed universe
    universe: list[str] = field(default_factory=get_tickers)

    # ── BaseOptionScanner template methods ───────────────────────────────────

    @property
    def _option_type(self) -> str:
        return "calls"

    @property
    def _exp_cache_prefix(self) -> str:
        return "call_"

    def _scan_params(self) -> ScannerOpts:
        return config.trend_call

    def _theme_fields(self, ticker: str, meta: Any) -> dict:
        momentum_pct: float = meta
        return {"theme_id": AI_MOMENTUM, "momentum_pct": momentum_pct, "move_pct": momentum_pct, "move_label": "90D"}

    def _make_subtitle(self, ticker: str, meta: Any) -> str:
        return f"{ticker} (+{meta:.0f}% {config.trend_call_momentum_days}d)"

    # ── Scanner logic ─────────────────────────────────────────────────────────

    def check(self) -> list[Signal]:
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
                current_price = fetch_price(ticker)
                if not current_price:
                    continue
                signals.extend(self._scan_options(ticker, momentum_pct, current_price))
            except Exception as e:
                logger.error("Error scanning calls for %s: %s", ticker, e)

        return signals

    def _filter_by_momentum(self) -> list[tuple[str, float]]:
        return filter_by_momentum(
            self.universe,
            config.trend_call_momentum_days,
            config.trend_call_momentum_min_pct,
            f"call_universe_momentum_{config.trend_call_momentum_days}d",
        )
