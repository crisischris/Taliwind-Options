import { useState } from 'react'
import { Info } from 'lucide-react'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Badge } from '@/components/ui/badge'
import { TooltipProvider, Tooltip, TooltipTrigger, TooltipContent } from '@/components/ui/tooltip'
import { cn } from '@/lib/utils'
import { OPTIONS_TABLE } from '@/constants/strings'
import { beCls, ivCls, probCls } from '@/utils/colors'
import type { Put } from '@/types/report'

type SortDir = 'asc' | 'desc'

function sortValue(p: Put, key: string, currentPrice: number): number | string {
  switch (key) {
    case 'contract_cost': return p.ask * 100
    case 'cost_pct':      return p.ask / currentPrice * 100
    case 'volume':        return p.volume ?? 0
    case 'expiry':        return p.expiry.replace(/-/g, '')
    default:              return (p as never)[key] as number | string
  }
}

interface Props {
  puts: Put[]
  currentPrice: number
  heroContract: string
  heroRowId: string
  prevContracts: Set<string>
}

export default function OptionsTable({ puts, currentPrice, heroContract, heroRowId, prevContracts }: Props) {
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

  const sorted = [...puts].sort((a, b) => {
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
    <TooltipProvider>
      <Table className="min-w-[900px]">
        <TableHeader>
          <TableRow className="hover:bg-transparent">
            {OPTIONS_TABLE.columns.map(col => (
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
          {sorted.map(p => {
            const costPct      = p.ask / currentPrice * 100
            const contractCost = p.ask * 100
            const isHero       = p.contract === heroContract
            const isNew        = prevContracts.size > 0 && !prevContracts.has(p.contract)

            return (
              <TableRow
                key={p.contract}
                id={isHero ? heroRowId : undefined}
                className={cn(
                  "even:bg-muted/20",
                  isHero && "bg-gold/10 border-l-2 border-l-gold/60",
                  isNew && !isHero && "border-l-2 border-l-gain/60",
                )}
                data-new={isNew ? 'true' : undefined}
              >
                <TableCell className="font-bold text-lg">
                  {Math.round(p.return_multiple)}x{isHero ? ' 👑' : ''}
                  {isNew && (
                    <Badge variant="success" className="ml-1.5 text-[10px] py-0 px-1.5 align-middle">NEW</Badge>
                  )}
                </TableCell>
                <TableCell className={probCls(p.prob_itm)}>{(p.prob_itm * 100).toFixed(1)}%</TableCell>
                <TableCell className="font-mono text-sm">{p.expiry}</TableCell>
                <TableCell>${Math.round(p.strike)}</TableCell>
                <TableCell className="font-semibold">${p.ask.toFixed(2)}</TableCell>
                <TableCell className="font-semibold">
                  ${contractCost.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </TableCell>
                <TableCell className="text-muted-foreground">{costPct.toFixed(2)}%</TableCell>
                <TableCell className={beCls(p.breakeven_drop_pct)}>{p.breakeven_drop_pct.toFixed(1)}%</TableCell>
                <TableCell className={ivCls(p.iv)}>{(p.iv * 100).toFixed(0)}%</TableCell>
                <TableCell>{p.open_interest.toLocaleString()}</TableCell>
                <TableCell>{p.volume != null ? p.volume.toLocaleString() : '—'}</TableCell>
              </TableRow>
            )
          })}
        </TableBody>
      </Table>
    </TooltipProvider>
  )
}
