from __future__ import annotations

import logging
from dataclasses import dataclass, field

import httpx

from ..config import config
from .base import Indicator, Signal
from .price import PriceThreshold

logger = logging.getLogger(__name__)

_BASE_URL = "https://www.alphavantage.co/query"


@dataclass
class AlphaVantageAlert(Indicator):
    """Fires a signal when a ticker crosses a configured price threshold, using Alpha Vantage."""

    thresholds: list[PriceThreshold] = field(default_factory=list)

    def check(self) -> list[Signal]:
        signals: list[Signal] = []

        for threshold in self.thresholds:
            try:
                price = self._fetch_price(threshold.ticker)
            except Exception as e:
                logger.error("Failed to fetch Alpha Vantage price for %s: %s", threshold.ticker, e)
                continue

            logger.debug("%s price: $%.2f", threshold.ticker, price)

            if threshold.above is not None and price > threshold.above:
                signals.append(Signal(
                    triggered=True,
                    title=f"{threshold.ticker} Above Threshold",
                    message=f"${price:.2f} > ${threshold.above:.2f}",
                    subtitle=threshold.ticker,
                    data={"ticker": threshold.ticker, "price": price, "source": "alphavantage"},
                ))

            if threshold.below is not None and price < threshold.below:
                signals.append(Signal(
                    triggered=True,
                    title=f"{threshold.ticker} Below Threshold",
                    message=f"${price:.2f} < ${threshold.below:.2f}",
                    subtitle=threshold.ticker,
                    data={"ticker": threshold.ticker, "price": price, "source": "alphavantage"},
                ))

        return signals

    @staticmethod
    def _fetch_price(ticker: str) -> float:
        if not config.alpha_vantage_api_key:
            raise ValueError("ALPHA_VANTAGE_API_KEY is not set")

        response = httpx.get(
            _BASE_URL,
            params={
                "function": "GLOBAL_QUOTE",
                "symbol": ticker,
                "apikey": config.alpha_vantage_api_key,
            },
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

        quote = data.get("Global Quote", {})
        price_str = quote.get("05. price")
        if not price_str:
            raise ValueError(f"No price data returned for {ticker}")

        return float(price_str)
