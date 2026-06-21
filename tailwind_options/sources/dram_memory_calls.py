from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from ..config import ScannerOpts, config
from ..constants import DRAM_MEMORY
from ._helpers import fetch_price, filter_by_momentum
from .base import BaseOptionScanner, Signal

logger = logging.getLogger(__name__)

_UNIVERSE: list[str] = [
    "MU",    # Micron — dominant pure-play DRAM/NAND manufacturer
    "MRVL",  # Marvell — HBM controllers and memory interface chips
    "WDC",   # Western Digital — HDDs and storage systems post-SanDisk spin-off
    "SNDK",  # SanDisk — NAND flash, spun off from WDC in Feb 2025
    "STX",   # Seagate — HDDs and storage systems
    "LRCX",  # Lam Research — critical etch equipment for DRAM fabs
    "AMAT",  # Applied Materials — deposition/etch across memory fabs
    "KLAC",  # KLA Corp — process control for memory fabs
    "SMCI",  # Super Micro Computer — HBM-intensive AI server systems
    "INTC",  # Intel — DRAM/NAND manufacturer and major memory consumer
    "ON",    # ON Semiconductor — analog/mixed-signal for storage
    "NXPI",  # NXP Semiconductors — automotive + embedded memory/storage
    "MXL",   # MaxLinear — memory interface and storage connectivity chips
]


@dataclass
class DramMemoryCallScanner(BaseOptionScanner):
    """
    Scans DRAM and memory supply-chain names for recent momentum,
    then surfaces cheap OTM calls as trend-continuation plays.
    """

    universe: list[str] = field(default_factory=lambda: list(_UNIVERSE))

    # ── BaseOptionScanner template methods ───────────────────────────────────

    @property
    def _option_type(self) -> str:
        return "calls"

    @property
    def _exp_cache_prefix(self) -> str:
        return "dram_"

    def _scan_params(self) -> ScannerOpts:
        return config.dram

    def _theme_fields(self, ticker: str, meta: Any) -> dict:
        momentum_pct: float = meta
        return {
            "theme_id": DRAM_MEMORY,
            "momentum_pct": momentum_pct,
            "move_pct": momentum_pct,
            "move_label": f"{config.dram_momentum_days}D",
        }

    def _make_subtitle(self, ticker: str, meta: Any) -> str:
        return f"{ticker} (+{meta:.0f}% {config.dram_momentum_days}d)"

    # ── Scanner logic ─────────────────────────────────────────────────────────

    def check(self) -> list[Signal]:
        momentum_tickers = self._filter_by_momentum()
        if not momentum_tickers:
            logger.info(
                "DramMemoryCallScanner: no tickers passed momentum filter (>= %.0f%% in %d days)",
                config.dram_momentum_min_pct,
                config.dram_momentum_days,
            )
            return []

        logger.info("%d DRAM/memory tickers passed momentum filter", len(momentum_tickers))

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
            config.dram_momentum_days,
            config.dram_momentum_min_pct,
            f"dram_momentum_{config.dram_momentum_days}d",
        )
