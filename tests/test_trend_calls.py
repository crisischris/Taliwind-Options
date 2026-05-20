from __future__ import annotations

import math
from datetime import date, timedelta
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

import tailwind_options.cache as cache_mod
from tailwind_options import cache
from tailwind_options.sources.trend_calls import (
    TrendCallScanner,
    _norm_cdf,
    _prob_itm_call,
)


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
        "contractSymbol": "TSLA260101C00300000",
        "strike": 300.0,
        "lastPrice": 3.0,
        "bid": 2.8,
        "ask": 3.2,
        "impliedVolatility": 0.6,
        "inTheMoney": False,
        "openInterest": 50,
        "volume": 20,
    }
    return pd.DataFrame([{**defaults, **r} for r in rows])


# ── _norm_cdf ─────────────────────────────────────────────────────────────────

def test_norm_cdf_at_zero():
    assert abs(_norm_cdf(0) - 0.5) < 1e-6


def test_norm_cdf_positive_large():
    assert _norm_cdf(4.0) > 0.99


def test_norm_cdf_negative_large():
    assert _norm_cdf(-4.0) < 0.01


# ── _prob_itm_call ────────────────────────────────────────────────────────────

def test_prob_itm_call_between_0_and_1():
    p = _prob_itm_call(S=200, K=250, T=0.5, sigma=0.6)
    assert 0.0 <= p <= 1.0


def test_prob_itm_call_zero_when_T_is_zero():
    assert _prob_itm_call(S=200, K=250, T=0, sigma=0.6) == 0.0


def test_prob_itm_call_zero_when_sigma_is_zero():
    assert _prob_itm_call(S=200, K=250, T=0.5, sigma=0) == 0.0


def test_prob_itm_call_zero_when_S_is_zero():
    assert _prob_itm_call(S=0, K=250, T=0.5, sigma=0.6) == 0.0


def test_prob_itm_call_zero_when_K_is_zero():
    assert _prob_itm_call(S=200, K=0, T=0.5, sigma=0.6) == 0.0


def test_prob_itm_call_higher_when_closer_to_atm():
    p_far = _prob_itm_call(S=100, K=200, T=1.0, sigma=0.5)
    p_near = _prob_itm_call(S=100, K=110, T=1.0, sigma=0.5)
    assert p_near > p_far


# ── TrendCallScanner.check ────────────────────────────────────────────────────

def test_check_empty_universe_returns_empty():
    scanner = TrendCallScanner(universe=[])
    assert scanner.check() == []


def test_check_no_momentum_tickers_returns_empty():
    download_result = _make_yf_download(["TSLA"], [(100.0, 100.0)])  # 0% gain
    with patch("tailwind_options.sources.trend_calls.yf.download", return_value=download_result):
        scanner = TrendCallScanner(universe=["TSLA"])
        signals = scanner.check()
    assert signals == []


def test_check_error_on_ticker_continues():
    download_result = _make_yf_download(["TSLA", "NVDA"], [(10.0, 90.0), (10.0, 90.0)])

    today = date.today()
    expiry = (today + timedelta(days=90)).isoformat()
    calls = _make_calls_df([{"contractSymbol": "NVDA_OK", "strike": 300.0, "ask": 3.0}])

    def ticker_side_effect(sym):
        t = MagicMock()
        if sym == "TSLA":
            raise RuntimeError("api error")
        t.fast_info.last_price = 150.0
        t.options = [expiry]
        t.option_chain.return_value = MagicMock(calls=calls)
        return t

    with patch("tailwind_options.sources.trend_calls.yf.download", return_value=download_result):
        with patch("tailwind_options.sources.trend_calls.yf.Ticker", side_effect=ticker_side_effect):
            scanner = TrendCallScanner(universe=["TSLA", "NVDA"])
            signals = scanner.check()

    assert any(s.data["ticker"] == "NVDA" for s in signals)


# ── _filter_by_momentum ───────────────────────────────────────────────────────

def test_filter_by_momentum_returns_passing_tickers():
    # TSLA: +800% (passes), NVDA: +5% (below 15% threshold)
    download_result = _make_yf_download(["TSLA", "NVDA"], [(10.0, 90.0), (10.0, 10.5)])
    with patch("tailwind_options.sources.trend_calls.yf.download", return_value=download_result):
        scanner = TrendCallScanner(universe=["TSLA", "NVDA"])
        result = scanner._filter_by_momentum()
    tickers = [r[0] for r in result]
    assert "TSLA" in tickers
    assert "NVDA" not in tickers


def test_filter_by_momentum_sorted_descending():
    download_result = _make_yf_download(
        ["TSLA", "NVDA", "PLTR"],
        [(10.0, 90.0), (10.0, 50.0), (10.0, 200.0)],
    )
    with patch("tailwind_options.sources.trend_calls.yf.download", return_value=download_result):
        scanner = TrendCallScanner(universe=["TSLA", "NVDA", "PLTR"])
        result = scanner._filter_by_momentum()
    gains = [r[1] for r in result]
    assert gains == sorted(gains, reverse=True)


def test_filter_by_momentum_uses_cache():
    download_result = _make_yf_download(["TSLA"], [(10.0, 90.0)])
    with patch("tailwind_options.sources.trend_calls.yf.download", return_value=download_result) as mock_dl:
        scanner = TrendCallScanner(universe=["TSLA"])
        scanner._filter_by_momentum()
        mock_dl.assert_called_once()
    with patch("tailwind_options.sources.trend_calls.yf.download") as mock_dl2:
        scanner._filter_by_momentum()
        mock_dl2.assert_not_called()


def test_filter_by_momentum_download_failure_returns_empty():
    with patch("tailwind_options.sources.trend_calls.yf.download", side_effect=Exception("network")):
        scanner = TrendCallScanner(universe=["TSLA"])
        result = scanner._filter_by_momentum()
    assert result == []


def test_filter_by_momentum_skips_insufficient_data():
    dates = pd.date_range("2025-01-01", periods=1, freq="D")
    cols = pd.MultiIndex.from_tuples([("Close", "TSLA")])
    df = pd.DataFrame([[100.0]], columns=cols, index=dates)
    with patch("tailwind_options.sources.trend_calls.yf.download", return_value=df):
        scanner = TrendCallScanner(universe=["TSLA"])
        result = scanner._filter_by_momentum()
    assert result == []


# ── _fetch_price ──────────────────────────────────────────────────────────────

def test_fetch_price_returns_price():
    mock_ticker = MagicMock()
    mock_ticker.fast_info.last_price = 150.0
    with patch("tailwind_options.sources.trend_calls.yf.Ticker", return_value=mock_ticker):
        scanner = TrendCallScanner(universe=["TSLA"])
        price = scanner._fetch_price("TSLA")
    assert price == 150.0


def test_fetch_price_none_when_no_price():
    mock_ticker = MagicMock()
    mock_ticker.fast_info.last_price = None
    with patch("tailwind_options.sources.trend_calls.yf.Ticker", return_value=mock_ticker):
        scanner = TrendCallScanner(universe=["TSLA"])
        price = scanner._fetch_price("TSLA")
    assert price is None


def test_fetch_price_uses_cache():
    mock_ticker = MagicMock()
    mock_ticker.fast_info.last_price = 150.0
    with patch("tailwind_options.sources.trend_calls.yf.Ticker", return_value=mock_ticker) as mock_yf:
        scanner = TrendCallScanner(universe=["TSLA"])
        scanner._fetch_price("TSLA")
        scanner._fetch_price("TSLA")
        mock_yf.assert_called_once()


# ── _scan_calls ───────────────────────────────────────────────────────────────

def test_scan_calls_no_expirations_returns_empty():
    mock_ticker = MagicMock()
    mock_ticker.options = []
    with patch("tailwind_options.sources.trend_calls.yf.Ticker", return_value=mock_ticker):
        scanner = TrendCallScanner(universe=["TSLA"])
        signals = scanner._scan_calls("TSLA", 90.0, 150.0)
    assert signals == []


def test_scan_calls_produces_signals():
    today = date.today()
    expiry = (today + timedelta(days=90)).isoformat()
    calls = _make_calls_df([{"contractSymbol": "TSLA_90D", "strike": 200.0, "ask": 3.0}])

    mock_ticker = MagicMock()
    mock_ticker.options = [expiry]
    mock_ticker.option_chain.return_value = MagicMock(calls=calls)

    with patch("tailwind_options.sources.trend_calls.yf.Ticker", return_value=mock_ticker):
        scanner = TrendCallScanner(universe=["TSLA"])
        signals = scanner._scan_calls("TSLA", 90.0, 150.0)

    assert len(signals) > 0
    assert signals[0].triggered is True
    assert signals[0].data["ticker"] == "TSLA"


def test_scan_calls_filters_itm():
    today = date.today()
    expiry = (today + timedelta(days=90)).isoformat()
    calls = _make_calls_df([{"contractSymbol": "ITM", "strike": 100.0, "ask": 3.0, "inTheMoney": True}])

    mock_ticker = MagicMock()
    mock_ticker.options = [expiry]
    mock_ticker.option_chain.return_value = MagicMock(calls=calls)

    with patch("tailwind_options.sources.trend_calls.yf.Ticker", return_value=mock_ticker):
        scanner = TrendCallScanner(universe=["TSLA"])
        signals = scanner._scan_calls("TSLA", 90.0, 150.0)

    assert signals == []


def test_scan_calls_filters_high_cost():
    today = date.today()
    expiry = (today + timedelta(days=90)).isoformat()
    # ask = 10.0, price = 150.0 → 6.7% > 4% limit
    calls = _make_calls_df([{"contractSymbol": "EXPENSIVE", "strike": 200.0, "ask": 10.0}])

    mock_ticker = MagicMock()
    mock_ticker.options = [expiry]
    mock_ticker.option_chain.return_value = MagicMock(calls=calls)

    with patch("tailwind_options.sources.trend_calls.yf.Ticker", return_value=mock_ticker):
        scanner = TrendCallScanner(universe=["TSLA"])
        signals = scanner._scan_calls("TSLA", 90.0, 150.0)

    assert signals == []


def test_scan_calls_uses_lastprice_when_ask_zero():
    today = date.today()
    expiry = (today + timedelta(days=90)).isoformat()
    calls = _make_calls_df([{
        "contractSymbol": "TSLA_NASK",
        "strike": 200.0,
        "ask": 0.0,
        "lastPrice": 3.0,
        "openInterest": 0,
        "volume": 0,
    }])

    mock_ticker = MagicMock()
    mock_ticker.options = [expiry]
    mock_ticker.option_chain.return_value = MagicMock(calls=calls)

    with patch("tailwind_options.sources.trend_calls.yf.Ticker", return_value=mock_ticker):
        scanner = TrendCallScanner(universe=["TSLA"])
        signals = scanner._scan_calls("TSLA", 90.0, 150.0)

    assert len(signals) > 0
    assert signals[0].data["ask"] == 3.0


def test_scan_calls_short_and_long_term_assignment():
    today = date.today()
    short_exp = (today + timedelta(days=90)).isoformat()
    long_exp = (today + timedelta(days=250)).isoformat()  # within 365-day max DTE
    calls = _make_calls_df([{"contractSymbol": "TSLA_C", "strike": 200.0, "ask": 3.0}])

    mock_ticker = MagicMock()
    mock_ticker.options = [short_exp, long_exp]
    mock_ticker.option_chain.return_value = MagicMock(calls=calls)

    with patch("tailwind_options.sources.trend_calls.yf.Ticker", return_value=mock_ticker):
        scanner = TrendCallScanner(universe=["TSLA"])
        signals = scanner._scan_calls("TSLA", 90.0, 150.0)

    terms = {s.data["term"] for s in signals}
    assert "short" in terms or "moonshot" in terms
    assert "long" in terms or "moonshot" in terms


def test_scan_calls_caps_short_at_10():
    today = date.today()
    expiry = (today + timedelta(days=90)).isoformat()
    rows = [
        {"contractSymbol": f"TSLA_{i}", "strike": 200.0 + i, "ask": 1.0 + i * 0.1}
        for i in range(20)
    ]
    calls = _make_calls_df(rows)

    mock_ticker = MagicMock()
    mock_ticker.options = [expiry]
    mock_ticker.option_chain.return_value = MagicMock(calls=calls)

    with patch("tailwind_options.sources.trend_calls.yf.Ticker", return_value=mock_ticker):
        scanner = TrendCallScanner(universe=["TSLA"])
        signals = scanner._scan_calls("TSLA", 90.0, 150.0)

    short_signals = [s for s in signals if s.data["term"] == "short"]
    assert len(short_signals) <= 10


def test_scan_calls_option_chain_error_continues():
    today = date.today()
    exp1 = (today + timedelta(days=90)).isoformat()
    exp2 = (today + timedelta(days=120)).isoformat()
    calls = _make_calls_df([{"contractSymbol": "TSLA_OK", "strike": 200.0, "ask": 3.0}])

    mock_ticker = MagicMock()
    mock_ticker.options = [exp1, exp2]

    def chain_side_effect(expiry):
        if expiry == exp1:
            raise Exception("api error")
        return MagicMock(calls=calls)

    mock_ticker.option_chain.side_effect = chain_side_effect

    with patch("tailwind_options.sources.trend_calls.yf.Ticker", return_value=mock_ticker):
        scanner = TrendCallScanner(universe=["TSLA"])
        signals = scanner._scan_calls("TSLA", 90.0, 150.0)

    assert len(signals) > 0


def test_scan_calls_includes_breakeven_rise_pct():
    today = date.today()
    expiry = (today + timedelta(days=90)).isoformat()
    calls = _make_calls_df([{"contractSymbol": "TSLA_C", "strike": 200.0, "ask": 3.0}])

    mock_ticker = MagicMock()
    mock_ticker.options = [expiry]
    mock_ticker.option_chain.return_value = MagicMock(calls=calls)

    with patch("tailwind_options.sources.trend_calls.yf.Ticker", return_value=mock_ticker):
        scanner = TrendCallScanner(universe=["TSLA"])
        signals = scanner._scan_calls("TSLA", 90.0, 150.0)

    assert len(signals) > 0
    assert "breakeven_rise_pct" in signals[0].data
    assert "momentum_pct" in signals[0].data
