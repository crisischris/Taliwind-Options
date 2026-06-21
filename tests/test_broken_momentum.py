from __future__ import annotations

from datetime import date, timedelta
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

import tailwind_options.cache as cache_mod
from tailwind_options import cache
from tailwind_options.sources.broken_momentum import BrokenMomentumScanner


@pytest.fixture(autouse=True)
def clear_cache(tmp_path, monkeypatch):
    monkeypatch.setattr(cache_mod, "_CACHE_DIR", tmp_path)


def _make_ohlcv(
    tickers: list[str],
    close_rows: list[list[float]],
    vol_rows: list[list[float]] | None = None,
) -> pd.DataFrame:
    """Full multi-level OHLCV DataFrame with Close + Volume."""
    n = len(close_rows)
    dates = pd.date_range(end=date.today(), periods=n, freq="D")
    vol_rows = vol_rows or [[1_000_000] * len(tickers)] * n
    close_cols = pd.MultiIndex.from_tuples([("Close", t) for t in tickers])
    vol_cols = pd.MultiIndex.from_tuples([("Volume", t) for t in tickers])
    close_df = pd.DataFrame(close_rows, columns=close_cols, index=dates)
    vol_df = pd.DataFrame(vol_rows, columns=vol_cols, index=dates)
    return pd.concat([close_df, vol_df], axis=1)


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


def _make_distribution_ohlcv(ticker: str, peak: float, current: float) -> pd.DataFrame:
    """Build a 35-row OHLCV series where distribution volume dominates the last 20 sessions."""
    n = 35
    # First few rows run up to peak, then decline
    close_vals = [peak * 0.5] * 5 + [peak] + [current] * (n - 6)
    # Alternate up/down in last 20 rows; heavy volume on down days
    vol_vals = [1_000_000] * (n - 20)
    for i in range(20):
        # Odd → price goes down, heavy volume (down_vol); even → up
        vol_vals.append(3_000_000 if i % 2 == 0 else 500_000)
    # Adjust close so odd positions go down
    for i in range(n - 20, n):
        close_vals[i] = current - 1 if (i - (n - 20)) % 2 == 0 else current + 1
    close_vals[-1] = current  # end at current

    return _make_ohlcv([ticker], [[v] for v in close_vals], [[v] for v in vol_vals])


# ── _find_broken_momentum ─────────────────────────────────────────────────────

def test_find_broken_momentum_no_ohlcv_returns_empty():
    cache.set("ohlcv_1y", None)
    scanner = BrokenMomentumScanner(universe=["AAPL"])
    with patch("tailwind_options.market_data.yf.download", return_value=None):
        result = scanner._find_broken_momentum()
    assert result == []


def test_find_broken_momentum_uses_cache():
    expected = [("AAPL", {"peak_price": 100.0, "peak_date": "2025-01-01", "drawdown_pct": 25.0, "down_vol_ratio": 2.0})]
    cache.set("broken_momentum_candidates", expected)
    scanner = BrokenMomentumScanner(universe=["AAPL"])
    result = scanner._find_broken_momentum()
    assert result == expected


def test_find_broken_momentum_skips_insufficient_data():
    # Only 5 rows — less than _VOLUME_WINDOW + 10 = 30
    data = _make_ohlcv(["AAPL"], [[100.0]] * 5, [[1_000_000]] * 5)
    cache.set("ohlcv_1y", data)
    scanner = BrokenMomentumScanner(universe=["AAPL"])
    result = scanner._find_broken_momentum()
    assert result == []


def test_find_broken_momentum_skips_insufficient_drawdown():
    """Ticker within 20% of high → not broken enough."""
    # Peak = 100, current = 90 → 10% drawdown < 20% threshold
    close_vals = [50.0] * 5 + [100.0] + [90.0] * 29
    vol_vals = [1_000_000] * 35
    data = _make_ohlcv(["AAPL"], [[v] for v in close_vals], [[v] for v in vol_vals])
    cache.set("ohlcv_1y", data)
    scanner = BrokenMomentumScanner(universe=["AAPL"])
    result = scanner._find_broken_momentum()
    assert result == []


def test_find_broken_momentum_finds_candidate():
    """Ticker that meets all criteria should be returned."""
    data = _make_distribution_ohlcv("NVDA", peak=200.0, current=140.0)  # 30% drawdown
    cache.set("ohlcv_1y", data)
    scanner = BrokenMomentumScanner(universe=["NVDA"])
    result = scanner._find_broken_momentum()
    assert len(result) == 1
    assert result[0][0] == "NVDA"
    assert result[0][1]["drawdown_pct"] >= 20.0


# ── _scan_puts ────────────────────────────────────────────────────────────────

def test_scan_puts_no_expirations_returns_empty():
    mock_ticker = MagicMock()
    mock_ticker.options = []
    with patch("yfinance.Ticker", return_value=mock_ticker):
        scanner = BrokenMomentumScanner(universe=["AAPL"])
        meta = {"peak_price": 200.0, "peak_date": "2025-01-01", "drawdown_pct": 30.0, "down_vol_ratio": 2.0}
        signals = scanner._scan_options("AAPL", meta, 140.0)
    assert signals == []


def test_scan_puts_produces_signals():
    today = date.today()
    expiry = (today + timedelta(days=120)).isoformat()
    puts = _make_puts_df([{"contractSymbol": "AAPL_120D", "strike": 100.0, "ask": 2.0}])

    mock_ticker = MagicMock()
    mock_ticker.options = [expiry]
    mock_ticker.option_chain.return_value = MagicMock(puts=puts)

    meta = {"peak_price": 200.0, "peak_date": "2025-01-01", "drawdown_pct": 30.0, "down_vol_ratio": 2.0}
    with patch("yfinance.Ticker", return_value=mock_ticker):
        scanner = BrokenMomentumScanner(universe=["AAPL"])
        signals = scanner._scan_options("AAPL", meta, 140.0)

    assert len(signals) > 0
    assert signals[0].triggered is True
    assert signals[0].data["theme_id"] == "broken-momentum"
    assert signals[0].data["move_label"] == "from peak"


def test_scan_puts_filters_itm():
    today = date.today()
    expiry = (today + timedelta(days=120)).isoformat()
    puts = _make_puts_df([{"contractSymbol": "ITM", "strike": 200.0, "ask": 3.0, "inTheMoney": True}])

    mock_ticker = MagicMock()
    mock_ticker.options = [expiry]
    mock_ticker.option_chain.return_value = MagicMock(puts=puts)

    meta = {"peak_price": 200.0, "peak_date": "2025-01-01", "drawdown_pct": 30.0, "down_vol_ratio": 2.0}
    with patch("yfinance.Ticker", return_value=mock_ticker):
        scanner = BrokenMomentumScanner(universe=["AAPL"])
        signals = scanner._scan_options("AAPL", meta, 140.0)

    assert signals == []


# ── check ─────────────────────────────────────────────────────────────────────

def test_check_no_candidates_returns_empty():
    cache.set("broken_momentum_candidates", [])
    mock_ticker = MagicMock()
    mock_ticker.fast_info.last_price = 140.0
    with patch("yfinance.Ticker", return_value=mock_ticker):
        scanner = BrokenMomentumScanner(universe=["AAPL"])
        signals = scanner.check()
    assert signals == []


def test_check_returns_signals_for_candidates():
    candidate = ("AAPL", {"peak_price": 200.0, "peak_date": "2025-01-01", "drawdown_pct": 30.0, "down_vol_ratio": 2.0})
    cache.set("broken_momentum_candidates", [candidate])

    today = date.today()
    expiry = (today + timedelta(days=120)).isoformat()
    puts = _make_puts_df([{"contractSymbol": "AAPL_120D", "strike": 100.0, "ask": 2.0}])

    mock_ticker = MagicMock()
    mock_ticker.fast_info.last_price = 140.0
    mock_ticker.options = [expiry]
    mock_ticker.option_chain.return_value = MagicMock(puts=puts)

    with patch("yfinance.Ticker", return_value=mock_ticker):
        scanner = BrokenMomentumScanner(universe=["AAPL"])
        signals = scanner.check()

    assert len(signals) > 0
    assert all(s.triggered for s in signals)
