import { useState } from 'react'
import { ChevronDown } from 'lucide-react'
import { Collapsible, CollapsibleTrigger, CollapsibleContent } from '@/components/ui/collapsible'
import { cn } from '@/lib/utils'
import { METHODOLOGY } from '@/constants/strings'

export default function MethodologyDisclosure() {
  const [open, setOpen] = useState(false)

  return (
    <Collapsible open={open} onOpenChange={setOpen} className="mb-6 border border-border rounded-xl bg-card overflow-hidden">
      <CollapsibleTrigger className="flex w-full items-center justify-between px-4 py-3 select-none text-left">
        <span className="text-sm font-medium text-muted-foreground">{METHODOLOGY.trigger}</span>
        <ChevronDown aria-hidden="true" className={cn("h-4 w-4 text-muted-foreground transition-transform duration-200", open && "rotate-180")} />
      </CollapsibleTrigger>

      <CollapsibleContent>
        <div className="px-5 pb-6 pt-4 space-y-8 border-t border-border">

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
            <ul className="space-y-4">
              {METHODOLOGY.judgementCalls.rules.map(({ rule, detail }) => (
                <li key={rule}>
                  <p className="text-sm font-semibold mb-0.5">{rule}</p>
                  <p className="text-sm text-muted-foreground leading-relaxed">{detail}</p>
                </li>
              ))}
            </ul>
          </section>

        </div>
      </CollapsibleContent>
    </Collapsible>
  )
}
