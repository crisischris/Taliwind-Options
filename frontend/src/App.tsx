import { useState, useEffect, useCallback } from 'react'
import { useManifest, useReport } from './hooks/useReport'
import StatsBar from './components/StatsBar'
import DiffBar from './components/DiffBar'
import HeroCard from './components/HeroCard'
import TickerCard from './components/TickerCard'
import TickersModal from './components/TickersModal'

export default function App() {
  const { manifest, error } = useManifest()
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [newOnly, setNewOnly]       = useState(false)
  const [showModal, setShowModal]   = useState(false)

  // Sync selectedId from hash on load and manifest change
  useEffect(() => {
    if (!manifest.length) return
    const hashId = location.hash.slice(1)
    const target = manifest.find(m => m.id === hashId)?.id ?? manifest[0]?.id ?? null
    setSelectedId(target)
  }, [manifest])

  // Hash routing
  useEffect(() => {
    function onHashChange() {
      const id = location.hash.slice(1)
      if (id && manifest.find(m => m.id === id)) setSelectedId(id)
    }
    window.addEventListener('hashchange', onHashChange)
    return () => window.removeEventListener('hashchange', onHashChange)
  }, [manifest])

  function selectReport(id: string) {
    location.hash = id
    setSelectedId(id)
    setNewOnly(false)
  }

  const { report, diff } = useReport(selectedId, manifest)

  const scrollToHero = useCallback((id: string) => {
    const row = document.getElementById(id)
    if (!row) return
    let el: HTMLElement | null = row.parentElement
    while (el) {
      const cb = el.querySelector<HTMLInputElement>(':scope > input[type="checkbox"]')
      if (cb && !cb.checked) cb.checked = true
      el = el.parentElement
    }
    row.scrollIntoView({ behavior: 'smooth', block: 'center' })
    row.classList.remove('hero-flash')
    void row.offsetWidth
    row.classList.add('hero-flash')
  }, [])

  const newTickers  = report ? report.tickers.filter(t => !diff.prevTickers.has(t.ticker)).length : 0
  const newPuts     = report ? report.tickers.flatMap(t => t.puts).filter(p => !diff.prevContracts.has(p.contract)).length : 0
  const hasNewItems = newTickers > 0 || newPuts > 0

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center" data-theme="night">
        <p className="text-base-content/50">No reports found — run the scanner to generate one.</p>
      </div>
    )
  }

  const shortHero    = report?.heroes.short?.contract    ?? ''
  const longHero     = report?.heroes.long?.contract     ?? ''
  const moonshotHero = report?.heroes.moonshot?.contract ?? ''

  return (
    <div className="min-h-screen p-4 sm:p-8" data-theme="night">
      <div className="max-w-7xl mx-auto">

        {/* Header */}
        <div className="mb-8 flex flex-col sm:flex-row sm:items-start justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Put Scan Reports</h1>
            <p className="text-base-content/50 text-sm mt-1">
              {report ? `Generated ${report.generated_at.replace('_', ' at ')}` : 'Loading…'}
            </p>
          </div>
          <select
            className="select select-bordered select-sm w-full sm:w-80 shrink-0"
            value={selectedId ?? ''}
            onChange={e => selectReport(e.target.value)}
          >
            {manifest.map(r => (
              <option key={r.id} value={r.id}>
                {r.generated_at.replace('_', ' at ')} — {r.tickers_flagged} tickers, {(r.short_puts ?? 0) + (r.long_puts ?? 0)} puts
              </option>
            ))}
          </select>
        </div>

        {report && (
          <>
            <StatsBar
              summary={report.summary}
              onShowTickers={() => setShowModal(true)}
            />

            <DiffBar tickers={report.tickers} diff={diff} />

            {/* Heroes */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
              <HeroCard put={report.heroes.short}    label="Best Short-Dated"           icon="⚡" heroRowId="hero-short"    onScrollTo={scrollToHero} />
              <HeroCard put={report.heroes.long}     label="Best Long-Dated / LEAP"     icon="🚀" heroRowId="hero-long"     onScrollTo={scrollToHero} />
              <HeroCard put={report.heroes.moonshot} label="Top Moonshot — return only" icon="🎰" heroRowId="hero-moonshot" onScrollTo={scrollToHero} />
            </div>

            {/* Toolbar */}
            <div className="flex justify-end gap-2 mb-4">
              {hasNewItems && diff.prevContracts.size > 0 && (
                <button
                  className={`btn btn-sm btn-ghost btn-outline ${newOnly ? 'btn-active' : ''}`}
                  onClick={() => setNewOnly(v => !v)}
                >
                  New Only
                </button>
              )}
              <button className="btn btn-sm btn-ghost btn-outline"
                onClick={() => document.querySelectorAll<HTMLInputElement>('.collapse input[type="checkbox"]')
                  .forEach(cb => { cb.checked = true })}>
                Expand All
              </button>
              <button className="btn btn-sm btn-ghost btn-outline"
                onClick={() => document.querySelectorAll<HTMLInputElement>('.collapse input[type="checkbox"]')
                  .forEach(cb => { cb.checked = false })}>
                Collapse All
              </button>
            </div>

            {/* Ticker cards */}
            <div>
              {report.tickers.map(ticker => (
                <TickerCard
                  key={ticker.ticker}
                  ticker={ticker}
                  shortHeroContract={shortHero}
                  longHeroContract={longHero}
                  moonshotHeroContract={moonshotHero}
                  prevContracts={diff.prevContracts}
                  prevTickers={diff.prevTickers}
                  newOnly={newOnly}
                />
              ))}
            </div>
          </>
        )}
      </div>

      {showModal && report && (
        <TickersModal tickers={report.tickers} onClose={() => setShowModal(false)} />
      )}
    </div>
  )
}
