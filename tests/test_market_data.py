from __future__ import annotations

from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

import tailwind_options.cache as cache_mod
from tailwind_options import cache
from tailwind_options.market_data import get_universe_info, get_universe_ohlcv


@pytest.fixture(autouse=True)
def clear_cache(tmp_path, monkeypatch):
    monkeypatch.setattr(cache_mod, "_CACHE_DIR", tmp_path)


def _make_download_df(tickers: list[str]) -> pd.DataFrame:
    dates = pd.date_range("2025-01-01", periods=2, freq="D")
    cols = pd.MultiIndex.from_tuples([("Close", t) for t in tickers])
    return pd.DataFrame([[100.0] * len(tickers), [110.0] * len(tickers)], columns=cols, index=dates)


# ── get_universe_ohlcv ────────────────────────────────────────────────────────

def test_get_universe_ohlcv_downloads_on_cache_miss():
    df = _make_download_df(["AAPL"])
    with patch("tailwind_options.market_data.yf.download", return_value=df) as mock_dl:
        result = get_universe_ohlcv(["AAPL"], "1y")
        mock_dl.assert_called_once()
    assert result is not None


def test_get_universe_ohlcv_uses_cache_on_second_call():
    df = _make_download_df(["AAPL"])
    with patch("tailwind_options.market_data.yf.download", return_value=df):
        get_universe_ohlcv(["AAPL"], "1y")
    with patch("tailwind_options.market_data.yf.download") as mock_dl2:
        get_universe_ohlcv(["AAPL"], "1y")
        mock_dl2.assert_not_called()


def test_get_universe_ohlcv_returns_none_on_download_failure():
    with patch("tailwind_options.market_data.yf.download", side_effect=Exception("network")):
        result = get_universe_ohlcv(["AAPL"], "1y")
    assert result is None


def test_get_universe_ohlcv_uses_period_as_cache_key():
    df_1y = _make_download_df(["AAPL"])
    df_6m = _make_download_df(["AAPL"])
    with patch("tailwind_options.market_data.yf.download", return_value=df_1y):
        get_universe_ohlcv(["AAPL"], "1y")
    with patch("tailwind_options.market_data.yf.download", return_value=df_6m) as mock_dl:
        get_universe_ohlcv(["AAPL"], "6mo")
        mock_dl.assert_called_once()


def test_get_universe_ohlcv_serves_cached_value():
    df = _make_download_df(["TSLA"])
    cache.set("ohlcv_1y", df)
    with patch("tailwind_options.market_data.yf.download") as mock_dl:
        result = get_universe_ohlcv(["TSLA"], "1y")
        mock_dl.assert_not_called()
    assert result is not None


# ── get_universe_info ─────────────────────────────────────────────────────────

def test_get_universe_info_fetches_and_returns_dict():
    mock_ticker = MagicMock()
    mock_ticker.info = {"sector": "Technology", "shortPercentOfFloat": 0.05}
    with patch("tailwind_options.market_data.yf.Ticker", return_value=mock_ticker):
        result = get_universe_info(["AAPL"])
    assert "AAPL" in result
    assert result["AAPL"]["sector"] == "Technology"


def test_get_universe_info_uses_cache_on_second_call():
    mock_ticker = MagicMock()
    mock_ticker.info = {"sector": "Technology"}
    with patch("tailwind_options.market_data.yf.Ticker", return_value=mock_ticker):
        get_universe_info(["AAPL"])
    with patch("tailwind_options.market_data.yf.Ticker") as mock_yf:
        get_universe_info(["AAPL"])
        mock_yf.assert_not_called()


def test_get_universe_info_omits_failed_tickers():
    def ticker_side_effect(sym):
        t = MagicMock()
        if sym == "AAPL":
            raise RuntimeError("api error")
        t.info = {"sector": "Technology"}
        return t

    with patch("tailwind_options.market_data.yf.Ticker", side_effect=ticker_side_effect):
        result = get_universe_info(["AAPL", "MSFT"])

    assert "AAPL" not in result
    assert "MSFT" in result


def test_get_universe_info_serves_cached_value():
    cached_info = {"AAPL": {"sector": "Technology"}}
    cache.set("universe_info", cached_info)
    with patch("tailwind_options.market_data.yf.Ticker") as mock_yf:
        result = get_universe_info(["AAPL"])
        mock_yf.assert_not_called()
    assert result == cached_info
