from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from ..config import ScannerOpts, config
from ..constants import SPACE
from ._helpers import fetch_price, filter_by_momentum
from .base import BaseOptionScanner, Signal

logger = logging.getLogger(__name__)

_UNIVERSE: list[str] = [
    "RKLB",  # Rocket Lab — launch services and spacecraft components
    "ASTS",  # AST SpaceMobile — LEO satellite broadband
    "LUNR",  # Intuitive Machines — lunar landers and space services
    "PL",    # Planet Labs — earth observation satellite constellation
    "SPIR",  # Spire Global — satellite data and analytics
    "KTOS",  # Kratos Defense — satellite ground systems and space tech
    "BWXT",  # BWX Technologies — nuclear propulsion and space reactors
    "RDW",   # Redwire Corp — space infrastructure and manufacturing
    "LMT",   # Lockheed Martin — space systems and launch vehicles
    "NOC",   # Northrop Grumman — space division and launch systems
    "GSAT",  # Globalstar — satellite communications
    "IRDM",  # Iridium Communications — LEO satellite network
    "SPCX",  # SpaceX-focused ETF / space economy basket
]


@dataclass
class SpaceCallScanner(BaseOptionScanner):
    """
    Scans pure-play and major space industry names for recent momentum,
    then surfaces cheap OTM calls as trend-continuation plays.
    """

    universe: list[str] = field(default_factory=lambda: list(_UNIVERSE))

    # ── BaseOptionScanner template methods ───────────────────────────────────

    @property
    def _option_type(self) -> str:
        return "calls"

    @property
    def _exp_cache_prefix(self) -> str:
        return "space_"

    def _scan_params(self) -> ScannerOpts:
        return config.space

    def _theme_fields(self, ticker: str, meta: Any) -> dict:
        momentum_pct: float = meta
        return {
            "theme_id": SPACE,
            "momentum_pct": momentum_pct,
            "move_pct": momentum_pct,
            "move_label": f"{config.space_momentum_days}D",
        }

    def _make_subtitle(self, ticker: str, meta: Any) -> str:
        return f"{ticker} (+{meta:.0f}% {config.space_momentum_days}d)"

    # ── Scanner logic ─────────────────────────────────────────────────────────

    def check(self) -> list[Signal]:
        momentum_tickers = self._filter_by_momentum()
        if not momentum_tickers:
            logger.info(
                "SpaceCallScanner: no tickers passed momentum filter (>= %.0f%% in %d days)",
                config.space_momentum_min_pct,
                config.space_momentum_days,
            )
            return []

        logger.info("%d space tickers passed momentum filter", len(momentum_tickers))

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
            config.space_momentum_days,
            config.space_momentum_min_pct,
            f"space_momentum_{config.space_momentum_days}d",
        )
