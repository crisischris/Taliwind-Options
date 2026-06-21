# Theme IDs — the canonical string values written into Signal.data["theme_id"]
# and used to name S3 report paths.
# Must match the `id:` field of each ThemeDefinition in frontend/src/constants/themes.ts.

MEAN_REVERSION    = "mean-reversion"
AI_MOMENTUM       = "ai-momentum"
BROKEN_MOMENTUM   = "broken-momentum"
VALUATION_GRAVITY = "valuation-gravity"
BREAKOUTS         = "52-week-breakouts"
SHORT_SQUEEZE     = "short-squeeze"
SECTOR_ROTATION   = "sector-rotation"
DRAM_MEMORY       = "dram-memory"
SPACE             = "space"

# Option data field names — must match the property names in frontend/src/types/report.ts
# and the `key:` values in frontend/src/constants/strings.ts column definitions.
BREAKEVEN_DROP = "breakeven_drop_pct"
BREAKEVEN_RISE = "breakeven_rise_pct"
