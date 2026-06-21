from __future__ import annotations

from datetime import date, timedelta
from unittest.mock import MagicMock, patch

import pytest

import tailwind_options.cache as cache_mod
from tailwind_options import cache
from tailwind_options.sources.valuation_gravity import ValuationGravityScanner


@pytest.fixture(autouse=True)
def clear_cache(tmp_path, monkeypatch):
    monkeypatch.setattr(cache_mod, "_CACHE_DIR", tmp_path)


def _make_puts_df(rows: list[dict]):
    import pandas as pd
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


def _make_info(ps=20.0, rev_growth=0.15, op_margin=0.05) -> dict:
    return {
        "priceToSalesTrailing12Months": ps,
        "revenueGrowth": rev_growth,
        "operatingMargins": op_margin,
    }


# ── _find_overvalued ──────────────────────────────────────────────────────────

def test_find_overvalued_uses_cache():
    expected = [("AAPL", {"ps_ratio": 20.0, "revenue_growth_pct": 15.0, "op_margin_pct": 5.0, "move_pct": 33.3})]
    cache.set("valuation_gravity_candidates", expected)
    scanner = ValuationGravityScanner(universe=["AAPL"])
    result = scanner._find_overvalued()
    assert result == expected


def test_find_overvalued_returns_qualifying_ticker():
    info_map = {"AAPL": _make_info(ps=25.0, rev_growth=0.15, op_margin=0.10)}
    cache.set("universe_info", info_map)
    scanner = ValuationGravityScanner(universe=["AAPL"])
    result = scanner._find_overvalued()
    assert len(result) == 1
    assert result[0][0] == "AAPL"
    assert result[0][1]["ps_ratio"] == 25.0


def test_find_overvalued_skips_low_ps():
    """P/S ≤ 15 → does not qualify."""
    info_map = {"AAPL": _make_info(ps=10.0, rev_growth=0.15, op_margin=0.10)}
    cache.set("universe_info", info_map)
    scanner = ValuationGravityScanner(universe=["AAPL"])
    result = scanner._find_overvalued()
    assert result == []


def test_find_overvalued_skips_negative_revenue_growth():
    info_map = {"AAPL": _make_info(ps=20.0, rev_growth=-0.10, op_margin=0.05)}
    cache.set("universe_info", info_map)
    scanner = ValuationGravityScanner(universe=["AAPL"])
    result = scanner._find_overvalued()
    assert result == []


def test_find_overvalued_skips_high_revenue_growth():
    """Revenue growth > 30% → still a rocket, skip."""
    info_map = {"AAPL": _make_info(ps=20.0, rev_growth=0.50, op_margin=0.05)}
    cache.set("universe_info", info_map)
    scanner = ValuationGravityScanner(universe=["AAPL"])
    result = scanner._find_overvalued()
    assert result == []


def test_find_overvalued_skips_extreme_loss():
    """Op margin below -30% → too risky to qualify."""
    info_map = {"AAPL": _make_info(ps=20.0, rev_growth=0.15, op_margin=-0.50)}
    cache.set("universe_info", info_map)
    scanner = ValuationGravityScanner(universe=["AAPL"])
    result = scanner._find_overvalued()
    assert result == []


def test_find_overvalued_skips_missing_fields():
    cache.set("universe_info", {"AAPL": {"priceToSalesTrailing12Months": 20.0}})
    scanner = ValuationGravityScanner(universe=["AAPL"])
    result = scanner._find_overvalued()
    assert result == []


# ── _scan_puts ────────────────────────────────────────────────────────────────

def test_scan_puts_no_expirations_returns_empty():
    mock_ticker = MagicMock()
    mock_ticker.options = []
    with patch("yfinance.Ticker", return_value=mock_ticker):
        scanner = ValuationGravityScanner(universe=["AAPL"])
        meta = {"ps_ratio": 20.0, "revenue_growth_pct": 15.0, "op_margin_pct": 5.0, "move_pct": 33.3}
        signals = scanner._scan_options("AAPL", meta, 200.0)
    assert signals == []


def test_scan_puts_produces_signals():
    today = date.today()
    expiry = (today + timedelta(days=180)).isoformat()
    puts = _make_puts_df([{"contractSymbol": "AAPL_180D", "strike": 150.0, "ask": 3.0}])

    mock_ticker = MagicMock()
    mock_ticker.options = [expiry]
    mock_ticker.option_chain.return_value = MagicMock(puts=puts)

    meta = {"ps_ratio": 20.0, "revenue_growth_pct": 15.0, "op_margin_pct": 5.0, "move_pct": 33.3}
    with patch("yfinance.Ticker", return_value=mock_ticker):
        scanner = ValuationGravityScanner(universe=["AAPL"])
        signals = scanner._scan_options("AAPL", meta, 200.0)

    assert len(signals) > 0
    assert signals[0].data["theme_id"] == "valuation-gravity"
    assert signals[0].data["move_label"] == "P/S premium"


def test_scan_puts_filters_itm():
    today = date.today()
    expiry = (today + timedelta(days=180)).isoformat()
    puts = _make_puts_df([{"contractSymbol": "ITM", "strike": 250.0, "ask": 3.0, "inTheMoney": True}])

    mock_ticker = MagicMock()
    mock_ticker.options = [expiry]
    mock_ticker.option_chain.return_value = MagicMock(puts=puts)

    meta = {"ps_ratio": 20.0, "revenue_growth_pct": 15.0, "op_margin_pct": 5.0, "move_pct": 33.3}
    with patch("yfinance.Ticker", return_value=mock_ticker):
        scanner = ValuationGravityScanner(universe=["AAPL"])
        signals = scanner._scan_options("AAPL", meta, 200.0)

    assert signals == []


# ── check ─────────────────────────────────────────────────────────────────────

def test_check_no_candidates_returns_empty():
    cache.set("valuation_gravity_candidates", [])
    scanner = ValuationGravityScanner(universe=["AAPL"])
    signals = scanner.check()
    assert signals == []


def test_check_returns_signals_for_candidates():
    candidate = ("AAPL", {"ps_ratio": 20.0, "revenue_growth_pct": 15.0, "op_margin_pct": 5.0, "move_pct": 33.3})
    cache.set("valuation_gravity_candidates", [candidate])

    today = date.today()
    expiry = (today + timedelta(days=180)).isoformat()
    puts = _make_puts_df([{"contractSymbol": "AAPL_180D", "strike": 150.0, "ask": 3.0}])

    mock_ticker = MagicMock()
    mock_ticker.fast_info.last_price = 200.0
    mock_ticker.options = [expiry]
    mock_ticker.option_chain.return_value = MagicMock(puts=puts)

    with patch("yfinance.Ticker", return_value=mock_ticker):
        scanner = ValuationGravityScanner(universe=["AAPL"])
        signals = scanner.check()

    assert len(signals) > 0
    assert all(s.triggered for s in signals)
