import logging

from indicators.config import config
from indicators.notifier import Alert, send_alert
from indicators.scheduler import is_market_open, register, register_daily, start
from indicators.sources import PriceAlert, PriceThreshold
from indicators.sources.gainer_puts import GainerPutScanner

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# ── Configure your indicators here ───────────────────────────────────────────

price_alerts = PriceAlert(
    thresholds=[
        # Notify if SPY drops below 500 or rises above 560
        PriceThreshold(ticker="SPY", below=500, above=560),
        # Notify if AAPL drops below 180
        PriceThreshold(ticker="AAPL", below=180),
    ]
)

put_scanner = GainerPutScanner()


# ── Jobs ──────────────────────────────────────────────────────────────────────

def run_checks() -> None:
    logger.info("Running checks for watchlist: %s", config.watchlist)

    for signal in price_alerts.check():
        if signal.triggered:
            send_alert(Alert(
                title=signal.title,
                message=signal.message,
                subtitle=signal.subtitle,
            ))


def run_daily_checks() -> None:
    logger.info("Running daily gainer put scan")

    for signal in put_scanner.check():
        if signal.triggered:
            send_alert(Alert(
                title=signal.title,
                message=signal.message,
                subtitle=signal.subtitle,
            ))


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    logger.info("Starting indicators — interval: %d min", config.check_interval_minutes)

    # Run once immediately on start if market is open, then on the interval
    if is_market_open():
        run_checks()

    register(run_checks)
    register_daily(run_daily_checks)
    start()
