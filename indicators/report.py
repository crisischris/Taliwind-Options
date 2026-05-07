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


def _num_tw(value: float) -> str:
    return "text-success" if value >= 0 else "text-error"


def _be_tw(drop_pct: float) -> str:
    if drop_pct < 25:
        return "text-success"
    if drop_pct < 50:
        return "text-warning"
    return "text-error"


def _iv_tw(iv: float) -> str:
    if iv < 1.0:
        return "text-success"
    if iv < 1.5:
        return "text-warning"
    return "text-error"


def _prob_tw(prob: float) -> str:
    if prob < 0.10:
        return "text-base-content/50"
    if prob < 0.25:
        return "text-warning"
    return "text-success"


_INFO_ICON = (
    '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" '
    'class="inline-block w-3.5 h-3.5 ml-1 mb-0.5 opacity-30 hover:opacity-70 '
    'transition-opacity cursor-help" stroke="currentColor" stroke-width="2">'
    '<path stroke-linecap="round" stroke-linejoin="round" '
    'd="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>'
    '</svg>'
)


def _th(label: str, tip: str, sortable: bool = False, initial_arrow: str = "") -> str:
    sort_cls = " cursor-pointer hover:text-primary select-none" if sortable else ""
    onclick = ' onclick="sortTable(this)"' if sortable else ""
    stop = ' onclick="event.stopPropagation()"' if sortable else ""
    tip_escaped = tip.replace('"', '&quot;')
    arrow = f'<span class="sort-arrow">{" " + initial_arrow if initial_arrow else ""}</span>' if sortable else ""
    icon = (
        f'<span class="inline-flex cursor-help"{stop} data-tip-text="{tip_escaped}" '
        f'onmouseenter="showTip(this)" onmouseleave="hideTip()">{_INFO_ICON}</span>'
    )
    return f'<th class="text-base-content/50{sort_cls}"{onclick}><span class="col-label">{label}</span>{arrow}{icon}</th>'


def _ticker_card(ticker: str, signals: list[Signal], hero_contract: str = "") -> str:
    d = signals[0].data
    gain_pct = d["gain_pct"]
    current_price = d["current_price"]
    gain_color = "text-success" if gain_pct >= 0 else "text-error"
    gain_sign = "+" if gain_pct >= 0 else ""

    rows_html = ""
    for s in signals:
        r = s.data
        cost_pct = r["ask"] / r["current_price"] * 100
        contract_cost = r["ask"] * 100
        iv = r["iv"]
        oi = int(r["open_interest"]) if r["open_interest"] else 0
        vol = int(r["volume"]) if r.get("volume") and r["volume"] == r["volume"] else "—"
        be_drop = r["breakeven_drop_pct"]
        ret_mult = r["return_multiple"]
        prob = r.get("prob_itm", 0.0)
        vol_str = f"{vol:,}" if isinstance(vol, int) else vol
        is_hero = r["contract"] == hero_contract
        row_class = "bg-yellow-400/10 outline outline-1 outline-yellow-400/40" if is_hero else ""
        row_id = 'id="hero-row"' if is_hero else ""
        crown = " 👑" if is_hero else ""
        expiry_sort = r['expiry'].replace('-', '')
        vol_sort = vol if isinstance(vol, int) else 0
        rows_html += f"""
              <tr {row_id} class="{row_class}">
                <td class="font-bold text-lg {_num_tw(ret_mult)}">{ret_mult:.0f}x{crown}</td>
                <td class="{_prob_tw(prob)}">{prob:.1%}</td>
                <td class="font-mono text-sm" data-sort="{expiry_sort}">{r['expiry']}</td>
                <td class="{_num_tw(r['strike'])}">${r['strike']:.0f}</td>
                <td class="font-semibold {_num_tw(r['ask'])}">${r['ask']:.2f}</td>
                <td class="font-semibold">${contract_cost:,.2f}</td>
                <td class="text-info">{cost_pct:.2f}%</td>
                <td class="{_be_tw(be_drop)}">{be_drop:.1f}%</td>
                <td class="{_iv_tw(iv)}">{iv:.0%}</td>
                <td>{oi:,}</td>
                <td data-sort="{vol_sort}">{vol_str}</td>
              </tr>"""

    return f"""
    <div class="collapse collapse-arrow bg-base-200 border border-base-300 rounded-xl mb-4">
      <input type="checkbox" checked />
      <div class="collapse-title flex items-center gap-3">
        <span class="text-xl font-bold">{ticker}</span>
        <span class="badge badge-lg {gain_color} badge-outline font-semibold">{gain_sign}{gain_pct:.0f}% YTD</span>
        <span class="text-base-content/50 text-sm">Current: ${current_price:.2f}</span>
        <span class="ml-auto text-base-content/40 text-xs">{len(signals)} put{'s' if len(signals) != 1 else ''}</span>
      </div>
      <div class="collapse-content px-0 pb-0">
        <div class="overflow-x-auto">
          <table class="table table-zebra table-sm w-full">
            <thead>
              <tr class="text-base-content/50">
                {_th("Return", "Strike price divided by ask price. If the stock hits the strike at expiry, you receive this many times your investment back.", sortable=True)}
                {_th("Prob ITM", "Black-Scholes risk-neutral probability this put expires in-the-money. Options are ranked by Return x Prob ITM combined — balancing payoff size against likelihood.", sortable=True)}
                {_th("Expiry", "Option expiration date. The put must expire in-the-money to have intrinsic value.", sortable=True)}
                {_th("Strike", "The price the stock must fall below for this put to have intrinsic value at expiry.", sortable=True)}
                {_th("Ask", "Current asking price per share. One contract = 100 shares, so multiply by 100 for total cost per contract.", sortable=True)}
                {_th("Contract Cost", "Total cost of one contract in USD (ask x 100 shares). This is the actual cash outlay.", sortable=True)}
                {_th("Cost %", "Ask as a percentage of the current stock price. How much you are risking relative to the stock's value.", sortable=True)}
                {_th("BE Drop", "Breakeven drop — how far the stock must fall from today's price for you to break even at expiry (strike minus ask, expressed as % below current price).", sortable=True)}
                {_th("IV", "Implied Volatility — the market's annualised expected price swing baked into the option price. Higher IV means more expensive options.", sortable=True)}
                {_th("Open Int", "Open Interest — total number of outstanding contracts. Higher open interest means a more liquid market, making it easier to enter and exit.", sortable=True)}
                {_th("Volume", "Contracts traded today. A real-time liquidity signal — high volume means active market interest right now.", sortable=True)}
              </tr>
            </thead>
            <tbody>{rows_html}
            </tbody>
          </table>
        </div>
      </div>
    </div>"""


def _hero_card(signal: Signal) -> str:
    r = signal.data
    cost_pct = r["ask"] / r["current_price"] * 100
    prob = r.get("prob_itm", 0.0)
    contract_cost = r["ask"] * 100
    return f"""
    <div class="card bg-gradient-to-br from-yellow-900/40 to-base-200 border-2 border-yellow-400/60 shadow-lg shadow-yellow-400/10 mb-8 cursor-pointer hover:border-yellow-300/80 transition-colors"
         onclick="scrollToHero()">
      <div class="card-body">
        <div class="flex items-center gap-3 mb-2">
          <span class="text-2xl">👑</span>
          <h2 class="card-title text-yellow-300/70 text-sm font-semibold uppercase tracking-widest">Best Opportunity — click to jump to row</h2>
        </div>
        <div class="flex items-baseline gap-4 mb-4">
          <span class="text-yellow-300 text-5xl font-black tracking-tight">{r['ticker']}</span>
          <span class="badge badge-warning badge-outline text-sm font-semibold">+{r['gain_pct']:.0f}% YTD</span>
          <span class="text-base-content/40 text-sm">@ ${r['current_price']:.2f}</span>
        </div>
        <div class="flex flex-wrap gap-6">
          <div>
            <div class="text-yellow-300 text-4xl font-black">{r['return_multiple']:.0f}x</div>
            <div class="text-base-content/50 text-xs uppercase tracking-wide mt-1">Return Multiple</div>
          </div>
          <div>
            <div class="{_prob_tw(prob)} text-4xl font-black">{prob:.1%}</div>
            <div class="text-base-content/50 text-xs uppercase tracking-wide mt-1">Prob ITM</div>
          </div>
          <div class="divider divider-horizontal"></div>
          <div>
            <div class="text-success text-2xl font-bold">${r['ask']:.2f}</div>
            <div class="text-base-content/50 text-xs uppercase tracking-wide mt-1">Ask / Share</div>
          </div>
          <div>
            <div class="text-success text-2xl font-bold">${contract_cost:,.2f}</div>
            <div class="text-base-content/50 text-xs uppercase tracking-wide mt-1">Contract Cost</div>
          </div>
          <div>
            <div class="text-base-content text-2xl font-bold">${r['strike']:.0f}</div>
            <div class="text-base-content/50 text-xs uppercase tracking-wide mt-1">Strike</div>
          </div>
          <div>
            <div class="text-base-content text-2xl font-bold">{r['expiry']}</div>
            <div class="text-base-content/50 text-xs uppercase tracking-wide mt-1">Expiry</div>
          </div>
          <div>
            <div class="{_iv_tw(r['iv'])} text-2xl font-bold">{r['iv']:.0%}</div>
            <div class="text-base-content/50 text-xs uppercase tracking-wide mt-1">IV</div>
          </div>
        </div>
        <div class="mt-3 font-mono text-xs text-base-content/30">{r['contract']}</div>
      </div>
    </div>"""


def _render(by_ticker: dict[str, list[Signal]], timestamp: str) -> str:
    total_puts = sum(len(v) for v in by_ticker.values())
    all_signals = sum(by_ticker.values(), [])
    hero = max(all_signals, key=lambda s: s.data["score"])
    hero_contract = hero.data["contract"]
    ticker_cards = "\n".join(
        _ticker_card(ticker, signals, hero_contract)
        for ticker, signals in by_ticker.items()
    )
    ticker_modal_rows = "\n".join(
        f'<tr><td class="font-bold">{t}</td>'
        f'<td class="text-success">+{sigs[0].data["gain_pct"]:.0f}%</td>'
        f'<td class="text-base-content/60">{len(sigs)} put{"s" if len(sigs) != 1 else ""}</td></tr>'
        for t, sigs in by_ticker.items()
    )
    ts_display = timestamp.replace("_", " at ")

    return f"""<!DOCTYPE html>
<html lang="en" data-theme="night">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Put Scan — {timestamp}</title>
  <link href="https://cdn.jsdelivr.net/npm/daisyui@4/dist/full.min.css" rel="stylesheet">
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    @keyframes hero-flash {{
      0%, 100% {{ background-color: rgba(234, 179, 8, 0.1); }}
      50% {{ background-color: rgba(234, 179, 8, 0.35); }}
    }}
    .hero-flash {{ animation: hero-flash 0.7s ease 3; }}
  </style>
  <script>
    function scrollToHero() {{
      const row = document.getElementById('hero-row');
      if (!row) return;
      row.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
      row.classList.remove('hero-flash');
      void row.offsetWidth; // reflow to restart animation
      row.classList.add('hero-flash');
    }}
    function sortTable(th) {{
      const table = th.closest('table');
      const colIdx = Array.from(th.parentElement.children).indexOf(th);
      const arrow = th.querySelector('.sort-arrow');
      const isDesc = arrow && arrow.textContent.includes('↓');
      const asc = isDesc;

      table.querySelectorAll('thead th .sort-arrow').forEach(a => {{ a.textContent = ''; }});
      if (arrow) arrow.textContent = asc ? ' ↑' : ' ↓';

      const tbody = table.querySelector('tbody');
      const rows = Array.from(tbody.querySelectorAll('tr'));
      rows.sort((a, b) => {{
        const ac = a.children[colIdx];
        const bc = b.children[colIdx];
        const at = ac.dataset.sort ?? ac.textContent.trim();
        const bt = bc.dataset.sort ?? bc.textContent.trim();
        const an = parseFloat(at.replace(/[^0-9.-]/g, ''));
        const bn = parseFloat(bt.replace(/[^0-9.-]/g, ''));
        if (!isNaN(an) && !isNaN(bn)) return asc ? an - bn : bn - an;
        return asc ? at.localeCompare(bt) : bt.localeCompare(at);
      }});
      rows.forEach(r => tbody.appendChild(r));
    }}
    function showTip(el) {{
      hideTip();
      const text = el.dataset.tipText;
      const tip = document.createElement('div');
      tip.id = '__col-tip';
      tip.style.cssText = [
        'position:fixed', 'z-index:9999', 'max-width:260px',
        'padding:8px 12px', 'border-radius:8px', 'font-size:12px',
        'line-height:1.6', 'pointer-events:none',
        'box-shadow:0 4px 20px rgba(0,0,0,0.6)',
        'background:#1d232a', 'color:#a6adbb',
        'border:1px solid rgba(255,255,255,0.1)'
      ].join(';');
      tip.textContent = text;
      document.body.appendChild(tip);
      const r = el.getBoundingClientRect();
      tip.style.top = (r.bottom + 8) + 'px';
      tip.style.left = '0px';
      const tw = tip.getBoundingClientRect().width;
      const left = Math.max(8, Math.min(r.left, window.innerWidth - tw - 8));
      tip.style.left = left + 'px';
    }}
    function hideTip() {{
      const t = document.getElementById('__col-tip');
      if (t) t.remove();
    }}
  </script>
</head>
<body class="min-h-screen p-8">

  <div class="max-w-7xl mx-auto">

    <div class="mb-8">
      <h1 class="text-3xl font-bold tracking-tight">Put Scan Report</h1>
      <p class="text-base-content/50 text-sm mt-1">Generated {ts_display}</p>
    </div>

    <div class="stats stats-horizontal shadow bg-base-200 border border-base-300 mb-8 w-full">
      <div class="stat">
        <div class="stat-figure text-primary">
          <button class="btn btn-ghost btn-circle" onclick="document.getElementById('tickers-modal').showModal()">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="inline-block w-8 h-8 stroke-current text-primary"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
          </button>
        </div>
        <div class="stat-title">Tickers Flagged</div>
        <div class="stat-value text-primary">{len(by_ticker)}</div>
        <div class="stat-desc">500%+ YTD gainers</div>
      </div>
      <div class="stat">
        <div class="stat-figure text-secondary">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="inline-block w-8 h-8 stroke-current"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4"></path></svg>
        </div>
        <div class="stat-title">Qualifying Puts</div>
        <div class="stat-value text-secondary">{total_puts}</div>
        <div class="stat-desc">Sorted by return multiple</div>
      </div>
      <div class="stat">
        <div class="stat-figure text-success">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="inline-block w-8 h-8 stroke-current"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"></path></svg>
        </div>
        <div class="stat-title">Top Return</div>
        <div class="stat-value text-success">{max(s.data['return_multiple'] for s in sum(by_ticker.values(), [])):.0f}x</div>
        <div class="stat-desc">Best moonshot available</div>
      </div>
    </div>

    {_hero_card(hero)}

    {ticker_cards}

  </div>

  <dialog id="tickers-modal" class="modal">
    <div class="modal-box">
      <h3 class="font-bold text-lg mb-4">Tickers Flagged — 500%+ YTD</h3>
      <table class="table table-sm w-full">
        <thead><tr><th>Ticker</th><th>YTD Gain</th><th>Puts Found</th></tr></thead>
        <tbody>{ticker_modal_rows}</tbody>
      </table>
      <div class="modal-action">
        <form method="dialog"><button class="btn btn-sm">Close</button></form>
      </div>
    </div>
    <form method="dialog" class="modal-backdrop"><button>close</button></form>
  </dialog>

</body>
</html>"""
