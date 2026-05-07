from __future__ import annotations

import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger

from .config import config

logger = logging.getLogger(__name__)

scheduler = BlockingScheduler(timezone="America/New_York")


def register(func, *, minutes: int | None = None) -> None:
    interval = minutes or config.check_interval_minutes
    scheduler.add_job(
        func,
        trigger=IntervalTrigger(minutes=interval),
        name=func.__name__,
        max_instances=1,
        coalesce=True,
    )
    logger.info("Registered job '%s' every %d min", func.__name__, interval)


def start() -> None:
    logger.info("Scheduler starting — press Ctrl+C to stop")
    scheduler.start()
