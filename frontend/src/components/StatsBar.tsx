import type { Summary } from '../types/report'

interface Props {
  summary: Summary
  onShowTickers: () => void
}

export default function StatsBar({ summary, onShowTickers }: Props) {
  return (
    <div className="stats stats-vertical sm:stats-horizontal shadow bg-base-200 border border-base-300 mb-8 w-full">
      <div className="stat">
        <div className="stat-figure text-primary">
          <button className="btn btn-ghost btn-circle" onClick={onShowTickers}>
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
              className="inline-block w-8 h-8 stroke-current text-primary">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2"
                d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
          </button>
        </div>
        <div className="stat-title">Tickers Flagged</div>
        <div className="stat-value text-primary">{summary.tickers_flagged}</div>
        <div className="stat-desc">500%+ YTD gainers</div>
      </div>

      <div className="stat">
        <div className="stat-figure text-secondary">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
            className="inline-block w-8 h-8 stroke-current">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2"
              d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4"/>
          </svg>
        </div>
        <div className="stat-title">Short-Dated Puts</div>
        <div className="stat-value text-secondary">{summary.short_puts}</div>
        <div className="stat-desc">Under 6 months to expiry</div>
      </div>

      <div className="stat">
        <div className="stat-figure text-accent">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
            className="inline-block w-8 h-8 stroke-current">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2"
              d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
          </svg>
        </div>
        <div className="stat-title">Long-Dated / LEAPs</div>
        <div className="stat-value text-accent">{summary.long_puts}</div>
        <div className="stat-desc">6+ months to expiry</div>
      </div>
    </div>
  )
}
