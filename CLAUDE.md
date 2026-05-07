# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
pip install -e .

# Run the app (blocks; Ctrl+C to stop)
python main.py

# Send a test notification without running the scheduler
.venv/bin/python -c "
from indicators.notifier import Alert, send_alert
send_alert(Alert(title='Test', subtitle='SPY', message='\$733.83 > \$560.00'))
"
```

There are no tests or linter configs yet.

## System dependencies

`terminal-notifier` must be installed for Mac notifications (`brew install terminal-notifier`). The old `osascript display notification` approach doesn't appear in System Settings → Notifications on macOS Sequoia.

## Architecture

This is a Python cron app that polls financial indicators on a schedule and fires desktop or SMS alerts when thresholds are crossed.

**Entry point — `main.py`**
This is where indicators are instantiated and configured, and where `run_checks()` is defined. Adding a new indicator means instantiating it here and calling `.check()` inside `run_checks()`.

**Core abstractions (`indicators/sources/base.py`)**
- `Indicator` — abstract base class; subclasses implement `check() -> list[Signal]`
- `Signal` — dataclass returned by `check()`; has `triggered`, `title`, `message`, `subtitle`, `data`

**Indicator implementations (`indicators/sources/`)**
- `PriceAlert` — fetches via `yfinance.Ticker.fast_info.last_price`; takes `PriceThreshold` objects (ticker + optional `above`/`below`)
- `AlphaVantageAlert` — same interface as `PriceAlert` but fetches via Alpha Vantage `GLOBAL_QUOTE` endpoint using `httpx`; requires `ALPHA_VANTAGE_API_KEY` in env

**Notification (`indicators/notifier.py`)**
- `send_alert(Alert)` — dispatches to `terminal-notifier` (mac) and/or Twilio SMS based on `NOTIFY_VIA` env var. Twilio is lazily imported and optional.

**Scheduler (`indicators/scheduler.py`)**
- Wraps APScheduler's `BlockingScheduler` (ET timezone). `register(func)` wraps the job in a market-hours guard using `exchange_calendars` (XNYS calendar) — jobs silently no-op outside NYSE trading hours (9:30–16:00 ET, Mon–Fri, holidays respected).
- `is_market_open()` is exported for use in `main.py` to gate the immediate startup check.

**Config (`indicators/config.py`)**
- All settings read from env vars at import time. Copy `.env.example` to `.env`. Key vars: `CHECK_INTERVAL_MINUTES`, `NOTIFY_VIA` (`mac`/`sms`/`both`), `WATCHLIST`, Twilio credentials, `ALPHA_VANTAGE_API_KEY`.

## Adding a new indicator

1. Create `indicators/sources/myindicator.py` — subclass `Indicator`, implement `check() -> list[Signal]`
2. Export it from `indicators/sources/__init__.py`
3. Instantiate it in `main.py` and call `.check()` inside `run_checks()`
