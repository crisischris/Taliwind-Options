import { SlidersHorizontal, Crown, RotateCcw } from 'lucide-react'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Switch } from '@/components/ui/switch'
import { Badge } from '@/components/ui/badge'
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from '@/components/ui/sheet'
import { FILTERS_SHEET } from '@/constants/strings'
import type { ReactNode } from 'react'

interface Methodology {
  trigger: string
  thesis: { heading: string; body: string }
  judgementCalls: { heading: string; intro: string }
}

interface Props<T extends Record<string, number>> {
  defaults: T
  methodology: Methodology
  onOpen?: () => void
  renderRules: (
    filters: T,
    set: <K extends keyof T>(key: K, value: number) => void,
    premium: boolean,
  ) => ReactNode
}

export default function FiltersSheet<T extends Record<string, number>>({
  defaults,
  methodology,
  onOpen,
  renderRules,
}: Props<T>) {
  const [open, setOpen]       = useState(false)
  const [premium, setPremium] = useState(false)
  const [filters, setFilters] = useState<T>(defaults)

  function set<K extends keyof T>(key: K, value: number) {
    setFilters(f => ({ ...f, [key]: value }))
  }

  function reset() { setFilters(defaults) }

  return (
    <Sheet open={open} onOpenChange={v => { if (v) onOpen?.(); setOpen(v) }}>
      <SheetTrigger asChild>
        <Button variant="outline" size="sm" className="gap-2">
          <SlidersHorizontal className="h-3.5 w-3.5" />
          {FILTERS_SHEET.triggerLabel}
        </Button>
      </SheetTrigger>

      <SheetContent side="right" className="w-full sm:w-[480px] overflow-y-auto flex flex-col">
        <SheetHeader className="mb-2">
          <SheetTitle>{methodology.trigger}</SheetTitle>
        </SheetHeader>

        <div className="flex items-center justify-between rounded-lg border border-border bg-muted/30 px-3 py-2 mb-6">
          <div className="flex items-center gap-2">
            <Crown className="h-4 w-4 text-gold" />
            <span className="text-sm font-medium">{FILTERS_SHEET.premiumLabel}</span>
            <Badge variant="gold" className="text-[10px] px-1.5 py-0">{FILTERS_SHEET.premiumBadge}</Badge>
          </div>
          <Switch checked={premium} onCheckedChange={setPremium} aria-label="Enable premium filters" />
        </div>

        <div className="space-y-8 flex-1">
          <section>
            <h3 className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-2">
              {methodology.thesis.heading}
            </h3>
            <p className="text-sm leading-relaxed">{methodology.thesis.body}</p>
          </section>

          <section>
            <h3 className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-1">
              {methodology.judgementCalls.heading}
            </h3>
            <p className="text-xs text-muted-foreground mb-4">{methodology.judgementCalls.intro}</p>
            <ul className="space-y-5">
              {renderRules(filters, set, premium)}
            </ul>
          </section>
        </div>

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
              <Button size="sm" disabled>{FILTERS_SHEET.getPremium}</Button>
              <p className="text-[10px] text-muted-foreground">{FILTERS_SHEET.comingSoon}</p>
            </div>
          </div>
        )}
      </SheetContent>
    </Sheet>
  )
}
