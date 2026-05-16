import { SlidersHorizontal, Crown, RotateCcw } from 'lucide-react'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Switch } from '@/components/ui/switch'
import { Badge } from '@/components/ui/badge'
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from '@/components/ui/sheet'
import { CALLS_METHODOLOGY, FILTERS_SHEET } from '@/constants/strings'
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
  const [open, setOpen]       = useState(false)
  const [premium, setPremium] = useState(false)
  const [filters, setFilters] = useState(DEFAULTS)

  function set<K extends keyof typeof DEFAULTS>(key: K, value: number) {
    setFilters(f => ({ ...f, [key]: value }))
  }

  function reset() { setFilters(DEFAULTS) }

  return (
    <Sheet open={open} onOpenChange={setOpen}>
      <SheetTrigger asChild>
        <Button variant="outline" size="sm" className="gap-2">
          <SlidersHorizontal className="h-3.5 w-3.5" />
          {FILTERS_SHEET.triggerLabel}
        </Button>
      </SheetTrigger>

      <SheetContent side="right" className="w-full sm:w-[480px] overflow-y-auto flex flex-col">
        <SheetHeader className="mb-2">
          <SheetTitle>{CALLS_METHODOLOGY.trigger}</SheetTitle>
        </SheetHeader>

        {/* Premium toggle — mockup only */}
        <div className="flex items-center justify-between rounded-lg border border-border bg-muted/30 px-3 py-2 mb-6">
          <div className="flex items-center gap-2">
            <Crown className="h-4 w-4 text-gold" />
            <span className="text-sm font-medium">{FILTERS_SHEET.premiumLabel}</span>
            <Badge variant="gold" className="text-[10px] px-1.5 py-0">{FILTERS_SHEET.premiumBadge}</Badge>
          </div>
          <Switch checked={premium} onCheckedChange={setPremium} />
        </div>

        <div className="space-y-8 flex-1">
          <section>
            <h3 className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-2">
              {CALLS_METHODOLOGY.thesis.heading}
            </h3>
            <p className="text-sm leading-relaxed">{CALLS_METHODOLOGY.thesis.body}</p>
          </section>

          <section>
            <h3 className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-1">
              {CALLS_METHODOLOGY.judgementCalls.heading}
            </h3>
            <p className="text-xs text-muted-foreground mb-4">{CALLS_METHODOLOGY.judgementCalls.intro}</p>

            <ul className="space-y-5">
              {/* Universe — fixed */}
              <FixedRule rule="Universe" detail="Tickers held across ARKK, ARKX, ARKQ, SMH, AIQ, BOTZ, and ROKT ETFs — a cross-section of AI, semiconductors, robotics, and space plays." />

              {/* Momentum threshold — editable */}
              {premium ? (
                <EditableRule rule="Minimum 90-day momentum" detail="The ticker must be up at least this much over the trailing 90 days. Lower = more tickers, weaker trend signal.">
                  <NumberInput value={filters.minMomentumPct} onChange={v => set('minMomentumPct', v)} min={5} max={200} unit="%" />
                </EditableRule>
              ) : (
                <FixedRule rule="15%+ momentum in 90 days" detail="The ticker must be up at least 15% over the trailing 90 days. This confirms the trend is live before we look for calls." />
              )}

              {/* OTM only — fixed */}
              <FixedRule rule="Out-of-the-money calls only" detail="We want cheap optionality on a continuation move, not intrinsic value. ITM calls are excluded." />

              {/* DTE range — editable */}
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

              {/* Cost % — editable */}
              {premium ? (
                <EditableRule rule="Max ask (% of stock price)" detail="Caps the premium cost. Higher = more expensive calls included.">
                  <NumberInput value={filters.maxCostPct} onChange={v => set('maxCostPct', v)} min={1} max={20} unit="%" />
                </EditableRule>
              ) : (
                <FixedRule rule="Ask ≤ 4% of stock price" detail="Keeps premium cost manageable. These are momentum names with naturally higher volatility, so we allow slightly more than the put scanner." />
              )}

              {/* IV cap — editable */}
              {premium ? (
                <EditableRule rule="Max implied volatility" detail="Filters out calls where the market is already pricing in a parabolic move.">
                  <NumberInput value={filters.maxIv} onChange={v => set('maxIv', v)} min={50} max={400} unit="%" />
                </EditableRule>
              ) : (
                <FixedRule rule="Implied volatility ≤ 150%" detail="High-momentum stocks carry high IV. We accept up to 150% — above that the market is already pricing in a parabolic move." />
              )}

              {/* Min OI — editable */}
              {premium ? (
                <EditableRule rule="Minimum open interest" detail="Higher = more liquid contracts only. Lower = includes thinly-traded options.">
                  <NumberInput value={filters.minOi} onChange={v => set('minOi', v)} min={0} max={500} />
                </EditableRule>
              ) : (
                <FixedRule rule="Minimum liquidity" detail="Open interest ≥ 10, or any volume traded today, or a recorded last price." />
              )}

              {/* Scoring — fixed */}
              <FixedRule rule="Scored by return × prob ITM" detail="Calls are ranked by return multiple (strike ÷ ask) multiplied by Black-Scholes probability of expiring in-the-money." />

              {/* Top N — editable */}
              {premium ? (
                <EditableRule rule="Results per bucket" detail="Maximum calls shown per term bucket (short, long, moonshot).">
                  <NumberInput value={filters.topN} onChange={v => set('topN', v)} min={3} max={50} />
                </EditableRule>
              ) : (
                <FixedRule rule="Top 10 per bucket" detail="Short-dated and long-dated calls are capped at 10 each. Moonshots — top 5 by raw return multiple — are surfaced separately." />
              )}
            </ul>
          </section>
        </div>

        {/* Apply bar — premium only */}
        {premium && (
          <div className="border-t border-border pt-4 mt-6 flex items-center justify-between gap-3">
            <button
              onClick={reset}
              className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground transition-colors"
            >
              <RotateCcw className="h-3 w-3" />
              Restore defaults
            </button>
            <div className="flex flex-col items-end gap-1">
              <Button size="sm" disabled>
                {FILTERS_SHEET.getPremium}
              </Button>
              <p className="text-[10px] text-muted-foreground">{FILTERS_SHEET.comingSoon}</p>
            </div>
          </div>
        )}
      </SheetContent>
    </Sheet>
  )
}
