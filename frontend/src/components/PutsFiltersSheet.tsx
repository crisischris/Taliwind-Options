import { METHODOLOGY } from '@/constants/strings'
import FiltersSheet from '@/components/FiltersSheet'
import { FixedRule, EditableRule, NumberInput } from '@/components/FiltersSheetPrimitives'

const DEFAULTS = {
  minGainPct:  500,
  minDte:       60,
  maxDte:     1000,
  maxCostPct:    5,
  maxIv:       200,
  minOi:        10,
  topN:         10,
}

export default function PutsFiltersSheet() {
  return (
    <FiltersSheet
      defaults={DEFAULTS}
      methodology={METHODOLOGY}
      renderRules={(filters, set, premium) => (
        <>
          <FixedRule rule="Universe" detail="S&P 500 and NASDAQ 100 constituents only — liquid, well-known names where options markets are active." />

          {premium ? (
            <EditableRule rule="Minimum 1-year gain" detail="Stocks must have gained at least this much over the trailing 12 months. Lower = more tickers, weaker mean-reversion thesis.">
              <NumberInput value={filters.minGainPct} onChange={v => set('minGainPct', v)} min={50} max={10000} unit="%" />
            </EditableRule>
          ) : (
            <FixedRule rule="500%+ over 1 year" detail="The stock must have appreciated at least 500% over the trailing 12 months. Below that threshold the mean-reversion thesis is weaker." />
          )}

          <FixedRule rule="Out-of-the-money puts only" detail="We want cheap optionality on a correction, not intrinsic value. ITM puts are excluded." />

          {premium ? (
            <EditableRule rule="Expiry window (DTE)" detail="Options must expire within this window. Too short = no time for the thesis. Too long = speculative pricing.">
              <div className="space-y-2">
                <div className="flex items-center justify-between text-xs text-muted-foreground">
                  <span>Min DTE</span><span>Max DTE</span>
                </div>
                <NumberInput value={filters.minDte} onChange={v => set('minDte', v)} min={7} max={365} unit=" days" />
                <NumberInput value={filters.maxDte} onChange={v => set('maxDte', v)} min={90} max={2000} unit=" days" />
              </div>
            </EditableRule>
          ) : (
            <FixedRule rule="Expiry between 60 and 1,000 DTE" detail="Too short and there is no time for the thesis to play out. Too long and pricing becomes speculative." />
          )}

          {premium ? (
            <EditableRule rule="Max ask (% of stock price)" detail="Caps the insurance cost. Higher = more expensive puts included.">
              <NumberInput value={filters.maxCostPct} onChange={v => set('maxCostPct', v)} min={1} max={20} unit="%" />
            </EditableRule>
          ) : (
            <FixedRule rule="Ask ≤ 5% of stock price" detail="Keeps the cost-of-insurance sensible. A put that costs more than 5% of the underlying is already pricing in meaningful downside." />
          )}

          {premium ? (
            <EditableRule rule="Max implied volatility" detail="Filters out puts where the market is already pricing in a crash.">
              <NumberInput value={filters.maxIv} onChange={v => set('maxIv', v)} min={50} max={500} unit="%" />
            </EditableRule>
          ) : (
            <FixedRule rule="Implied volatility ≤ 200%" detail="Extremely high IV means the market is already pricing in a crash. We want names where the put is still relatively cheap." />
          )}

          {premium ? (
            <EditableRule rule="Minimum open interest" detail="Higher = more liquid contracts only. Lower = includes thinly-traded LEAPs.">
              <NumberInput value={filters.minOi} onChange={v => set('minOi', v)} min={0} max={500} />
            </EditableRule>
          ) : (
            <FixedRule rule="Minimum liquidity" detail="Open interest ≥ 10, or any volume traded today, or a recorded last price. Catches thinly-traded LEAPs that are still quote-able." />
          )}

          <FixedRule rule="Scored by return × prob ITM" detail="Puts are ranked by return multiple (strike ÷ ask) multiplied by Black-Scholes probability of expiring in-the-money." />

          {premium ? (
            <EditableRule rule="Results per bucket" detail="Maximum puts shown per term bucket (short, long, moonshot).">
              <NumberInput value={filters.topN} onChange={v => set('topN', v)} min={3} max={50} />
            </EditableRule>
          ) : (
            <FixedRule rule="Top 10 per bucket" detail="Short-dated and long-dated puts are capped at 10 each. Moonshots — top 5 by raw return multiple — are surfaced separately." />
          )}
        </>
      )}
    />
  )
}
