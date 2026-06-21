# Tailwind Options — Theme Roadmap

Each theme maps to a scanner that finds a specific type of asymmetric options play. Themes appear in the UI under the Puts or Calls report pages. Users select a theme to see the relevant thesis and scanner rules.

## Status key

| Status | Meaning |
|--------|---------|
| ✅ Live | Scanner is built and wired into the Lambda handler |
| 🔧 Ready to build | All required data is available via yfinance; scanner not yet written |

---

## Put Themes

### ✅ Mean Reversion
**Data:** yfinance price history (1Y) — already in production  
**Signal:** S&P 500 / NASDAQ 100 names up 500%+ over the trailing year  
**Thesis:** Options markets chronically underprice downside on extreme gainers. Cheap OTM puts offer asymmetric payoff if the mean-reversion thesis plays out.

**Key rules:**
- Universe: S&P 500 + NASDAQ 100
- 500%+ gain over trailing 12 months
- OTM puts, 60–1,000 DTE
- Ask ≤ 5% of stock price, IV ≤ 200%
- Scored by return multiple × prob ITM

---

### ✅ Broken Momentum
**Data:** `yf.Ticker.info` — `fiftyTwoWeekHigh`, `regularMarketVolume`, `averageVolume`; `yf.download` for daily OHLCV  
**Signal:** Former 52-week high makers now 20%+ below peak, with distribution volume pattern  
**Thesis:** Stocks that were recently leaders but are now in quiet institutional distribution offer cheap put setups — the thesis has price confirmation already.

**Key rules:**
- Universe: S&P 500 + NASDAQ 100
- Made a 52-week high in the past 180 days
- Currently 20%+ below the trailing 52-week high
- Down-day average volume > up-day average volume over the past 20 sessions
- OTM puts, 60–365 DTE
- Ask ≤ 5% of stock price, IV ≤ 150%
- Scored by return multiple × prob ITM

**To build:** `tailwind_options/sources/broken_momentum.py` — subclass `Indicator`, use `yf.download` for 20-day OHLCV, compute 52W high from `info['fiftyTwoWeekHigh']`, filter on volume pattern.

---

### ✅ Valuation Gravity
**Data:** `yf.Ticker.info` — `priceToSalesTrailing12Months`, `revenueGrowth`, `operatingMargins`  
**Signal:** High P/S names with decelerating revenue growth  
**Thesis:** The market is slow to reprice deteriorating growth stories. Expensive stocks at 15x+ revenue with declining growth are compression setups — small premium, large payoff on a re-rating.

**Key rules:**
- Universe: S&P 500 + NASDAQ 100
- Price-to-sales > 15x (trailing 12 months)
- Year-over-year revenue growth positive but declining (market still pricing in growth)
- Operating margin > -30% (excludes distressed names — we want compression, not insolvency)
- OTM puts, 90–730 DTE (LEAPs preferred — this is a slow thesis)
- Ask ≤ 5% of stock price, IV ≤ 180%
- Scored by return multiple × prob ITM

**To build:** `tailwind_options/sources/valuation_gravity.py` — fetch `info` dict for universe, filter on P/S and `revenueGrowth`, scan options chain.

---

---

## Call Themes

### ✅ AI Momentum
**Data:** yfinance ETF holdings + 90-day price history — already in production  
**Signal:** Names in ARKK, ARKX, ARKQ, SMH, AIQ, BOTZ, ROKT with 15%+ 90-day momentum  
**Thesis:** Thematic ETF names with live momentum are the cheapest way to get exposure to structural AI and tech tailwinds. Cheap OTM calls are trend-continuation bets.

**Key rules:**
- Universe: ARKK, ARKX, ARKQ, SMH, AIQ, BOTZ, ROKT holdings
- 15%+ momentum over trailing 90 days
- OTM calls, 60–365 DTE
- Ask ≤ 4% of stock price, IV ≤ 150%
- Scored by return multiple × prob ITM

---

### ✅ 52-Week Breakouts
**Data:** `yf.Ticker.info` — `fiftyTwoWeekHigh`, `regularMarketVolume`, `averageVolume10days`  
**Signal:** S&P 500 / NASDAQ 100 names within 2% of their 52-week high with volume > 1.5× 20-day average  
**Thesis:** Resistance becomes support. Stocks breaking to new highs on volume are entering price discovery — momentum accelerates once overhead supply is cleared.

**Key rules:**
- Universe: S&P 500 + NASDAQ 100
- Within 2% of 52-week high
- Today's volume ≥ 1.5× 20-day average volume
- OTM calls, 30–180 DTE
- Ask ≤ 4% of stock price, IV ≤ 120%
- Scored by return multiple × prob ITM

**To build:** `tailwind_options/sources/breakout_calls.py` — fetch `info` for universe, filter on `fiftyTwoWeekHigh` proximity and volume ratio, scan options chain.

---

### ✅ Short Squeeze
**Data:** `yf.Ticker.info` — `shortPercentOfFloat`; `yf.download` for 30-day price history  
**Signal:** High short interest (>15% of float) names with positive 30-day momentum  
**Thesis:** Heavily-shorted stocks that start moving up force short sellers to cover, amplifying the move. Cheap OTM calls on names where the squeeze has started offer asymmetric payoff if it accelerates.

**Key rules:**
- Universe: S&P 500 + NASDAQ 100
- Short interest > 15% of float
- 10%+ price momentum over trailing 30 days (squeeze must already be in motion)
- OTM calls, 30–90 DTE (squeezes move fast — shorter-dated options preferred)
- Ask ≤ 4% of stock price, IV ≤ 150%
- Scored by return multiple × prob ITM

**To build:** `tailwind_options/sources/short_squeeze_calls.py` — fetch `info['shortPercentOfFloat']`, combine with 30-day momentum from `yf.download`, scan options chain.

---

### ✅ Sector Rotation
**Data:** yfinance sector ETF holdings + 30-day price history for sector ETFs and their constituents  
**Signal:** Names in outperforming sectors (sector ETF beating SPY by 5%+ over 30 days) that are also top-20% performers within that sector  
**Thesis:** Capital rotation amplifies moves in sector leaders disproportionately. Cheap OTM calls on the top individual names in live-rotation sectors capture macro tailwinds with individual-stock leverage.

**Key rules:**
- Universe: XLK (tech), XLE (energy), XLF (financials), XLI (industrials), XLV (healthcare), XLY (consumer discretionary) holdings
- Sector ETF must outperform SPY by ≥ 5% over trailing 30 days
- Individual name must rank in top 20% of sector by 30-day relative strength
- OTM calls, 45–180 DTE
- Ask ≤ 4% of stock price, IV ≤ 130%
- Scored by return multiple × prob ITM

**To build:** `tailwind_options/sources/sector_rotation_calls.py` — fetch sector ETF holdings and SPY/sector 30-day returns, filter leaders, scan options chain. Pattern closely mirrors `trend_calls.py`.

---

---

## Build priority

| Priority | Theme | Effort | Notes |
|----------|-------|--------|-------|
| 1 | Broken Momentum (puts) | Low | Straightforward extension of existing put scanner |
| 2 | 52-Week Breakouts (calls) | Low | Straightforward extension of existing call scanner |
| 3 | Valuation Gravity (puts) | Low | Uses `info` dict; no price history download needed |
| 4 | Short Squeeze (calls) | Medium | Uses `shortPercentOfFloat` + momentum; similar to AI Momentum |
| 5 | Sector Rotation (calls) | Medium | Most complex — needs SPY RS calc across sector ETFs |
