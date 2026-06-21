from __future__ import annotations

from io import StringIO
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

import tailwind_options.cache as cache_mod
from tailwind_options import cache
from tailwind_options.universe import _read_html, get_universe

# ── fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def clear_cache(tmp_path, monkeypatch):
    monkeypatch.setattr(cache_mod, "_CACHE_DIR", tmp_path)


def _mock_response(html: str) -> MagicMock:
    resp = MagicMock()
    resp.text = html
    resp.raise_for_status = MagicMock()
    return resp


SP500_HTML = """<table><tr><th>Symbol</th></tr><tr><td>AAPL</td></tr><tr><td>MSFT</td></tr></table>"""
NASDAQ_HTML = """<table><tr><th>Ticker</th></tr><tr><td>AAPL</td></tr><tr><td>NVDA</td></tr></table>"""


# ── _read_html ────────────────────────────────────────────────────────────────

def test_read_html_returns_list_of_dataframes():
    html = "<table><tr><th>A</th></tr><tr><td>1</td></tr></table>"
    with patch("tailwind_options.universe.httpx.get") as mock_get:
        mock_get.return_value = _mock_response(html)
        result = _read_html("http://example.com")
    assert isinstance(result, list)
    assert len(result) > 0


def test_read_html_raises_on_http_error():
    with patch("tailwind_options.universe.httpx.get") as mock_get:
        mock_get.return_value.raise_for_status.side_effect = Exception("404")
        with pytest.raises(Exception):
            _read_html("http://example.com")


# ── get_universe ──────────────────────────────────────────────────────────────

def test_returns_cached_universe(tmp_path):
    cache.set("universe", ["AAPL", "MSFT"])
    result = get_universe()
    assert result == ["AAPL", "MSFT"]


def test_fetches_and_deduplicates(tmp_path):
    sp = pd.DataFrame({"Symbol": ["AAPL", "MSFT"]})
    nq = pd.DataFrame({"Ticker": ["AAPL", "NVDA"]})  # AAPL duplicate

    with patch("tailwind_options.universe._read_html") as mock_html:
        mock_html.side_effect = [[sp], [None, None, None, None, None, nq]]
        result = get_universe()

    assert "AAPL" in result
    assert "MSFT" in result
    assert "NVDA" in result
    assert result.count("AAPL") == 1  # deduplicated


def test_caches_result_after_fetch():
    sp = pd.DataFrame({"Symbol": ["AAPL"]})
    nq = pd.DataFrame({"Ticker": ["NVDA"]})

    with patch("tailwind_options.universe._read_html") as mock_html:
        mock_html.side_effect = [[sp], [None, None, None, None, None, nq]]
        get_universe()

    assert cache.get("universe") is not None


def test_sp500_fetch_fails_continues(tmp_path):
    nq = pd.DataFrame({"Ticker": ["NVDA"]})

    with patch("tailwind_options.universe._read_html") as mock_html:
        def side_effect(url):
            if "S%26P" in url:
                raise Exception("network error")
            return [None, None, None, None, None, nq]
        mock_html.side_effect = side_effect
        result = get_universe()

    assert "NVDA" in result


def test_nasdaq_fetch_fails_continues():
    sp = pd.DataFrame({"Symbol": ["AAPL"]})

    with patch("tailwind_options.universe._read_html") as mock_html:
        def side_effect(url):
            if "Nasdaq" in url:
                raise Exception("network error")
            return [sp]
        mock_html.side_effect = side_effect
        result = get_universe()

    assert "AAPL" in result


def test_both_fail_returns_empty():
    with patch("tailwind_options.universe._read_html", side_effect=Exception("fail")):
        result = get_universe()
    assert result == []


def test_dot_in_symbol_replaced_with_dash():
    sp = pd.DataFrame({"Symbol": ["BRK.B", "AAPL"]})
    nq = pd.DataFrame({"Ticker": []})

    with patch("tailwind_options.universe._read_html") as mock_html:
        mock_html.side_effect = [[sp], [None, None, None, None, None, nq]]
        result = get_universe()

    assert "BRK-B" in result
    assert "BRK.B" not in result
