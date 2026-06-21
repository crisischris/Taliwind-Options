from __future__ import annotations

from datetime import date, timedelta
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

import tailwind_options.cache as cache_mod
from tailwind_options import cache
from tailwind_options.sources.short_squeeze_calls import ShortSqueezeCallScanner


@pytest.fixture(autouse=True)
def clear_cache(tmp_path, monkeypatch):
    monkeypatch.setattr(cache_mod, "_CACHE_DIR", tmp_path)


def _make_yf_download(tickers: list[str], prices: list[tuple[float, float]], n: int = 35) -> pd.DataFrame:
    """Multi-level close DataFrame with n rows (first is start price, last is end price)."""
    dates = pd.date_range("2025-01-01", periods=n, freq="D")
    cols = pd.MultiIndex.from_tuples([("Close", t) for t in tickers])
    rows = []
    for i in range(n):
        t = i / (n - 1)  # 0 to 1
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


# ── _find_squeeze_candidates ──────────────────────────────────────────────────

def test_find_squeeze_candidates_uses_cache():
    expected = [("GME", {"short_float_pct": 25.0, "momentum_pct": 30.0, "move_pct": 25.0})]
    cache.set("squeeze_candidates_30d", expected)
    scanner = ShortSqueezeCallScanner(universe=["GME"])
    result = scanner._find_squeeze_candidates()
    assert result == expected


def test_find_squeeze_candidates_no_ohlcv_returns_empty():
    with patch("tailwind_options.market_data.yf.download", side_effect=Exception("net")):
        scanner = ShortSqueezeCallScanner(universe=["GME"])
        result = scanner._find_squeeze_candidates()
    assert result == []


def test_find_squeeze_candidates_skips_low_momentum():
    """Ticker with only 5% momentum → below 10% threshold."""
    data = _make_yf_download(["GME"], [(100.0, 105.0)])  # +5%, 35 rows
    cache.set("ohlcv_1y", data)
    scanner = ShortSqueezeCallScanner(universe=["GME"])
    result = scanner._find_squeeze_candidates()
    assert result == []


def test_find_squeeze_candidates_skips_low_short_float():
    """High momentum but short float only 5% → below 15% threshold."""
    data = _make_yf_download(["GME"], [(100.0, 130.0)])  # +30%, 35 rows
    cache.set("ohlcv_1y", data)
    mock_ticker = MagicMock()
    mock_ticker.info = {"shortPercentOfFloat": 0.05}
    with patch("yfinance.Ticker", return_value=mock_ticker):
        scanner = ShortSqueezeCallScanner(universe=["GME"])
        result = scanner._find_squeeze_candidates()
    assert result == []


def test_find_squeeze_candidates_finds_qualifying_ticker():
    """High momentum + high short float → qualifies."""
    data = _make_yf_download(["GME"], [(100.0, 135.0)])  # +35%, 35 rows
    cache.set("ohlcv_1y", data)
    mock_ticker = MagicMock()
    mock_ticker.info = {"shortPercentOfFloat": 0.20}  # 20%
    with patch("yfinance.Ticker", return_value=mock_ticker):
        scanner = ShortSqueezeCallScanner(universe=["GME"])
        result = scanner._find_squeeze_candidates()
    assert len(result) == 1
    assert result[0][0] == "GME"
    assert result[0][1]["short_float_pct"] == 20.0


def test_find_squeeze_candidates_skips_missing_short_info():
    data = _make_yf_download(["GME"], [(100.0, 135.0)])  # 35 rows
    cache.set("ohlcv_1y", data)
    mock_ticker = MagicMock()
    mock_ticker.info = {}  # shortPercentOfFloat missing
    with patch("yfinance.Ticker", return_value=mock_ticker):
        scanner = ShortSqueezeCallScanner(universe=["GME"])
        result = scanner._find_squeeze_candidates()
    assert result == []


# ── _scan_calls ───────────────────────────────────────────────────────────────

def test_scan_calls_no_expirations_returns_empty():
    mock_ticker = MagicMock()
    mock_ticker.options = []
    with patch("yfinance.Ticker", return_value=mock_ticker):
        scanner = ShortSqueezeCallScanner(universe=["GME"])
        meta = {"short_float_pct": 20.0, "momentum_pct": 30.0, "move_pct": 20.0}
        signals = scanner._scan_options("GME", meta, 130.0)
    assert signals == []


def test_scan_calls_produces_signals():
    today = date.today()
    expiry = (today + timedelta(days=60)).isoformat()
    calls = _make_calls_df([{"contractSymbol": "GME_60D", "strike": 150.0, "ask": 3.0}])

    mock_ticker = MagicMock()
    mock_ticker.options = [expiry]
    mock_ticker.option_chain.return_value = MagicMock(calls=calls)

    meta = {"short_float_pct": 20.0, "momentum_pct": 30.0, "move_pct": 20.0}
    with patch("yfinance.Ticker", return_value=mock_ticker):
        scanner = ShortSqueezeCallScanner(universe=["GME"])
        signals = scanner._scan_options("GME", meta, 130.0)

    assert len(signals) > 0
    assert signals[0].data["theme_id"] == "short-squeeze"
    assert signals[0].data["move_label"] == "short float"


def test_scan_calls_filters_itm():
    today = date.today()
    expiry = (today + timedelta(days=60)).isoformat()
    calls = _make_calls_df([{"contractSymbol": "ITM", "strike": 50.0, "ask": 3.0, "inTheMoney": True}])

    mock_ticker = MagicMock()
    mock_ticker.options = [expiry]
    mock_ticker.option_chain.return_value = MagicMock(calls=calls)

    meta = {"short_float_pct": 20.0, "momentum_pct": 30.0, "move_pct": 20.0}
    with patch("yfinance.Ticker", return_value=mock_ticker):
        scanner = ShortSqueezeCallScanner(universe=["GME"])
        signals = scanner._scan_options("GME", meta, 130.0)

    assert signals == []


# ── check ─────────────────────────────────────────────────────────────────────

def test_check_no_candidates_returns_empty():
    cache.set("squeeze_candidates_30d", [])
    scanner = ShortSqueezeCallScanner(universe=["GME"])
    signals = scanner.check()
    assert signals == []


def test_check_returns_signals_for_candidates():
    candidate = ("GME", {"short_float_pct": 20.0, "momentum_pct": 30.0, "move_pct": 20.0})
    cache.set("squeeze_candidates_30d", [candidate])

    today = date.today()
    expiry = (today + timedelta(days=60)).isoformat()
    calls = _make_calls_df([{"contractSymbol": "GME_60D", "strike": 150.0, "ask": 3.0}])

    mock_ticker = MagicMock()
    mock_ticker.fast_info.last_price = 130.0
    mock_ticker.options = [expiry]
    mock_ticker.option_chain.return_value = MagicMock(calls=calls)

    with patch("yfinance.Ticker", return_value=mock_ticker):
        scanner = ShortSqueezeCallScanner(universe=["GME"])
        signals = scanner.check()

    assert len(signals) > 0
    assert all(s.triggered for s in signals)
