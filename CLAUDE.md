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

# Python: lint + unit tests (run both before pushing)
ruff check .
ruff format .
python -m pytest tests/

# Integration tests (require deployed beta + AWS credentials)
pip install -e . boto3 pytest
pytest tests/integration/ -v --override-ini="addopts=" --tb=short

# Frontend: full CI check — type-check, lint, and tests (run before pushing)
cd frontend && npm run ci

# Run the React dev server (proxies JSON reports from the Python server)
# Terminal 1: python -m http.server 8765 --directory reports/
# Terminal 2: cd frontend && npm run dev

# Format frontend
cd frontend && npx prettier --write .
```

## Architecture

This is a Lambda-based scanner that runs daily at 9:31 AM ET (prod only), finds S&P 500 / NASDAQ 100 tickers with extreme YTD gains, surfaces cheap OTM puts on those tickers, and writes a JSON report to S3. A React static site reads those reports.

**Entry point — `lambda_handler.py`**
AWS Lambda handler. Runs the scanner, writes JSON report + manifest to S3. Uses `context.aws_request_id` prefixed on every log line for CloudWatch querying.

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
- Vite + React + TypeScript + Tailwind + shadcn/ui
- `npm run dev` for local dev (proxies JSON from `:8765`)
- `npm run build` outputs to `frontend/dist/` which CDK deploys to S3

**Infrastructure (`infra/`)**
- `stage_config.py` — `StageConfig` dataclass, single source of truth for per-stage naming
- CDK stack: Lambda (Python 3.12), EventBridge Scheduler (prod only, 9:31 AM ET), S3 static site
- Deploy with: `cdk deploy -c stage=beta` or `cdk deploy -c stage=prod`
- CI/CD: GitHub Actions pipeline — beta deploy → integration tests → prod deploy on push to `main`

## Adding a new indicator

1. Create `indicators/sources/myindicator.py` — subclass `Indicator`, implement `check() -> list[Signal]`
2. Export it from `indicators/sources/__init__.py`
3. Call it in `lambda_handler.py`

---

## Style Guide

### Python

- **Formatter**: `ruff format` (configured in `pyproject.toml`)
- **Linter**: `ruff check` — rules: E, F, I (isort), UP (pyupgrade), N (naming)
- **Naming**: `snake_case` for variables/functions/modules, `PascalCase` for classes, `UPPER_SNAKE` for module-level constants
- **Type hints**: required on all function signatures. Use `Any` for boto3 clients and Lambda context. Use `list[T]` not `List[T]`.
- **Imports**: stdlib → third-party → local, each group alphabetically. No implicit relative imports.
- **Line length**: 100 characters

### TypeScript / React

- **Formatter**: Prettier (`frontend/.prettierrc`) — single quotes, no semicolons, 100 char width
- **Components**: PascalCase filenames and function names. Default export name must match filename.
- **Hooks**: `camelCase`, prefixed with `use`
- **Imports**: external packages first, then `@/` absolute internal imports. No relative `./` imports for components — use `@/components/...` consistently.
- **Strings**: all user-facing strings live in `frontend/src/constants/strings.ts`. No hardcoded UI text in components.
- **State**: consolidate related boolean states into a single object rather than N separate `useState` calls.
- **shadcn/ui**: always use shadcn components. Do not introduce new UI libraries without discussion.

### General

- No comments unless the WHY is non-obvious
- No dead code — delete unused exports, components, and constants immediately
- No `console.log` or debug prints committed
