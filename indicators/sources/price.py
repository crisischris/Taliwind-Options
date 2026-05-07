from __future__ import annotations

import logging
from dataclasses import dataclass, field

import yfinance as yf

from .base import Indicator, Signal

logger = logging.getLogger(__name__)


@dataclass
class PriceThreshold:
    ticker: str
    above: float | None = None   # alert when price rises above this
    below: float | None = None   # alert when price drops below this


@dataclass
class PriceAlert(Indicator):
    """Fires a signal when a ticker crosses a configured price threshold."""

    thresholds: list[PriceThreshold] = field(default_factory=list)

    def check(self) -> list[Signal]:
        signals: list[Signal] = []

        for threshold in self.thresholds:
            try:
                price = self._fetch_price(threshold.ticker)
            except Exception as e:
                logger.error("Failed to fetch price for %s: %s", threshold.ticker, e)
                continue

            logger.debug("%s price: $%.2f", threshold.ticker, price)

            if threshold.above is not None and price > threshold.above:
                signals.append(Signal(
                    triggered=True,
                    title=f"{threshold.ticker} Above Threshold",
                    message=f"${price:.2f} > ${threshold.above:.2f}",
                    subtitle=threshold.ticker,
                    data={"ticker": threshold.ticker, "price": price},
                ))

            if threshold.below is not None and price < threshold.below:
                signals.append(Signal(
                    triggered=True,
                    title=f"{threshold.ticker} Below Threshold",
                    message=f"${price:.2f} < ${threshold.below:.2f}",
                    subtitle=threshold.ticker,
                    data={"ticker": threshold.ticker, "price": price},
                ))

        return signals

    @staticmethod
    def _fetch_price(ticker: str) -> float:
        data = yf.Ticker(ticker)
        info = data.fast_info
        price = info.last_price
        if price is None:
            raise ValueError(f"No price data returned for {ticker}")
        return float(price)
