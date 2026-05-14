from __future__ import annotations

import json
import math

import pytest

from indicators.report import _build_report, _first_signal, _put_to_dict, _update_manifest
from tests.conftest import make_signal


# ── _put_to_dict ──────────────────────────────────────────────────────────────

def test_put_to_dict_basic_fields():
    s = make_signal()
    d = _put_to_dict(s)
    assert d["contract"] == s.data["contract"]
    assert d["term"] == "short"
    assert d["expiry"] == s.data["expiry"]
    assert d["strike"] == s.data["strike"]
    assert d["ask"] == s.data["ask"]
    assert d["iv"] == s.data["iv"]
    assert d["return_multiple"] == s.data["return_multiple"]
    assert d["prob_itm"] == s.data["prob_itm"]


def test_put_to_dict_no_context_fields_by_default():
    d = _put_to_dict(make_signal())
    assert "ticker" not in d
    assert "gain_pct" not in d
    assert "current_price" not in d


def test_put_to_dict_with_context():
    d = _put_to_dict(make_signal(), with_context=True)
    assert d["ticker"] == "AAPL"
    assert d["gain_pct"] == 600.0
    assert d["current_price"] == 200.0


def test_put_to_dict_nan_open_interest():
    s = make_signal(open_interest=float("nan"))
    d = _put_to_dict(s)
    assert d["open_interest"] == 0


def test_put_to_dict_nan_volume():
    s = make_signal(volume=float("nan"))
    d = _put_to_dict(s)
    assert d["volume"] is None


def test_put_to_dict_none_volume():
    s = make_signal(volume=None)
    d = _put_to_dict(s)
    assert d["volume"] is None


def test_put_to_dict_valid_volume():
    s = make_signal(volume=42)
    d = _put_to_dict(s)
    assert d["volume"] == 42


# ── _first_signal ─────────────────────────────────────────────────────────────

def test_first_signal_found_in_first_bucket():
    s = make_signal("AAPL")
    result = _first_signal("AAPL", {"AAPL": [s]}, {})
    assert result is s


def test_first_signal_found_in_second_bucket():
    s = make_signal("MSFT")
    result = _first_signal("MSFT", {}, {"MSFT": [s]})
    assert result is s


def test_first_signal_not_found_raises():
    with pytest.raises(ValueError, match="AAPL"):
        _first_signal("AAPL", {}, {})


# ── _build_report ─────────────────────────────────────────────────────────────

def test_build_report_structure():
    signals = [make_signal("AAPL", term="short"), make_signal("TSLA", term="long")]
    report = _build_report(signals, "put-scan-2026-01-01_09-31", "2026-01-01_09-31")
    assert report["id"] == "put-scan-2026-01-01_09-31"
    assert report["generated_at"] == "2026-01-01_09-31"
    assert "summary" in report
    assert "heroes" in report
    assert "tickers" in report


def test_build_report_summary_counts():
    signals = [
        make_signal("AAPL", term="short"),
        make_signal("AAPL", term="short", contract="AAPL261219P00140000"),
        make_signal("TSLA", term="long"),
        make_signal("NVDA", term="moonshot"),
    ]
    report = _build_report(signals, "id", "ts")
    assert report["summary"]["short_puts"] == 2
    assert report["summary"]["long_puts"] == 1
    assert report["summary"]["moonshot_puts"] == 1
    assert report["summary"]["tickers_flagged"] == 3


def test_build_report_empty_signals():
    report = _build_report([], "id", "ts")
    assert report["heroes"]["short"] is None
    assert report["heroes"]["long"] is None
    assert report["heroes"]["moonshot"] is None
    assert report["tickers"] == []
    assert report["summary"]["tickers_flagged"] == 0


def test_build_report_hero_is_max_score():
    low = make_signal("AAPL", term="short", score=1.0, contract="AAPL_LOW")
    high = make_signal("AAPL", term="short", score=9.0, contract="AAPL_HIGH")
    report = _build_report([low, high], "id", "ts")
    assert report["heroes"]["short"]["contract"] == "AAPL_HIGH"


def test_build_report_moonshot_hero_is_max_return():
    low = make_signal("AAPL", term="moonshot", return_multiple=10.0, contract="AAPL_LOW")
    high = make_signal("TSLA", term="moonshot", return_multiple=99.0, contract="TSLA_HIGH")
    report = _build_report([low, high], "id", "ts")
    assert report["heroes"]["moonshot"]["contract"] == "TSLA_HIGH"


def test_build_report_ticker_puts_include_all_terms():
    signals = [
        make_signal("AAPL", term="short"),
        make_signal("AAPL", term="long", contract="AAPL_LONG"),
        make_signal("AAPL", term="moonshot", contract="AAPL_MOON"),
    ]
    report = _build_report(signals, "id", "ts")
    assert len(report["tickers"]) == 1
    assert len(report["tickers"][0]["puts"]) == 3


def test_build_report_ticker_order_preserves_insertion():
    signals = [make_signal("TSLA", term="short"), make_signal("AAPL", term="long")]
    report = _build_report(signals, "id", "ts")
    tickers = [t["ticker"] for t in report["tickers"]]
    assert tickers == ["TSLA", "AAPL"]


# ── _update_manifest ──────────────────────────────────────────────────────────

def test_update_manifest_creates_file(tmp_path, monkeypatch):
    import indicators.report as report_mod
    monkeypatch.setattr(report_mod, "_MANIFEST", tmp_path / "manifest.json")
    _update_manifest("put-scan-001", {"tickers_flagged": 3, "short_puts": 2, "long_puts": 1, "moonshot_puts": 0}, "2026-01-01_09-31")
    data = json.loads((tmp_path / "manifest.json").read_text())
    assert len(data) == 1
    assert data[0]["id"] == "put-scan-001"


def test_update_manifest_prepends_newest(tmp_path, monkeypatch):
    import indicators.report as report_mod
    manifest = tmp_path / "manifest.json"
    monkeypatch.setattr(report_mod, "_MANIFEST", manifest)
    summary = {"tickers_flagged": 1, "short_puts": 1, "long_puts": 0, "moonshot_puts": 0}
    _update_manifest("id-old", summary, "ts-old")
    _update_manifest("id-new", summary, "ts-new")
    data = json.loads(manifest.read_text())
    assert data[0]["id"] == "id-new"
    assert data[1]["id"] == "id-old"


def test_update_manifest_deduplicates(tmp_path, monkeypatch):
    import indicators.report as report_mod
    manifest = tmp_path / "manifest.json"
    monkeypatch.setattr(report_mod, "_MANIFEST", manifest)
    summary = {"tickers_flagged": 1, "short_puts": 1, "long_puts": 0, "moonshot_puts": 0}
    _update_manifest("same-id", summary, "ts1")
    _update_manifest("same-id", summary, "ts2")
    data = json.loads(manifest.read_text())
    assert len(data) == 1


def test_update_manifest_handles_corrupt_file(tmp_path, monkeypatch):
    import indicators.report as report_mod
    manifest = tmp_path / "manifest.json"
    manifest.write_text("not json")
    monkeypatch.setattr(report_mod, "_MANIFEST", manifest)
    summary = {"tickers_flagged": 1, "short_puts": 0, "long_puts": 0, "moonshot_puts": 0}
    _update_manifest("id-1", summary, "ts")
    data = json.loads(manifest.read_text())
    assert len(data) == 1
