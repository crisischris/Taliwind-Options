#!/usr/bin/env python3
"""Generate mock reports for all 5 new themes for local UI testing."""
from __future__ import annotations

import sys
sys.path.insert(0, ".")

from tailwind_options.sources.base import Signal
from tailwind_options.report import write_theme_report_locally


def sig(data: dict) -> Signal:
    return Signal(triggered=True, title="", subtitle="", message="", data=data)


def put(ticker, theme_id, move_pct, move_label, current_price, contract, term,
        expiry, strike, ask, iv, oi, volume, breakeven_drop_pct, return_multiple, prob_itm):
    score = return_multiple * prob_itm
    return sig({
        "ticker": ticker, "theme_id": theme_id,
        "move_pct": move_pct, "move_label": move_label,
        "current_price": current_price,
        "contract": contract, "term": term, "expiry": expiry,
        "strike": strike, "ask": ask, "iv": iv,
        "open_interest": oi, "volume": volume,
        "breakeven_drop_pct": breakeven_drop_pct,
        "return_multiple": return_multiple, "prob_itm": prob_itm, "score": score,
    })


def call(ticker, theme_id, move_pct, move_label, current_price, contract, term,
         expiry, strike, ask, iv, oi, volume, breakeven_rise_pct, return_multiple, prob_itm):
    score = return_multiple * prob_itm
    return sig({
        "ticker": ticker, "theme_id": theme_id,
        "move_pct": move_pct, "move_label": move_label,
        "current_price": current_price,
        "contract": contract, "term": term, "expiry": expiry,
        "strike": strike, "ask": ask, "iv": iv,
        "open_interest": oi, "volume": volume,
        "breakeven_rise_pct": breakeven_rise_pct,
        "return_multiple": return_multiple, "prob_itm": prob_itm, "score": score,
    })


# ── Broken Momentum (puts) ───────────────────────────────────────────────────
# Former 52W-high leaders now 20%+ below peak, distribution volume pattern.
# move_pct = -drawdown_pct (negative), move_label = "from peak"

broken_momentum_signals = [
    # SHOP — $55.40, 52W high $89.20 → down 37.9%
    put("SHOP","broken-momentum",-37.9,"from peak",55.40, "SHOP260717P00035000","short","2026-07-17",35.0,1.05,0.82,312,28,36.8,33.3,0.087),
    put("SHOP","broken-momentum",-37.9,"from peak",55.40, "SHOP260717P00040000","short","2026-07-17",40.0,1.55,0.79,890,142,25.3,25.8,0.119),
    put("SHOP","broken-momentum",-37.9,"from peak",55.40, "SHOP260717P00030000","short","2026-07-17",30.0,0.68,0.87,204,11,46.5,44.1,0.058),
    put("SHOP","broken-momentum",-37.9,"from peak",55.40, "SHOP260717P00042000","short","2026-07-17",42.0,1.85,0.78,156,35,22.3,22.7,0.132),
    put("SHOP","broken-momentum",-37.9,"from peak",55.40, "SHOP260717P00038000","short","2026-07-17",38.0,1.28,0.80,478,67,29.2,29.7,0.103),
    put("SHOP","broken-momentum",-37.9,"from peak",55.40, "SHOP261120P00025000","long","2026-11-20",25.0,0.92,0.91,531,8,54.9,27.2,0.051),
    put("SHOP","broken-momentum",-37.9,"from peak",55.40, "SHOP261120P00030000","long","2026-11-20",30.0,1.42,0.88,714,22,46.5,21.1,0.072),
    put("SHOP","broken-momentum",-37.9,"from peak",55.40, "SHOP261120P00035000","long","2026-11-20",35.0,2.15,0.85,389,14,37.8,16.3,0.098),
    put("SHOP","broken-momentum",-37.9,"from peak",55.40, "SHOP261120P00020000","long","2026-11-20",20.0,0.65,0.95,278,4,63.1,30.8,0.038),
    put("SHOP","broken-momentum",-37.9,"from peak",55.40, "SHOP260717P00015000","moonshot","2026-07-17",15.0,0.08,1.22,1840,310,72.9,187.5,0.013),
    put("SHOP","broken-momentum",-37.9,"from peak",55.40, "SHOP260717P00012000","moonshot","2026-07-17",12.0,0.05,1.31,920,87,78.2,240.0,0.011),
    put("SHOP","broken-momentum",-37.9,"from peak",55.40, "SHOP260717P00018000","moonshot","2026-07-17",18.0,0.12,1.18,603,45,67.5,150.0,0.018),

    # ROKU — $52.80, 52W high $84.50 → down 37.5%
    put("ROKU","broken-momentum",-37.5,"from peak",52.80, "ROKU260717P00032000","short","2026-07-17",32.0,0.98,0.88,445,56,39.4,32.7,0.092),
    put("ROKU","broken-momentum",-37.5,"from peak",52.80, "ROKU260717P00038000","short","2026-07-17",38.0,1.72,0.83,622,98,30.7,22.1,0.131),
    put("ROKU","broken-momentum",-37.5,"from peak",52.80, "ROKU260717P00035000","short","2026-07-17",35.0,1.28,0.85,334,42,34.9,27.3,0.110),
    put("ROKU","broken-momentum",-37.5,"from peak",52.80, "ROKU260717P00028000","short","2026-07-17",28.0,0.72,0.92,189,17,46.2,38.9,0.073),
    put("ROKU","broken-momentum",-37.5,"from peak",52.80, "ROKU261120P00025000","long","2026-11-20",25.0,1.05,0.93,712,9,52.1,23.8,0.062),
    put("ROKU","broken-momentum",-37.5,"from peak",52.80, "ROKU261120P00030000","long","2026-11-20",30.0,1.65,0.89,501,21,43.8,18.2,0.083),
    put("ROKU","broken-momentum",-37.5,"from peak",52.80, "ROKU261120P00020000","long","2026-11-20",20.0,0.70,0.97,388,6,61.2,28.6,0.044),
    put("ROKU","broken-momentum",-37.5,"from peak",52.80, "ROKU260717P00010000","moonshot","2026-07-17",10.0,0.06,1.28,2140,420,80.9,166.7,0.012),
    put("ROKU","broken-momentum",-37.5,"from peak",52.80, "ROKU260717P00008000","moonshot","2026-07-17",8.0,0.04,1.35,870,189,84.8,200.0,0.010),

    # DKNG — $30.20, 52W high $48.60 → down 37.9%
    put("DKNG","broken-momentum",-37.9,"from peak",30.20, "DKNG260717P00020000","short","2026-07-17",20.0,0.58,0.91,567,88,34.4,34.5,0.095),
    put("DKNG","broken-momentum",-37.9,"from peak",30.20, "DKNG260717P00022000","short","2026-07-17",22.0,0.82,0.88,398,54,27.7,26.8,0.117),
    put("DKNG","broken-momentum",-37.9,"from peak",30.20, "DKNG260717P00018000","short","2026-07-17",18.0,0.42,0.94,234,31,40.7,42.9,0.074),
    put("DKNG","broken-momentum",-37.9,"from peak",30.20, "DKNG261120P00015000","long","2026-11-20",15.0,0.55,0.97,892,7,50.5,27.3,0.058),
    put("DKNG","broken-momentum",-37.9,"from peak",30.20, "DKNG261120P00017000","long","2026-11-20",17.0,0.78,0.94,456,12,44.2,21.8,0.073),
    put("DKNG","broken-momentum",-37.9,"from peak",30.20, "DKNG260717P00008000","moonshot","2026-07-17",8.0,0.05,1.29,1340,267,73.5,160.0,0.014),
    put("DKNG","broken-momentum",-37.9,"from peak",30.20, "DKNG260717P00006000","moonshot","2026-07-17",6.0,0.03,1.38,780,142,80.1,200.0,0.010),

    # LULU — $258.40, 52W high $420.10 → down 38.5%
    put("LULU","broken-momentum",-38.5,"from peak",258.40, "LULU260717P00170000","short","2026-07-17",170.0,5.80,0.72,289,33,35.9,29.3,0.083),
    put("LULU","broken-momentum",-38.5,"from peak",258.40, "LULU260717P00185000","short","2026-07-17",185.0,7.90,0.70,412,57,28.9,23.4,0.104),
    put("LULU","broken-momentum",-38.5,"from peak",258.40, "LULU260717P00160000","short","2026-07-17",160.0,4.50,0.74,178,19,41.0,35.6,0.068),
    put("LULU","broken-momentum",-38.5,"from peak",258.40, "LULU261120P00140000","long","2026-11-20",140.0,7.20,0.78,534,8,46.5,19.4,0.079),
    put("LULU","broken-momentum",-38.5,"from peak",258.40, "LULU261120P00155000","long","2026-11-20",155.0,9.40,0.75,367,14,40.7,16.5,0.093),
    put("LULU","broken-momentum",-38.5,"from peak",258.40, "LULU270115P00090000","long","2027-01-15",90.0,4.20,0.83,891,3,63.2,21.4,0.057),
    put("LULU","broken-momentum",-38.5,"from peak",258.40, "LULU260717P00060000","moonshot","2026-07-17",60.0,0.35,1.08,1240,210,76.9,171.4,0.016),
    put("LULU","broken-momentum",-38.5,"from peak",258.40, "LULU260717P00050000","moonshot","2026-07-17",50.0,0.22,1.15,780,87,80.7,227.3,0.011),
]

# ── Valuation Gravity (puts) ─────────────────────────────────────────────────
# High P/S (15x+) with decelerating revenue growth.
# move_pct = (ps/15 - 1)*100, move_label = "P/S premium"

valuation_gravity_signals = [
    # SNOW — $135.20, P/S ~18.0x → move_pct = (18/15-1)*100 = 20.0%
    put("SNOW","valuation-gravity",20.0,"P/S premium",135.20, "SNOW260717P00090000","short","2026-07-17",90.0,3.80,0.88,412,47,34.2,23.7,0.091),
    put("SNOW","valuation-gravity",20.0,"P/S premium",135.20, "SNOW260717P00100000","short","2026-07-17",100.0,5.10,0.84,689,98,22.2,19.6,0.118),
    put("SNOW","valuation-gravity",20.0,"P/S premium",135.20, "SNOW260717P00085000","short","2026-07-17",85.0,3.20,0.91,278,23,38.5,26.6,0.078),
    put("SNOW","valuation-gravity",20.0,"P/S premium",135.20, "SNOW260717P00080000","short","2026-07-17",80.0,2.70,0.93,195,14,42.5,29.6,0.065),
    put("SNOW","valuation-gravity",20.0,"P/S premium",135.20, "SNOW260717P00075000","short","2026-07-17",75.0,2.20,0.96,143,9,47.0,34.1,0.053),
    put("SNOW","valuation-gravity",20.0,"P/S premium",135.20, "SNOW261120P00075000","long","2026-11-20",75.0,4.50,0.92,823,12,41.4,16.7,0.089),
    put("SNOW","valuation-gravity",20.0,"P/S premium",135.20, "SNOW261120P00065000","long","2026-11-20",65.0,3.10,0.96,567,8,51.6,21.0,0.068),
    put("SNOW","valuation-gravity",20.0,"P/S premium",135.20, "SNOW261120P00085000","long","2026-11-20",85.0,6.20,0.89,445,17,33.9,13.7,0.103),
    put("SNOW","valuation-gravity",20.0,"P/S premium",135.20, "SNOW261218P00060000","long","2026-12-18",60.0,2.80,0.99,334,5,56.8,21.4,0.059),
    put("SNOW","valuation-gravity",20.0,"P/S premium",135.20, "SNOW270115P00050000","long","2027-01-15",50.0,2.90,1.01,1240,11,62.4,17.2,0.052),
    put("SNOW","valuation-gravity",20.0,"P/S premium",135.20, "SNOW260717P00030000","moonshot","2026-07-17",30.0,0.15,1.24,2890,534,78.1,200.0,0.012),
    put("SNOW","valuation-gravity",20.0,"P/S premium",135.20, "SNOW260717P00025000","moonshot","2026-07-17",25.0,0.09,1.31,1450,289,81.6,277.8,0.010),
    put("SNOW","valuation-gravity",20.0,"P/S premium",135.20, "SNOW270115P00025000","moonshot","2027-01-15",25.0,0.35,1.18,3420,78,74.3,71.4,0.015),

    # CRWD — $328.50, P/S ~22.0x → move_pct = (22/15-1)*100 = 46.7%
    put("CRWD","valuation-gravity",46.7,"P/S premium",328.50, "CRWD260717P00220000","short","2026-07-17",220.0,8.20,0.79,534,62,36.4,26.8,0.087),
    put("CRWD","valuation-gravity",46.7,"P/S premium",328.50, "CRWD260717P00240000","short","2026-07-17",240.0,11.40,0.76,712,109,23.5,21.1,0.112),
    put("CRWD","valuation-gravity",46.7,"P/S premium",328.50, "CRWD260717P00200000","short","2026-07-17",200.0,6.20,0.82,312,34,43.8,32.3,0.071),
    put("CRWD","valuation-gravity",46.7,"P/S premium",328.50, "CRWD260717P00210000","short","2026-07-17",210.0,7.10,0.80,423,48,40.2,29.6,0.079),
    put("CRWD","valuation-gravity",46.7,"P/S premium",328.50, "CRWD261120P00180000","long","2026-11-20",180.0,9.80,0.83,890,14,45.3,18.4,0.089),
    put("CRWD","valuation-gravity",46.7,"P/S premium",328.50, "CRWD261120P00160000","long","2026-11-20",160.0,7.90,0.86,634,9,51.6,20.3,0.076),
    put("CRWD","valuation-gravity",46.7,"P/S premium",328.50, "CRWD261120P00200000","long","2026-11-20",200.0,13.20,0.80,512,21,40.1,15.2,0.101),
    put("CRWD","valuation-gravity",46.7,"P/S premium",328.50, "CRWD270115P00140000","long","2027-01-15",140.0,8.50,0.89,1890,33,57.0,16.5,0.071),
    put("CRWD","valuation-gravity",46.7,"P/S premium",328.50, "CRWD260717P00080000","moonshot","2026-07-17",80.0,0.45,1.12,2340,456,75.5,177.8,0.014),
    put("CRWD","valuation-gravity",46.7,"P/S premium",328.50, "CRWD270115P00060000","moonshot","2027-01-15",60.0,0.65,1.08,1120,178,81.5,92.3,0.017),

    # ZS — $182.40, P/S ~16.5x → move_pct = (16.5/15-1)*100 = 10.0%
    put("ZS","valuation-gravity",10.0,"P/S premium",182.40, "ZS260717P00120000","short","2026-07-17",120.0,4.20,0.86,367,42,37.7,28.6,0.079),
    put("ZS","valuation-gravity",10.0,"P/S premium",182.40, "ZS260717P00130000","short","2026-07-17",130.0,5.60,0.83,489,68,29.5,23.2,0.097),
    put("ZS","valuation-gravity",10.0,"P/S premium",182.40, "ZS260717P00115000","short","2026-07-17",115.0,3.70,0.88,245,28,41.9,31.1,0.069),
    put("ZS","valuation-gravity",10.0,"P/S premium",182.40, "ZS261120P00100000","long","2026-11-20",100.0,5.80,0.90,712,9,47.0,17.2,0.085),
    put("ZS","valuation-gravity",10.0,"P/S premium",182.40, "ZS261120P00090000","long","2026-11-20",90.0,4.50,0.93,534,7,52.7,20.0,0.071),
    put("ZS","valuation-gravity",10.0,"P/S premium",182.40, "ZS270115P00075000","long","2027-01-15",75.0,4.20,0.96,890,12,59.0,17.9,0.060),
    put("ZS","valuation-gravity",10.0,"P/S premium",182.40, "ZS260717P00040000","moonshot","2026-07-17",40.0,0.20,1.19,1780,312,78.0,200.0,0.012),

    # DDOG — $128.60, P/S ~19.5x → move_pct = (19.5/15-1)*100 = 30.0%
    put("DDOG","valuation-gravity",30.0,"P/S premium",128.60, "DDOG260717P00085000","short","2026-07-17",85.0,3.50,0.84,423,51,33.8,24.3,0.088),
    put("DDOG","valuation-gravity",30.0,"P/S premium",128.60, "DDOG260717P00095000","short","2026-07-17",95.0,4.90,0.81,567,84,24.2,19.4,0.113),
    put("DDOG","valuation-gravity",30.0,"P/S premium",128.60, "DDOG260717P00080000","short","2026-07-17",80.0,2.90,0.87,289,32,38.8,27.6,0.073),
    put("DDOG","valuation-gravity",30.0,"P/S premium",128.60, "DDOG261120P00070000","long","2026-11-20",70.0,4.20,0.88,634,8,46.0,16.7,0.086),
    put("DDOG","valuation-gravity",30.0,"P/S premium",128.60, "DDOG261120P00060000","long","2026-11-20",60.0,3.10,0.92,478,6,53.3,19.4,0.069),
    put("DDOG","valuation-gravity",30.0,"P/S premium",128.60, "DDOG270115P00055000","long","2027-01-15",55.0,3.40,0.94,1120,14,57.0,16.2,0.061),
    put("DDOG","valuation-gravity",30.0,"P/S premium",128.60, "DDOG260717P00030000","moonshot","2026-07-17",30.0,0.12,1.22,2230,412,76.8,250.0,0.013),
    put("DDOG","valuation-gravity",30.0,"P/S premium",128.60, "DDOG260717P00025000","moonshot","2026-07-17",25.0,0.08,1.29,1340,234,80.5,312.5,0.010),
]

# ── 52-Week Breakouts (calls) ─────────────────────────────────────────────────
# Within 2% of 52W high, volume ≥ 1.5× 20-day avg.
# move_pct = (vol_ratio - 1)*100, move_label = "vol ratio"

breakout_calls_signals = [
    # AAPL — $204.80, 52W high $208.50 (within 1.8%), vol_ratio 1.87x → move_pct=87.0
    call("AAPL","52-week-breakouts",87.0,"vol ratio",204.80, "AAPL260619C00215000","short","2026-06-19",215.0,3.10,0.24,8920,1240,6.9,69.4,0.073),
    call("AAPL","52-week-breakouts",87.0,"vol ratio",204.80, "AAPL260619C00220000","short","2026-06-19",220.0,2.05,0.27,5678,892,8.9,102.4,0.053),
    call("AAPL","52-week-breakouts",87.0,"vol ratio",204.80, "AAPL260619C00225000","short","2026-06-19",225.0,1.35,0.30,3421,567,10.8,155.6,0.038),
    call("AAPL","52-week-breakouts",87.0,"vol ratio",204.80, "AAPL260619C00230000","short","2026-06-19",230.0,0.92,0.33,2134,389,12.8,228.3,0.027),
    call("AAPL","52-week-breakouts",87.0,"vol ratio",204.80, "AAPL260619C00210000","short","2026-06-19",210.0,5.20,0.22,12450,2340,4.7,40.4,0.105),
    call("AAPL","52-week-breakouts",87.0,"vol ratio",204.80, "AAPL260717C00225000","short","2026-07-17",225.0,2.80,0.29,4560,712,10.8,89.3,0.062),
    call("AAPL","52-week-breakouts",87.0,"vol ratio",204.80, "AAPL260717C00240000","short","2026-07-17",240.0,1.20,0.34,2340,412,18.0,208.3,0.034),
    call("AAPL","52-week-breakouts",87.0,"vol ratio",204.80, "AAPL261120C00240000","long","2026-11-20",240.0,4.80,0.28,6780,890,18.0,50.0,0.098),
    call("AAPL","52-week-breakouts",87.0,"vol ratio",204.80, "AAPL261120C00250000","long","2026-11-20",250.0,3.20,0.31,4230,534,24.8,78.1,0.072),
    call("AAPL","52-week-breakouts",87.0,"vol ratio",204.80, "AAPL261120C00260000","long","2026-11-20",260.0,2.10,0.34,2890,345,29.0,119.0,0.051),
    call("AAPL","52-week-breakouts",87.0,"vol ratio",204.80, "AAPL261218C00265000","long","2026-12-18",265.0,2.40,0.33,3120,289,31.3,104.2,0.056),
    call("AAPL","52-week-breakouts",87.0,"vol ratio",204.80, "AAPL260619C00300000","moonshot","2026-06-19",300.0,0.08,0.52,890,178,46.9,1250.0,0.014),
    call("AAPL","52-week-breakouts",87.0,"vol ratio",204.80, "AAPL260619C00320000","moonshot","2026-06-19",320.0,0.04,0.58,534,98,57.5,2500.0,0.010),

    # META — $588.40, 52W high $602.20 (within 2.3%), vol_ratio 2.12x → move_pct=112.0
    call("META","52-week-breakouts",112.0,"vol ratio",588.40, "META260619C00620000","short","2026-06-19",620.0,8.90,0.31,3456,478,5.4,69.7,0.083),
    call("META","52-week-breakouts",112.0,"vol ratio",588.40, "META260619C00640000","short","2026-06-19",640.0,5.40,0.34,2134,312,9.8,118.5,0.055),
    call("META","52-week-breakouts",112.0,"vol ratio",588.40, "META260619C00660000","short","2026-06-19",660.0,3.20,0.37,1234,189,12.9,200.0,0.037),
    call("META","52-week-breakouts",112.0,"vol ratio",588.40, "META260717C00650000","short","2026-07-17",650.0,7.80,0.35,4520,712,10.5,83.3,0.073),
    call("META","52-week-breakouts",112.0,"vol ratio",588.40, "META260717C00680000","short","2026-07-17",680.0,4.50,0.38,2780,423,15.8,151.1,0.048),
    call("META","52-week-breakouts",112.0,"vol ratio",588.40, "META261120C00680000","long","2026-11-20",680.0,15.60,0.32,5670,890,15.8,43.6,0.108),
    call("META","52-week-breakouts",112.0,"vol ratio",588.40, "META261120C00720000","long","2026-11-20",720.0,9.80,0.35,3420,567,22.5,73.5,0.079),
    call("META","52-week-breakouts",112.0,"vol ratio",588.40, "META261120C00760000","long","2026-11-20",760.0,6.20,0.38,2140,345,29.8,122.6,0.056),
    call("META","52-week-breakouts",112.0,"vol ratio",588.40, "META261218C00750000","long","2026-12-18",750.0,8.40,0.37,2890,412,28.1,89.3,0.063),
    call("META","52-week-breakouts",112.0,"vol ratio",588.40, "META260619C00800000","moonshot","2026-06-19",800.0,0.35,0.58,789,134,36.6,1714.3,0.015),
    call("META","52-week-breakouts",112.0,"vol ratio",588.40, "META260619C00900000","moonshot","2026-06-19",900.0,0.12,0.65,423,78,53.3,5000.0,0.010),

    # MSFT — $432.60, 52W high $441.20 (within 2.0%), vol_ratio 1.65x → move_pct=65.0
    call("MSFT","52-week-breakouts",65.0,"vol ratio",432.60, "MSFT260619C00450000","short","2026-06-19",450.0,5.60,0.22,6780,934,4.5,80.4,0.071),
    call("MSFT","52-week-breakouts",65.0,"vol ratio",432.60, "MSFT260619C00460000","short","2026-06-19",460.0,3.40,0.25,4230,623,6.8,132.4,0.051),
    call("MSFT","52-week-breakouts",65.0,"vol ratio",432.60, "MSFT260619C00470000","short","2026-06-19",470.0,2.10,0.28,2890,412,8.9,219.0,0.036),
    call("MSFT","52-week-breakouts",65.0,"vol ratio",432.60, "MSFT260717C00460000","short","2026-07-17",460.0,6.80,0.24,7890,1120,6.8,67.6,0.081),
    call("MSFT","52-week-breakouts",65.0,"vol ratio",432.60, "MSFT261120C00480000","long","2026-11-20",480.0,8.90,0.25,9870,1340,11.0,53.9,0.089),
    call("MSFT","52-week-breakouts",65.0,"vol ratio",432.60, "MSFT261120C00500000","long","2026-11-20",500.0,5.60,0.28,6780,890,15.8,89.3,0.064),
    call("MSFT","52-week-breakouts",65.0,"vol ratio",432.60, "MSFT261218C00510000","long","2026-12-18",510.0,6.20,0.27,5430,712,18.0,82.3,0.068),
    call("MSFT","52-week-breakouts",65.0,"vol ratio",432.60, "MSFT260619C00550000","moonshot","2026-06-19",550.0,0.18,0.42,2340,456,27.6,1388.9,0.013),

    # AMZN — $226.80, 52W high $231.40 (within 2.0%), vol_ratio 1.92x → move_pct=92.0
    call("AMZN","52-week-breakouts",92.0,"vol ratio",226.80, "AMZN260619C00240000","short","2026-06-19",240.0,2.80,0.26,7890,1120,5.8,85.7,0.068),
    call("AMZN","52-week-breakouts",92.0,"vol ratio",226.80, "AMZN260619C00250000","short","2026-06-19",250.0,1.60,0.29,5230,789,10.3,156.3,0.045),
    call("AMZN","52-week-breakouts",92.0,"vol ratio",226.80, "AMZN260619C00245000","short","2026-06-19",245.0,2.10,0.28,6450,934,8.0,116.7,0.056),
    call("AMZN","52-week-breakouts",92.0,"vol ratio",226.80, "AMZN260717C00255000","short","2026-07-17",255.0,2.90,0.30,8920,1340,12.7,89.7,0.062),
    call("AMZN","52-week-breakouts",92.0,"vol ratio",226.80, "AMZN261120C00260000","long","2026-11-20",260.0,5.80,0.28,11230,1670,14.7,43.1,0.098),
    call("AMZN","52-week-breakouts",92.0,"vol ratio",226.80, "AMZN261120C00275000","long","2026-11-20",275.0,3.60,0.31,7890,1120,21.4,76.4,0.071),
    call("AMZN","52-week-breakouts",92.0,"vol ratio",226.80, "AMZN261218C00280000","long","2026-12-18",280.0,4.20,0.30,8430,1230,23.9,66.7,0.075),
    call("AMZN","52-week-breakouts",92.0,"vol ratio",226.80, "AMZN260619C00320000","moonshot","2026-06-19",320.0,0.12,0.48,3240,567,41.5,1666.7,0.012),
    call("AMZN","52-week-breakouts",92.0,"vol ratio",226.80, "AMZN260619C00350000","moonshot","2026-06-19",350.0,0.05,0.55,1890,312,54.5,4000.0,0.010),
]

# ── Short Squeeze (calls) ────────────────────────────────────────────────────
# High short interest (>15% float) with 10%+ 30-day momentum.
# move_pct = short float %, move_label = "short float"

short_squeeze_signals = [
    # MRNA — $28.40, 18.3% short float, 30D momentum +14.2%
    call("MRNA","short-squeeze",18.3,"short float",28.40, "MRNA260619C00035000","short","2026-06-19",35.0,0.48,1.12,1890,342,23.2,72.9,0.073),
    call("MRNA","short-squeeze",18.3,"short float",28.40, "MRNA260619C00040000","short","2026-06-19",40.0,0.22,1.21,1120,234,41.5,159.1,0.041),
    call("MRNA","short-squeeze",18.3,"short float",28.40, "MRNA260619C00032000","short","2026-06-19",32.0,0.78,1.05,2560,489,12.7,41.0,0.105),
    call("MRNA","short-squeeze",18.3,"short float",28.40, "MRNA260717C00038000","short","2026-07-17",38.0,0.55,1.15,1340,267,34.5,69.1,0.062),
    call("MRNA","short-squeeze",18.3,"short float",28.40, "MRNA260717C00045000","short","2026-07-17",45.0,0.18,1.28,789,145,58.8,250.0,0.029),
    call("MRNA","short-squeeze",18.3,"short float",28.40, "MRNA260717C00050000","short","2026-07-17",50.0,0.09,1.35,534,98,76.4,555.6,0.014),
    call("MRNA","short-squeeze",18.3,"short float",28.40, "MRNA260619C00060000","moonshot","2026-06-19",60.0,0.03,1.48,890,178,111.3,2000.0,0.016),
    call("MRNA","short-squeeze",18.3,"short float",28.40, "MRNA260619C00080000","moonshot","2026-06-19",80.0,0.02,1.62,567,89,181.7,4000.0,0.010),
    call("MRNA","short-squeeze",18.3,"short float",28.40, "MRNA260717C00100000","moonshot","2026-07-17",100.0,0.03,1.55,423,67,252.1,3333.3,0.011),

    # ENPH — $62.80, 22.1% short float, 30D momentum +18.7%
    call("ENPH","short-squeeze",22.1,"short float",62.80, "ENPH260619C00075000","short","2026-06-19",75.0,0.92,1.08,1230,234,19.5,81.5,0.082),
    call("ENPH","short-squeeze",22.1,"short float",62.80, "ENPH260619C00085000","short","2026-06-19",85.0,0.45,1.15,789,145,35.5,188.9,0.045),
    call("ENPH","short-squeeze",22.1,"short float",62.80, "ENPH260619C00070000","short","2026-06-19",70.0,1.42,1.04,1780,345,11.5,49.3,0.112),
    call("ENPH","short-squeeze",22.1,"short float",62.80, "ENPH260717C00080000","short","2026-07-17",80.0,1.15,1.10,1120,212,27.9,69.6,0.068),
    call("ENPH","short-squeeze",22.1,"short float",62.80, "ENPH260717C00095000","short","2026-07-17",95.0,0.48,1.22,678,123,51.1,197.9,0.033),
    call("ENPH","short-squeeze",22.1,"short float",62.80, "ENPH260619C00120000","moonshot","2026-06-19",120.0,0.08,1.38,890,167,90.8,1500.0,0.018),
    call("ENPH","short-squeeze",22.1,"short float",62.80, "ENPH260619C00150000","moonshot","2026-06-19",150.0,0.03,1.52,534,89,139.0,5000.0,0.010),

    # PAYC — $158.20, 16.8% short float, 30D momentum +11.3%
    call("PAYC","short-squeeze",16.8,"short float",158.20, "PAYC260619C00180000","short","2026-06-19",180.0,2.10,0.92,890,167,13.8,85.7,0.067),
    call("PAYC","short-squeeze",16.8,"short float",158.20, "PAYC260619C00195000","short","2026-06-19",195.0,0.95,1.01,534,98,23.3,205.3,0.037),
    call("PAYC","short-squeeze",16.8,"short float",158.20, "PAYC260619C00175000","short","2026-06-19",175.0,3.20,0.89,1230,234,10.6,54.7,0.093),
    call("PAYC","short-squeeze",16.8,"short float",158.20, "PAYC260717C00190000","short","2026-07-17",190.0,2.80,0.95,1120,212,20.1,67.9,0.072),
    call("PAYC","short-squeeze",16.8,"short float",158.20, "PAYC260717C00210000","short","2026-07-17",210.0,1.10,1.05,678,123,33.4,190.9,0.038),
    call("PAYC","short-squeeze",16.8,"short float",158.20, "PAYC260619C00250000","moonshot","2026-06-19",250.0,0.15,1.18,1240,245,57.8,1000.0,0.016),
    call("PAYC","short-squeeze",16.8,"short float",158.20, "PAYC260619C00300000","moonshot","2026-06-19",300.0,0.06,1.28,678,134,89.6,3333.3,0.011),
]

# ── Sector Rotation (calls) ──────────────────────────────────────────────────
# Outperforming sectors (ETF beats SPY by 5%+ over 30D), top-20% names within sector.
# move_pct = sector RS vs SPY, move_label = "sector RS"

sector_rotation_signals = [
    # XLF sector (financials) beating SPY by +9.2% over 30D
    # JPM — $242.80
    call("JPM","sector-rotation",9.2,"sector RS",242.80, "JPM260717C00260000","short","2026-07-17",260.0,3.80,0.28,4560,678,7.1,68.4,0.079),
    call("JPM","sector-rotation",9.2,"sector RS",242.80, "JPM260717C00275000","short","2026-07-17",275.0,1.90,0.32,2890,423,13.7,144.7,0.050),
    call("JPM","sector-rotation",9.2,"sector RS",242.80, "JPM260717C00250000","short","2026-07-17",250.0,6.20,0.25,6780,1120,3.4,40.3,0.105),
    call("JPM","sector-rotation",9.2,"sector RS",242.80, "JPM260717C00285000","short","2026-07-17",285.0,1.10,0.35,1780,267,17.8,259.1,0.034),
    call("JPM","sector-rotation",9.2,"sector RS",242.80, "JPM261120C00275000","long","2026-11-20",275.0,5.80,0.29,7890,1120,13.7,47.4,0.089),
    call("JPM","sector-rotation",9.2,"sector RS",242.80, "JPM261120C00290000","long","2026-11-20",290.0,3.60,0.32,5230,789,19.8,80.6,0.064),
    call("JPM","sector-rotation",9.2,"sector RS",242.80, "JPM261218C00295000","long","2026-12-18",295.0,4.20,0.31,6120,890,21.7,70.2,0.071),
    call("JPM","sector-rotation",9.2,"sector RS",242.80, "JPM261120C00305000","long","2026-11-20",305.0,2.40,0.35,3420,534,25.9,127.1,0.048),
    call("JPM","sector-rotation",9.2,"sector RS",242.80, "JPM260717C00340000","moonshot","2026-07-17",340.0,0.18,0.52,1240,245,40.1,1111.1,0.015),
    call("JPM","sector-rotation",9.2,"sector RS",242.80, "JPM260717C00380000","moonshot","2026-07-17",380.0,0.06,0.60,789,145,57.5,5000.0,0.010),

    # GS — $594.20
    call("GS","sector-rotation",9.2,"sector RS",594.20, "GS260717C00640000","short","2026-07-17",640.0,8.40,0.26,2340,345,7.7,76.2,0.074),
    call("GS","sector-rotation",9.2,"sector RS",594.20, "GS260717C00660000","short","2026-07-17",660.0,5.20,0.29,1560,234,11.2,126.9,0.053),
    call("GS","sector-rotation",9.2,"sector RS",594.20, "GS260717C00620000","short","2026-07-17",620.0,13.50,0.23,3890,567,4.3,46.3,0.104),
    call("GS","sector-rotation",9.2,"sector RS",594.20, "GS261120C00660000","long","2026-11-20",660.0,14.80,0.27,4560,678,11.2,44.6,0.093),
    call("GS","sector-rotation",9.2,"sector RS",594.20, "GS261120C00700000","long","2026-11-20",700.0,8.90,0.30,2890,423,17.8,78.7,0.067),
    call("GS","sector-rotation",9.2,"sector RS",594.20, "GS261218C00720000","long","2026-12-18",720.0,9.80,0.29,3120,456,21.2,73.5,0.072),
    call("GS","sector-rotation",9.2,"sector RS",594.20, "GS260717C00800000","moonshot","2026-07-17",800.0,0.60,0.48,890,167,34.6,1000.0,0.018),

    # XLE sector (energy) beating SPY by +7.5% over 30D
    # XOM — $114.80
    call("XOM","sector-rotation",7.5,"sector RS",114.80, "XOM260717C00125000","short","2026-07-17",125.0,1.20,0.22,6780,1120,9.7,104.2,0.068),
    call("XOM","sector-rotation",7.5,"sector RS",114.80, "XOM260717C00130000","short","2026-07-17",130.0,0.72,0.25,4230,689,13.2,180.6,0.047),
    call("XOM","sector-rotation",7.5,"sector RS",114.80, "XOM260717C00120000","short","2026-07-17",120.0,2.20,0.20,9870,1560,4.5,54.5,0.095),
    call("XOM","sector-rotation",7.5,"sector RS",114.80, "XOM260717C00135000","short","2026-07-17",135.0,0.42,0.28,2890,456,17.6,309.5,0.031),
    call("XOM","sector-rotation",7.5,"sector RS",114.80, "XOM261120C00130000","long","2026-11-20",130.0,2.10,0.23,8910,1340,13.2,61.9,0.083),
    call("XOM","sector-rotation",7.5,"sector RS",114.80, "XOM261120C00140000","long","2026-11-20",140.0,1.30,0.26,5670,890,21.9,107.7,0.059),
    call("XOM","sector-rotation",7.5,"sector RS",114.80, "XOM261218C00145000","long","2026-12-18",145.0,1.60,0.25,6230,967,26.3,90.6,0.064),
    call("XOM","sector-rotation",7.5,"sector RS",114.80, "XOM260717C00170000","moonshot","2026-07-17",170.0,0.05,0.45,2340,456,47.6,3000.0,0.012),

    # CVX — $158.40
    call("CVX","sector-rotation",7.5,"sector RS",158.40, "CVX260717C00170000","short","2026-07-17",170.0,2.10,0.20,5670,890,7.3,81.0,0.072),
    call("CVX","sector-rotation",7.5,"sector RS",158.40, "CVX260717C00180000","short","2026-07-17",180.0,1.10,0.23,3420,534,14.0,163.6,0.046),
    call("CVX","sector-rotation",7.5,"sector RS",158.40, "CVX260717C00165000","short","2026-07-17",165.0,3.40,0.18,7890,1230,4.2,47.1,0.101),
    call("CVX","sector-rotation",7.5,"sector RS",158.40, "CVX261120C00178000","long","2026-11-20",178.0,3.20,0.21,6120,934,12.4,55.6,0.079),
    call("CVX","sector-rotation",7.5,"sector RS",158.40, "CVX261120C00190000","long","2026-11-20",190.0,1.80,0.24,3890,612,20.0,105.6,0.053),
    call("CVX","sector-rotation",7.5,"sector RS",158.40, "CVX261218C00195000","long","2026-12-18",195.0,2.20,0.23,4560,712,23.1,88.6,0.058),
    call("CVX","sector-rotation",7.5,"sector RS",158.40, "CVX260717C00230000","moonshot","2026-07-17",230.0,0.08,0.38,1890,345,45.2,1875.0,0.013),
]


if __name__ == "__main__":
    tasks = [
        ("broken-momentum",   "puts",  broken_momentum_signals),
        ("valuation-gravity", "puts",  valuation_gravity_signals),
        ("52-week-breakouts", "calls", breakout_calls_signals),
        ("short-squeeze",     "calls", short_squeeze_signals),
        ("sector-rotation",   "calls", sector_rotation_signals),
    ]
    for theme_id, page, signals in tasks:
        path = write_theme_report_locally(signals, page, theme_id)
        print(f"  ✓ {theme_id} ({page}) → {path}")
    print("\nDone. Open http://localhost:5173/ to view all themes.")
