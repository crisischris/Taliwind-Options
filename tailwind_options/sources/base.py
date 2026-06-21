from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Any

import yfinance as yf

from .. import cache
from ..config import ScannerOpts
from ..constants import BREAKEVEN_DROP, BREAKEVEN_RISE
from ._helpers import (
    TERM_BOUNDARY_DAYS,
    bucket_candidates,
    filter_option_chain,
    format_option_message,
    prob_itm_call,
    prob_itm_put,
)

logger = logging.getLogger(__name__)


@dataclass
class Signal:
    triggered: bool
    title: str
    message: str
    subtitle: str = ""
    data: dict[str, Any] = field(default_factory=dict)


class Indicator(ABC):
    """Base class for all indicator checks."""

    @abstractmethod
    def check(self) -> list[Signal]:
        """Run the indicator logic and return any triggered signals."""
        ...


class BaseOptionScanner(Indicator, ABC):
    """
    Abstract base for all option scanners. Subclasses implement five template
    methods describing what makes their theme unique; the scanning loop lives here.
    """

    @property
    @abstractmethod
    def _option_type(self) -> str:
        """'calls' or 'puts'"""
        ...

    @property
    @abstractmethod
    def _exp_cache_prefix(self) -> str:
        """Prefix for the expiration cache key, e.g. 'call_', 'dram_', ''."""
        ...

    @abstractmethod
    def _scan_params(self) -> ScannerOpts:
        ...

    @abstractmethod
    def _theme_fields(self, ticker: str, meta: Any) -> dict:
        """Theme-specific fields merged into every candidate dict."""
        ...

    @abstractmethod
    def _make_subtitle(self, ticker: str, meta: Any) -> str:
        """Signal subtitle for this ticker/meta combo."""
        ...

    def _scan_options(self, ticker: str, meta: Any, current_price: float) -> list[Signal]:
        """Fetch the option chain, filter, score, and return Signals."""
        params = self._scan_params()
        option_type = self._option_type
        today = date.today()
        min_exp = today + timedelta(days=params.min_dte)
        max_exp = today + timedelta(days=params.max_dte)

        exp_key = f"{self._exp_cache_prefix}expirations_{ticker}"
        expirations = cache.get(exp_key)
        if expirations is None:
            t = yf.Ticker(ticker)
            expirations = [e for e in t.options if min_exp <= date.fromisoformat(e) <= max_exp]
            cache.set(exp_key, expirations)
        else:
            t = yf.Ticker(ticker)

        if not expirations:
            logger.debug("%s: no expirations in %d–%d DTE window", ticker, params.min_dte, params.max_dte)
            return []

        prob_fn = prob_itm_call if option_type == "calls" else prob_itm_put
        title_prefix = "Call Opportunity" if option_type == "calls" else "Put Opportunity"
        theme_fields = self._theme_fields(ticker, meta)

        candidates: list[dict] = []
        for expiry in expirations:
            chain_key = f"{option_type}_{ticker}_{expiry}"
            chain = cache.get(chain_key)
            if chain is None:
                try:
                    chain = getattr(t.option_chain(expiry), option_type)
                    cache.set(chain_key, chain)
                except Exception as e:
                    logger.error("%s: failed to fetch %s for %s: %s", ticker, option_type, expiry, e)
                    continue

            for _, row in filter_option_chain(chain, current_price, params.min_oi, params.max_cost_pct, params.max_iv).iterrows():
                ask = row["effective_ask"]
                dte = (date.fromisoformat(expiry) - today).days
                iv = row["impliedVolatility"]
                prob_itm = prob_fn(current_price, row["strike"], dte / 365.0, iv)
                return_multiple = row["strike"] / ask
                if option_type == "calls":
                    breakeven = {BREAKEVEN_RISE: (row["strike"] + ask - current_price) / current_price * 100}
                else:
                    breakeven = {BREAKEVEN_DROP: (current_price - (row["strike"] - ask)) / current_price * 100}
                candidates.append({
                    "ticker": ticker,
                    "current_price": current_price,
                    "strike": row["strike"],
                    "expiry": expiry,
                    "ask": ask,
                    "bid": row["bid"],
                    "iv": iv,
                    "open_interest": row["openInterest"],
                    "volume": row.get("volume"),
                    "contract": row["contractSymbol"],
                    **breakeven,
                    "return_multiple": return_multiple,
                    "prob_itm": prob_itm,
                    "score": return_multiple * prob_itm,
                    "dte": dte,
                    "term": "short" if dte < TERM_BOUNDARY_DAYS else "long",
                    **theme_fields,
                })

        return [
            Signal(
                triggered=True,
                title=f"{title_prefix}: {ticker}",
                subtitle=self._make_subtitle(ticker, meta),
                message=format_option_message(c),
                data=c,
            )
            for c in bucket_candidates(candidates)
        ]
