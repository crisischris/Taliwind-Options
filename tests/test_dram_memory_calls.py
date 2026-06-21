from __future__ import annotations

from datetime import date, timedelta
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

import tailwind_options.cache as cache_mod
from tailwind_options import cache
from tailwind_options.sources.dram_memory_calls import DramMemoryCallScanner


@pytest.fixture(autouse=True)
def clear_cache(tmp_path, monkeypatch):
    monkeypatch.setattr(cache_mod, "_CACHE_DIR", tmp_path)


def _make_yf_download(tickers: list[str], prices: list[tuple[float, float]]) -> pd.DataFrame:
    dates = pd.date_range("2025-01-01", periods=2, freq="D")
    cols = pd.MultiIndex.from_tuples([("Close", t) for t in tickers])
    rows = [[p[0] for p in prices], [p[1] for p in prices]]
    return pd.DataFrame(rows, columns=cols, index=dates)


def _make_calls_df(rows: list[dict]) -> pd.DataFrame:
    defaults = {
        "contractSymbol": "MU260101C00100000",
        "strike": 100.0,
        "lastPrice": 3.0,
        "bid": 2.8,
        "ask": 3.2,
        "impliedVolatility": 0.6,
        "inTheMoney": False,
        "openInterest": 50,
        "volume": 20,
    }
    return pd.DataFrame([{**defaults, **r} for r in rows])


# ── check ─────────────────────────────────────────────────────────────────────

def test_check_no_momentum_returns_empty():
    data = _make_yf_download(["MU"], [(100.0, 100.0)])  # 0% gain
    with patch("tailwind_options.sources._helpers.yf.download", return_value=data):
        signals = DramMemoryCallScanner(universe=["MU"]).check()
    assert signals == []


def test_check_error_on_ticker_continues():
    data = _make_yf_download(["MU", "MRVL"], [(10.0, 90.0), (10.0, 90.0)])
    today = date.today()
    expiry = (today + timedelta(days=90)).isoformat()
    calls = _make_calls_df([{"contractSymbol": "MRVL_OK", "strike": 80.0, "ask": 2.0}])

    def ticker_side_effect(sym):
        t = MagicMock()
        if sym == "MU":
            raise RuntimeError("api error")
        t.fast_info.last_price = 70.0
        t.options = [expiry]
        t.option_chain.return_value = MagicMock(calls=calls)
        return t

    with patch("tailwind_options.sources._helpers.yf.download", return_value=data):
        with patch("yfinance.Ticker", side_effect=ticker_side_effect):
            signals = DramMemoryCallScanner(universe=["MU", "MRVL"]).check()

    assert any(s.data["ticker"] == "MRVL" for s in signals)


# ── _filter_by_momentum ───────────────────────────────────────────────────────

def test_filter_passes_above_threshold():
    data = _make_yf_download(["MU", "INTC"], [(10.0, 90.0), (10.0, 10.5)])
    with patch("tailwind_options.sources._helpers.yf.download", return_value=data):
        result = DramMemoryCallScanner(universe=["MU", "INTC"])._filter_by_momentum()
    tickers = [r[0] for r in result]
    assert "MU" in tickers
    assert "INTC" not in tickers


def test_filter_sorted_descending():
    data = _make_yf_download(["MU", "MRVL", "WDC"], [(10.0, 90.0), (10.0, 50.0), (10.0, 200.0)])
    with patch("tailwind_options.sources._helpers.yf.download", return_value=data):
        result = DramMemoryCallScanner(universe=["MU", "MRVL", "WDC"])._filter_by_momentum()
    gains = [r[1] for r in result]
    assert gains == sorted(gains, reverse=True)


def test_filter_uses_cache():
    data = _make_yf_download(["MU"], [(10.0, 90.0)])
    with patch("tailwind_options.sources._helpers.yf.download", return_value=data) as mock_dl:
        scanner = DramMemoryCallScanner(universe=["MU"])
        scanner._filter_by_momentum()
        mock_dl.assert_called_once()
    with patch("tailwind_options.sources._helpers.yf.download") as mock_dl2:
        scanner._filter_by_momentum()
        mock_dl2.assert_not_called()


def test_filter_download_failure_returns_empty():
    with patch("tailwind_options.sources._helpers.yf.download", side_effect=Exception("network")):
        result = DramMemoryCallScanner(universe=["MU"])._filter_by_momentum()
    assert result == []


def test_filter_skips_insufficient_data():
    dates = pd.date_range("2025-01-01", periods=1, freq="D")
    cols = pd.MultiIndex.from_tuples([("Close", "MU")])
    df = pd.DataFrame([[100.0]], columns=cols, index=dates)
    with patch("tailwind_options.sources._helpers.yf.download", return_value=df):
        result = DramMemoryCallScanner(universe=["MU"])._filter_by_momentum()
    assert result == []


# ── _scan_calls ───────────────────────────────────────────────────────────────

def test_scan_calls_no_expirations_returns_empty():
    t = MagicMock()
    t.options = []
    with patch("yfinance.Ticker", return_value=t):
        signals = DramMemoryCallScanner(universe=["MU"])._scan_options("MU", 20.0, 80.0)
    assert signals == []


def test_scan_calls_produces_signals():
    today = date.today()
    expiry = (today + timedelta(days=90)).isoformat()
    calls = _make_calls_df([{"contractSymbol": "MU_C", "strike": 100.0, "ask": 2.0}])
    t = MagicMock()
    t.options = [expiry]
    t.option_chain.return_value = MagicMock(calls=calls)
    with patch("yfinance.Ticker", return_value=t):
        signals = DramMemoryCallScanner(universe=["MU"])._scan_options("MU", 20.0, 80.0)
    assert len(signals) > 0
    assert signals[0].triggered is True
    assert signals[0].data["ticker"] == "MU"
    assert signals[0].data["theme_id"] == "dram-memory"


def test_scan_calls_filters_itm():
    today = date.today()
    expiry = (today + timedelta(days=90)).isoformat()
    calls = _make_calls_df([{"inTheMoney": True, "strike": 50.0, "ask": 2.0}])
    t = MagicMock()
    t.options = [expiry]
    t.option_chain.return_value = MagicMock(calls=calls)
    with patch("yfinance.Ticker", return_value=t):
        signals = DramMemoryCallScanner(universe=["MU"])._scan_options("MU", 20.0, 80.0)
    assert signals == []


def test_scan_calls_filters_high_cost():
    today = date.today()
    expiry = (today + timedelta(days=90)).isoformat()
    # ask 10 on price 80 = 12.5% > 5% limit
    calls = _make_calls_df([{"strike": 100.0, "ask": 10.0}])
    t = MagicMock()
    t.options = [expiry]
    t.option_chain.return_value = MagicMock(calls=calls)
    with patch("yfinance.Ticker", return_value=t):
        signals = DramMemoryCallScanner(universe=["MU"])._scan_options("MU", 20.0, 80.0)
    assert signals == []


def test_scan_calls_uses_lastprice_when_ask_zero():
    today = date.today()
    expiry = (today + timedelta(days=90)).isoformat()
    calls = _make_calls_df([{"strike": 100.0, "ask": 0.0, "lastPrice": 2.0, "openInterest": 0, "volume": 0}])
    t = MagicMock()
    t.options = [expiry]
    t.option_chain.return_value = MagicMock(calls=calls)
    with patch("yfinance.Ticker", return_value=t):
        signals = DramMemoryCallScanner(universe=["MU"])._scan_options("MU", 20.0, 80.0)
    assert len(signals) > 0
    assert signals[0].data["ask"] == 2.0


def test_scan_calls_short_and_long_term_assignment():
    today = date.today()
    short_exp = (today + timedelta(days=90)).isoformat()
    long_exp = (today + timedelta(days=250)).isoformat()
    calls = _make_calls_df([{"contractSymbol": "MU_C", "strike": 100.0, "ask": 2.0}])
    t = MagicMock()
    t.options = [short_exp, long_exp]
    t.option_chain.return_value = MagicMock(calls=calls)
    with patch("yfinance.Ticker", return_value=t):
        signals = DramMemoryCallScanner(universe=["MU"])._scan_options("MU", 20.0, 80.0)
    terms = {s.data["term"] for s in signals}
    assert "short" in terms or "moonshot" in terms


def test_scan_calls_caps_short_at_10():
    today = date.today()
    expiry = (today + timedelta(days=90)).isoformat()
    rows = [{"contractSymbol": f"MU_{i}", "strike": 100.0 + i, "ask": 1.0 + i * 0.1} for i in range(20)]
    calls = _make_calls_df(rows)
    t = MagicMock()
    t.options = [expiry]
    t.option_chain.return_value = MagicMock(calls=calls)
    with patch("yfinance.Ticker", return_value=t):
        signals = DramMemoryCallScanner(universe=["MU"])._scan_options("MU", 20.0, 80.0)
    assert len([s for s in signals if s.data["term"] == "short"]) <= 10


def test_scan_calls_includes_breakeven_rise_pct():
    today = date.today()
    expiry = (today + timedelta(days=90)).isoformat()
    calls = _make_calls_df([{"contractSymbol": "MU_C", "strike": 100.0, "ask": 2.0}])
    t = MagicMock()
    t.options = [expiry]
    t.option_chain.return_value = MagicMock(calls=calls)
    with patch("yfinance.Ticker", return_value=t):
        signals = DramMemoryCallScanner(universe=["MU"])._scan_options("MU", 20.0, 80.0)
    assert len(signals) > 0
    assert "breakeven_rise_pct" in signals[0].data


def test_scan_calls_chain_error_continues():
    today = date.today()
    exp1 = (today + timedelta(days=90)).isoformat()
    exp2 = (today + timedelta(days=120)).isoformat()
    calls = _make_calls_df([{"contractSymbol": "MU_OK", "strike": 100.0, "ask": 2.0}])
    t = MagicMock()
    t.options = [exp1, exp2]

    def chain_side_effect(expiry):
        if expiry == exp1:
            raise Exception("api error")
        return MagicMock(calls=calls)

    t.option_chain.side_effect = chain_side_effect
    with patch("yfinance.Ticker", return_value=t):
        signals = DramMemoryCallScanner(universe=["MU"])._scan_options("MU", 20.0, 80.0)
    assert len(signals) > 0
