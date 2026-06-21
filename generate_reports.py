#!/usr/bin/env python3
"""
Generate local test reports for all themes.

Usage:
    python generate_reports.py           # all themes
    python generate_reports.py puts      # put themes only
    python generate_reports.py calls     # call themes only
    python generate_reports.py mean-reversion broken-momentum  # specific themes
"""
from __future__ import annotations

import logging
import sys

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
log = logging.getLogger(__name__)


def run_scanner(name: str, scanner_cls, page: str) -> None:
    from tailwind_options.report import write_theme_report_locally

    log.info("Running %s...", name)
    try:
        signals = [s for s in scanner_cls().check() if s.triggered]
        if not signals:
            log.info("%s: no signals", name)
            return
        write_theme_report_locally(signals, page, name)
        log.info("%s: %d signals written", name, len(signals))
    except Exception:
        log.exception("%s: scanner failed", name)


ALL_SCANNERS: list[tuple[str, str, str]] = [
    # (theme_id, module.ClassName, page)
    ("mean-reversion",   "tailwind_options.sources.gainer_puts.GainerPutScanner",          "puts"),
    ("broken-momentum",  "tailwind_options.sources.broken_momentum.BrokenMomentumScanner", "puts"),
    ("valuation-gravity","tailwind_options.sources.valuation_gravity.ValuationGravityScanner", "puts"),
    ("ai-momentum",      "tailwind_options.sources.trend_calls.TrendCallScanner",          "calls"),
    ("52-week-breakouts","tailwind_options.sources.breakout_calls.BreakoutCallScanner",     "calls"),
    ("short-squeeze",    "tailwind_options.sources.short_squeeze_calls.ShortSqueezeCallScanner", "calls"),
    ("sector-rotation",  "tailwind_options.sources.sector_rotation_calls.SectorRotationCallScanner", "calls"),
]


def import_class(dotted: str):
    module_path, class_name = dotted.rsplit(".", 1)
    import importlib
    mod = importlib.import_module(module_path)
    return getattr(mod, class_name)


def main() -> None:
    args = sys.argv[1:]

    if not args:
        targets = ALL_SCANNERS
    elif args[0] == "puts":
        targets = [(t, m, p) for t, m, p in ALL_SCANNERS if p == "puts"]
    elif args[0] == "calls":
        targets = [(t, m, p) for t, m, p in ALL_SCANNERS if p == "calls"]
    else:
        requested = set(args)
        targets = [(t, m, p) for t, m, p in ALL_SCANNERS if t in requested]
        unknown = requested - {t for t, *_ in targets}
        if unknown:
            log.error("Unknown theme(s): %s", ", ".join(sorted(unknown)))
            sys.exit(1)

    if not targets:
        log.error("No matching scanners found")
        sys.exit(1)

    log.info("Running %d scanner(s): %s", len(targets), ", ".join(t for t, *_ in targets))
    for theme_id, module_class, page in targets:
        run_scanner(theme_id, import_class(module_class), page)

    log.info("Done. Open http://localhost:5173/ to view reports.")


if __name__ == "__main__":
    main()
