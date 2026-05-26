import { useState, useRef, useEffect } from 'react'
import { Info } from 'lucide-react'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Badge } from '@/components/ui/badge'
import { TooltipProvider, Tooltip, TooltipTrigger, TooltipContent } from '@/components/ui/tooltip'
import { cn } from '@/lib/utils'
import { beCls, ivCls, probCls } from '@/utils/colors'
import type { BaseOption } from '@/types/report'

export type { BaseOption }

// Hover on desktop, tap-to-pin on mobile. Uses a short delay before closing so
// the `click` event (which fires after pointer-leave on mobile) can cancel it.
function ColumnTip({ tip }: { tip: string }) {
  const [open, setOpen] = useState(false)
  const pinned = useRef(false)
  const closeTimer = useRef<ReturnType<typeof setTimeout> | null>(null)
  const triggerRef = useRef<HTMLButtonElement>(null)

  useEffect(() => {
    if (!open) return
    function onDocPointerDown(e: PointerEvent) {
      if (!triggerRef.current?.contains(e.target as Node)) {
        pinned.current = false
        setOpen(false)
      }
    }
    document.addEventListener('pointerdown', onDocPointerDown)
    return () => document.removeEventListener('pointerdown', onDocPointerDown)
  }, [open])

  function onOpenChange(val: boolean) {
    if (pinned.current) return
    if (!val) {
      closeTimer.current = setTimeout(() => setOpen(false), 100)
    } else {
      if (closeTimer.current) clearTimeout(closeTimer.current)
      setOpen(true)
    }
  }

  function onClick(e: React.MouseEvent) {
    e.stopPropagation()
    if (closeTimer.current) clearTimeout(closeTimer.current)
    if (pinned.current) {
      pinned.current = false
      setOpen(false)
    } else {
      pinned.current = true
      setOpen(true)
    }
  }

  return (
    <Tooltip open={open} onOpenChange={onOpenChange}>
      <TooltipTrigger ref={triggerRef} type="button" className="inline-flex cursor-help focus:outline-none" onClick={onClick}>
        <Info aria-hidden="true" className="h-3.5 w-3.5 opacity-30 hover:opacity-70 transition-opacity" />
      </TooltipTrigger>
      <TooltipContent>{tip}</TooltipContent>
    </Tooltip>
  )
}

type SortDir = 'asc' | 'desc'

function sortValue<T extends BaseOption>(o: T, key: string, currentPrice: number): number | string {
  switch (key) {
    case 'contract_cost': return o.ask * 100
    case 'cost_pct':      return o.ask / currentPrice * 100
    case 'volume':        return o.volume ?? 0
    case 'expiry':        return o.expiry.replace(/-/g, '')
    default:              return (o as never)[key] as number | string
  }
}

interface Props<T extends BaseOption> {
  options: T[]
  currentPrice: number
  heroContract: string
  heroRowId: string
  prevContracts: Set<string>
  columns: readonly { key: string; label: string; tip: string }[]
  getBreakeven: (o: T) => number
}

export default function OptionsTable<T extends BaseOption>({
  options, currentPrice, heroContract, heroRowId, prevContracts, columns, getBreakeven,
}: Props<T>) {
  const [sortKey, setSortKey] = useState<string | null>(null)
  const [sortDir, setSortDir] = useState<SortDir>('desc')

  function handleSort(key: string) {
    if (sortKey === key) {
      setSortDir(d => d === 'desc' ? 'asc' : 'desc')
    } else {
      setSortKey(key)
      setSortDir('desc')
    }
  }

  const sorted = sortKey
    ? [...options].sort((a, b) => {
        const av = sortValue(a, sortKey, currentPrice)
        const bv = sortValue(b, sortKey, currentPrice)
        const an = parseFloat(String(av))
        const bn = parseFloat(String(bv))
        if (!isNaN(an) && !isNaN(bn)) return sortDir === 'desc' ? bn - an : an - bn
        return sortDir === 'desc'
          ? String(bv).localeCompare(String(av))
          : String(av).localeCompare(String(bv))
      })
    : options

  return (
    <TooltipProvider delayDuration={0}>
      <Table className="min-w-[900px]">
        <TableHeader>
          <TableRow className="hover:bg-transparent">
            {columns.map(col => (
              <TableHead
                key={col.key}
                scope="col"
                aria-sort={sortKey === col.key ? (sortDir === 'desc' ? 'descending' : 'ascending') : 'none'}
                className="cursor-pointer hover:text-foreground select-none"
                onClick={() => handleSort(col.key)}
              >
                <span className="inline-flex items-center gap-1">
                  {col.label}
                  {sortKey === col.key && (
                    <span aria-hidden="true" className="text-xs">{sortDir === 'desc' ? '↓' : '↑'}</span>
                  )}
                  <ColumnTip tip={col.tip} />
                </span>
              </TableHead>
            ))}
          </TableRow>
        </TableHeader>
        <TableBody>
          {sorted.map(o => {
            const costPct      = o.ask / currentPrice * 100
            const contractCost = o.ask * 100
            const be           = getBreakeven(o)
            const isHero       = o.contract === heroContract
            const isNew        = prevContracts.size > 0 && !prevContracts.has(o.contract)

            return (
              <TableRow
                key={o.contract}
                id={isHero ? heroRowId : undefined}
                className={cn(
                  'even:bg-muted/20',
                  isHero && 'bg-gold/10 border-l-2 border-l-gold/60',
                  isNew && !isHero && 'border-l-2 border-l-gain/60',
                )}
                data-new={isNew ? 'true' : undefined}
              >
                <TableCell className="font-bold text-lg">
                  {Math.round(o.return_multiple)}x{isHero ? <span aria-label="top pick"> 👑</span> : ''}
                  {isNew && (
                    <Badge variant="success" className="ml-1.5 text-[10px] py-0 px-1.5 align-middle">NEW</Badge>
                  )}
                </TableCell>
                <TableCell className={probCls(o.prob_itm)}>{(o.prob_itm * 100).toFixed(1)}%</TableCell>
                <TableCell className="font-mono text-sm">{o.expiry}</TableCell>
                <TableCell>${Math.round(o.strike)}</TableCell>
                <TableCell className="font-semibold">${o.ask.toFixed(2)}</TableCell>
                <TableCell className="font-semibold">
                  ${contractCost.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </TableCell>
                <TableCell className="text-muted-foreground">{costPct.toFixed(2)}%</TableCell>
                <TableCell className={beCls(be)}>{be.toFixed(1)}%</TableCell>
                <TableCell className={ivCls(o.iv)}>{(o.iv * 100).toFixed(0)}%</TableCell>
                <TableCell>{o.open_interest.toLocaleString()}</TableCell>
                <TableCell>{o.volume != null ? o.volume.toLocaleString() : '—'}</TableCell>
              </TableRow>
            )
          })}
        </TableBody>
      </Table>
    </TooltipProvider>
  )
}
