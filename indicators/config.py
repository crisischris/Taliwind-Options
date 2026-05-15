import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    # Gainer put scanner
    gainer_min_gain_pct: float = float(os.getenv("GAINER_MIN_GAIN_PCT", "500"))
    gainer_cache_floor_pct: float = float(os.getenv("GAINER_CACHE_FLOOR_PCT", "100"))
    gainer_put_max_cost_pct: float = float(os.getenv("GAINER_PUT_MAX_COST_PCT", "0.05"))
    gainer_put_max_iv: float = float(os.getenv("GAINER_PUT_MAX_IV", "2.00"))
    gainer_put_min_oi: int = int(os.getenv("GAINER_PUT_MIN_OI", "10"))
    gainer_put_min_dte: int = int(os.getenv("GAINER_PUT_MIN_DTE", "60"))
    gainer_put_max_dte: int = int(os.getenv("GAINER_PUT_MAX_DTE", "1000"))

    # Trend call scanner (ARK ETF momentum plays)
    trend_call_momentum_min_pct: float = float(os.getenv("TREND_CALL_MOMENTUM_MIN_PCT", "15"))
    trend_call_momentum_days: int = int(os.getenv("TREND_CALL_MOMENTUM_DAYS", "90"))
    trend_call_max_cost_pct: float = float(os.getenv("TREND_CALL_MAX_COST_PCT", "0.04"))
    trend_call_max_iv: float = float(os.getenv("TREND_CALL_MAX_IV", "1.50"))
    trend_call_min_oi: int = int(os.getenv("TREND_CALL_MIN_OI", "10"))
    trend_call_min_dte: int = int(os.getenv("TREND_CALL_MIN_DTE", "60"))
    trend_call_max_dte: int = int(os.getenv("TREND_CALL_MAX_DTE", "365"))


config = Config()
