from __future__ import annotations

from datetime import date, timedelta
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

import tailwind_options.cache as cache_mod
from tailwind_options import cache
from tailwind_options.sources.space_calls import SpaceCallScanner


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
        "contractSymbol": "RKLB260101C00020000",
        "strike": 20.0,
        "lastPrice": 1.0,
        "bid": 0.9,
        "ask": 1.1,
        "impliedVolatility": 0.9,
        "inTheMoney": False,
        "openInterest": 50,
        "volume": 20,
    }
    return pd.DataFrame([{**defaults, **r} for r in rows])


# ── check ─────────────────────────────────────────────────────────────────────

def test_check_no_momentum_returns_empty():
    data = _make_yf_download(["RKLB"], [(10.0, 10.0)])  # 0% gain
    with patch("tailwind_options.sources._helpers.yf.download", return_value=data):
        signals = SpaceCallScanner(universe=["RKLB"]).check()
    assert signals == []


def test_check_error_on_ticker_continues():
    data = _make_yf_download(["RKLB", "ASTS"], [(5.0, 50.0), (5.0, 50.0)])
    today = date.today()
    expiry = (today + timedelta(days=90)).isoformat()
    calls = _make_calls_df([{"contractSymbol": "ASTS_OK", "strike": 30.0, "ask": 0.8}])

    def ticker_side_effect(sym):
        t = MagicMock()
        if sym == "RKLB":
            raise RuntimeError("api error")
        t.fast_info.last_price = 25.0
        t.options = [expiry]
        t.option_chain.return_value = MagicMock(calls=calls)
        return t

    with patch("tailwind_options.sources._helpers.yf.download", return_value=data):
        with patch("yfinance.Ticker", side_effect=ticker_side_effect):
            signals = SpaceCallScanner(universe=["RKLB", "ASTS"]).check()

    assert any(s.data["ticker"] == "ASTS" for s in signals)


# ── _filter_by_momentum ───────────────────────────────────────────────────────

def test_filter_passes_above_threshold():
    data = _make_yf_download(["RKLB", "LMT"], [(5.0, 50.0), (100.0, 100.5)])
    with patch("tailwind_options.sources._helpers.yf.download", return_value=data):
        result = SpaceCallScanner(universe=["RKLB", "LMT"])._filter_by_momentum()
    tickers = [r[0] for r in result]
    assert "RKLB" in tickers
    assert "LMT" not in tickers


def test_filter_sorted_descending():
    data = _make_yf_download(["RKLB", "ASTS", "LUNR"], [(5.0, 50.0), (5.0, 30.0), (5.0, 100.0)])
    with patch("tailwind_options.sources._helpers.yf.download", return_value=data):
        result = SpaceCallScanner(universe=["RKLB", "ASTS", "LUNR"])._filter_by_momentum()
    gains = [r[1] for r in result]
    assert gains == sorted(gains, reverse=True)


def test_filter_uses_cache():
    data = _make_yf_download(["RKLB"], [(5.0, 50.0)])
    with patch("tailwind_options.sources._helpers.yf.download", return_value=data) as mock_dl:
        scanner = SpaceCallScanner(universe=["RKLB"])
        scanner._filter_by_momentum()
        mock_dl.assert_called_once()
    with patch("tailwind_options.sources._helpers.yf.download") as mock_dl2:
        scanner._filter_by_momentum()
        mock_dl2.assert_not_called()


def test_filter_download_failure_returns_empty():
    with patch("tailwind_options.sources._helpers.yf.download", side_effect=Exception("network")):
        result = SpaceCallScanner(universe=["RKLB"])._filter_by_momentum()
    assert result == []


def test_filter_skips_insufficient_data():
    dates = pd.date_range("2025-01-01", periods=1, freq="D")
    cols = pd.MultiIndex.from_tuples([("Close", "RKLB")])
    df = pd.DataFrame([[10.0]], columns=cols, index=dates)
    with patch("tailwind_options.sources._helpers.yf.download", return_value=df):
        result = SpaceCallScanner(universe=["RKLB"])._filter_by_momentum()
    assert result == []


# ── _scan_calls ───────────────────────────────────────────────────────────────

def test_scan_calls_no_expirations_returns_empty():
    t = MagicMock()
    t.options = []
    with patch("yfinance.Ticker", return_value=t):
        signals = SpaceCallScanner(universe=["RKLB"])._scan_options("RKLB", 30.0, 20.0)
    assert signals == []


def test_scan_calls_produces_signals():
    today = date.today()
    expiry = (today + timedelta(days=90)).isoformat()
    calls = _make_calls_df([{"contractSymbol": "RKLB_C", "strike": 25.0, "ask": 0.8}])
    t = MagicMock()
    t.options = [expiry]
    t.option_chain.return_value = MagicMock(calls=calls)
    with patch("yfinance.Ticker", return_value=t):
        signals = SpaceCallScanner(universe=["RKLB"])._scan_options("RKLB", 30.0, 20.0)
    assert len(signals) > 0
    assert signals[0].triggered is True
    assert signals[0].data["ticker"] == "RKLB"
    assert signals[0].data["theme_id"] == "space"


def test_scan_calls_filters_itm():
    today = date.today()
    expiry = (today + timedelta(days=90)).isoformat()
    calls = _make_calls_df([{"inTheMoney": True, "strike": 10.0, "ask": 0.5}])
    t = MagicMock()
    t.options = [expiry]
    t.option_chain.return_value = MagicMock(calls=calls)
    with patch("yfinance.Ticker", return_value=t):
        signals = SpaceCallScanner(universe=["RKLB"])._scan_options("RKLB", 30.0, 20.0)
    assert signals == []


def test_scan_calls_filters_high_cost():
    today = date.today()
    expiry = (today + timedelta(days=90)).isoformat()
    # ask 3.0 on price 20.0 = 15% > 5% limit
    calls = _make_calls_df([{"strike": 25.0, "ask": 3.0}])
    t = MagicMock()
    t.options = [expiry]
    t.option_chain.return_value = MagicMock(calls=calls)
    with patch("yfinance.Ticker", return_value=t):
        signals = SpaceCallScanner(universe=["RKLB"])._scan_options("RKLB", 30.0, 20.0)
    assert signals == []


def test_scan_calls_uses_lastprice_when_ask_zero():
    today = date.today()
    expiry = (today + timedelta(days=90)).isoformat()
    calls = _make_calls_df([{"strike": 25.0, "ask": 0.0, "lastPrice": 0.8, "openInterest": 0, "volume": 0}])
    t = MagicMock()
    t.options = [expiry]
    t.option_chain.return_value = MagicMock(calls=calls)
    with patch("yfinance.Ticker", return_value=t):
        signals = SpaceCallScanner(universe=["RKLB"])._scan_options("RKLB", 30.0, 20.0)
    assert len(signals) > 0
    assert signals[0].data["ask"] == 0.8


def test_scan_calls_short_and_long_term_assignment():
    today = date.today()
    short_exp = (today + timedelta(days=90)).isoformat()
    long_exp = (today + timedelta(days=250)).isoformat()
    calls = _make_calls_df([{"contractSymbol": "RKLB_C", "strike": 25.0, "ask": 0.8}])
    t = MagicMock()
    t.options = [short_exp, long_exp]
    t.option_chain.return_value = MagicMock(calls=calls)
    with patch("yfinance.Ticker", return_value=t):
        signals = SpaceCallScanner(universe=["RKLB"])._scan_options("RKLB", 30.0, 20.0)
    terms = {s.data["term"] for s in signals}
    assert "short" in terms or "moonshot" in terms


def test_scan_calls_caps_short_at_10():
    today = date.today()
    expiry = (today + timedelta(days=90)).isoformat()
    rows = [{"contractSymbol": f"RKLB_{i}", "strike": 25.0 + i, "ask": 0.5 + i * 0.05} for i in range(20)]
    calls = _make_calls_df(rows)
    t = MagicMock()
    t.options = [expiry]
    t.option_chain.return_value = MagicMock(calls=calls)
    with patch("yfinance.Ticker", return_value=t):
        signals = SpaceCallScanner(universe=["RKLB"])._scan_options("RKLB", 30.0, 20.0)
    assert len([s for s in signals if s.data["term"] == "short"]) <= 10


def test_scan_calls_includes_breakeven_rise_pct():
    today = date.today()
    expiry = (today + timedelta(days=90)).isoformat()
    calls = _make_calls_df([{"contractSymbol": "RKLB_C", "strike": 25.0, "ask": 0.8}])
    t = MagicMock()
    t.options = [expiry]
    t.option_chain.return_value = MagicMock(calls=calls)
    with patch("yfinance.Ticker", return_value=t):
        signals = SpaceCallScanner(universe=["RKLB"])._scan_options("RKLB", 30.0, 20.0)
    assert len(signals) > 0
    assert "breakeven_rise_pct" in signals[0].data


def test_scan_calls_chain_error_continues():
    today = date.today()
    exp1 = (today + timedelta(days=90)).isoformat()
    exp2 = (today + timedelta(days=120)).isoformat()
    calls = _make_calls_df([{"contractSymbol": "RKLB_OK", "strike": 25.0, "ask": 0.8}])
    t = MagicMock()
    t.options = [exp1, exp2]

    def chain_side_effect(expiry):
        if expiry == exp1:
            raise Exception("api error")
        return MagicMock(calls=calls)

    t.option_chain.side_effect = chain_side_effect
    with patch("yfinance.Ticker", return_value=t):
        signals = SpaceCallScanner(universe=["RKLB"])._scan_options("RKLB", 30.0, 20.0)
    assert len(signals) > 0
