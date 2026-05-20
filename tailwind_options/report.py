from __future__ import annotations

import json
import logging
import socket
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

from .sources.base import Signal
from .universe import get_company_names

logger = logging.getLogger(__name__)

_REPORTS_DIR = Path(__file__).parent.parent / "reports"
_SERVER_PORT = 8765


def generate_and_open(put_signals: list[Signal], call_signals: list[Signal] | None = None) -> Path:
    _REPORTS_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")

    puts_dir = _REPORTS_DIR / "puts"
    puts_dir.mkdir(exist_ok=True)
    puts_id = f"put-scan-{timestamp}"
    puts_data = _build_puts_report(put_signals, puts_id, timestamp)
    puts_path = puts_dir / f"{puts_id}.json"
    puts_path.write_text(json.dumps(puts_data, indent=2), encoding="utf-8")
    _update_manifest(puts_dir / "manifest.json", puts_id, puts_data["summary"], timestamp)
    logger.info("Puts report saved: %s", puts_path)

    if call_signals:
        calls_dir = _REPORTS_DIR / "calls"
        calls_dir.mkdir(exist_ok=True)
        calls_id = f"call-scan-{timestamp}"
        calls_data = _build_calls_report(call_signals, calls_id, timestamp)
        calls_path = calls_dir / f"{calls_id}.json"
        calls_path.write_text(json.dumps(calls_data, indent=2), encoding="utf-8")
        _update_manifest(calls_dir / "manifest.json", calls_id, calls_data["summary"], timestamp)
        logger.info("Calls report saved: %s", calls_path)

    _ensure_server()
    subprocess.run(["open", f"http://localhost:{_SERVER_PORT}/index.html#{puts_id}"])
    return puts_path


def _build_puts_report(put_signals: list[Signal], report_id: str, timestamp: str) -> dict:
    by_short: dict[str, list[Signal]] = {}
    by_long: dict[str, list[Signal]] = {}
    by_moonshot: dict[str, list[Signal]] = {}

    for s in put_signals:
        t = s.data["ticker"]
        term = s.data.get("term")
        if term == "short":
            by_short.setdefault(t, []).append(s)
        elif term == "long":
            by_long.setdefault(t, []).append(s)
        else:
            by_moonshot.setdefault(t, []).append(s)

    short_signals = sum(by_short.values(), [])
    long_signals = sum(by_long.values(), [])
    moonshot_signals = sum(by_moonshot.values(), [])

    short_hero = max(short_signals, key=lambda s: s.data["score"]) if short_signals else None
    long_hero = max(long_signals, key=lambda s: s.data["score"]) if long_signals else None
    moonshot_hero = (
        max(moonshot_signals, key=lambda s: s.data["return_multiple"]) if moonshot_signals else None
    )

    all_tickers = list(dict.fromkeys(list(by_short) + list(by_long) + list(by_moonshot)))
    company_names = get_company_names()

    return {
        "id": report_id,
        "generated_at": timestamp,
        "summary": {
            "tickers_flagged": len(all_tickers),
            "short_puts": len(short_signals),
            "long_puts": len(long_signals),
            "moonshot_puts": len(moonshot_signals),
        },
        "heroes": {
            "short": _put_to_dict(short_hero, with_context=True) if short_hero else None,
            "long": _put_to_dict(long_hero, with_context=True) if long_hero else None,
            "moonshot": _put_to_dict(moonshot_hero, with_context=True) if moonshot_hero else None,
        },
        "tickers": [
            {
                "ticker": t,
                "company_name": company_names.get(t),
                "gain_pct": _first_signal(t, by_short, by_long, by_moonshot).data["gain_pct"],
                "current_price": _first_signal(t, by_short, by_long, by_moonshot).data["current_price"],
                "puts": [
                    _put_to_dict(s)
                    for s in (by_short.get(t, []) + by_long.get(t, []) + by_moonshot.get(t, []))
                ],
            }
            for t in all_tickers
        ],
    }


def _build_calls_report(call_signals: list[Signal], report_id: str, timestamp: str) -> dict:
    by_short: dict[str, list[Signal]] = {}
    by_long: dict[str, list[Signal]] = {}
    by_moonshot: dict[str, list[Signal]] = {}

    for s in call_signals:
        t = s.data["ticker"]
        term = s.data.get("term")
        if term == "short":
            by_short.setdefault(t, []).append(s)
        elif term == "long":
            by_long.setdefault(t, []).append(s)
        else:
            by_moonshot.setdefault(t, []).append(s)

    short_signals = sum(by_short.values(), [])
    long_signals = sum(by_long.values(), [])
    moonshot_signals = sum(by_moonshot.values(), [])

    short_hero = max(short_signals, key=lambda s: s.data["score"]) if short_signals else None
    long_hero = max(long_signals, key=lambda s: s.data["score"]) if long_signals else None
    moonshot_hero = (
        max(moonshot_signals, key=lambda s: s.data["return_multiple"]) if moonshot_signals else None
    )

    all_tickers = list(dict.fromkeys(list(by_short) + list(by_long) + list(by_moonshot)))
    company_names = get_company_names()

    return {
        "id": report_id,
        "generated_at": timestamp,
        "summary": {
            "tickers_flagged": len(all_tickers),
            "short_calls": len(short_signals),
            "long_calls": len(long_signals),
            "moonshot_calls": len(moonshot_signals),
        },
        "heroes": {
            "short": _call_to_dict(short_hero, with_context=True) if short_hero else None,
            "long": _call_to_dict(long_hero, with_context=True) if long_hero else None,
            "moonshot": _call_to_dict(moonshot_hero, with_context=True) if moonshot_hero else None,
        },
        "tickers": [
            {
                "ticker": t,
                "company_name": company_names.get(t),
                "momentum_pct": _first_signal(t, by_short, by_long, by_moonshot).data["momentum_pct"],
                "current_price": _first_signal(t, by_short, by_long, by_moonshot).data["current_price"],
                "calls": [
                    _call_to_dict(s)
                    for s in (by_short.get(t, []) + by_long.get(t, []) + by_moonshot.get(t, []))
                ],
            }
            for t in all_tickers
        ],
    }


def _first_signal(ticker: str, *buckets: dict[str, list[Signal]]) -> Signal:
    for b in buckets:
        if ticker in b:
            return b[ticker][0]
    raise ValueError(f"Ticker {ticker} not found in any bucket")


def _put_to_dict(s: Signal, with_context: bool = False) -> dict:
    r = s.data
    oi_raw = r.get("open_interest")
    oi = int(oi_raw) if oi_raw and oi_raw == oi_raw else 0
    vol_raw = r.get("volume")
    vol = int(vol_raw) if vol_raw and vol_raw == vol_raw else None

    d: dict = {
        "contract": r["contract"],
        "term": r.get("term", "moonshot"),
        "expiry": r["expiry"],
        "strike": r["strike"],
        "ask": r["ask"],
        "iv": r["iv"],
        "open_interest": oi,
        "volume": vol,
        "breakeven_drop_pct": r["breakeven_drop_pct"],
        "return_multiple": r["return_multiple"],
        "prob_itm": r.get("prob_itm", 0.0),
        "score": r.get("score", 0.0),
    }
    if with_context:
        d.update({
            "ticker": r["ticker"],
            "gain_pct": r["gain_pct"],
            "current_price": r["current_price"],
        })
    return d


def _call_to_dict(s: Signal, with_context: bool = False) -> dict:
    r = s.data
    oi_raw = r.get("open_interest")
    oi = int(oi_raw) if oi_raw and oi_raw == oi_raw else 0
    vol_raw = r.get("volume")
    vol = int(vol_raw) if vol_raw and vol_raw == vol_raw else None

    d: dict = {
        "contract": r["contract"],
        "term": r.get("term", "moonshot"),
        "expiry": r["expiry"],
        "strike": r["strike"],
        "ask": r["ask"],
        "iv": r["iv"],
        "open_interest": oi,
        "volume": vol,
        "breakeven_rise_pct": r["breakeven_rise_pct"],
        "return_multiple": r["return_multiple"],
        "prob_itm": r.get("prob_itm", 0.0),
        "score": r.get("score", 0.0),
    }
    if with_context:
        d.update({
            "ticker": r["ticker"],
            "momentum_pct": r["momentum_pct"],
            "current_price": r["current_price"],
        })
    return d


def _update_manifest(manifest_path: Path, report_id: str, summary: dict, timestamp: str) -> None:
    entries: list[dict] = []
    if manifest_path.exists():
        try:
            entries = json.loads(manifest_path.read_text())
        except Exception:
            pass
    entries = [e for e in entries if e.get("id") != report_id]
    entries.insert(0, {"id": report_id, "generated_at": timestamp, **summary})
    manifest_path.write_text(json.dumps(entries, indent=2), encoding="utf-8")


def _ensure_server() -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        if sock.connect_ex(("localhost", _SERVER_PORT)) != 0:
            subprocess.Popen(
                [sys.executable, "-m", "http.server", str(_SERVER_PORT)],
                cwd=_REPORTS_DIR,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            time.sleep(0.5)
            logger.info("Started local report server on http://localhost:%d", _SERVER_PORT)
