# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
pip install -e .

# Invoke the scanner locally (runs a full scan, no S3 write)
python -c "
from indicators.sources.gainer_puts import GainerPutScanner
signals = [s for s in GainerPutScanner().check() if s.triggered]
print(f'{len(signals)} signals found')
"

# Run the React dev server (proxies JSON reports from the Python server)
# Terminal 1: python -m http.server 8765 --directory reports/
# Terminal 2: cd frontend && npm run dev
```

There are no tests or linter configs yet.

## Architecture

This is a Lambda-based scanner that runs twice daily (9:35 AM and midday ET), finds S&P 500 / NASDAQ 100 tickers with extreme YTD gains, surfaces cheap OTM puts on those tickers, and writes a JSON report to S3. A React static site reads those reports.

**Entry point — `lambda_handler.py`**
AWS Lambda handler. Loads SSM secrets, runs the scanner, writes JSON to S3.

**Core abstractions (`indicators/sources/base.py`)**
- `Indicator` — abstract base class; subclasses implement `check() -> list[Signal]`
- `Signal` — dataclass returned by `check()`; has `triggered`, `title`, `message`, `subtitle`, `data`

**Scanner (`indicators/sources/gainer_puts.py`)**
- `GainerPutScanner` — fetches 1-year history for the universe, finds gainers above threshold, scans option chains for qualifying puts, scores by return × prob ITM

**Reports (`indicators/report.py`)**
- `_build_report(signals, report_id, timestamp)` — builds the JSON structure written to S3
- Locally: `generate_and_open(signals)` writes JSON to `reports/` and opens the dev server

**Config (`indicators/config.py`)**
- All settings read from env vars. Key vars: `GAINER_MIN_GAIN_PCT`, `GAINER_PUT_MAX_COST_PCT`, `GAINER_PUT_MAX_IV`, `GAINER_PUT_MIN_OI`, `GAINER_PUT_MIN_DTE`, `GAINER_PUT_MAX_DTE`

**Frontend (`frontend/`)**
- Vite + React + TypeScript + Tailwind + DaisyUI
- `npm run dev` for local dev (proxies JSON from `:8765`)
- `npm run build` outputs to `frontend/dist/` which CDK deploys to S3

**Infrastructure (`infra/`)**
- CDK stack: Lambda (Python 3.12), EventBridge cron (twice daily), S3 static site, SSM secrets

## Adding a new indicator

1. Create `indicators/sources/myindicator.py` — subclass `Indicator`, implement `check() -> list[Signal]`
2. Export it from `indicators/sources/__init__.py`
3. Call it in `lambda_handler.py`
