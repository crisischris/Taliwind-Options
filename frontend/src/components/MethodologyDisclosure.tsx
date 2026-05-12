import { useState } from 'react'
import { ChevronDown } from 'lucide-react'
import { Collapsible, CollapsibleContent } from '@/components/ui/collapsible'
import { cn } from '@/lib/utils'
import { METHODOLOGY } from '@/constants/strings'

export default function MethodologyDisclosure() {
  const [open, setOpen] = useState(false)

  return (
    <Collapsible open={open} onOpenChange={setOpen} className="mb-6 border border-border rounded-xl bg-card overflow-hidden">
      <div
        className="flex items-center justify-between px-4 py-3 cursor-pointer select-none"
        onClick={() => setOpen(o => !o)}
      >
        <span className="text-sm font-medium text-muted-foreground">{METHODOLOGY.trigger}</span>
        <ChevronDown className={cn("h-4 w-4 text-muted-foreground transition-transform duration-200", open && "rotate-180")} />
      </div>

      <CollapsibleContent>
        <div className="px-5 pb-5 pt-1 space-y-5 border-t border-border">

          <section>
            <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground mb-2">
              {METHODOLOGY.thesis.heading}
            </h3>
            <p className="text-sm leading-relaxed">{METHODOLOGY.thesis.body}</p>
          </section>

          <section>
            <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground mb-1">
              {METHODOLOGY.judgementCalls.heading}
            </h3>
            <p className="text-xs text-muted-foreground mb-3">{METHODOLOGY.judgementCalls.intro}</p>
            <ul className="space-y-2">
              {METHODOLOGY.judgementCalls.rules.map(({ rule, detail }) => (
                <li key={rule} className="flex gap-3 text-sm">
                  <span className="font-semibold shrink-0 text-foreground">{rule}</span>
                  <span className="text-muted-foreground leading-relaxed">{detail}</span>
                </li>
              ))}
            </ul>
          </section>

        </div>
      </CollapsibleContent>
    </Collapsible>
  )
}
