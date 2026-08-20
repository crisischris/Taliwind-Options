import { themeById } from '@/constants/themes'
import { FILTERS_SHEET } from '@/constants/strings'
import FiltersSheet from '@/components/FiltersSheet'
import { FixedRule, EditableRule, NumberInput } from '@/components/FiltersSheetPrimitives'
import { track } from '@/lib/analytics'

const PUTS_DEFAULTS = {
  minGainPct:  500,
  minDte:       60,
  maxDte:     1000,
  maxCostPct:    5,
  maxIv:       200,
  minOi:        10,
  topN:         10,
}

const CALLS_DEFAULTS = {
  minMomentumPct:  15,
  minDte:          60,
  maxDte:         365,
  maxCostPct:       4,
  maxIv:          150,
  minOi:           10,
  topN:            10,
}

interface Props {
  base:    'puts' | 'calls'
  themeId: string
}

export default function ThemeFiltersSheet({ base, themeId }: Props) {
  const theme = themeById(themeId)!
  const isPuts = base === 'puts'
  const methodology = {
    trigger:        isPuts ? FILTERS_SHEET.putsMethodologyTrigger : FILTERS_SHEET.callsMethodologyTrigger,
    thesis:         { heading: FILTERS_SHEET.thesisHeading,        body: theme.thesis },
    judgementCalls: { heading: FILTERS_SHEET.judgementCallsHeading, intro: theme.judgementCalls!.intro },
  }

  return (
    <FiltersSheet
      key={themeId}
      defaults={isPuts ? PUTS_DEFAULTS : CALLS_DEFAULTS}
      methodology={methodology}
      onOpen={() => track('filters_opened', { base, theme: themeId })}
      renderRules={(rawFilters, rawSet, premium) => {
        const filters = rawFilters as Record<string, number>
        const set = rawSet as (key: string, value: number) => void
        return (
        <>
          {premium ? (
            <>
              {isPuts ? (
                <EditableRule rule="Minimum 1-year gain" detail="Stocks must have gained at least this much. Lower = more tickers, weaker thesis.">
                  <NumberInput value={filters.minGainPct ?? 500} onChange={v => set('minGainPct', v)} min={50} max={10000} unit="%" />
                </EditableRule>
              ) : (
                <EditableRule rule="Minimum 90-day momentum" detail="The ticker must be up at least this much over the trailing 90 days. Lower = more tickers, weaker trend signal.">
                  <NumberInput value={filters.minMomentumPct ?? 15} onChange={v => set('minMomentumPct', v)} min={5} max={200} unit="%" />
                </EditableRule>
              )}
              <FixedRule rule={isPuts ? 'Out-of-the-money puts only' : 'Out-of-the-money calls only'} detail="We want cheap optionality, not intrinsic value. ITM options are excluded." />
              <EditableRule rule="Expiry window (DTE)" detail="Options must expire within this window.">
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-xs text-muted-foreground">
                    <span>Min DTE</span><span>Max DTE</span>
                  </div>
                  <NumberInput value={filters.minDte} onChange={v => set('minDte', v)} min={7} max={365} unit=" days" />
                  <NumberInput value={filters.maxDte} onChange={v => set('maxDte', v)} min={90} max={isPuts ? 2000 : 730} unit=" days" />
                </div>
              </EditableRule>
              <EditableRule rule="Max ask (% of stock price)" detail={`Caps the ${isPuts ? 'insurance' : 'premium'} cost. Higher = more expensive options included.`}>
                <NumberInput value={filters.maxCostPct} onChange={v => set('maxCostPct', v)} min={1} max={20} unit="%" />
              </EditableRule>
              <EditableRule rule="Max implied volatility" detail={`Filters out ${isPuts ? 'puts where the market is already pricing in a crash' : 'calls where the market is already pricing in a parabolic move'}.`}>
                <NumberInput value={filters.maxIv} onChange={v => set('maxIv', v)} min={50} max={isPuts ? 500 : 400} unit="%" />
              </EditableRule>
              <EditableRule rule="Minimum open interest" detail="Higher = more liquid contracts only.">
                <NumberInput value={filters.minOi} onChange={v => set('minOi', v)} min={0} max={500} />
              </EditableRule>
              <FixedRule rule="Scored by expected value × prob ITM × liquidity" detail={`${isPuts ? 'Puts' : 'Calls'} are ranked by risk-neutral expected payoff divided by ask, multiplied by Black-Scholes probability of expiring ITM and a liquidity factor that penalizes wide spreads and thin open interest.`} />
              <EditableRule rule="Results per bucket" detail={`Maximum ${isPuts ? 'puts' : 'calls'} shown per term bucket (short, long, moonshot).`}>
                <NumberInput value={filters.topN} onChange={v => set('topN', v)} min={3} max={50} />
              </EditableRule>
            </>
          ) : (
            theme.judgementCalls!.rules.map(({ rule, detail }) => (
              <FixedRule key={rule} rule={rule} detail={detail} />
            ))
          )}
        </>
        )
      }}
    />
  )
}
