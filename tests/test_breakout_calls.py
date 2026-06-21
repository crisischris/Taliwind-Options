from __future__ import annotations

from datetime import date, timedelta
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

import tailwind_options.cache as cache_mod
from tailwind_options import cache
from tailwind_options.sources.breakout_calls import BreakoutCallScanner


@pytest.fixture(autouse=True)
def clear_cache(tmp_path, monkeypatch):
    monkeypatch.setattr(cache_mod, "_CACHE_DIR", tmp_path)


def _make_ohlcv(
    tickers: list[str],
    close_rows: list[list[float]],
    vol_rows: list[list[float]] | None = None,
) -> pd.DataFrame:
    n = len(close_rows)
    dates = pd.date_range(end=date.today(), periods=n, freq="D")
    vol_rows = vol_rows or [[1_000_000] * len(tickers)] * n
    close_cols = pd.MultiIndex.from_tuples([("Close", t) for t in tickers])
    vol_cols = pd.MultiIndex.from_tuples([("Volume", t) for t in tickers])
    close_df = pd.DataFrame(close_rows, columns=close_cols, index=dates)
    vol_df = pd.DataFrame(vol_rows, columns=vol_cols, index=dates)
    return pd.concat([close_df, vol_df], axis=1)


def _make_calls_df(rows: list[dict]) -> pd.DataFrame:
    defaults = {
        "contractSymbol": "TICKER260101C00300000",
        "strike": 300.0,
        "lastPrice": 3.0,
        "bid": 2.8,
        "ask": 3.2,
        "impliedVolatility": 0.5,
        "inTheMoney": False,
        "openInterest": 50,
        "volume": 20,
    }
    return pd.DataFrame([{**defaults, **r} for r in rows])


# ── _find_breakouts ───────────────────────────────────────────────────────────

def test_find_breakouts_no_ohlcv_returns_empty():
    with patch("tailwind_options.market_data.yf.download", side_effect=Exception("net")):
        scanner = BreakoutCallScanner(universe=["AAPL"])
        result = scanner._find_breakouts()
    assert result == []


def test_find_breakouts_uses_cache():
    expected = [("AAPL", {"high_52w": 200.0, "pct_from_high": 1.0, "vol_ratio": 2.0, "move_pct": 100.0})]
    cache.set("breakout_candidates", expected)
    scanner = BreakoutCallScanner(universe=["AAPL"])
    result = scanner._find_breakouts()
    assert result == expected


def test_find_breakouts_skips_insufficient_data():
    data = _make_ohlcv(["AAPL"], [[100.0]] * 5, [[1_000_000]] * 5)
    cache.set("ohlcv_1y", data)
    scanner = BreakoutCallScanner(universe=["AAPL"])
    result = scanner._find_breakouts()
    assert result == []


def test_find_breakouts_skips_far_from_high():
    """Ticker 10% below 52W high → exceeds max_pct_from_high=2%."""
    n = 30
    # Max at start, current is 10% below
    close_vals = [100.0] + [90.0] * (n - 1)
    vol_vals = [1_000_000] * n
    data = _make_ohlcv(["AAPL"], [[v] for v in close_vals], [[v] for v in vol_vals])
    cache.set("ohlcv_1y", data)
    scanner = BreakoutCallScanner(universe=["AAPL"])
    result = scanner._find_breakouts()
    assert result == []


def test_find_breakouts_skips_low_volume():
    """Ticker near 52W high but with insufficient volume boost."""
    n = 30
    # Near high (1% below)
    close_vals = [100.0] + [99.0] * (n - 1)
    # Today's volume is only 1x average (not 1.5x)
    vol_vals = [[1_000_000]] * n
    data = _make_ohlcv(["AAPL"], [[v] for v in close_vals], vol_vals)
    cache.set("ohlcv_1y", data)
    scanner = BreakoutCallScanner(universe=["AAPL"])
    result = scanner._find_breakouts()
    assert result == []


def test_find_breakouts_finds_candidate():
    """Ticker within 1% of 52W high with 2x volume → qualifies."""
    n = 30
    # Max in first row; current (last) is 99 (1% below)
    close_vals = [100.0] + [99.0] * (n - 1)
    # Avg volume over last 20 sessions is 1M, today (last) is 2M
    vol_vals = [[1_000_000]] * (n - 1) + [[2_000_000]]
    data = _make_ohlcv(["AAPL"], [[v] for v in close_vals], vol_vals)
    cache.set("ohlcv_1y", data)
    scanner = BreakoutCallScanner(universe=["AAPL"])
    result = scanner._find_breakouts()
    assert len(result) == 1
    assert result[0][0] == "AAPL"
    assert result[0][1]["vol_ratio"] >= 1.5


# ── _scan_calls ───────────────────────────────────────────────────────────────

def test_scan_calls_no_expirations_returns_empty():
    mock_ticker = MagicMock()
    mock_ticker.options = []
    with patch("yfinance.Ticker", return_value=mock_ticker):
        scanner = BreakoutCallScanner(universe=["AAPL"])
        meta = {"high_52w": 200.0, "pct_from_high": 1.0, "vol_ratio": 2.0, "move_pct": 100.0}
        signals = scanner._scan_options("AAPL", meta, 198.0)
    assert signals == []


def test_scan_calls_produces_signals():
    today = date.today()
    expiry = (today + timedelta(days=90)).isoformat()
    calls = _make_calls_df([{"contractSymbol": "AAPL_90D", "strike": 210.0, "ask": 3.0}])

    mock_ticker = MagicMock()
    mock_ticker.options = [expiry]
    mock_ticker.option_chain.return_value = MagicMock(calls=calls)

    meta = {"high_52w": 200.0, "pct_from_high": 1.0, "vol_ratio": 2.0, "move_pct": 100.0}
    with patch("yfinance.Ticker", return_value=mock_ticker):
        scanner = BreakoutCallScanner(universe=["AAPL"])
        signals = scanner._scan_options("AAPL", meta, 198.0)

    assert len(signals) > 0
    assert signals[0].triggered is True
    assert signals[0].data["theme_id"] == "52-week-breakouts"
    assert signals[0].data["move_label"] == "vol ratio"


def test_scan_calls_filters_itm():
    today = date.today()
    expiry = (today + timedelta(days=90)).isoformat()
    calls = _make_calls_df([{"contractSymbol": "ITM", "strike": 100.0, "ask": 3.0, "inTheMoney": True}])

    mock_ticker = MagicMock()
    mock_ticker.options = [expiry]
    mock_ticker.option_chain.return_value = MagicMock(calls=calls)

    meta = {"high_52w": 200.0, "pct_from_high": 1.0, "vol_ratio": 2.0, "move_pct": 100.0}
    with patch("yfinance.Ticker", return_value=mock_ticker):
        scanner = BreakoutCallScanner(universe=["AAPL"])
        signals = scanner._scan_options("AAPL", meta, 198.0)

    assert signals == []


# ── check ─────────────────────────────────────────────────────────────────────

def test_check_no_candidates_returns_empty():
    cache.set("breakout_candidates", [])
    scanner = BreakoutCallScanner(universe=["AAPL"])
    signals = scanner.check()
    assert signals == []


def test_check_returns_signals_for_candidates():
    candidate = ("AAPL", {"high_52w": 200.0, "pct_from_high": 1.0, "vol_ratio": 2.0, "move_pct": 100.0})
    cache.set("breakout_candidates", [candidate])

    today = date.today()
    expiry = (today + timedelta(days=90)).isoformat()
    calls = _make_calls_df([{"contractSymbol": "AAPL_90D", "strike": 210.0, "ask": 3.0}])

    mock_ticker = MagicMock()
    mock_ticker.fast_info.last_price = 198.0
    mock_ticker.options = [expiry]
    mock_ticker.option_chain.return_value = MagicMock(calls=calls)

    with patch("yfinance.Ticker", return_value=mock_ticker):
        scanner = BreakoutCallScanner(universe=["AAPL"])
        signals = scanner.check()

    assert len(signals) > 0
    assert all(s.triggered for s in signals)
