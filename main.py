import logging

import setproctitle
setproctitle.setproctitle("indicators")  # shows as "indicators" in Activity Monitor instead of "python"

from indicators.notifier import Alert, send_alert
from indicators.report import generate_and_open
from indicators.scheduler import register_daily, start
from indicators.sources.gainer_puts import GainerPutScanner

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# ── Configure your indicators here ───────────────────────────────────────────

put_scanner = GainerPutScanner()


# ── Jobs ──────────────────────────────────────────────────────────────────────

def run_daily_checks() -> None:
    logger.info("Running daily gainer put scan")

    signals = [s for s in put_scanner.check() if s.triggered]
    if not signals:
        logger.info("No qualifying puts found")
        return

    by_ticker: dict[str, list] = {}
    for s in signals:
        by_ticker.setdefault(s.data["ticker"], []).append(s)

    ticker_lines = [
        f"{ticker} (+{puts[0].data['gain_pct']:.0f}%) — {len(puts)} put{'s' if len(puts) > 1 else ''}"
        for ticker, puts in by_ticker.items()
    ]

    send_alert(Alert(
        title=f"Put Scanner: {len(signals)} opportunit{'ies' if len(signals) > 1 else 'y'} across {len(by_ticker)} ticker{'s' if len(by_ticker) > 1 else ''}",
        message=", ".join(ticker_lines),
        subtitle="Gainer Put Scan",
    ))
    generate_and_open(signals)


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    register_daily(run_daily_checks)
    start()
