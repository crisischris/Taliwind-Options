import type { Ticker } from '../types/report'

interface Props {
  tickers: Ticker[]
  onClose: () => void
}

export default function TickersModal({ tickers, onClose }: Props) {
  return (
    <dialog className="modal modal-open">
      <div className="modal-box">
        <h3 className="font-bold text-lg mb-4">Tickers Flagged</h3>
        <table className="table table-sm w-full">
          <thead>
            <tr><th>Ticker</th><th>YTD Gain</th><th>Puts Found</th></tr>
          </thead>
          <tbody>
            {tickers.map(t => {
              const shortCount = t.puts.filter(p => p.term === 'short').length
              const longCount  = t.puts.filter(p => p.term === 'long').length
              const sign       = t.gain_pct >= 0 ? '+' : ''
              return (
                <tr key={t.ticker}>
                  <td className="font-bold">{t.ticker}</td>
                  <td className="text-success">{sign}{Math.round(t.gain_pct)}%</td>
                  <td className="text-base-content/60">{shortCount}s / {longCount}l</td>
                </tr>
              )
            })}
          </tbody>
        </table>
        <div className="modal-action">
          <button className="btn btn-sm" onClick={onClose}>Close</button>
        </div>
      </div>
      <div className="modal-backdrop" onClick={onClose} />
    </dialog>
  )
}
