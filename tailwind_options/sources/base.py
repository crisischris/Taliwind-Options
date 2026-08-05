from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, wait
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

# Wide DTE windows can mean a dozen+ expiries per ticker. Fetch them concurrently
# (I/O-bound) and bound the wait per expiry so one slow/hung request to Yahoo
# Finance can't quietly burn minutes of the Lambda's fixed budget.
_CHAIN_FETCH_WORKERS = 8
_CHAIN_FETCH_TIMEOUT_S = 20
_CHAIN_FETCH_RETRIES = 1


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

        chains = self._fetch_chains(ticker, option_type, expirations)

        candidates: list[dict] = []
        for expiry in expirations:
            chain = chains.get(expiry)
            if chain is None:
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

    def _fetch_chains(
        self, ticker: str, option_type: str, expirations: list[str]
    ) -> dict[str, Any]:
        """Fetch one option chain per expiry concurrently, bounded to one
        _CHAIN_FETCH_TIMEOUT_S wait for the whole batch.

        Uses wait() + shutdown(wait=False) rather than the executor as a context
        manager: __exit__ calls shutdown(wait=True), which blocks until every
        submitted thread actually finishes — a still-running request doesn't stop
        just because we stopped waiting on its future, so that would silently
        reintroduce the unbounded hang this method exists to prevent.
        """
        pool = ThreadPoolExecutor(max_workers=_CHAIN_FETCH_WORKERS)
        futures = {
            pool.submit(self._fetch_one_chain, ticker, option_type, expiry): expiry
            for expiry in expirations
        }
        done, not_done = wait(futures, timeout=_CHAIN_FETCH_TIMEOUT_S)

        chains: dict[str, Any] = {}
        for future in done:
            chains[futures[future]] = future.result()
        for future in not_done:
            expiry = futures[future]
            logger.error(
                "%s: timed out fetching %s for %s after %ds",
                ticker, option_type, expiry, _CHAIN_FETCH_TIMEOUT_S,
            )
            chains[expiry] = None

        pool.shutdown(wait=False, cancel_futures=True)
        return chains

    def _fetch_one_chain(self, ticker: str, option_type: str, expiry: str) -> Any | None:
        chain_key = f"{option_type}_{ticker}_{expiry}"
        cached = cache.get(chain_key)
        if cached is not None:
            return cached

        # A fresh Ticker per call — yf.Ticker keeps mutable per-instance state
        # (_expirations, _underlying) that isn't safe to share across the
        # concurrent fetches in _fetch_chains.
        for attempt in range(_CHAIN_FETCH_RETRIES + 1):
            try:
                chain = getattr(yf.Ticker(ticker).option_chain(expiry), option_type)
                cache.set(chain_key, chain)
                return chain
            except Exception as e:
                if attempt < _CHAIN_FETCH_RETRIES:
                    logger.warning(
                        "%s: retrying %s for %s after error: %s", ticker, option_type, expiry, e
                    )
                    continue
                logger.error("%s: failed to fetch %s for %s: %s", ticker, option_type, expiry, e)
                return None
