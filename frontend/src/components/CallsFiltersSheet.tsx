import { CALLS_METHODOLOGY } from '@/constants/strings'
import FiltersSheet from '@/components/FiltersSheet'
import { FixedRule, EditableRule, NumberInput } from '@/components/FiltersSheetPrimitives'

const DEFAULTS = {
  minMomentumPct:  15,
  minDte:          60,
  maxDte:         365,
  maxCostPct:       4,
  maxIv:          150,
  minOi:           10,
  topN:            10,
}

export default function CallsFiltersSheet() {
  return (
    <FiltersSheet
      defaults={DEFAULTS}
      methodology={CALLS_METHODOLOGY}
      renderRules={(filters, set, premium) => (
        <>
          <FixedRule rule="Universe" detail="Tickers held across ARKK, ARKX, ARKQ, SMH, AIQ, BOTZ, and ROKT ETFs — a cross-section of AI, semiconductors, robotics, and space plays." />

          {premium ? (
            <EditableRule rule="Minimum 90-day momentum" detail="The ticker must be up at least this much over the trailing 90 days. Lower = more tickers, weaker trend signal.">
              <NumberInput value={filters.minMomentumPct} onChange={v => set('minMomentumPct', v)} min={5} max={200} unit="%" />
            </EditableRule>
          ) : (
            <FixedRule rule="15%+ momentum in 90 days" detail="The ticker must be up at least 15% over the trailing 90 days. This confirms the trend is live before we look for calls." />
          )}

          <FixedRule rule="Out-of-the-money calls only" detail="We want cheap optionality on a continuation move, not intrinsic value. ITM calls are excluded." />

          {premium ? (
            <EditableRule rule="Expiry window (DTE)" detail="Options must expire within this window. Too short = no time for the thesis. Too long = speculative pricing.">
              <div className="space-y-2">
                <div className="flex items-center justify-between text-xs text-muted-foreground">
                  <span>Min DTE</span><span>Max DTE</span>
                </div>
                <NumberInput value={filters.minDte} onChange={v => set('minDte', v)} min={7} max={365} unit=" days" />
                <NumberInput value={filters.maxDte} onChange={v => set('maxDte', v)} min={90} max={730} unit=" days" />
              </div>
            </EditableRule>
          ) : (
            <FixedRule rule="Expiry between 60 and 365 DTE" detail="Long enough for the thesis to play out. LEAPs are included — macro trends take time." />
          )}

          {premium ? (
            <EditableRule rule="Max ask (% of stock price)" detail="Caps the premium cost. Higher = more expensive calls included.">
              <NumberInput value={filters.maxCostPct} onChange={v => set('maxCostPct', v)} min={1} max={20} unit="%" />
            </EditableRule>
          ) : (
            <FixedRule rule="Ask ≤ 4% of stock price" detail="Keeps premium cost manageable. These are momentum names with naturally higher volatility, so we allow slightly more than the put scanner." />
          )}

          {premium ? (
            <EditableRule rule="Max implied volatility" detail="Filters out calls where the market is already pricing in a parabolic move.">
              <NumberInput value={filters.maxIv} onChange={v => set('maxIv', v)} min={50} max={400} unit="%" />
            </EditableRule>
          ) : (
            <FixedRule rule="Implied volatility ≤ 150%" detail="High-momentum stocks carry high IV. We accept up to 150% — above that the market is already pricing in a parabolic move." />
          )}

          {premium ? (
            <EditableRule rule="Minimum open interest" detail="Higher = more liquid contracts only. Lower = includes thinly-traded options.">
              <NumberInput value={filters.minOi} onChange={v => set('minOi', v)} min={0} max={500} />
            </EditableRule>
          ) : (
            <FixedRule rule="Minimum liquidity" detail="Open interest ≥ 10, or any volume traded today, or a recorded last price." />
          )}

          <FixedRule rule="Scored by return × prob ITM" detail="Calls are ranked by return multiple (strike ÷ ask) multiplied by Black-Scholes probability of expiring in-the-money." />

          {premium ? (
            <EditableRule rule="Results per bucket" detail="Maximum calls shown per term bucket (short, long, moonshot).">
              <NumberInput value={filters.topN} onChange={v => set('topN', v)} min={3} max={50} />
            </EditableRule>
          ) : (
            <FixedRule rule="Top 10 per bucket" detail="Short-dated and long-dated calls are capped at 10 each. Moonshots — top 5 by raw return multiple — are surfaced separately." />
          )}
        </>
      )}
    />
  )
}
