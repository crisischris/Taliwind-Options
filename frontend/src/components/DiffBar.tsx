import type { Ticker } from '../types/report'
import type { DiffSets } from '../hooks/useReport'

interface Props {
  tickers: Ticker[]
  diff: DiffSets
}

export default function DiffBar({ tickers, diff }: Props) {
  const { prevContracts, prevTickers, prevReportId } = diff
  if (prevContracts.size === 0) return null

  const newPuts    = tickers.flatMap(t => t.puts).filter(p => !prevContracts.has(p.contract)).length
  const newTickers = tickers.filter(t => !prevTickers.has(t.ticker)).length
  const prevLabel  = prevReportId?.replace('put-scan-', '').replace('_', ' at ') ?? ''

  const parts: string[] = []
  if (newTickers > 0) parts.push(`${newTickers} new ticker${newTickers !== 1 ? 's' : ''}`)
  if (newPuts > 0)    parts.push(`${newPuts} new put${newPuts !== 1 ? 's' : ''}`)

  return (
    <div className="alert bg-base-200 border border-base-300 mb-6 text-sm flex flex-wrap items-center gap-3">
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
        className="w-4 h-4 shrink-0 stroke-current opacity-50">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2"
          d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
      </svg>
      <span>
        vs <span className="font-mono text-base-content/60">{prevLabel}</span>
        {' — '}
        {parts.length > 0
          ? parts.map((p, i) => (
              <span key={i}>
                {i > 0 && ', '}
                <span className="font-semibold text-success">{p}</span>
              </span>
            ))
          : <span className="text-base-content/50">no new items</span>
        }
      </span>
    </div>
  )
}
