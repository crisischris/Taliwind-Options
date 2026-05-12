import { useState, useEffect } from 'react'
import { ChevronDown } from 'lucide-react'
import { Collapsible, CollapsibleContent } from '@/components/ui/collapsible'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { TICKER_CARD } from '@/constants/strings'
import type { Ticker } from '@/types/report'
import OptionsTable from './OptionsTable'

export interface ExpansionOverride {
  open: boolean
  v: number
}

interface Props {
  ticker: Ticker
  shortHeroContract: string
  longHeroContract: string
  moonshotHeroContract: string
  prevContracts: Set<string>
  prevTickers: Set<string>
  expansionOverride?: ExpansionOverride | null
}

export default function TickerCard({
  ticker, shortHeroContract, longHeroContract, moonshotHeroContract,
  prevContracts, prevTickers, expansionOverride,
}: Props) {
  const [shortOpen, setShortOpen]       = useState(true)
  const [longOpen, setLongOpen]         = useState(true)
  const [moonshotOpen, setMoonshotOpen] = useState(true)

  useEffect(() => {
    if (expansionOverride == null) return
    setShortOpen(expansionOverride.open)
    setLongOpen(expansionOverride.open)
    setMoonshotOpen(expansionOverride.open)
  }, [expansionOverride])

  const short     = ticker.puts.filter(p => p.term === 'short')
  const long      = ticker.puts.filter(p => p.term === 'long')
  const moonshots = ticker.puts.filter(p => p.term === 'moonshot')

  const isNewTicker = prevTickers.size > 0 && !prevTickers.has(ticker.ticker)
  const newPutCount = prevContracts.size > 0
    ? ticker.puts.filter(p => !prevContracts.has(p.contract)).length
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
        {!isNewTicker && newPutCount > 0 && (
          <Badge variant="success" className="font-semibold">
            {newPutCount} new put{newPutCount !== 1 ? 's' : ''}
          </Badge>
        )}
        <div className="ml-auto flex gap-1">
          <Button variant="ghost" size="sm" className="h-6 px-2 text-xs opacity-50 hover:opacity-90"
            onClick={() => { setShortOpen(true); setLongOpen(true); setMoonshotOpen(true) }}>
            {TICKER_CARD.expand}
          </Button>
          <Button variant="ghost" size="sm" className="h-6 px-2 text-xs opacity-50 hover:opacity-90"
            onClick={() => { setShortOpen(false); setLongOpen(false); setMoonshotOpen(false) }}>
            {TICKER_CARD.collapse}
          </Button>
        </div>
      </div>

      {short.length > 0 && (
        <TermSection label={TICKER_CARD.short.label}
          count={short.length} open={shortOpen} onToggle={setShortOpen} borderTop>
          <OptionsTable puts={short} currentPrice={ticker.current_price}
            heroContract={shortHeroContract} heroRowId="hero-short"
            prevContracts={prevContracts} />
        </TermSection>
      )}
      {long.length > 0 && (
        <TermSection label={TICKER_CARD.long.label}
          count={long.length} open={longOpen} onToggle={setLongOpen} borderTop>
          <OptionsTable puts={long} currentPrice={ticker.current_price}
            heroContract={longHeroContract} heroRowId="hero-long"
            prevContracts={prevContracts} />
        </TermSection>
      )}
      {moonshots.length > 0 && (
        <TermSection label={TICKER_CARD.moonshot.label}
          labelCls="text-gold/80" headerCls="bg-gold/5"
          count={moonshots.length} open={moonshotOpen} onToggle={setMoonshotOpen} borderTop>
          <OptionsTable puts={moonshots} currentPrice={ticker.current_price}
            heroContract={moonshotHeroContract} heroRowId="hero-moonshot"
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
          "flex items-center gap-2 px-4 py-2.5 cursor-pointer select-none bg-muted/40",
          borderTop && "border-t border-border",
          open && "border-b border-border",
          headerCls,
        )}
        onClick={() => onToggle(!open)}
      >
        <span className={cn("text-xs font-semibold uppercase tracking-wider text-muted-foreground", labelCls)}>
          {label}
        </span>
        <span className="text-xs font-normal text-muted-foreground/60">({count})</span>
        <ChevronDown className={cn("h-3 w-3 ml-auto text-muted-foreground transition-transform duration-200", open && "rotate-180")} />
      </div>
      <CollapsibleContent>{children}</CollapsibleContent>
    </Collapsible>
  )
}
