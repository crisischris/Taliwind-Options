import { useState, useEffect } from 'react'
import { ChevronDown, ExternalLink } from 'lucide-react'
import { Collapsible, CollapsibleContent } from '@/components/ui/collapsible'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { TICKER_CARD } from '@/constants/strings'
import OptionsTable, { type BaseOption } from '@/components/OptionsTable'

export interface ExpansionOverride {
  open: boolean
  v: number
}

export interface HeroRef {
  contract: string
  rowId: string
}

interface Props<T extends BaseOption> {
  ticker: string
  companyName?: string
  currentPrice: number
  options: T[]
  optionLabel: string
  columns: readonly { key: string; label: string; tip: string }[]
  getBreakeven: (o: T) => number
  shortHero: HeroRef
  longHero: HeroRef
  moonshotHero: HeroRef
  prevContracts: Set<string>
  prevTickers: Set<string>
  newOnly?: boolean
  expansionOverride?: ExpansionOverride | null
}

export default function TickerCard<T extends BaseOption>({
  ticker, companyName, currentPrice, options, optionLabel,
  columns, getBreakeven,
  shortHero, longHero, moonshotHero,
  prevContracts, prevTickers, newOnly, expansionOverride,
}: Props<T>) {
  const [open, setOpen] = useState({ short: true, long: true, moonshot: true })

  useEffect(() => {
    if (expansionOverride == null) return
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setOpen({ short: expansionOverride.open, long: expansionOverride.open, moonshot: expansionOverride.open })
  }, [expansionOverride])

  const buckets = { short: [] as T[], long: [] as T[], moonshot: [] as T[] }
  let newOptionCount = 0
  for (const o of options) {
    const actuallyNew = prevContracts.size > 0 && !prevContracts.has(o.contract)
    if (actuallyNew) newOptionCount++
    if (!newOnly || prevContracts.size === 0 || actuallyNew) buckets[o.term].push(o)
  }
  const { short, long, moonshot: moonshots } = buckets

  const isNewTicker = prevTickers.size > 0 && !prevTickers.has(ticker)

  return (
    <div className="border border-border rounded-xl bg-card shadow-sm overflow-hidden">
      <div className="flex flex-wrap items-center gap-3 px-4 py-3">
        {companyName && (
          <a
            href={`https://finance.yahoo.com/quote/${ticker}/`}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1 text-sm font-medium text-foreground hover:text-primary transition-colors"
          >
            {companyName}
            <ExternalLink className="h-3 w-3 text-muted-foreground" />
          </a>
        )}
        <span className="text-muted-foreground text-sm">
          {TICKER_CARD.priceAtScan}: <span className="font-medium text-foreground">${currentPrice.toFixed(2)}</span>
        </span>
        {isNewTicker && (
          <Badge variant="success" className="font-bold text-[10px]">NEW TICKER</Badge>
        )}
        {!isNewTicker && newOptionCount > 0 && (
          <Badge variant="success" className="font-semibold">
            {newOptionCount} new {optionLabel}{newOptionCount !== 1 ? 's' : ''}
          </Badge>
        )}
        <div className="ml-auto flex gap-1">
          <Button variant="ghost" size="sm" className="h-6 px-2 text-xs opacity-50 hover:opacity-90"
            onClick={() => setOpen({ short: true, long: true, moonshot: true })}>
            {TICKER_CARD.expand}
          </Button>
          <Button variant="ghost" size="sm" className="h-6 px-2 text-xs opacity-50 hover:opacity-90"
            onClick={() => setOpen({ short: false, long: false, moonshot: false })}>
            {TICKER_CARD.collapse}
          </Button>
        </div>
      </div>

      {short.length > 0 && (
        <TermSection label={TICKER_CARD.short.label}
          count={short.length} open={open.short}
          onToggle={v => setOpen(s => ({ ...s, short: v }))} borderTop>
          <OptionsTable options={short} currentPrice={currentPrice}
            heroContract={shortHero.contract} heroRowId={shortHero.rowId}
            prevContracts={prevContracts} columns={columns} getBreakeven={getBreakeven} />
        </TermSection>
      )}
      {long.length > 0 && (
        <TermSection label={TICKER_CARD.long.label}
          count={long.length} open={open.long}
          onToggle={v => setOpen(s => ({ ...s, long: v }))} borderTop>
          <OptionsTable options={long} currentPrice={currentPrice}
            heroContract={longHero.contract} heroRowId={longHero.rowId}
            prevContracts={prevContracts} columns={columns} getBreakeven={getBreakeven} />
        </TermSection>
      )}
      {moonshots.length > 0 && (
        <TermSection label={TICKER_CARD.moonshot.label}
          labelCls="text-gold/80" headerCls="bg-gold/5"
          count={moonshots.length} open={open.moonshot}
          onToggle={v => setOpen(s => ({ ...s, moonshot: v }))} borderTop>
          <OptionsTable options={moonshots} currentPrice={currentPrice}
            heroContract={moonshotHero.contract} heroRowId={moonshotHero.rowId}
            prevContracts={prevContracts} columns={columns} getBreakeven={getBreakeven} />
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
