"""Shared fixtures for the test suite."""
from __future__ import annotations

import pytest

from tailwind_options.sources.base import Signal


def make_call_signal(ticker="AAPL", term="short", **overrides) -> Signal:
    data = {
        "ticker": ticker,
        "momentum_pct": 90.0,
        "current_price": 200.0,
        "strike": 250.0,
        "expiry": "2026-12-19",
        "ask": 4.00,
        "bid": 3.80,
        "iv": 0.60,
        "open_interest": 50,
        "volume": 10,
        "contract": f"{ticker}261219C00250000",
        "breakeven_rise_pct": 27.0,
        "return_multiple": 62.5,
        "prob_itm": 0.12,
        "score": 7.5,
        "dte": 219,
        "term": term,
    }
    data.update(overrides)
    return Signal(
        triggered=True,
        title=f"Call Opportunity: {ticker}",
        subtitle=f"{ticker} (+90% 90d)",
        message="62x return | $4.00 ask | $250 strike | Exp 2026-12-19",
        data=data,
    )


def make_signal(ticker="AAPL", term="short", **overrides) -> Signal:
    data = {
        "ticker": ticker,
        "gain_pct": 600.0,
        "current_price": 200.0,
        "strike": 150.0,
        "expiry": "2026-12-19",
        "ask": 3.00,
        "bid": 2.80,
        "iv": 0.80,
        "open_interest": 50,
        "volume": 10,
        "contract": f"{ticker}261219P00150000",
        "breakeven_drop_pct": 23.5,
        "return_multiple": 50.0,
        "prob_itm": 0.15,
        "score": 7.5,
        "dte": 219,
        "term": term,
    }
    data.update(overrides)
    return Signal(
        triggered=True,
        title=f"Put Opportunity: {ticker}",
        subtitle=f"{ticker} (+600% YTD)",
        message="50x return | $3.00 ask | $150 strike | Exp 2026-12-19",
        data=data,
    )


@pytest.fixture
def short_signal():
    return make_signal(term="short", dte=90, contract="AAPL260919P00150000")


@pytest.fixture
def long_signal():
    return make_signal(term="long", dte=400, contract="AAPL271219P00150000")


@pytest.fixture
def moonshot_signal():
    return make_signal(term="moonshot", return_multiple=200.0, contract="AAPL280119P00150000")
