from __future__ import annotations

import json
import logging
import socket
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from .constants import AI_MOMENTUM, BREAKEVEN_DROP, BREAKEVEN_RISE, MEAN_REVERSION
from .sources.base import Signal
from .universe import get_company_names

logger = logging.getLogger(__name__)

_REPORTS_DIR = Path(__file__).parent.parent / "reports"
_SERVER_PORT = 8765


def write_theme_report_to_s3(
    signals: list[Signal],
    s3: Any,
    bucket_name: str,
    timestamp: str,
    page: str,
    theme_id: str,
) -> None:
    """Build and write a theme report + manifest entry to S3."""
    prefix = "put" if page == "puts" else "call"
    report_id = f"{prefix}-scan-{timestamp}"
    report_data = (
        _build_puts_report(signals, report_id, timestamp)
        if page == "puts"
        else _build_calls_report(signals, report_id, timestamp)
    )
    report_key = f"{page}/{theme_id}/{report_id}.json"
    manifest_key = f"{page}/{theme_id}/manifest.json"

    s3.put_object(
        Bucket=bucket_name,
        Key=report_key,
        Body=json.dumps(report_data, indent=2),
        ContentType="application/json",
    )
    logger.info("Report written to s3://%s/%s", bucket_name, report_key)
    _write_manifest_to_s3(s3, bucket_name, manifest_key, report_id, report_data["summary"], timestamp)


def _write_manifest_to_s3(
    s3: Any,
    bucket_name: str,
    key: str,
    report_id: str,
    summary: dict,
    timestamp: str,
) -> None:
    try:
        existing = json.loads(s3.get_object(Bucket=bucket_name, Key=key)["Body"].read())
    except Exception:
        existing = []
    existing = [e for e in existing if e.get("id") != report_id]
    existing.insert(0, {"id": report_id, "generated_at": timestamp, **summary})
    s3.put_object(
        Bucket=bucket_name,
        Key=key,
        Body=json.dumps(existing, indent=2),
        ContentType="application/json",
        CacheControl="no-store",
    )
    logger.info("%s updated (%d entries)", key, len(existing))


def write_theme_report_locally(signals: list[Signal], page: str, theme_id: str) -> Path:
    """Write a single theme's signals to reports/{page}/{theme_id}/ and update its manifest."""
    _REPORTS_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    prefix = "put" if page == "puts" else "call"
    report_id = f"{prefix}-scan-{timestamp}"

    theme_dir = _REPORTS_DIR / page / theme_id
    theme_dir.mkdir(parents=True, exist_ok=True)

    report_data = (
        _build_puts_report(signals, report_id, timestamp)
        if page == "puts"
        else _build_calls_report(signals, report_id, timestamp)
    )
    report_path = theme_dir / f"{report_id}.json"
    report_path.write_text(json.dumps(report_data, indent=2), encoding="utf-8")
    _update_manifest(theme_dir / "manifest.json", report_id, report_data["summary"], timestamp)
    logger.info("%s/%s report saved: %s", page, theme_id, report_path)
    return report_path


def generate_and_open(put_signals: list[Signal], call_signals: list[Signal] | None = None) -> Path:
    puts_theme_id = put_signals[0].data.get("theme_id", MEAN_REVERSION) if put_signals else MEAN_REVERSION
    puts_path = write_theme_report_locally(put_signals, "puts", puts_theme_id)

    if call_signals:
        calls_theme_id = call_signals[0].data.get("theme_id", AI_MOMENTUM)
        write_theme_report_locally(call_signals, "calls", calls_theme_id)

    _ensure_server()
    subprocess.run(["open", f"http://localhost:5173/"])
    return puts_path


def _build_puts_report(put_signals: list[Signal], report_id: str, timestamp: str) -> dict:
    return _build_report(put_signals, report_id, timestamp, "puts")


def _build_calls_report(call_signals: list[Signal], report_id: str, timestamp: str) -> dict:
    return _build_report(call_signals, report_id, timestamp, "calls")


def _build_report(signals: list[Signal], report_id: str, timestamp: str, page: str) -> dict:
    is_puts = page == "puts"
    option_key = "puts" if is_puts else "calls"
    default_theme = MEAN_REVERSION if is_puts else AI_MOMENTUM
    default_move_label = "1Y" if is_puts else "90D"
    default_move_field = "gain_pct" if is_puts else "momentum_pct"

    by_short: dict[str, list[Signal]] = {}
    by_long: dict[str, list[Signal]] = {}
    by_moonshot: dict[str, list[Signal]] = {}

    for s in signals:
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
            f"short_{option_key}": len(short_signals),
            f"long_{option_key}": len(long_signals),
            f"moonshot_{option_key}": len(moonshot_signals),
        },
        "heroes": {
            "short": _option_to_dict(short_hero, is_puts, with_context=True) if short_hero else None,
            "long": _option_to_dict(long_hero, is_puts, with_context=True) if long_hero else None,
            "moonshot": _option_to_dict(moonshot_hero, is_puts, with_context=True) if moonshot_hero else None,
        },
        "tickers": [
            {
                "ticker": t,
                "company_name": company_names.get(t),
                "theme_id": (f := _first_signal(t, by_short, by_long, by_moonshot).data).get("theme_id", default_theme),
                default_move_field: f.get(default_move_field, 0),
                "move_pct": f.get("move_pct", f.get(default_move_field, 0)),
                "move_label": f.get("move_label", default_move_label),
                "current_price": f["current_price"],
                option_key: [
                    _option_to_dict(s, is_puts)
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


def _option_to_dict(s: Signal, is_put: bool, with_context: bool = False) -> dict:
    r = s.data
    oi_raw = r.get("open_interest")
    oi = int(oi_raw) if oi_raw and oi_raw == oi_raw else 0
    vol_raw = r.get("volume")
    vol = int(vol_raw) if vol_raw and vol_raw == vol_raw else None
    breakeven_key = BREAKEVEN_DROP if is_put else BREAKEVEN_RISE

    d: dict = {
        "contract": r["contract"],
        "term": r.get("term", "moonshot"),
        "expiry": r["expiry"],
        "strike": r["strike"],
        "ask": r["ask"],
        "iv": r["iv"],
        "open_interest": oi,
        "volume": vol,
        breakeven_key: r[breakeven_key],
        "return_multiple": r["return_multiple"],
        "ev_multiple": r.get("ev_multiple", 0.0),
        "liquidity": r.get("liquidity", 0.0),
        "prob_itm": r.get("prob_itm", 0.0),
        "score": r.get("score", 0.0),
    }
    if with_context:
        default_theme = MEAN_REVERSION if is_put else AI_MOMENTUM
        default_move_label = "1Y" if is_put else "90D"
        move_field = "gain_pct" if is_put else "momentum_pct"
        d.update({
            "ticker": r["ticker"],
            "theme_id": r.get("theme_id", default_theme),
            move_field: r.get(move_field, r.get("move_pct", 0)),
            "move_pct": r.get("move_pct", r.get(move_field, 0)),
            "move_label": r.get("move_label", default_move_label),
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
