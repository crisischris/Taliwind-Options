"""
Sector Rotation call scanner.

Uses the S&P 500 + NASDAQ 100 universe. Computes each ticker's 30-day return,
groups by sector (from yf.Ticker.info), computes a market median return as the
benchmark, and qualifies sectors whose median return beats the market by 5%+.
Within qualifying sectors, the top 20% of performers get their OTM calls scanned.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from ..config import ScannerOpts, config
from ..constants import SECTOR_ROTATION
from ..market_data import get_universe_info, get_universe_ohlcv
from ..universe import get_universe
from ._helpers import cache_or_compute, fetch_price
from .base import BaseOptionScanner, Signal

logger = logging.getLogger(__name__)


@dataclass
class SectorRotationCallScanner(BaseOptionScanner):
    universe: list[str] = field(default_factory=get_universe)

    # ── BaseOptionScanner template methods ───────────────────────────────────

    @property
    def _option_type(self) -> str:
        return "calls"

    @property
    def _exp_cache_prefix(self) -> str:
        return "call_"

    def _scan_params(self) -> ScannerOpts:
        return config.rotation

    def _theme_fields(self, ticker: str, meta: Any) -> dict:
        return {
            "theme_id": SECTOR_ROTATION,
            "sector": meta["sector"],
            "sector_median_pct": meta["sector_median_pct"],
            "return_30d_pct": meta["return_30d_pct"],
            "sector_rs_pct": meta["sector_rs_pct"],
            "move_pct": meta["move_pct"],
            "move_label": "sector RS",
        }

    def _make_subtitle(self, ticker: str, meta: Any) -> str:
        return f"{ticker} ({meta['sector']}, +{meta['sector_rs_pct']:.0f}% sector RS)"

    # ── Scanner logic ─────────────────────────────────────────────────────────

    def check(self) -> list[Signal]:
        candidates = self._find_rotation_leaders()
        if not candidates:
            logger.info("SectorRotationCallScanner: no qualifying tickers")
            return []

        logger.info("SectorRotationCallScanner: %d qualifying tickers", len(candidates))
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

    def _find_rotation_leaders(self) -> list[tuple[str, dict]]:
        return cache_or_compute(
            f"rotation_leaders_{config.rotation_momentum_days}d",
            self._compute_rotation_leaders,
        )

    def _compute_rotation_leaders(self) -> list[tuple[str, dict]]:
        data = get_universe_ohlcv(self.universe, "1y")
        if data is None:
            return []

        closes = data["Close"] if "Close" in data.columns else data.xs("Close", axis=1, level=0)
        lookback = config.rotation_momentum_days
        info_map = get_universe_info(self.universe)

        # Compute 30-day returns for all tickers
        ticker_returns: dict[str, float] = {}
        for ticker in closes.columns:
            try:
                series = closes[ticker].dropna()
                if len(series) < lookback + 5:
                    continue
                start = float(series.iloc[-lookback])
                end = float(series.iloc[-1])
                if start <= 0:
                    continue
                ticker_returns[ticker] = (end - start) / start * 100
            except Exception:
                pass

        if not ticker_returns:
            return []

        # Market median return (equal-weighted proxy for index)
        all_returns = sorted(ticker_returns.values())
        mid = len(all_returns) // 2
        market_median = (all_returns[mid - 1] + all_returns[mid]) / 2 if len(all_returns) % 2 == 0 else all_returns[mid]

        # Group tickers by sector
        sector_tickers: dict[str, list[str]] = {}
        for ticker, ret in ticker_returns.items():
            sector = info_map.get(ticker, {}).get("sector")
            if not sector:
                continue
            sector_tickers.setdefault(sector, []).append(ticker)

        # Find qualifying sectors: median sector return > market median + threshold
        threshold = config.rotation_min_outperform_pct
        qualifying_sectors: set[str] = set()
        sector_medians: dict[str, float] = {}
        for sector, tickers in sector_tickers.items():
            returns = sorted(ticker_returns[t] for t in tickers)
            mid_s = len(returns) // 2
            sec_median = (returns[mid_s - 1] + returns[mid_s]) / 2 if len(returns) % 2 == 0 else returns[mid_s]
            sector_medians[sector] = sec_median
            if sec_median >= market_median + threshold:
                qualifying_sectors.add(sector)

        if not qualifying_sectors:
            logger.info("SectorRotation: no sectors outperformed market by %.0f%%+", threshold)
            return []

        # Within qualifying sectors, keep top 20% by return
        result: list[tuple[str, dict]] = []
        top_pct = config.rotation_top_pct

        for sector in qualifying_sectors:
            tickers_in_sector = sector_tickers[sector]
            sector_rets = sorted(
                [(t, ticker_returns[t]) for t in tickers_in_sector],
                key=lambda x: x[1], reverse=True,
            )
            cutoff = max(1, int(len(sector_rets) * top_pct))
            for ticker, ret in sector_rets[:cutoff]:
                sector_rs = ret - market_median
                result.append((ticker, {
                    "sector": sector,
                    "sector_median_pct": round(sector_medians[sector], 1),
                    "return_30d_pct": round(ret, 1),
                    "sector_rs_pct": round(sector_rs, 1),
                    "move_pct": round(sector_rs, 1),
                }))

        return result
