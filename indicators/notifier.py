import subprocess
import logging
from dataclasses import dataclass

from .config import config

logger = logging.getLogger(__name__)


@dataclass
class Alert:
    title: str
    message: str
    subtitle: str = ""


def _notify_mac(alert: Alert) -> None:
    cmd = ["terminal-notifier", "-title", alert.title, "-message", alert.message]
    if alert.subtitle:
        cmd += ["-subtitle", alert.subtitle]
    subprocess.run(cmd, check=True)


def _notify_sms(alert: Alert) -> None:
    try:
        from twilio.rest import Client  # type: ignore
    except ImportError:
        logger.error("Twilio not installed. Run: pip install twilio")
        return

    client = Client(config.twilio_account_sid, config.twilio_auth_token)
    body = f"{alert.title}: {alert.message}"
    if alert.subtitle:
        body = f"{alert.title} ({alert.subtitle}): {alert.message}"

    client.messages.create(
        body=body,
        from_=config.twilio_from_number,
        to=config.twilio_to_number,
    )
    logger.info("SMS sent to %s", config.twilio_to_number)


def send_alert(alert: Alert) -> None:
    via = config.notify_via
    logger.info("Sending alert [%s]: %s — %s", via, alert.title, alert.message)

    if via in ("mac", "both"):
        try:
            _notify_mac(alert)
        except Exception as e:
            logger.error("Mac notification failed: %s", e)

    if via in ("sms", "both"):
        try:
            _notify_sms(alert)
        except Exception as e:
            logger.error("SMS notification failed: %s", e)
