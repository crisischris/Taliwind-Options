from __future__ import annotations

import logging
from zoneinfo import ZoneInfo

import exchange_calendars as xcals
import pandas as pd
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger(__name__)

scheduler = BlockingScheduler(timezone="America/New_York")

_ET = ZoneInfo("America/New_York")
_nyse = xcals.get_calendar("XNYS")


def is_market_open() -> bool:
    return _nyse.is_open_at_time(pd.Timestamp.now(tz="America/New_York"))


def register_daily(func) -> None:
    """Register a job to run once daily at 9:35 AM ET on trading days."""
    def guarded() -> None:
        if not is_market_open():
            logger.debug("Market closed — skipping '%s'", func.__name__)
            return
        func()

    guarded.__name__ = func.__name__

    scheduler.add_job(
        guarded,
        trigger=CronTrigger(hour=9, minute=35, day_of_week="mon-fri", timezone=_ET),
        name=func.__name__,
        max_instances=1,
        coalesce=True,
    )
    logger.info("Registered daily job '%s' at 09:35 ET (NYSE trading days only)", func.__name__)


def start() -> None:
    logger.info("Scheduler starting — press Ctrl+C to stop")
    scheduler.start()
