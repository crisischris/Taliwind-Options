# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
pip install -e .

# Run the app (blocks; Ctrl+C to stop)
python main.py
```

There are no tests or linter configs yet.

## Architecture

This is a Python cron app that polls financial indicators on a schedule and fires desktop or SMS alerts when thresholds are crossed.

**Entry point — `main.py`**
This is where indicators are instantiated and configured, and where `run_checks()` is defined. Adding a new indicator means instantiating it here and calling `.check()` inside `run_checks()`.

**Core abstractions (`indicators/sources/base.py`)**
- `Indicator` — abstract base class; subclasses implement `check() -> list[Signal]`
- `Signal` — dataclass returned by `check()`; has `triggered`, `title`, `message`, `subtitle`, `data`

**Existing indicator (`indicators/sources/price.py`)**
- `PriceAlert` — takes a list of `PriceThreshold` objects (ticker + optional `above`/`below` float). Fetches price via `yfinance.Ticker.fast_info.last_price` and emits a `Signal` for each crossed threshold.

**Notification (`indicators/notifier.py`)**
- `send_alert(Alert)` — dispatches to `_notify_mac` (osascript) and/or `_notify_sms` (Twilio) based on `NOTIFY_VIA` env var. Twilio is lazily imported and optional.

**Scheduler (`indicators/scheduler.py`)**
- Thin wrapper around APScheduler's `BlockingScheduler` (ET timezone). `register(func)` adds a job on the configured interval; `start()` blocks.

**Config (`indicators/config.py`)**
- All settings read from env vars at import time. Copy `.env.example` to `.env` to configure. Key vars: `CHECK_INTERVAL_MINUTES`, `NOTIFY_VIA` (`mac`/`sms`/`both`), `WATCHLIST`, Twilio credentials.

## Adding a new indicator

1. Create `indicators/sources/myindicator.py` — subclass `Indicator`, implement `check() -> list[Signal]`
2. Export it from `indicators/sources/__init__.py`
3. Instantiate it in `main.py` and call `.check()` inside `run_checks()`
