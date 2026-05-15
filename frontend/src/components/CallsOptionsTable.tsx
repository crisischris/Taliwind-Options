import { useState } from 'react'
import { Info } from 'lucide-react'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Badge } from '@/components/ui/badge'
import { TooltipProvider, Tooltip, TooltipTrigger, TooltipContent } from '@/components/ui/tooltip'
import { cn } from '@/lib/utils'
import { CALLS_OPTIONS_TABLE } from '@/constants/strings'
import { beCls, ivCls, probCls } from '@/utils/colors'
import type { Call } from '@/types/report'

type SortDir = 'asc' | 'desc'

function sortValue(c: Call, key: string, currentPrice: number): number | string {
  switch (key) {
    case 'contract_cost':      return c.ask * 100
    case 'cost_pct':           return c.ask / currentPrice * 100
    case 'volume':             return c.volume ?? 0
    case 'expiry':             return c.expiry.replace(/-/g, '')
    default:                   return (c as never)[key] as number | string
  }
}

interface Props {
  calls: Call[]
  currentPrice: number
  heroContract: string
  heroRowId: string
  prevContracts: Set<string>
}

export default function CallsOptionsTable({ calls, currentPrice, heroContract, heroRowId, prevContracts }: Props) {
  const [sortKey, setSortKey] = useState<string | null>(null)
  const [sortDir, setSortDir] = useState<SortDir>('desc')

  function handleSort(key: string) {
    if (sortKey === key) {
      setSortDir(d => (d === 'desc' ? 'asc' : 'desc'))
    } else {
      setSortKey(key)
      setSortDir('desc')
    }
  }

  const sorted = [...calls].sort((a, b) => {
    if (!sortKey) return 0
    const av = sortValue(a, sortKey, currentPrice)
    const bv = sortValue(b, sortKey, currentPrice)
    const an = parseFloat(String(av))
    const bn = parseFloat(String(bv))
    if (!isNaN(an) && !isNaN(bn)) return sortDir === 'desc' ? bn - an : an - bn
    return sortDir === 'desc'
      ? String(bv).localeCompare(String(av))
      : String(av).localeCompare(String(bv))
  })

  return (
    <TooltipProvider delayDuration={0}>
      <Table className="min-w-[900px]">
        <TableHeader>
          <TableRow className="hover:bg-transparent">
            {CALLS_OPTIONS_TABLE.columns.map(col => (
              <TableHead
                key={col.key}
                className="cursor-pointer hover:text-foreground select-none"
                onClick={() => handleSort(col.key)}
              >
                <span className="inline-flex items-center gap-1">
                  {col.label}
                  {sortKey === col.key && (
                    <span className="text-xs">{sortDir === 'desc' ? '↓' : '↑'}</span>
                  )}
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <Info
                        className="h-3.5 w-3.5 opacity-30 hover:opacity-70 cursor-help transition-opacity"
                        onClick={e => e.stopPropagation()}
                      />
                    </TooltipTrigger>
                    <TooltipContent>{col.tip}</TooltipContent>
                  </Tooltip>
                </span>
              </TableHead>
            ))}
          </TableRow>
        </TableHeader>
        <TableBody>
          {sorted.map(c => {
            const costPct      = c.ask / currentPrice * 100
            const contractCost = c.ask * 100
            const isHero       = c.contract === heroContract
            const isNew        = prevContracts.size > 0 && !prevContracts.has(c.contract)

            return (
              <TableRow
                key={c.contract}
                id={isHero ? heroRowId : undefined}
                className={cn(
                  'even:bg-muted/20',
                  isHero && 'bg-gold/10 border-l-2 border-l-gold/60',
                  isNew && !isHero && 'border-l-2 border-l-gain/60',
                )}
                data-new={isNew ? 'true' : undefined}
              >
                <TableCell className="font-bold text-lg">
                  {Math.round(c.return_multiple)}x{isHero ? ' 👑' : ''}
                  {isNew && (
                    <Badge variant="success" className="ml-1.5 text-[10px] py-0 px-1.5 align-middle">NEW</Badge>
                  )}
                </TableCell>
                <TableCell className={probCls(c.prob_itm)}>{(c.prob_itm * 100).toFixed(1)}%</TableCell>
                <TableCell className="font-mono text-sm">{c.expiry}</TableCell>
                <TableCell>${Math.round(c.strike)}</TableCell>
                <TableCell className="font-semibold">${c.ask.toFixed(2)}</TableCell>
                <TableCell className="font-semibold">
                  ${contractCost.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </TableCell>
                <TableCell className="text-muted-foreground">{costPct.toFixed(2)}%</TableCell>
                <TableCell className={beCls(c.breakeven_rise_pct)}>{c.breakeven_rise_pct.toFixed(1)}%</TableCell>
                <TableCell className={ivCls(c.iv)}>{(c.iv * 100).toFixed(0)}%</TableCell>
                <TableCell>{c.open_interest.toLocaleString()}</TableCell>
                <TableCell>{c.volume != null ? c.volume.toLocaleString() : '—'}</TableCell>
              </TableRow>
            )
          })}
        </TableBody>
      </Table>
    </TooltipProvider>
  )
}
