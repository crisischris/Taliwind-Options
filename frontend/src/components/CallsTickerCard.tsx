import { useState, useEffect } from 'react'
import { ChevronDown } from 'lucide-react'
import { Collapsible, CollapsibleContent } from '@/components/ui/collapsible'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { CALLS_TICKER_CARD } from '@/constants/strings'
import type { CallTicker } from '@/types/report'
import CallsOptionsTable from '@/components/CallsOptionsTable'
import type { ExpansionOverride } from '@/components/TickerCard'

interface Props {
  ticker: CallTicker
  shortHeroContract: string
  longHeroContract: string
  moonshotHeroContract: string
  prevContracts: Set<string>
  prevTickers: Set<string>
  newOnly?: boolean
  expansionOverride?: ExpansionOverride | null
}

export default function CallsTickerCard({
  ticker, shortHeroContract, longHeroContract, moonshotHeroContract,
  prevContracts, prevTickers, newOnly, expansionOverride,
}: Props) {
  const [open, setOpen] = useState({ short: true, long: true, moonshot: true })

  useEffect(() => {
    if (expansionOverride == null) return
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setOpen({ short: expansionOverride.open, long: expansionOverride.open, moonshot: expansionOverride.open })
  }, [expansionOverride])

  const isNew = (c: { contract: string }) =>
    !newOnly || prevContracts.size === 0 || !prevContracts.has(c.contract)

  const short     = ticker.calls.filter(c => c.term === 'short'    && isNew(c))
  const long      = ticker.calls.filter(c => c.term === 'long'     && isNew(c))
  const moonshots = ticker.calls.filter(c => c.term === 'moonshot' && isNew(c))

  const isNewTicker  = prevTickers.size > 0 && !prevTickers.has(ticker.ticker)
  const newCallCount = prevContracts.size > 0
    ? ticker.calls.filter(c => !prevContracts.has(c.contract)).length
    : 0

  return (
    <div className="border border-border rounded-xl bg-card shadow-sm overflow-hidden">
      <div className="flex flex-wrap items-center gap-3 px-4 py-3">
        <span className="text-muted-foreground text-sm">
          Current: <span className="font-medium text-foreground">${ticker.current_price.toFixed(2)}</span>
        </span>
        {isNewTicker && (
          <Badge variant="success" className="font-bold text-[10px]">NEW TICKER</Badge>
        )}
        {!isNewTicker && newCallCount > 0 && (
          <Badge variant="success" className="font-semibold">
            {newCallCount} new call{newCallCount !== 1 ? 's' : ''}
          </Badge>
        )}
        <div className="ml-auto flex gap-1">
          <Button variant="ghost" size="sm" className="h-6 px-2 text-xs opacity-50 hover:opacity-90"
            onClick={() => setOpen({ short: true, long: true, moonshot: true })}>
            {CALLS_TICKER_CARD.expand}
          </Button>
          <Button variant="ghost" size="sm" className="h-6 px-2 text-xs opacity-50 hover:opacity-90"
            onClick={() => setOpen({ short: false, long: false, moonshot: false })}>
            {CALLS_TICKER_CARD.collapse}
          </Button>
        </div>
      </div>

      {short.length > 0 && (
        <TermSection label={CALLS_TICKER_CARD.short.label}
          count={short.length} open={open.short}
          onToggle={v => setOpen(s => ({ ...s, short: v }))} borderTop>
          <CallsOptionsTable calls={short} currentPrice={ticker.current_price}
            heroContract={shortHeroContract} heroRowId="hero-call-short"
            prevContracts={prevContracts} />
        </TermSection>
      )}
      {long.length > 0 && (
        <TermSection label={CALLS_TICKER_CARD.long.label}
          count={long.length} open={open.long}
          onToggle={v => setOpen(s => ({ ...s, long: v }))} borderTop>
          <CallsOptionsTable calls={long} currentPrice={ticker.current_price}
            heroContract={longHeroContract} heroRowId="hero-call-long"
            prevContracts={prevContracts} />
        </TermSection>
      )}
      {moonshots.length > 0 && (
        <TermSection label={CALLS_TICKER_CARD.moonshot.label}
          labelCls="text-gold/80" headerCls="bg-gold/5"
          count={moonshots.length} open={open.moonshot}
          onToggle={v => setOpen(s => ({ ...s, moonshot: v }))} borderTop>
          <CallsOptionsTable calls={moonshots} currentPrice={ticker.current_price}
            heroContract={moonshotHeroContract} heroRowId="hero-call-moonshot"
            prevContracts={prevContracts} />
        </TermSection>
      )}
    </div>
  )
}

interface TermSectionProps {
  label: string
  labelCls?: string
  headerCls?: string
  count: number
  open: boolean
  onToggle: (v: boolean) => void
  borderTop?: boolean
  children: React.ReactNode
}

function TermSection({ label, labelCls, headerCls, count, open, onToggle, borderTop, children }: TermSectionProps) {
  return (
    <Collapsible open={open} onOpenChange={onToggle}>
      <div
        className={cn(
          'flex items-center gap-2 px-4 py-2.5 cursor-pointer select-none bg-muted/40',
          borderTop && 'border-t border-border',
          open && 'border-b border-border',
          headerCls,
        )}
        onClick={() => onToggle(!open)}
      >
        <span className={cn('text-xs font-semibold uppercase tracking-wider text-muted-foreground', labelCls)}>
          {label}
        </span>
        <span className="text-xs font-normal text-muted-foreground/60">({count})</span>
        <ChevronDown className={cn('h-3 w-3 ml-auto text-muted-foreground transition-transform duration-200', open && 'rotate-180')} />
      </div>
      <CollapsibleContent>{children}</CollapsibleContent>
    </Collapsible>
  )
}
