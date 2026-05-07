from __future__ import annotations

import subprocess
import logging
from datetime import datetime
from pathlib import Path

from .sources.base import Signal

logger = logging.getLogger(__name__)

_REPORTS_DIR = Path(__file__).parent.parent / "reports"


def generate_and_open(signals: list[Signal]) -> Path:
    _REPORTS_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    path = _REPORTS_DIR / f"put-scan-{timestamp}.html"

    by_ticker: dict[str, list[Signal]] = {}
    for s in signals:
        by_ticker.setdefault(s.data["ticker"], []).append(s)

    path.write_text(_render(by_ticker, timestamp), encoding="utf-8")
    logger.info("Report saved: %s", path)
    subprocess.run(["open", str(path)])
    return path


def _render(by_ticker: dict[str, list[Signal]], timestamp: str) -> str:
    total_puts = sum(len(v) for v in by_ticker.values())
    ticker_cards = "\n".join(_ticker_card(ticker, signals) for ticker, signals in by_ticker.items())

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Put Scan — {timestamp}</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: #0f1117; color: #e2e8f0; padding: 2rem; }}
  h1 {{ font-size: 1.5rem; font-weight: 600; margin-bottom: 0.25rem; }}
  .meta {{ color: #64748b; font-size: 0.85rem; margin-bottom: 2rem; }}
  .summary {{ display: flex; gap: 1rem; margin-bottom: 2rem; flex-wrap: wrap; }}
  .stat {{ background: #1e2330; border: 1px solid #2d3447; border-radius: 8px; padding: 1rem 1.5rem; }}
  .stat-value {{ font-size: 2rem; font-weight: 700; color: #38bdf8; }}
  .stat-label {{ font-size: 0.75rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; margin-top: 0.25rem; }}
  .ticker-card {{ background: #1e2330; border: 1px solid #2d3447; border-radius: 10px; margin-bottom: 1.5rem; overflow: hidden; }}
  .ticker-header {{ padding: 1rem 1.5rem; background: #252b3b; display: flex; align-items: baseline; gap: 1rem; border-bottom: 1px solid #2d3447; }}
  .ticker-name {{ font-size: 1.25rem; font-weight: 700; color: #f1f5f9; }}
  .ticker-gain {{ font-size: 0.9rem; font-weight: 600; color: #f87171; }}
  .ticker-price {{ font-size: 0.85rem; color: #64748b; margin-left: auto; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 0.85rem; }}
  th {{ text-align: left; padding: 0.6rem 1rem; color: #64748b; font-weight: 500; text-transform: uppercase; font-size: 0.72rem; letter-spacing: 0.05em; border-bottom: 1px solid #2d3447; }}
  td {{ padding: 0.6rem 1rem; border-bottom: 1px solid #1a2030; color: #cbd5e1; }}
  tr:last-child td {{ border-bottom: none; }}
  tr:hover td {{ background: #252b3b; }}
  .iv-low {{ color: #4ade80; }}
  .iv-mid {{ color: #facc15; }}
  .iv-high {{ color: #f87171; }}
  .cost {{ color: #38bdf8; font-weight: 500; }}
  .contract {{ font-family: monospace; font-size: 0.75rem; color: #475569; }}
</style>
</head>
<body>
<h1>Put Scan Report</h1>
<p class="meta">Generated {timestamp} &nbsp;·&nbsp; {len(by_ticker)} ticker{'s' if len(by_ticker) != 1 else ''} &nbsp;·&nbsp; {total_puts} qualifying put{'s' if total_puts != 1 else ''}</p>

<div class="summary">
  <div class="stat"><div class="stat-value">{len(by_ticker)}</div><div class="stat-label">Tickers</div></div>
  <div class="stat"><div class="stat-value">{total_puts}</div><div class="stat-label">Qualifying Puts</div></div>
</div>

{ticker_cards}
</body>
</html>"""


def _iv_class(iv: float) -> str:
    if iv < 1.0:
        return "iv-low"
    if iv < 1.5:
        return "iv-mid"
    return "iv-high"


def _ticker_card(ticker: str, signals: list[Signal]) -> str:
    d = signals[0].data
    gain_pct = d["gain_pct"]
    current_price = d["current_price"]

    rows = sorted(signals, key=lambda s: (s.data["expiry"], s.data["strike"]))

    rows_html = ""
    for s in rows:
        r = s.data
        cost_pct = r["ask"] / r["current_price"] * 100
        iv = r["iv"]
        oi = int(r["open_interest"]) if r["open_interest"] else 0
        vol = int(r["volume"]) if r.get("volume") and r["volume"] == r["volume"] else "—"
        rows_html += f"""
    <tr>
      <td>{r['expiry']}</td>
      <td>${r['strike']:.0f}</td>
      <td>${r['ask']:.2f}</td>
      <td class="cost">{cost_pct:.2f}%</td>
      <td class="{_iv_class(iv)}">{iv:.0%}</td>
      <td>{oi:,}</td>
      <td>{vol if isinstance(vol, str) else f'{vol:,}'}</td>
      <td class="contract">{r['contract']}</td>
    </tr>"""

    return f"""<div class="ticker-card">
  <div class="ticker-header">
    <span class="ticker-name">{ticker}</span>
    <span class="ticker-gain">+{gain_pct:.0f}% YTD</span>
    <span class="ticker-price">Current: ${current_price:.2f}</span>
  </div>
  <table>
    <thead>
      <tr>
        <th>Expiry</th><th>Strike</th><th>Ask</th><th>Cost %</th><th>IV</th><th>Open Int</th><th>Volume</th><th>Contract</th>
      </tr>
    </thead>
    <tbody>{rows_html}
    </tbody>
  </table>
</div>"""
