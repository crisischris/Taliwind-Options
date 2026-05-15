from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

import indicators.cache as cache_mod
from indicators import cache
from indicators.ark_holdings import _fetch_from_yf, get_tickers


@pytest.fixture(autouse=True)
def clear_cache(tmp_path, monkeypatch):
    monkeypatch.setattr(cache_mod, "_CACHE_DIR", tmp_path)


def _mock_holdings(symbols: list[str]) -> pd.DataFrame:
    return pd.DataFrame({"holdingPercent": [0.05] * len(symbols)}, index=pd.Index(symbols, name="symbol"))


def _mock_ticker(symbols: list[str]) -> MagicMock:
    t = MagicMock()
    t.funds_data.top_holdings = _mock_holdings(symbols)
    return t


# ── get_tickers ───────────────────────────────────────────────────────────────

def test_get_tickers_file_cache_hit():
    cache.set("ark_holdings", ["AAPL", "TSLA"])
    result = get_tickers()
    assert result == ["AAPL", "TSLA"]


def test_get_tickers_s3_cache_hit():
    mock_s3 = MagicMock()
    tickers = ["AAPL", "NVDA"]
    mock_s3.get_object.return_value = {
        "Body": MagicMock(read=lambda: json.dumps(tickers).encode())
    }
    result = get_tickers(s3=mock_s3, bucket="my-bucket")
    assert result == tickers
    mock_s3.get_object.assert_called_once()


def test_get_tickers_s3_miss_fetches_from_yf():
    mock_s3 = MagicMock()
    mock_s3.get_object.side_effect = Exception("NoSuchKey")

    with patch("indicators.ark_holdings.yf.Ticker", return_value=_mock_ticker(["AAPL", "TSLA"])):
        result = get_tickers(s3=mock_s3, bucket="my-bucket")

    assert "AAPL" in result
    assert "TSLA" in result


def test_get_tickers_s3_miss_writes_back_to_s3():
    mock_s3 = MagicMock()
    mock_s3.get_object.side_effect = Exception("NoSuchKey")

    with patch("indicators.ark_holdings.yf.Ticker", return_value=_mock_ticker(["AAPL", "TSLA"])):
        get_tickers(s3=mock_s3, bucket="my-bucket")

    mock_s3.put_object.assert_called_once()
    body = json.loads(mock_s3.put_object.call_args.kwargs["Body"])
    assert "AAPL" in body


def test_get_tickers_no_s3_falls_through_to_yf():
    with patch("indicators.ark_holdings.yf.Ticker", return_value=_mock_ticker(["AAPL"])):
        result = get_tickers()
    assert "AAPL" in result


def test_get_tickers_s3_write_failure_is_swallowed():
    mock_s3 = MagicMock()
    mock_s3.get_object.side_effect = Exception("miss")
    mock_s3.put_object.side_effect = Exception("write failed")

    with patch("indicators.ark_holdings.yf.Ticker", return_value=_mock_ticker(["AAPL"])):
        result = get_tickers(s3=mock_s3, bucket="my-bucket")

    assert isinstance(result, list)


# ── _fetch_from_yf ────────────────────────────────────────────────────────────

def test_fetch_from_yf_returns_tickers():
    with patch("indicators.ark_holdings.yf.Ticker", return_value=_mock_ticker(["AAPL", "TSLA"])):
        result = _fetch_from_yf()
    assert "AAPL" in result
    assert "TSLA" in result


def test_fetch_from_yf_deduplicates_across_etfs():
    with patch("indicators.ark_holdings.yf.Ticker", return_value=_mock_ticker(["AAPL"])):
        result = _fetch_from_yf()
    assert result.count("AAPL") == 1


def test_fetch_from_yf_returns_sorted():
    with patch("indicators.ark_holdings.yf.Ticker", return_value=_mock_ticker(["TSLA", "AAPL", "NVDA"])):
        result = _fetch_from_yf()
    assert result == sorted(result)


def test_fetch_from_yf_etf_error_returns_empty():
    mock_ticker = MagicMock()
    mock_ticker.funds_data.top_holdings = pd.DataFrame()  # empty
    mock_ticker.funds_data.top_holdings.index = pd.Index([])
    with patch("indicators.ark_holdings.yf.Ticker", side_effect=Exception("network error")):
        result = _fetch_from_yf()
    assert result == []


def test_fetch_from_yf_skips_invalid_symbols():
    with patch("indicators.ark_holdings.yf.Ticker", return_value=_mock_ticker(["-", "nan", "TSLA"])):
        result = _fetch_from_yf()
    assert "-" not in result
    assert "nan" not in result
    assert "TSLA" in result
