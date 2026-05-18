from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

import indicators.cache as cache_mod
from indicators import cache
from indicators.call_universe import _fetch_from_yf, get_tickers


@pytest.fixture(autouse=True)
def clear_cache(tmp_path, monkeypatch):
    monkeypatch.setattr(cache_mod, "_CACHE_DIR", tmp_path)


def _mock_holdings(symbols: list[str]) -> pd.DataFrame:
    return pd.DataFrame(
        {"Name": [f"{s} Inc" for s in symbols], "Holding Percent": [0.05] * len(symbols)},
        index=pd.Index(symbols, name="Symbol"),
    )


def _mock_ticker(symbols: list[str]) -> MagicMock:
    t = MagicMock()
    t.funds_data.top_holdings = _mock_holdings(symbols)
    return t


# ── get_tickers ───────────────────────────────────────────────────────────────

def test_get_tickers_file_cache_hit():
    cache.set("call_universe", ["AAPL", "TSLA"])
    result = get_tickers()
    assert result == ["AAPL", "TSLA"]


def test_get_tickers_s3_cache_hit():
    mock_s3 = MagicMock()
    payload = {"tickers": ["AAPL", "NVDA"], "names": {"AAPL": "Apple Inc", "NVDA": "Nvidia"}}
    mock_s3.get_object.return_value = {
        "Body": MagicMock(read=lambda: json.dumps(payload).encode())
    }
    result = get_tickers(s3=mock_s3, bucket="my-bucket")
    assert result == payload["tickers"]
    mock_s3.get_object.assert_called_once()


def test_get_tickers_s3_old_format_refetches():
    mock_s3 = MagicMock()
    mock_s3.get_object.return_value = {
        "Body": MagicMock(read=lambda: json.dumps(["AAPL", "NVDA"]).encode())
    }
    with patch("indicators.call_universe.yf.Ticker", return_value=_mock_ticker(["AAPL"])):
        result = get_tickers(s3=mock_s3, bucket="my-bucket")
    assert "AAPL" in result
    mock_s3.put_object.assert_called_once()


def test_get_tickers_s3_miss_fetches_from_yf():
    mock_s3 = MagicMock()
    mock_s3.get_object.side_effect = Exception("NoSuchKey")

    with patch("indicators.call_universe.yf.Ticker", return_value=_mock_ticker(["AAPL", "TSLA"])):
        result = get_tickers(s3=mock_s3, bucket="my-bucket")

    assert "AAPL" in result
    assert "TSLA" in result


def test_get_tickers_s3_miss_writes_back_to_s3():
    mock_s3 = MagicMock()
    mock_s3.get_object.side_effect = Exception("NoSuchKey")

    with patch("indicators.call_universe.yf.Ticker", return_value=_mock_ticker(["AAPL", "TSLA"])):
        get_tickers(s3=mock_s3, bucket="my-bucket")

    mock_s3.put_object.assert_called_once()
    body = json.loads(mock_s3.put_object.call_args.kwargs["Body"])
    assert "AAPL" in body["tickers"]
    assert "names" in body


def test_get_tickers_no_s3_falls_through_to_yf():
    with patch("indicators.call_universe.yf.Ticker", return_value=_mock_ticker(["AAPL"])):
        result = get_tickers()
    assert "AAPL" in result


def test_get_tickers_s3_write_failure_is_swallowed():
    mock_s3 = MagicMock()
    mock_s3.get_object.side_effect = Exception("miss")
    mock_s3.put_object.side_effect = Exception("write failed")

    with patch("indicators.call_universe.yf.Ticker", return_value=_mock_ticker(["AAPL"])):
        result = get_tickers(s3=mock_s3, bucket="my-bucket")

    assert isinstance(result, list)


# ── _fetch_from_yf ────────────────────────────────────────────────────────────

def test_fetch_from_yf_returns_tickers():
    with patch("indicators.call_universe.yf.Ticker", return_value=_mock_ticker(["AAPL", "TSLA"])):
        tickers, names = _fetch_from_yf()
    assert "AAPL" in tickers
    assert "TSLA" in tickers


def test_fetch_from_yf_returns_names():
    with patch("indicators.call_universe.yf.Ticker", return_value=_mock_ticker(["AAPL"])):
        tickers, names = _fetch_from_yf()
    assert "AAPL" in names
    assert names["AAPL"] == "AAPL Inc"


def test_fetch_from_yf_deduplicates_across_etfs():
    with patch("indicators.call_universe.yf.Ticker", return_value=_mock_ticker(["AAPL"])):
        tickers, _ = _fetch_from_yf()
    assert tickers.count("AAPL") == 1


def test_fetch_from_yf_returns_sorted():
    with patch("indicators.call_universe.yf.Ticker", return_value=_mock_ticker(["TSLA", "AAPL", "NVDA"])):
        tickers, _ = _fetch_from_yf()
    assert tickers == sorted(tickers)


def test_fetch_from_yf_etf_error_returns_empty():
    with patch("indicators.call_universe.yf.Ticker", side_effect=Exception("network error")):
        tickers, names = _fetch_from_yf()
    assert tickers == []
    assert names == {}


def test_fetch_from_yf_skips_invalid_symbols():
    with patch("indicators.call_universe.yf.Ticker", return_value=_mock_ticker(["-", "nan", "TSLA"])):
        tickers, _ = _fetch_from_yf()
    assert "-" not in tickers
    assert "nan" not in tickers
    assert "TSLA" in tickers
