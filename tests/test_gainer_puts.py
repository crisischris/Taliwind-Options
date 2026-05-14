from __future__ import annotations

import math
from datetime import date, timedelta
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

import indicators.cache as cache_mod
from indicators import cache
from indicators.sources.gainer_puts import (
    GainerPutScanner,
    _norm_cdf,
    _prob_itm_put,
    _TERM_BOUNDARY_DAYS,
)


# ── fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def clear_cache(tmp_path, monkeypatch):
    monkeypatch.setattr(cache_mod, "_CACHE_DIR", tmp_path)


def _make_history(tickers: list[str], prices: list[tuple[float, float]]) -> pd.DataFrame:
    """Cached closes DataFrame — plain columns are ticker names (post-selection)."""
    dates = pd.date_range("2025-01-01", periods=2, freq="D")
    return pd.DataFrame(
        {t: [p[0], p[1]] for t, p in zip(tickers, prices)},
        index=dates,
    )


def _make_yf_download(tickers: list[str], prices: list[tuple[float, float]]) -> pd.DataFrame:
    """MultiIndex DataFrame matching yfinance's actual download return format."""
    dates = pd.date_range("2025-01-01", periods=2, freq="D")
    cols = pd.MultiIndex.from_tuples([("Close", t) for t in tickers])
    rows = [[p[0] for p in prices], [p[1] for p in prices]]
    return pd.DataFrame(rows, columns=cols, index=dates)


def _make_puts_df(rows: list[dict]) -> pd.DataFrame:
    defaults = {
        "contractSymbol": "TICKER260101P00100000",
        "strike": 100.0,
        "lastPrice": 2.0,
        "bid": 1.8,
        "ask": 2.2,
        "impliedVolatility": 0.5,
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


def test_norm_cdf_symmetry():
    assert abs(_norm_cdf(1.5) + _norm_cdf(-1.5) - 1.0) < 1e-9


def test_norm_cdf_196():
    assert abs(_norm_cdf(1.96) - 0.975) < 0.001


# ── _prob_itm_put ─────────────────────────────────────────────────────────────

def test_prob_itm_returns_between_0_and_1():
    p = _prob_itm_put(S=200, K=150, T=0.5, sigma=0.8)
    assert 0.0 <= p <= 1.0


def test_prob_itm_zero_when_T_is_zero():
    assert _prob_itm_put(S=200, K=150, T=0, sigma=0.8) == 0.0


def test_prob_itm_zero_when_sigma_is_zero():
    assert _prob_itm_put(S=200, K=150, T=0.5, sigma=0) == 0.0


def test_prob_itm_zero_when_S_is_zero():
    assert _prob_itm_put(S=0, K=150, T=0.5, sigma=0.8) == 0.0


def test_prob_itm_zero_when_K_is_zero():
    assert _prob_itm_put(S=200, K=0, T=0.5, sigma=0.8) == 0.0


def test_prob_itm_higher_when_deeper_otm():
    """Strike much lower than spot → lower prob ITM."""
    p_atm = _prob_itm_put(S=100, K=100, T=1.0, sigma=0.5)
    p_otm = _prob_itm_put(S=100, K=50, T=1.0, sigma=0.5)
    assert p_otm < p_atm


def test_prob_itm_negative_T_returns_zero():
    assert _prob_itm_put(S=200, K=150, T=-1, sigma=0.8) == 0.0


# ── _find_gainers ─────────────────────────────────────────────────────────────

def test_find_gainers_uses_cache(tmp_path):
    history = _make_history(["AAPL"], [(10.0, 70.0)])  # +600%
    cache.set("history_1y", history)

    scanner = GainerPutScanner(universe=["AAPL"])
    gainers = scanner._find_gainers(500.0)
    assert len(gainers) == 1
    assert gainers[0][0] == "AAPL"
    assert abs(gainers[0][1] - 600.0) < 0.1


def test_find_gainers_filters_by_threshold():
    history = _make_history(["AAPL", "MSFT"], [(10.0, 70.0), (10.0, 15.0)])  # +600%, +50%
    cache.set("history_1y", history)

    scanner = GainerPutScanner(universe=["AAPL", "MSFT"])
    gainers = scanner._find_gainers(500.0)
    tickers = [g[0] for g in gainers]
    assert "AAPL" in tickers
    assert "MSFT" not in tickers


def test_find_gainers_sorted_descending():
    history = _make_history(
        ["AAPL", "MSFT", "NVDA"],
        [(10.0, 70.0), (10.0, 110.0), (10.0, 170.0)],  # +600%, +1000%, +1600%
    )
    cache.set("history_1y", history)
    scanner = GainerPutScanner(universe=["AAPL", "MSFT", "NVDA"])
    gainers = scanner._find_gainers(100.0)
    gains = [g[1] for g in gainers]
    assert gains == sorted(gains, reverse=True)


def test_find_gainers_skips_insufficient_data():
    history = _make_history(["AAPL"], [(10.0, 70.0)])
    # Remove one row so only 1 data point
    history = history.iloc[[0]]
    cache.set("history_1y", history)
    scanner = GainerPutScanner(universe=["AAPL"])
    gainers = scanner._find_gainers(100.0)
    assert gainers == []


def test_find_gainers_skips_zero_start_price():
    history = _make_history(["AAPL"], [(0.0, 100.0)])
    cache.set("history_1y", history)
    scanner = GainerPutScanner(universe=["AAPL"])
    gainers = scanner._find_gainers(100.0)
    assert gainers == []


def test_find_gainers_download_failure_returns_empty():
    scanner = GainerPutScanner(universe=["AAPL"])
    with patch("indicators.sources.gainer_puts.yf.download", side_effect=Exception("network error")):
        gainers = scanner._find_gainers(500.0)
    assert gainers == []


def test_find_gainers_fetches_and_caches():
    download_result = _make_yf_download(["AAPL"], [(10.0, 70.0)])
    with patch("indicators.sources.gainer_puts.yf.download", return_value=download_result) as mock_dl:
        scanner = GainerPutScanner(universe=["AAPL"])
        scanner._find_gainers(500.0)
        mock_dl.assert_called_once()

    # Second call should hit cache, not download again
    with patch("indicators.sources.gainer_puts.yf.download") as mock_dl2:
        scanner._find_gainers(500.0)
        mock_dl2.assert_not_called()


# ── _scan_puts ────────────────────────────────────────────────────────────────

def _setup_scanner_with_expirations(monkeypatch, expirations, puts_df):
    """Helper to build a GainerPutScanner with mocked yfinance."""
    mock_ticker = MagicMock()
    mock_ticker.options = expirations
    mock_chain = MagicMock()
    mock_chain.puts = puts_df
    mock_ticker.option_chain.return_value = mock_chain

    with patch("indicators.sources.gainer_puts.yf.Ticker", return_value=mock_ticker):
        scanner = GainerPutScanner(universe=["AAPL"])
        signals = scanner._scan_puts("AAPL", 600.0, 200.0)
    return signals


def test_scan_puts_no_expirations_in_window():
    mock_ticker = MagicMock()
    mock_ticker.options = []
    with patch("indicators.sources.gainer_puts.yf.Ticker", return_value=mock_ticker):
        scanner = GainerPutScanner(universe=["AAPL"])
        signals = scanner._scan_puts("AAPL", 600.0, 200.0)
    assert signals == []


def test_scan_puts_produces_signals():
    today = date.today()
    expiry = (today + timedelta(days=90)).isoformat()
    puts = _make_puts_df([{"contractSymbol": "AAPL_90D", "strike": 150.0, "ask": 3.0}])

    mock_ticker = MagicMock()
    mock_ticker.options = [expiry]
    mock_ticker.option_chain.return_value = MagicMock(puts=puts)

    with patch("indicators.sources.gainer_puts.yf.Ticker", return_value=mock_ticker):
        scanner = GainerPutScanner(universe=["AAPL"])
        signals = scanner._scan_puts("AAPL", 600.0, 200.0)

    assert len(signals) > 0
    assert signals[0].triggered is True


def test_scan_puts_short_term_assignment():
    today = date.today()
    expiry = (today + timedelta(days=90)).isoformat()  # < 180 days → short
    puts = _make_puts_df([{"contractSymbol": "AAPL_SHORT", "strike": 150.0, "ask": 3.0}])

    mock_ticker = MagicMock()
    mock_ticker.options = [expiry]
    mock_ticker.option_chain.return_value = MagicMock(puts=puts)

    with patch("indicators.sources.gainer_puts.yf.Ticker", return_value=mock_ticker):
        scanner = GainerPutScanner(universe=["AAPL"])
        signals = scanner._scan_puts("AAPL", 600.0, 200.0)

    terms = {s.data["term"] for s in signals}
    assert "short" in terms or "moonshot" in terms


def test_scan_puts_long_term_assignment():
    today = date.today()
    expiry = (today + timedelta(days=400)).isoformat()  # > 180 days → long
    puts = _make_puts_df([{"contractSymbol": "AAPL_LONG", "strike": 150.0, "ask": 3.0}])

    mock_ticker = MagicMock()
    mock_ticker.options = [expiry]
    mock_ticker.option_chain.return_value = MagicMock(puts=puts)

    with patch("indicators.sources.gainer_puts.yf.Ticker", return_value=mock_ticker):
        scanner = GainerPutScanner(universe=["AAPL"])
        signals = scanner._scan_puts("AAPL", 600.0, 200.0)

    terms = {s.data["term"] for s in signals}
    assert "long" in terms or "moonshot" in terms


def test_scan_puts_filters_itm():
    today = date.today()
    expiry = (today + timedelta(days=90)).isoformat()
    puts = _make_puts_df([{"contractSymbol": "ITM", "strike": 250.0, "ask": 3.0, "inTheMoney": True}])

    mock_ticker = MagicMock()
    mock_ticker.options = [expiry]
    mock_ticker.option_chain.return_value = MagicMock(puts=puts)

    with patch("indicators.sources.gainer_puts.yf.Ticker", return_value=mock_ticker):
        scanner = GainerPutScanner(universe=["AAPL"])
        signals = scanner._scan_puts("AAPL", 600.0, 200.0)

    assert signals == []


def test_scan_puts_filters_high_cost():
    today = date.today()
    expiry = (today + timedelta(days=90)).isoformat()
    # ask = 20.0, price = 200.0 → 10% > 5% limit
    puts = _make_puts_df([{"contractSymbol": "EXPENSIVE", "strike": 150.0, "ask": 20.0}])

    mock_ticker = MagicMock()
    mock_ticker.options = [expiry]
    mock_ticker.option_chain.return_value = MagicMock(puts=puts)

    with patch("indicators.sources.gainer_puts.yf.Ticker", return_value=mock_ticker):
        scanner = GainerPutScanner(universe=["AAPL"])
        signals = scanner._scan_puts("AAPL", 600.0, 200.0)

    assert signals == []


def test_scan_puts_uses_lastprice_when_ask_zero():
    today = date.today()
    expiry = (today + timedelta(days=90)).isoformat()
    puts = _make_puts_df([{
        "contractSymbol": "AAPL_NASK",
        "strike": 150.0,
        "ask": 0.0,
        "lastPrice": 3.0,
        "openInterest": 0,
        "volume": 0,
    }])

    mock_ticker = MagicMock()
    mock_ticker.options = [expiry]
    mock_ticker.option_chain.return_value = MagicMock(puts=puts)

    with patch("indicators.sources.gainer_puts.yf.Ticker", return_value=mock_ticker):
        scanner = GainerPutScanner(universe=["AAPL"])
        signals = scanner._scan_puts("AAPL", 600.0, 200.0)

    assert len(signals) > 0
    assert signals[0].data["ask"] == 3.0


def test_scan_puts_caps_short_at_10():
    today = date.today()
    expiry = (today + timedelta(days=90)).isoformat()
    rows = [
        {"contractSymbol": f"AAPL_{i}", "strike": 150.0 - i, "ask": 1.0 + i * 0.1}
        for i in range(20)
    ]
    puts = _make_puts_df(rows)

    mock_ticker = MagicMock()
    mock_ticker.options = [expiry]
    mock_ticker.option_chain.return_value = MagicMock(puts=puts)

    with patch("indicators.sources.gainer_puts.yf.Ticker", return_value=mock_ticker):
        scanner = GainerPutScanner(universe=["AAPL"])
        signals = scanner._scan_puts("AAPL", 600.0, 200.0)

    short_signals = [s for s in signals if s.data["term"] == "short"]
    assert len(short_signals) <= 10


def test_scan_puts_option_chain_error_continues():
    today = date.today()
    exp1 = (today + timedelta(days=90)).isoformat()
    exp2 = (today + timedelta(days=120)).isoformat()
    puts = _make_puts_df([{"contractSymbol": "AAPL_OK", "strike": 150.0, "ask": 3.0}])

    mock_ticker = MagicMock()
    mock_ticker.options = [exp1, exp2]

    def chain_side_effect(expiry):
        if expiry == exp1:
            raise Exception("api error")
        return MagicMock(puts=puts)

    mock_ticker.option_chain.side_effect = chain_side_effect

    with patch("indicators.sources.gainer_puts.yf.Ticker", return_value=mock_ticker):
        scanner = GainerPutScanner(universe=["AAPL"])
        signals = scanner._scan_puts("AAPL", 600.0, 200.0)

    assert len(signals) > 0  # exp2 succeeded


# ── check ─────────────────────────────────────────────────────────────────────

def test_check_no_gainers_returns_empty():
    history = _make_history(["AAPL"], [(10.0, 11.0)])  # only +10%
    cache.set("history_1y", history)

    mock_ticker = MagicMock()
    mock_ticker.fast_info.last_price = 11.0

    with patch("indicators.sources.gainer_puts.yf.Ticker", return_value=mock_ticker):
        scanner = GainerPutScanner(universe=["AAPL"])
        signals = scanner.check()

    assert signals == []


def test_check_below_report_threshold_not_in_signals(monkeypatch):
    """Ticker above cache floor but below report threshold → not in returned signals."""
    history = _make_history(["AAPL"], [(10.0, 20.0)])  # +100% — above floor, below 500%
    cache.set("history_1y", history)

    mock_ticker = MagicMock()
    mock_ticker.fast_info.last_price = 20.0
    mock_ticker.options = []

    with patch("indicators.sources.gainer_puts.yf.Ticker", return_value=mock_ticker):
        scanner = GainerPutScanner(universe=["AAPL"])
        signals = scanner.check()

    assert signals == []


def test_check_error_on_one_ticker_does_not_stop_others():
    history = _make_history(["AAPL", "TSLA"], [(10.0, 70.0), (10.0, 70.0)])
    cache.set("history_1y", history)

    today = date.today()
    expiry = (today + timedelta(days=90)).isoformat()
    puts = _make_puts_df([{"contractSymbol": "TSLA_OK", "strike": 50.0, "ask": 1.0}])

    call_count = {"n": 0}

    def ticker_side_effect(sym):
        t = MagicMock()
        if sym == "AAPL":
            t.fast_info.last_price = None  # causes _fetch_price to return None
        else:
            t.fast_info.last_price = 70.0
            t.options = [expiry]
            t.option_chain.return_value = MagicMock(puts=puts)
        return t

    with patch("indicators.sources.gainer_puts.yf.Ticker", side_effect=ticker_side_effect):
        scanner = GainerPutScanner(universe=["AAPL", "TSLA"])
        signals = scanner.check()

    assert any(s.data["ticker"] == "TSLA" for s in signals)


def test_check_returns_signal_objects():
    history = _make_history(["AAPL"], [(10.0, 70.0)])
    cache.set("history_1y", history)

    today = date.today()
    expiry = (today + timedelta(days=90)).isoformat()
    puts = _make_puts_df([{"contractSymbol": "AAPL_SIG", "strike": 100.0, "ask": 2.0}])

    mock_ticker = MagicMock()
    mock_ticker.fast_info.last_price = 200.0
    mock_ticker.options = [expiry]
    mock_ticker.option_chain.return_value = MagicMock(puts=puts)

    with patch("indicators.sources.gainer_puts.yf.Ticker", return_value=mock_ticker):
        scanner = GainerPutScanner(universe=["AAPL"])
        signals = scanner.check()

    from indicators.sources.base import Signal
    assert all(isinstance(s, Signal) for s in signals)
    assert all(s.triggered for s in signals)
