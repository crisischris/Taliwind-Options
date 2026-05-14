import { SlidersHorizontal, Lock, Crown, RotateCcw } from 'lucide-react'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Switch } from '@/components/ui/switch'
import { Badge } from '@/components/ui/badge'
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from '@/components/ui/sheet'
import { METHODOLOGY, PUTS_FILTERS_SHEET } from '@/constants/strings'

const DEFAULTS = {
  minGainPct:  500,
  minDte:       60,
  maxDte:     1000,
  maxCostPct:    5,
  maxIv:       200,
  minOi:        10,
  topN:         10,
}

function Label({ children }: { children: React.ReactNode }) {
  return <p className="text-sm font-semibold mb-1">{children}</p>
}

function Hint({ children }: { children: React.ReactNode }) {
  return <p className="text-xs text-muted-foreground leading-relaxed">{children}</p>
}

function FixedRule({ rule, detail }: { rule: string; detail: string }) {
  return (
    <li className="border-l-2 border-border pl-3">
      <div className="flex items-center gap-1.5 mb-0.5">
        <Label>{rule}</Label>
        <Lock className="h-3 w-3 text-muted-foreground/50" />
      </div>
      <Hint>{detail}</Hint>
    </li>
  )
}

interface EditableRuleProps {
  rule: string
  detail: string
  children: React.ReactNode
}

function EditableRule({ rule, detail, children }: EditableRuleProps) {
  return (
    <li className="border-l-2 border-primary/40 pl-3 space-y-2">
      <Label>{rule}</Label>
      {children}
      <Hint>{detail}</Hint>
    </li>
  )
}

function NumberInput({
  value, onChange, min, max, unit = '',
}: {
  value: number; onChange: (v: number) => void; min: number; max: number; unit?: string
}) {
  return (
    <div className="flex items-center gap-2">
      <input
        type="range"
        min={min} max={max}
        value={value}
        onChange={e => onChange(Number(e.target.value))}
        className="flex-1 accent-primary h-1.5"
      />
      <span className="text-sm font-mono w-20 text-right tabular-nums">
        {value.toLocaleString()}{unit}
      </span>
    </div>
  )
}

export default function PutsFiltersSheet() {
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
          {PUTS_FILTERS_SHEET.triggerLabel}
        </Button>
      </SheetTrigger>

      <SheetContent side="right" className="w-full sm:w-[480px] overflow-y-auto flex flex-col">
        <SheetHeader className="mb-2">
          <SheetTitle>{METHODOLOGY.trigger}</SheetTitle>
        </SheetHeader>

        {/* Premium toggle — mockup only */}
        <div className="flex items-center justify-between rounded-lg border border-border bg-muted/30 px-3 py-2 mb-6">
          <div className="flex items-center gap-2">
            <Crown className="h-4 w-4 text-gold" />
            <span className="text-sm font-medium">{PUTS_FILTERS_SHEET.premiumLabel}</span>
            <Badge variant="gold" className="text-[10px] px-1.5 py-0">{PUTS_FILTERS_SHEET.premiumBadge}</Badge>
          </div>
          <Switch checked={premium} onCheckedChange={setPremium} />
        </div>

        <div className="space-y-8 flex-1">
          <section>
            <h3 className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-2">
              {METHODOLOGY.thesis.heading}
            </h3>
            <p className="text-sm leading-relaxed">{METHODOLOGY.thesis.body}</p>
          </section>

          <section>
            <h3 className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-1">
              {METHODOLOGY.judgementCalls.heading}
            </h3>
            <p className="text-xs text-muted-foreground mb-4">{METHODOLOGY.judgementCalls.intro}</p>

            <ul className="space-y-5">
              {/* Universe — fixed */}
              <FixedRule rule="Universe" detail="S&P 500 and NASDAQ 100 constituents only — liquid, well-known names where options markets are active." />

              {/* YTD gain — editable */}
              {premium ? (
                <EditableRule rule="Minimum YTD gain" detail="Stocks must have gained at least this much over the trailing 12 months. Lower = more tickers, weaker mean-reversion thesis.">
                  <NumberInput value={filters.minGainPct} onChange={v => set('minGainPct', v)} min={50} max={10000} unit="%" />
                </EditableRule>
              ) : (
                <FixedRule rule="500%+ YTD gain" detail="The stock must have appreciated at least 500% over the trailing 12 months. Below that threshold the mean-reversion thesis is weaker." />
              )}

              {/* OTM only — fixed */}
              <FixedRule rule="Out-of-the-money puts only" detail="We want cheap optionality on a correction, not intrinsic value. ITM puts are excluded." />

              {/* DTE range — editable */}
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

              {/* Cost % — editable */}
              {premium ? (
                <EditableRule rule="Max ask (% of stock price)" detail="Caps the insurance cost. Higher = more expensive puts included.">
                  <NumberInput value={filters.maxCostPct} onChange={v => set('maxCostPct', v)} min={1} max={20} unit="%" />
                </EditableRule>
              ) : (
                <FixedRule rule="Ask ≤ 5% of stock price" detail="Keeps the cost-of-insurance sensible. A put that costs more than 5% of the underlying is already pricing in meaningful downside." />
              )}

              {/* IV cap — editable */}
              {premium ? (
                <EditableRule rule="Max implied volatility" detail="Filters out puts where the market is already pricing in a crash.">
                  <NumberInput value={filters.maxIv} onChange={v => set('maxIv', v)} min={50} max={500} unit="%" />
                </EditableRule>
              ) : (
                <FixedRule rule="Implied volatility ≤ 200%" detail="Extremely high IV means the market is already pricing in a crash. We want names where the put is still relatively cheap." />
              )}

              {/* Min OI — editable */}
              {premium ? (
                <EditableRule rule="Minimum open interest" detail="Higher = more liquid contracts only. Lower = includes thinly-traded LEAPs.">
                  <NumberInput value={filters.minOi} onChange={v => set('minOi', v)} min={0} max={500} />
                </EditableRule>
              ) : (
                <FixedRule rule="Minimum liquidity" detail="Open interest ≥ 10, or any volume traded today, or a recorded last price. Catches thinly-traded LEAPs that are still quote-able." />
              )}

              {/* Scoring — fixed */}
              <FixedRule rule="Scored by return × prob ITM" detail="Puts are ranked by return multiple (strike ÷ ask) multiplied by Black-Scholes probability of expiring in-the-money." />

              {/* Top N — editable */}
              {premium ? (
                <EditableRule rule="Results per bucket" detail="Maximum puts shown per term bucket (short, long, moonshot).">
                  <NumberInput value={filters.topN} onChange={v => set('topN', v)} min={3} max={50} />
                </EditableRule>
              ) : (
                <FixedRule rule="Top 10 per bucket" detail="Short-dated and long-dated puts are capped at 10 each. Moonshots — top 5 by raw return multiple — are surfaced separately." />
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
                {PUTS_FILTERS_SHEET.getPremium}
              </Button>
              <p className="text-[10px] text-muted-foreground">{PUTS_FILTERS_SHEET.comingSoon}</p>
            </div>
          </div>
        )}
      </SheetContent>
    </Sheet>
  )
}
