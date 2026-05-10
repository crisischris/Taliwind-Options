import type { Put } from '../types/report'
import { ivCls, probCls } from '../utils/colors'

interface HeroPut extends Put {
  gain_pct: number
  current_price: number
}

interface Props {
  put: HeroPut | null
  label: string
  icon: string
  heroRowId: string
  onScrollTo: (id: string) => void
}

export default function HeroCard({ put, label, icon, heroRowId, onScrollTo }: Props) {
  if (!put) return null
  const contractCost = put.ask * 100

  return (
    <div
      className="card bg-gradient-to-br from-yellow-900/40 to-base-200 border-2 border-yellow-400/60 shadow-lg shadow-yellow-400/10 cursor-pointer hover:border-yellow-300/80 transition-colors"
      onClick={() => onScrollTo(heroRowId)}
    >
      <div className="card-body">
        <div className="flex items-center gap-3 mb-2">
          <span className="text-2xl">{icon}</span>
          <h2 className="card-title text-yellow-300/70 text-sm font-semibold uppercase tracking-widest">
            {label} — click to jump to row
          </h2>
        </div>

        <div className="flex flex-wrap items-baseline gap-4 mb-4">
          <span className="text-yellow-300 text-5xl font-black tracking-tight">{put.ticker}</span>
          <span className="badge badge-warning badge-outline text-sm font-semibold">
            +{Math.round(put.gain_pct)}% YTD
          </span>
          <span className="text-base-content/40 text-sm">@ ${put.current_price.toFixed(2)}</span>
        </div>

        <div className="flex flex-wrap gap-6">
          <div>
            <div className="text-yellow-300 text-4xl font-black">{Math.round(put.return_multiple)}x</div>
            <div className="text-base-content/50 text-xs uppercase tracking-wide mt-1">Return Multiple</div>
          </div>
          <div>
            <div className={`${probCls(put.prob_itm)} text-4xl font-black`}>
              {(put.prob_itm * 100).toFixed(1)}%
            </div>
            <div className="text-base-content/50 text-xs uppercase tracking-wide mt-1">Prob ITM</div>
          </div>

          <div className="divider divider-horizontal hidden sm:flex" />

          <div>
            <div className="text-success text-2xl font-bold">${put.ask.toFixed(2)}</div>
            <div className="text-base-content/50 text-xs uppercase tracking-wide mt-1">Ask / Share</div>
          </div>
          <div>
            <div className="text-success text-2xl font-bold">
              ${contractCost.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </div>
            <div className="text-base-content/50 text-xs uppercase tracking-wide mt-1">Contract Cost</div>
          </div>
          <div>
            <div className="text-base-content text-2xl font-bold">${Math.round(put.strike)}</div>
            <div className="text-base-content/50 text-xs uppercase tracking-wide mt-1">Strike</div>
          </div>
          <div>
            <div className="text-base-content text-2xl font-bold">{put.expiry}</div>
            <div className="text-base-content/50 text-xs uppercase tracking-wide mt-1">Expiry</div>
          </div>
          <div>
            <div className={`${ivCls(put.iv)} text-2xl font-bold`}>{(put.iv * 100).toFixed(0)}%</div>
            <div className="text-base-content/50 text-xs uppercase tracking-wide mt-1">IV</div>
          </div>
        </div>

        <div className="mt-3 font-mono text-xs text-base-content/30">{put.contract}</div>
      </div>
    </div>
  )
}
