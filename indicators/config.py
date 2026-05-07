import os
from dotenv import load_dotenv

load_dotenv()


def _get_list(key: str, default: str = "") -> list[str]:
    raw = os.getenv(key, default)
    return [item.strip() for item in raw.split(",") if item.strip()]


class Config:
    check_interval_minutes: int = int(os.getenv("CHECK_INTERVAL_MINUTES", "15"))
    notify_via: str = os.getenv("NOTIFY_VIA", "mac").lower()
    watchlist: list[str] = _get_list("WATCHLIST", "SPY")

    # Twilio
    twilio_account_sid: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    twilio_auth_token: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    twilio_from_number: str = os.getenv("TWILIO_FROM_NUMBER", "")
    twilio_to_number: str = os.getenv("TWILIO_TO_NUMBER", "")

    # Alpha Vantage
    alpha_vantage_api_key: str = os.getenv("ALPHA_VANTAGE_API_KEY", "")


config = Config()
