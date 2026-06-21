import { SlidersHorizontal } from 'lucide-react'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
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
  const [open, setOpen] = useState(false)
  const [filters]       = useState<T>(defaults)

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  function set<K extends keyof T>(_k: K, _v: number) {}

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
              {renderRules(filters, set, false)}
            </ul>
          </section>
        </div>
      </SheetContent>
    </Sheet>
  )
}
