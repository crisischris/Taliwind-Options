from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from ..constants import MEAN_REVERSION
from ..config import ScannerOpts, config
from ..market_data import get_universe_ohlcv
from ..universe import get_universe
from ._helpers import fetch_price
from .base import BaseOptionScanner, Signal

logger = logging.getLogger(__name__)


@dataclass
class GainerPutScanner(BaseOptionScanner):
    """
    Scans the S&P 500 + NASDAQ 100 universe for tickers with extreme 1-year gains,
    then surfaces cheap OTM puts on those tickers as potential reversion plays.
    """

    universe: list[str] = field(default_factory=get_universe)

    # ── BaseOptionScanner template methods ───────────────────────────────────

    @property
    def _option_type(self) -> str:
        return "puts"

    @property
    def _exp_cache_prefix(self) -> str:
        return ""

    def _scan_params(self) -> ScannerOpts:
        return config.gainer_put

    def _theme_fields(self, ticker: str, meta: Any) -> dict:
        gain_pct: float = meta
        return {"theme_id": MEAN_REVERSION, "gain_pct": gain_pct, "move_pct": gain_pct, "move_label": "1Y"}

    def _make_subtitle(self, ticker: str, meta: Any) -> str:
        return f"{ticker} (+{meta:.0f}% YTD)"

    # ── Scanner logic ─────────────────────────────────────────────────────────

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
                current_price = fetch_price(ticker)
                if not current_price:
                    continue
                puts = self._scan_options(ticker, gain_pct, current_price)
                if gain_pct >= config.gainer_min_gain_pct:
                    signals.extend(puts)
            except Exception as e:
                logger.error("Error scanning puts for %s: %s", ticker, e)

        return signals

    def _find_gainers(self, threshold_pct: float) -> list[tuple[str, float]]:
        data = get_universe_ohlcv(self.universe, "1y")
        if data is None:
            return []
        closes = data["Close"] if "Close" in data.columns else data.xs("Close", axis=1, level=0)

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
