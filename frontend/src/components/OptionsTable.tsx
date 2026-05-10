import { useState } from 'react'
import type { Put } from '../types/report'
import { numCls, beCls, ivCls, probCls } from '../utils/colors'

const COLUMNS = [
  { key: 'return_multiple', label: 'Return',        tip: 'Strike price divided by ask price. If the stock hits the strike at expiry, you receive this many times your investment back.' },
  { key: 'prob_itm',        label: 'Prob ITM',      tip: 'Black-Scholes risk-neutral probability this put expires in-the-money. Options are ranked by Return x Prob ITM combined.' },
  { key: 'expiry',          label: 'Expiry',        tip: 'Option expiration date. The put must expire in-the-money to have intrinsic value.' },
  { key: 'strike',          label: 'Strike',        tip: 'The price the stock must fall below for this put to have intrinsic value at expiry.' },
  { key: 'ask',             label: 'Ask',           tip: 'Current asking price per share. One contract = 100 shares, so multiply by 100 for total cost.' },
  { key: 'contract_cost',   label: 'Contract Cost', tip: 'Total cost of one contract in USD (ask x 100 shares). This is the actual cash outlay.' },
  { key: 'cost_pct',        label: 'Cost %',        tip: "Ask as a percentage of the current stock price. How much you are risking relative to the stock's value." },
  { key: 'breakeven_drop_pct', label: 'BE Drop',    tip: "Breakeven drop — how far the stock must fall for you to break even at expiry (strike minus ask, expressed as % below current price)." },
  { key: 'iv',              label: 'IV',            tip: "Implied Volatility — the market's annualised expected price swing baked into the option price." },
  { key: 'open_interest',   label: 'Open Int',      tip: 'Open Interest — total number of outstanding contracts. Higher = more liquid.' },
  { key: 'volume',          label: 'Volume',        tip: 'Contracts traded today. A real-time liquidity signal.' },
]

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
    <div className="overflow-x-auto">
      <table className="table table-zebra table-sm w-full min-w-[900px]">
        <thead>
          <tr className="text-base-content/50">
            {COLUMNS.map(col => (
              <th key={col.key}
                className="cursor-pointer hover:text-primary select-none whitespace-nowrap"
                onClick={() => handleSort(col.key)}
              >
                {col.label}
                {sortKey === col.key && (
                  <span className="ml-1">{sortDir === 'desc' ? '↓' : '↑'}</span>
                )}
                <Tip text={col.tip} />
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {sorted.map(p => {
            const costPct      = p.ask / currentPrice * 100
            const contractCost = p.ask * 100
            const isHero       = p.contract === heroContract
            const isNew        = prevContracts.size > 0 && !prevContracts.has(p.contract)

            return (
              <tr
                key={p.contract}
                id={isHero ? heroRowId : undefined}
                className={[
                  isHero ? 'bg-yellow-400/10 outline outline-1 outline-yellow-400/40' : '',
                  isNew  ? 'border-l-2 border-success/60' : '',
                ].join(' ')}
                data-new={isNew ? 'true' : undefined}
              >
                <td className={`font-bold text-lg ${numCls(p.return_multiple)}`}>
                  {Math.round(p.return_multiple)}x{isHero ? ' 👑' : ''}
                  {isNew && <span className="badge badge-success badge-xs ml-1 font-bold align-middle">NEW</span>}
                </td>
                <td className={probCls(p.prob_itm)}>{(p.prob_itm * 100).toFixed(1)}%</td>
                <td className="font-mono text-sm">{p.expiry}</td>
                <td className={numCls(p.strike)}>${Math.round(p.strike)}</td>
                <td className={`font-semibold ${numCls(p.ask)}`}>${p.ask.toFixed(2)}</td>
                <td className="font-semibold">
                  ${contractCost.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </td>
                <td className="text-info">{costPct.toFixed(2)}%</td>
                <td className={beCls(p.breakeven_drop_pct)}>{p.breakeven_drop_pct.toFixed(1)}%</td>
                <td className={ivCls(p.iv)}>{(p.iv * 100).toFixed(0)}%</td>
                <td>{p.open_interest.toLocaleString()}</td>
                <td>{p.volume != null ? p.volume.toLocaleString() : '—'}</td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}

function Tip({ text }: { text: string }) {
  const [visible, setVisible] = useState(false)
  const [pos, setPos] = useState({ top: 0, left: 0 })

  function show(e: React.MouseEvent) {
    e.stopPropagation()
    const r = (e.currentTarget as HTMLElement).getBoundingClientRect()
    setPos({ top: r.bottom + 8, left: Math.max(8, r.left) })
    setVisible(true)
  }

  return (
    <span
      className="inline-flex cursor-help ml-1"
      onClick={e => e.stopPropagation()}
      onMouseEnter={show}
      onMouseLeave={() => setVisible(false)}
    >
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
        className="inline-block w-3.5 h-3.5 mb-0.5 opacity-30 hover:opacity-70 transition-opacity"
        stroke="currentColor" strokeWidth="2">
        <path strokeLinecap="round" strokeLinejoin="round"
          d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
      </svg>
      {visible && (
        <div
          style={{ position: 'fixed', top: pos.top, left: pos.left, zIndex: 9999 }}
          className="max-w-[260px] px-3 py-2 rounded-lg text-xs leading-relaxed pointer-events-none
                     shadow-xl bg-[#1d232a] text-[#a6adbb] border border-white/10"
        >
          {text}
        </div>
      )}
    </span>
  )
}
