import { useState } from 'react'
import type { Ticker } from '../types/report'
import OptionsTable from './OptionsTable'

interface Props {
  ticker: Ticker
  shortHeroContract: string
  longHeroContract: string
  moonshotHeroContract: string
  prevContracts: Set<string>
  prevTickers: Set<string>
  newOnly: boolean
}

export default function TickerCard({
  ticker, shortHeroContract, longHeroContract, moonshotHeroContract,
  prevContracts, prevTickers, newOnly,
}: Props) {
  const [open, setOpen] = useState(true)
  const [shortOpen, setShortOpen] = useState(true)
  const [longOpen, setLongOpen] = useState(true)
  const [moonshotOpen, setMoonshotOpen] = useState(true)

  const short     = ticker.puts.filter(p => p.term === 'short')
  const long_     = ticker.puts.filter(p => p.term === 'long')
  const moonshots = ticker.puts.filter(p => p.term === 'moonshot')

  const isNewTicker = prevTickers.size > 0 && !prevTickers.has(ticker.ticker)
  const newPutCount = prevContracts.size > 0
    ? ticker.puts.filter(p => !prevContracts.has(p.contract)).length
    : 0
  const hasNew = isNewTicker || newPutCount > 0

  if (newOnly && !hasNew) return null

  const gainSign = ticker.gain_pct >= 0 ? '+' : ''
  const gainCls  = ticker.gain_pct >= 0 ? 'text-success' : 'text-error'

  return (
    <div className="collapse collapse-arrow bg-base-200 border border-base-300 rounded-xl mb-4">
      <input type="checkbox" checked={open} onChange={e => setOpen(e.target.checked)} />
      <div className="collapse-title flex flex-wrap items-center gap-2 gap-x-3">
        <span className="text-xl font-bold">{ticker.ticker}</span>
        <span className={`badge badge-lg ${gainCls} badge-outline font-semibold`}>
          {gainSign}{Math.round(ticker.gain_pct)}% YTD
        </span>
        {isNewTicker
          ? <span className="badge badge-success badge-sm font-bold">NEW TICKER</span>
          : newPutCount > 0
            ? <span className="badge badge-success badge-outline badge-sm font-semibold">{newPutCount} new</span>
            : null
        }
        <span className="text-base-content/50 text-sm">Current: ${ticker.current_price.toFixed(2)}</span>
        <div className="ml-auto flex items-center gap-3">
          <div className="relative z-10 flex gap-1" onClick={e => e.stopPropagation()}>
            <button className="btn btn-xs btn-ghost opacity-40 hover:opacity-90"
              onClick={() => { setShortOpen(true); setLongOpen(true); setMoonshotOpen(true) }}>
              expand
            </button>
            <button className="btn btn-xs btn-ghost opacity-40 hover:opacity-90"
              onClick={() => { setShortOpen(false); setLongOpen(false); setMoonshotOpen(false) }}>
              collapse
            </button>
          </div>
          <span className="text-base-content/40 text-xs">
            {ticker.puts.length} put{ticker.puts.length !== 1 ? 's' : ''}
          </span>
        </div>
      </div>

      <div className="collapse-content px-0 pb-0">
        {short.length > 0 && (
          <TermSection label="⚡ Short-Dated < 6 months" labelCls="text-base-content/50"
            count={short.length} open={shortOpen} onToggle={setShortOpen} borderTop={false}>
            <OptionsTable puts={short} currentPrice={ticker.current_price}
              heroContract={shortHeroContract} heroRowId="hero-short"
              prevContracts={prevContracts} />
          </TermSection>
        )}
        {long_.length > 0 && (
          <TermSection label="🚀 Long-Dated / LEAPs 6+ months" labelCls="text-base-content/50"
            count={long_.length} open={longOpen} onToggle={setLongOpen} borderTop={short.length > 0}>
            <OptionsTable puts={long_} currentPrice={ticker.current_price}
              heroContract={longHeroContract} heroRowId="hero-long"
              prevContracts={prevContracts} />
          </TermSection>
        )}
        {moonshots.length > 0 && (
          <TermSection label="🎰 Moonshots — return only" labelCls="text-warning/70"
            count={moonshots.length} open={moonshotOpen} onToggle={setMoonshotOpen}
            borderTop={short.length > 0 || long_.length > 0}>
            <OptionsTable puts={moonshots} currentPrice={ticker.current_price}
              heroContract={moonshotHeroContract} heroRowId="hero-moonshot"
              prevContracts={prevContracts} />
          </TermSection>
        )}
      </div>
    </div>
  )
}

interface TermSectionProps {
  label: string
  labelCls: string
  count: number
  open: boolean
  onToggle: (v: boolean) => void
  borderTop: boolean
  children: React.ReactNode
}

function TermSection({ label, labelCls, count, open, onToggle, borderTop, children }: TermSectionProps) {
  return (
    <div className={`collapse collapse-arrow ${borderTop ? 'border-t border-base-300' : ''}`}>
      <input type="checkbox" checked={open} onChange={e => onToggle(e.target.checked)} />
      <div className={`collapse-title min-h-0 py-2 px-4 text-xs font-semibold ${labelCls} uppercase tracking-wider flex items-center gap-2`}>
        {label} <span className="font-normal normal-case opacity-60">({count})</span>
      </div>
      <div className="collapse-content px-0 pb-0">{children}</div>
    </div>
  )
}
