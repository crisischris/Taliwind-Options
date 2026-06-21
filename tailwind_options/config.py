import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class ScannerOpts:
    """Standard option-chain scanning parameters shared by every scanner."""
    min_dte:      int
    max_dte:      int
    min_oi:       int
    max_cost_pct: float
    max_iv:       float


def _opts(
    prefix: str,
    *,
    min_dte: int,
    max_dte: int,
    min_oi: int = 10,
    max_cost_pct: float = 0.05,
    max_iv: float = 1.50,
) -> ScannerOpts:
    p = prefix.upper()
    return ScannerOpts(
        min_dte=      int(os.getenv(f"{p}_MIN_DTE",      str(min_dte))),
        max_dte=      int(os.getenv(f"{p}_MAX_DTE",      str(max_dte))),
        min_oi=       int(os.getenv(f"{p}_MIN_OI",       str(min_oi))),
        max_cost_pct= float(os.getenv(f"{p}_MAX_COST_PCT", str(max_cost_pct))),
        max_iv=       float(os.getenv(f"{p}_MAX_IV",       str(max_iv))),
    )


class Config:
    # Gainer put scanner
    gainer_min_gain_pct:    float = float(os.getenv("GAINER_MIN_GAIN_PCT",    "500"))
    gainer_cache_floor_pct: float = float(os.getenv("GAINER_CACHE_FLOOR_PCT", "100"))
    gainer_put: ScannerOpts = _opts("GAINER_PUT", min_dte=60,  max_dte=1000, max_cost_pct=0.05, max_iv=2.00)

    # Trend call scanner (ARK ETF momentum plays)
    trend_call_momentum_min_pct: float = float(os.getenv("TREND_CALL_MOMENTUM_MIN_PCT", "15"))
    trend_call_momentum_days:    int   = int(os.getenv("TREND_CALL_MOMENTUM_DAYS",    "90"))
    trend_call: ScannerOpts = _opts("TREND_CALL", min_dte=60, max_dte=365, max_cost_pct=0.04, max_iv=1.50)

    # Broken momentum put scanner
    broken_mom: ScannerOpts = _opts("BROKEN_MOM", min_dte=60, max_dte=365, max_cost_pct=0.05, max_iv=1.50)

    # Valuation gravity put scanner
    val_gravity_min_ps:             float = float(os.getenv("VAL_GRAVITY_MIN_PS",             "15.0"))
    val_gravity_max_revenue_growth: float = float(os.getenv("VAL_GRAVITY_MAX_REVENUE_GROWTH", "0.30"))
    val_gravity_min_op_margin:      float = float(os.getenv("VAL_GRAVITY_MIN_OP_MARGIN",      "-0.30"))
    val_gravity: ScannerOpts = _opts("VAL_GRAVITY", min_dte=90, max_dte=730, max_cost_pct=0.05, max_iv=1.80)

    # 52-week breakout call scanner
    breakout_max_pct_from_high: float = float(os.getenv("BREAKOUT_MAX_PCT_FROM_HIGH", "0.02"))
    breakout_min_volume_ratio:  float = float(os.getenv("BREAKOUT_MIN_VOLUME_RATIO",  "1.5"))
    breakout: ScannerOpts = _opts("BREAKOUT", min_dte=30, max_dte=365, max_cost_pct=0.04, max_iv=1.20)

    # Short squeeze call scanner
    squeeze_min_short_float_pct: float = float(os.getenv("SQUEEZE_MIN_SHORT_FLOAT_PCT", "15.0"))
    squeeze_min_momentum_pct:    float = float(os.getenv("SQUEEZE_MIN_MOMENTUM_PCT",    "10.0"))
    squeeze_momentum_days:       int   = int(os.getenv("SQUEEZE_MOMENTUM_DAYS",       "30"))
    squeeze: ScannerOpts = _opts("SQUEEZE", min_dte=30, max_dte=365, max_cost_pct=0.04, max_iv=1.50)

    # Sector rotation call scanner
    rotation_min_outperform_pct: float = float(os.getenv("ROTATION_MIN_OUTPERFORM_PCT", "5.0"))
    rotation_momentum_days:      int   = int(os.getenv("ROTATION_MOMENTUM_DAYS",      "30"))
    rotation_top_pct:            float = float(os.getenv("ROTATION_TOP_PCT",           "0.20"))
    rotation: ScannerOpts = _opts("ROTATION", min_dte=45, max_dte=365, max_cost_pct=0.04, max_iv=1.30)

    # DRAM / memory call scanner
    dram_momentum_min_pct: float = float(os.getenv("DRAM_MOMENTUM_MIN_PCT", "10.0"))
    dram_momentum_days:    int   = int(os.getenv("DRAM_MOMENTUM_DAYS",    "30"))
    dram: ScannerOpts = _opts("DRAM", min_dte=30, max_dte=365, max_cost_pct=0.05, max_iv=2.00)

    # Space call scanner
    space_momentum_min_pct: float = float(os.getenv("SPACE_MOMENTUM_MIN_PCT", "10.0"))
    space_momentum_days:    int   = int(os.getenv("SPACE_MOMENTUM_DAYS",    "30"))
    space: ScannerOpts = _opts("SPACE", min_dte=30, max_dte=365, max_cost_pct=0.05, max_iv=2.50)


config = Config()
