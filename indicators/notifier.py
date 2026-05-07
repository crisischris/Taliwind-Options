import subprocess
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Alert:
    title: str
    message: str
    subtitle: str = ""


def send_alert(alert: Alert) -> None:
    logger.info("Sending alert: %s — %s", alert.title, alert.message)
    cmd = ["terminal-notifier", "-title", alert.title, "-message", alert.message]
    if alert.subtitle:
        cmd += ["-subtitle", alert.subtitle]
    try:
        subprocess.run(cmd, check=True)
    except Exception as e:
        logger.error("Notification failed: %s", e)
