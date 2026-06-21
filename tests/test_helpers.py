"""Tests for shared option-scanning helpers in tailwind_options.sources._helpers."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

import tailwind_options.cache as cache_mod

from tailwind_options.sources._helpers import (
    RISK_FREE_RATE,
    TERM_BOUNDARY_DAYS,
    bucket_candidates,
    fetch_price,
    filter_by_momentum,
    filter_option_chain,
    format_option_message,
    norm_cdf,
    prob_itm_call,
    prob_itm_put,
)


@pytest.fixture(autouse=True)
def clear_cache(tmp_path, monkeypatch):
    monkeypatch.setattr(cache_mod, "_CACHE_DIR", tmp_path)


def _make_chain(rows: list[dict]) -> pd.DataFrame:
    defaults = {
        "contractSymbol": "X260101C00100000",
        "strike": 100.0,
        "lastPrice": 2.0,
        "bid": 1.8,
        "ask": 2.2,
        "impliedVolatility": 0.5,
        "inTheMoney": False,
        "openInterest": 50,
        "volume": 10,
    }
    return pd.DataFrame([{**defaults, **r} for r in rows])


def _candidate(**overrides) -> dict:
    base = {
        "term": "short",
        "prob_itm": 0.2,
        "score": 10.0,
        "ask": 2.0,
        "contract": "X_C",
        "return_multiple": 50.0,
    }
    return {**base, **overrides}


# ── constants ─────────────────────────────────────────────────────────────────

def test_risk_free_rate():
    assert RISK_FREE_RATE == 0.05


def test_term_boundary_days():
    assert TERM_BOUNDARY_DAYS == 180


# ── norm_cdf ──────────────────────────────────────────────────────────────────

def test_norm_cdf_at_zero():
    assert abs(norm_cdf(0) - 0.5) < 1e-6


def test_norm_cdf_positive_large():
    assert norm_cdf(4.0) > 0.99


def test_norm_cdf_negative_large():
    assert norm_cdf(-4.0) < 0.01


def test_norm_cdf_symmetry():
    assert abs(norm_cdf(1.5) + norm_cdf(-1.5) - 1.0) < 1e-9


def test_norm_cdf_196():
    assert abs(norm_cdf(1.96) - 0.975) < 0.001


# ── prob_itm_call ─────────────────────────────────────────────────────────────

def test_prob_itm_call_between_0_and_1():
    assert 0.0 <= prob_itm_call(S=200, K=250, T=0.5, sigma=0.6) <= 1.0


def test_prob_itm_call_zero_when_T_is_zero():
    assert prob_itm_call(S=200, K=250, T=0, sigma=0.6) == 0.0


def test_prob_itm_call_zero_when_sigma_is_zero():
    assert prob_itm_call(S=200, K=250, T=0.5, sigma=0) == 0.0


def test_prob_itm_call_zero_when_S_is_zero():
    assert prob_itm_call(S=0, K=250, T=0.5, sigma=0.6) == 0.0


def test_prob_itm_call_zero_when_K_is_zero():
    assert prob_itm_call(S=200, K=0, T=0.5, sigma=0.6) == 0.0


def test_prob_itm_call_higher_when_closer_to_atm():
    p_far = prob_itm_call(S=100, K=200, T=1.0, sigma=0.5)
    p_near = prob_itm_call(S=100, K=110, T=1.0, sigma=0.5)
    assert p_near > p_far


def test_prob_itm_call_negative_T_returns_zero():
    assert prob_itm_call(S=200, K=150, T=-1, sigma=0.6) == 0.0


# ── prob_itm_put ──────────────────────────────────────────────────────────────

def test_prob_itm_put_between_0_and_1():
    assert 0.0 <= prob_itm_put(S=200, K=150, T=0.5, sigma=0.8) <= 1.0


def test_prob_itm_put_zero_when_T_is_zero():
    assert prob_itm_put(S=200, K=150, T=0, sigma=0.8) == 0.0


def test_prob_itm_put_zero_when_sigma_is_zero():
    assert prob_itm_put(S=200, K=150, T=0.5, sigma=0) == 0.0


def test_prob_itm_put_zero_when_S_is_zero():
    assert prob_itm_put(S=0, K=150, T=0.5, sigma=0.8) == 0.0


def test_prob_itm_put_zero_when_K_is_zero():
    assert prob_itm_put(S=200, K=0, T=0.5, sigma=0.8) == 0.0


def test_prob_itm_put_higher_when_deeper_itm():
    p_atm = prob_itm_put(S=100, K=100, T=1.0, sigma=0.5)
    p_otm = prob_itm_put(S=100, K=50, T=1.0, sigma=0.5)
    assert p_atm > p_otm


def test_prob_itm_put_negative_T_returns_zero():
    assert prob_itm_put(S=200, K=150, T=-1, sigma=0.8) == 0.0


# ── fetch_price ───────────────────────────────────────────────────────────────

def test_fetch_price_returns_price():
    t = MagicMock()
    t.fast_info.last_price = 150.0
    with patch("yfinance.Ticker", return_value=t):
        assert fetch_price("AAPL") == 150.0


def test_fetch_price_none_when_no_price():
    t = MagicMock()
    t.fast_info.last_price = None
    with patch("yfinance.Ticker", return_value=t):
        assert fetch_price("AAPL") is None


def test_fetch_price_uses_cache():
    t = MagicMock()
    t.fast_info.last_price = 150.0
    with patch("yfinance.Ticker", return_value=t) as mock_yf:
        fetch_price("AAPL")
        fetch_price("AAPL")
        mock_yf.assert_called_once()


# ── filter_option_chain ───────────────────────────────────────────────────────

def test_filter_passes_qualifying_row():
    chain = _make_chain([{"strike": 110.0, "ask": 2.0}])
    result = filter_option_chain(chain, current_price=100.0, min_oi=10, max_cost_pct=0.05, max_iv=1.5)
    assert len(result) == 1
    assert result.iloc[0]["effective_ask"] == 2.0


def test_filter_removes_itm():
    chain = _make_chain([{"inTheMoney": True, "strike": 90.0, "ask": 2.0}])
    result = filter_option_chain(chain, 100.0, 10, 0.05, 1.5)
    assert len(result) == 0


def test_filter_removes_high_cost():
    # ask 8 on price 100 = 8% > 5% limit
    chain = _make_chain([{"strike": 110.0, "ask": 8.0}])
    result = filter_option_chain(chain, 100.0, 10, 0.05, 1.5)
    assert len(result) == 0


def test_filter_removes_high_iv():
    chain = _make_chain([{"strike": 110.0, "ask": 2.0, "impliedVolatility": 2.0}])
    result = filter_option_chain(chain, 100.0, 10, 0.05, 1.5)
    assert len(result) == 0


def test_filter_uses_lastprice_when_ask_zero():
    chain = _make_chain([{"strike": 110.0, "ask": 0.0, "lastPrice": 2.0, "openInterest": 0, "volume": 0}])
    result = filter_option_chain(chain, 100.0, 10, 0.05, 1.5)
    assert len(result) == 1
    assert result.iloc[0]["effective_ask"] == 2.0


def test_filter_removes_zero_ask_and_lastprice():
    chain = _make_chain([{"strike": 110.0, "ask": 0.0, "lastPrice": 0.0}])
    result = filter_option_chain(chain, 100.0, 10, 0.05, 1.5)
    assert len(result) == 0


def test_filter_passes_low_oi_if_volume_present():
    chain = _make_chain([{"strike": 110.0, "ask": 2.0, "openInterest": 0, "volume": 5}])
    result = filter_option_chain(chain, 100.0, 10, 0.05, 1.5)
    assert len(result) == 1


def test_filter_passes_low_oi_if_lastprice_present():
    chain = _make_chain([{"strike": 110.0, "ask": 0.0, "lastPrice": 2.0, "openInterest": 0, "volume": 0}])
    result = filter_option_chain(chain, 100.0, 10, 0.05, 1.5)
    assert len(result) == 1


# ── format_option_message ─────────────────────────────────────────────────────

def test_format_option_message_output():
    c = {"return_multiple": 50.0, "ask": 3.25, "strike": 150.0, "expiry": "2026-12-19"}
    msg = format_option_message(c)
    assert "50x return" in msg
    assert "$3.25 ask" in msg
    assert "$150 strike" in msg
    assert "Exp 2026-12-19" in msg


def test_format_option_message_rounds_return():
    c = {"return_multiple": 49.7, "ask": 1.00, "strike": 100.0, "expiry": "2027-01-01"}
    assert format_option_message(c).startswith("50x")


# ── filter_by_momentum ────────────────────────────────────────────────────────

def _make_download(tickers: list[str], prices: list[tuple[float, float]]) -> pd.DataFrame:
    dates = pd.date_range("2025-01-01", periods=2, freq="D")
    cols = pd.MultiIndex.from_tuples([("Close", t) for t in tickers])
    rows = [[p[0] for p in prices], [p[1] for p in prices]]
    return pd.DataFrame(rows, columns=cols, index=dates)


def test_filter_by_momentum_passes_above_threshold():
    data = _make_download(["MU", "INTC"], [(10.0, 90.0), (10.0, 10.5)])
    with patch("tailwind_options.sources._helpers.yf.download", return_value=data):
        result = filter_by_momentum(["MU", "INTC"], 30, 10.0, "test_key_1")
    tickers = [r[0] for r in result]
    assert "MU" in tickers
    assert "INTC" not in tickers


def test_filter_by_momentum_sorted_descending():
    data = _make_download(["A", "B", "C"], [(5.0, 50.0), (5.0, 30.0), (5.0, 100.0)])
    with patch("tailwind_options.sources._helpers.yf.download", return_value=data):
        result = filter_by_momentum(["A", "B", "C"], 30, 10.0, "test_key_2")
    gains = [r[1] for r in result]
    assert gains == sorted(gains, reverse=True)


def test_filter_by_momentum_uses_cache():
    data = _make_download(["MU"], [(10.0, 90.0)])
    with patch("tailwind_options.sources._helpers.yf.download", return_value=data) as mock_dl:
        filter_by_momentum(["MU"], 30, 10.0, "test_key_3")
        mock_dl.assert_called_once()
    with patch("tailwind_options.sources._helpers.yf.download") as mock_dl2:
        filter_by_momentum(["MU"], 30, 10.0, "test_key_3")
        mock_dl2.assert_not_called()


def test_filter_by_momentum_download_failure_returns_empty():
    with patch("tailwind_options.sources._helpers.yf.download", side_effect=Exception("network")):
        result = filter_by_momentum(["MU"], 30, 10.0, "test_key_4")
    assert result == []


def test_filter_by_momentum_skips_insufficient_data():
    dates = pd.date_range("2025-01-01", periods=1, freq="D")
    cols = pd.MultiIndex.from_tuples([("Close", "MU")])
    df = pd.DataFrame([[10.0]], columns=cols, index=dates)
    with patch("tailwind_options.sources._helpers.yf.download", return_value=df):
        result = filter_by_momentum(["MU"], 30, 10.0, "test_key_5")
    assert result == []


# ── bucket_candidates ─────────────────────────────────────────────────────────

def test_bucket_returns_short_long_moonshots():
    candidates = [
        _candidate(term="short", contract="S1", score=10.0),
        _candidate(term="long", contract="L1", score=8.0),
    ]
    result = bucket_candidates(candidates)
    terms = {c["term"] for c in result}
    assert "short" in terms
    assert "long" in terms


def test_bucket_caps_short_at_10():
    candidates = [
        _candidate(term="short", contract=f"S{i}", score=float(i), return_multiple=float(i))
        for i in range(20)
    ]
    result = bucket_candidates(candidates)
    assert len([c for c in result if c["term"] == "short"]) <= 10


def test_bucket_caps_long_at_10():
    candidates = [
        _candidate(term="long", contract=f"L{i}", score=float(i), return_multiple=float(i))
        for i in range(20)
    ]
    result = bucket_candidates(candidates)
    assert len([c for c in result if c["term"] == "long"]) <= 10


def test_bucket_moonshots_not_in_short_long():
    short = _candidate(term="short", contract="S1", score=10.0, return_multiple=5.0)
    long = _candidate(term="long", contract="L1", score=8.0, return_multiple=4.0)
    extra = _candidate(term="short", contract="M1", score=1.0, return_multiple=100.0)
    # Fill short bucket to capacity so extra spills to moonshots
    shorts = [_candidate(term="short", contract=f"SF{i}", score=float(10 - i), return_multiple=1.0) for i in range(10)]
    result = bucket_candidates([short, long, extra] + shorts)
    moonshot_contracts = {c["contract"] for c in result if c["term"] == "moonshot"}
    short_contracts = {c["contract"] for c in result if c["term"] == "short"}
    assert moonshot_contracts.isdisjoint(short_contracts)


def test_bucket_filters_low_prob_itm():
    candidates = [_candidate(term="short", contract="S1", prob_itm=0.005)]
    result = bucket_candidates(candidates)
    assert result == []


def test_bucket_moonshots_tag_term():
    # single candidate that won't fit in either short or long bucket (both full)
    base = [_candidate(term="short", contract=f"S{i}", score=float(10 - i)) for i in range(10)]
    extra = _candidate(term="short", contract="EXTRA", score=0.0, return_multiple=999.0)
    result = bucket_candidates(base + [extra])
    moonshots = [c for c in result if c["term"] == "moonshot"]
    assert any(c["contract"] == "EXTRA" for c in moonshots)
