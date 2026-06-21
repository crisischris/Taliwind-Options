from __future__ import annotations

from datetime import date, timedelta
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

import tailwind_options.cache as cache_mod
from tailwind_options import cache
from tailwind_options.sources.sector_rotation_calls import SectorRotationCallScanner


@pytest.fixture(autouse=True)
def clear_cache(tmp_path, monkeypatch):
    monkeypatch.setattr(cache_mod, "_CACHE_DIR", tmp_path)


def _make_yf_download(tickers: list[str], prices: list[tuple[float, float]], n: int = 35) -> pd.DataFrame:
    """Multi-level close DataFrame with n rows (linearly interpolated start→end)."""
    dates = pd.date_range("2025-01-01", periods=n, freq="D")
    cols = pd.MultiIndex.from_tuples([("Close", t) for t in tickers])
    rows = []
    for i in range(n):
        t = i / (n - 1)
        row = [p[0] + t * (p[1] - p[0]) for p in prices]
        rows.append(row)
    return pd.DataFrame(rows, columns=cols, index=dates)


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


# ── _find_rotation_leaders ────────────────────────────────────────────────────

def test_find_rotation_leaders_uses_cache():
    expected = [("NVDA", {"sector": "Technology", "sector_median_pct": 15.0, "return_30d_pct": 20.0, "sector_rs_pct": 10.0, "move_pct": 10.0})]
    cache.set("rotation_leaders_30d", expected)
    scanner = SectorRotationCallScanner(universe=["NVDA"])
    result = scanner._find_rotation_leaders()
    assert result == expected


def test_find_rotation_leaders_no_ohlcv_returns_empty():
    with patch("tailwind_options.market_data.yf.download", side_effect=Exception("net")):
        scanner = SectorRotationCallScanner(universe=["NVDA"])
        result = scanner._find_rotation_leaders()
    assert result == []


def test_find_rotation_leaders_no_outperforming_sectors_returns_empty():
    """All stocks in same sector → sector median == market median, no outperformance."""
    data = _make_yf_download(["AAPL", "MSFT"], [(100.0, 105.0), (100.0, 106.0)])
    cache.set("ohlcv_1y", data)
    info_map = {
        "AAPL": {"sector": "Technology"},
        "MSFT": {"sector": "Technology"},
    }
    cache.set("universe_info", info_map)
    scanner = SectorRotationCallScanner(universe=["AAPL", "MSFT"])
    result = scanner._find_rotation_leaders()
    assert result == []


def test_find_rotation_leaders_finds_outperforming_sector():
    """Tech stocks return 20% vs energy stocks returning 5% → Tech outperforms by 15%."""
    # 2 tech + 3 energy: market median = 5% (energy dominates), tech median = ~20%
    tickers = ["NVDA", "AAPL", "XOM", "CVX", "COP"]
    prices = [(100.0, 120.0), (100.0, 120.0), (100.0, 105.0), (100.0, 105.0), (100.0, 105.0)]
    data = _make_yf_download(tickers, prices)
    cache.set("ohlcv_1y", data)
    info_map = {
        "NVDA": {"sector": "Technology"},
        "AAPL": {"sector": "Technology"},
        "XOM": {"sector": "Energy"},
        "CVX": {"sector": "Energy"},
        "COP": {"sector": "Energy"},
    }
    cache.set("universe_info", info_map)
    scanner = SectorRotationCallScanner(universe=tickers)
    result = scanner._find_rotation_leaders()
    tickers_in_result = [r[0] for r in result]
    assert "NVDA" in tickers_in_result or "AAPL" in tickers_in_result
    assert "XOM" not in tickers_in_result


def test_find_rotation_leaders_skips_tickers_without_sector():
    data = _make_yf_download(["NVDA"], [(100.0, 120.0)])
    cache.set("ohlcv_1y", data)
    cache.set("universe_info", {})  # no sector info
    scanner = SectorRotationCallScanner(universe=["NVDA"])
    result = scanner._find_rotation_leaders()
    assert result == []


# ── _scan_calls ───────────────────────────────────────────────────────────────

def test_scan_calls_no_expirations_returns_empty():
    mock_ticker = MagicMock()
    mock_ticker.options = []
    with patch("yfinance.Ticker", return_value=mock_ticker):
        scanner = SectorRotationCallScanner(universe=["NVDA"])
        meta = {"sector": "Technology", "sector_median_pct": 15.0, "return_30d_pct": 20.0, "sector_rs_pct": 10.0, "move_pct": 10.0}
        signals = scanner._scan_options("NVDA", meta, 500.0)
    assert signals == []


def test_scan_calls_produces_signals():
    today = date.today()
    expiry = (today + timedelta(days=90)).isoformat()
    calls = _make_calls_df([{"contractSymbol": "NVDA_90D", "strike": 550.0, "ask": 5.0}])

    mock_ticker = MagicMock()
    mock_ticker.options = [expiry]
    mock_ticker.option_chain.return_value = MagicMock(calls=calls)

    meta = {"sector": "Technology", "sector_median_pct": 15.0, "return_30d_pct": 20.0, "sector_rs_pct": 10.0, "move_pct": 10.0}
    with patch("yfinance.Ticker", return_value=mock_ticker):
        scanner = SectorRotationCallScanner(universe=["NVDA"])
        signals = scanner._scan_options("NVDA", meta, 500.0)

    assert len(signals) > 0
    assert signals[0].data["theme_id"] == "sector-rotation"
    assert signals[0].data["move_label"] == "sector RS"


def test_scan_calls_filters_itm():
    today = date.today()
    expiry = (today + timedelta(days=90)).isoformat()
    calls = _make_calls_df([{"contractSymbol": "ITM", "strike": 100.0, "ask": 3.0, "inTheMoney": True}])

    mock_ticker = MagicMock()
    mock_ticker.options = [expiry]
    mock_ticker.option_chain.return_value = MagicMock(calls=calls)

    meta = {"sector": "Technology", "sector_median_pct": 15.0, "return_30d_pct": 20.0, "sector_rs_pct": 10.0, "move_pct": 10.0}
    with patch("yfinance.Ticker", return_value=mock_ticker):
        scanner = SectorRotationCallScanner(universe=["NVDA"])
        signals = scanner._scan_options("NVDA", meta, 500.0)

    assert signals == []


# ── check ─────────────────────────────────────────────────────────────────────

def test_check_no_candidates_returns_empty():
    cache.set("rotation_leaders_30d", [])
    scanner = SectorRotationCallScanner(universe=["NVDA"])
    signals = scanner.check()
    assert signals == []


def test_check_returns_signals_for_candidates():
    candidate = ("NVDA", {"sector": "Technology", "sector_median_pct": 15.0, "return_30d_pct": 20.0, "sector_rs_pct": 10.0, "move_pct": 10.0})
    cache.set("rotation_leaders_30d", [candidate])

    today = date.today()
    expiry = (today + timedelta(days=90)).isoformat()
    calls = _make_calls_df([{"contractSymbol": "NVDA_90D", "strike": 550.0, "ask": 5.0}])

    mock_ticker = MagicMock()
    mock_ticker.fast_info.last_price = 500.0
    mock_ticker.options = [expiry]
    mock_ticker.option_chain.return_value = MagicMock(calls=calls)

    with patch("yfinance.Ticker", return_value=mock_ticker):
        scanner = SectorRotationCallScanner(universe=["NVDA"])
        signals = scanner.check()

    assert len(signals) > 0
    assert all(s.triggered for s in signals)
