from __future__ import annotations

import json
from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest

import indicators.cache as cache_mod
from indicators import cache
from indicators.ark_holdings import _fetch_from_ark, get_tickers


@pytest.fixture(autouse=True)
def clear_cache(tmp_path, monkeypatch):
    monkeypatch.setattr(cache_mod, "_CACHE_DIR", tmp_path)


def _mock_urlopen(csv_text: str):
    """Return a context-manager mock that yields a readable HTTP response."""
    resp = MagicMock()
    resp.read.return_value = csv_text.encode("utf-8")
    resp.__enter__ = lambda s: s
    resp.__exit__ = MagicMock(return_value=False)
    return resp


_SAMPLE_CSV = "date,fund,company,ticker,cusip,shares,market value ($),weight (%)\n2026-01-01,ARKK,Apple Inc,AAPL,123,100,20000,5.0\n2026-01-01,ARKK,Tesla Inc,TSLA,456,50,10000,2.5\n"


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


def test_get_tickers_s3_miss_fetches_from_ark():
    mock_s3 = MagicMock()
    mock_s3.get_object.side_effect = Exception("NoSuchKey")

    resp = _mock_urlopen(_SAMPLE_CSV)
    with patch("urllib.request.urlopen", return_value=resp):
        result = get_tickers(s3=mock_s3, bucket="my-bucket")

    assert "AAPL" in result
    assert "TSLA" in result


def test_get_tickers_s3_miss_writes_back_to_s3():
    mock_s3 = MagicMock()
    mock_s3.get_object.side_effect = Exception("NoSuchKey")

    resp = _mock_urlopen(_SAMPLE_CSV)
    with patch("urllib.request.urlopen", return_value=resp):
        get_tickers(s3=mock_s3, bucket="my-bucket")

    mock_s3.put_object.assert_called_once()
    body = json.loads(mock_s3.put_object.call_args.kwargs["Body"])
    assert "AAPL" in body


def test_get_tickers_no_s3_falls_through_to_ark():
    resp = _mock_urlopen(_SAMPLE_CSV)
    with patch("urllib.request.urlopen", return_value=resp):
        result = get_tickers()

    assert isinstance(result, list)
    assert "AAPL" in result


def test_get_tickers_s3_write_failure_is_swallowed():
    mock_s3 = MagicMock()
    mock_s3.get_object.side_effect = Exception("miss")
    mock_s3.put_object.side_effect = Exception("write failed")

    resp = _mock_urlopen(_SAMPLE_CSV)
    with patch("urllib.request.urlopen", return_value=resp):
        result = get_tickers(s3=mock_s3, bucket="my-bucket")

    assert isinstance(result, list)


# ── _fetch_from_ark ───────────────────────────────────────────────────────────

def test_fetch_from_ark_parses_ticker_column():
    resp = _mock_urlopen(_SAMPLE_CSV)
    with patch("urllib.request.urlopen", return_value=resp):
        result = _fetch_from_ark()
    assert "AAPL" in result
    assert "TSLA" in result


def test_fetch_from_ark_deduplicates_across_etfs():
    # Both ETFs hold AAPL — should appear only once
    resp = _mock_urlopen(_SAMPLE_CSV)
    with patch("urllib.request.urlopen", return_value=resp):
        result = _fetch_from_ark()
    assert result.count("AAPL") == 1


def test_fetch_from_ark_skips_dash_tickers():
    csv = "ticker\n-\nTSLA\n"
    resp = _mock_urlopen(csv)
    with patch("urllib.request.urlopen", return_value=resp):
        result = _fetch_from_ark()
    assert "-" not in result


def test_fetch_from_ark_returns_sorted():
    resp = _mock_urlopen(_SAMPLE_CSV)
    with patch("urllib.request.urlopen", return_value=resp):
        result = _fetch_from_ark()
    assert result == sorted(result)


def test_fetch_from_ark_network_error_returns_empty():
    with patch("urllib.request.urlopen", side_effect=Exception("network error")):
        result = _fetch_from_ark()
    assert result == []
