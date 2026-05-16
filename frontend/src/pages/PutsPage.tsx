import { useState, useEffect, useCallback, useRef } from 'react'
import { formatTimestamp, getScanLabel } from '@/utils/timestamp'
import { useManifest, useReport } from '@/hooks/useReport'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'
import { HERO_CARD, PUTS_PAGE, OPTIONS_TABLE } from '@/constants/strings'
import PutsFiltersSheet from '@/components/PutsFiltersSheet'
import HeroCardDeck from '@/components/HeroCardDeck'
import ScanBadge from '@/components/ScanBadge'
import TickerCard, { type ExpansionOverride } from '@/components/TickerCard'
import type { Put } from '@/types/report'

export default function PutsPage() {
  // Read hero row from hash on mount (format: #puts;hero-short). useRef so it
  // doesn't cause a re-render when consumed and survives across report fetches.
  const pendingHeroRef = useRef<string | null>(location.hash.slice(1).split(';')[1] ?? null)
  const { manifest, error } = useManifest('puts')
  const [selectedId, setSelectedId]         = useState<string | null>(null)
  const [selectedTicker, setSelectedTicker] = useState<string | null>(null)
  const [newOnly, setNewOnly]               = useState(false)
  const [expansion, setExpansion]           = useState<ExpansionOverride | null>(null)

  useEffect(() => {
    if (!manifest.length) return
    const hashId = location.hash.slice(1).split(';')[0]
    const target = manifest.find(m => m.id === hashId)?.id ?? manifest[0]?.id ?? null
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setSelectedId(target)
  }, [manifest])

  useEffect(() => {
    function onHashChange() {
      const id = location.hash.slice(1)
      if (id && manifest.find(m => m.id === id)) setSelectedId(id)
    }
    window.addEventListener('hashchange', onHashChange)
    return () => window.removeEventListener('hashchange', onHashChange)
  }, [manifest])

  // eslint-disable-next-line react-hooks/set-state-in-effect
  useEffect(() => { setSelectedTicker(null) }, [selectedId])

  function selectReport(id: string) {
    location.hash = id
    setSelectedId(id)
    setNewOnly(false)
  }

  const { report, diff } = useReport('puts', selectedId, manifest)

  function scrollTickerTabIntoView(ticker: string) {
    document.getElementById(`ticker-tab-${ticker}`)
      ?.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' })
  }

  const scrollToHero = useCallback((heroRowId: string) => {
    if (report) {
      const heroTicker =
        heroRowId === 'hero-short'    ? report.heroes.short?.ticker
        : heroRowId === 'hero-long'   ? report.heroes.long?.ticker
        : report.heroes.moonshot?.ticker
      if (heroTicker) {
        setSelectedTicker(heroTicker)
        scrollTickerTabIntoView(heroTicker)
      }
    }
    setExpansion(p => ({ open: true, v: (p?.v ?? 0) + 1 }))
    setTimeout(() => {
      const row = document.getElementById(heroRowId)
      if (!row) return
      row.scrollIntoView({ behavior: 'smooth', block: 'center' })
      row.classList.remove('hero-flash')
      void row.offsetWidth
      row.classList.add('hero-flash')
    }, 50)
  }, [report])

  useEffect(() => {
    if (!pendingHeroRef.current || !report) return
    const rowId = pendingHeroRef.current
    pendingHeroRef.current = null
    const heroTicker =
      rowId === 'hero-short'  ? report.heroes.short?.ticker
      : rowId === 'hero-long' ? report.heroes.long?.ticker
      : report.heroes.moonshot?.ticker
    setExpansion(p => ({ open: true, v: (p?.v ?? 0) + 1 }))
    setTimeout(() => {
      if (heroTicker) {
        setSelectedTicker(heroTicker)
        scrollTickerTabIntoView(heroTicker)
      }
      setTimeout(() => {
        const row = document.getElementById(rowId)
        if (!row) return
        row.scrollIntoView({ behavior: 'smooth', block: 'center' })
        row.classList.remove('hero-flash')
        void row.offsetWidth
        row.classList.add('hero-flash')
        location.hash = 'puts'
      }, 150)
    }, 0)
  }, [report])

  const shortHero    = report?.heroes.short?.contract    ?? ''
  const longHero     = report?.heroes.long?.contract     ?? ''
  const moonshotHero = report?.heroes.moonshot?.contract ?? ''

  // Compute which tickers are visible (applying newOnly filter)
  const visibleTickers = report
    ? report.tickers.filter(t => {
        if (!newOnly) return true
        const isNew = diff.prevTickers.size > 0 && !diff.prevTickers.has(t.ticker)
        const hasNewPuts = diff.prevContracts.size > 0 && t.puts.some(p => !diff.prevContracts.has(p.contract))
        return isNew || hasNewPuts
      })
    : []

  // Active ticker: use selectedTicker if still visible, else fall back to first
  const activeTicker = visibleTickers.find(t => t.ticker === selectedTicker) ?? visibleTickers[0] ?? null

  // Sync selectedTicker state whenever activeTicker resolves differently
  useEffect(() => {
    if (activeTicker && activeTicker.ticker !== selectedTicker) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setSelectedTicker(activeTicker.ticker)
    }
  }, [activeTicker, selectedTicker])

  const hasNewItems = report
    ? report.tickers.some(t => {
        const isNew = diff.prevTickers.size > 0 && !diff.prevTickers.has(t.ticker)
        const hasNew = diff.prevContracts.size > 0 && t.puts.some(p => !diff.prevContracts.has(p.contract))
        return isNew || hasNew
      })
    : false

  if (error) {
    return (
      <div className="flex items-center justify-center py-32">
        <p className="text-muted-foreground">{PUTS_PAGE.empty}</p>
      </div>
    )
  }

  return (
    <div className="p-4 sm:p-8">
      <div className="max-w-7xl mx-auto">

        {/* Page header */}
        <div className="mb-8 flex flex-col sm:flex-row sm:items-start justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">{PUTS_PAGE.title}</h1>
            <div className="flex items-center gap-2 text-muted-foreground text-sm mt-1">
              {report && <ScanBadge />}
              {report ? `Generated ${formatTimestamp(report.generated_at)}` : PUTS_PAGE.loading}
            </div>
          </div>
          <div className="flex flex-col gap-1 w-full sm:w-80 shrink-0">
            <select
              className={cn(
                "rounded-md border border-input bg-card text-sm px-3 py-1.5",
                "w-full focus:outline-none focus:ring-2 focus:ring-ring",
              )}
              value={selectedId ?? ''}
              onChange={e => selectReport(e.target.value)}
            >
              {manifest.map(r => (
                <option key={r.id} value={r.id}>
                  {getScanLabel()} — {formatTimestamp(r.generated_at)} — {r.tickers_flagged} tickers
                </option>
              ))}
            </select>
            {diff.prevContracts.size > 0 && report && (() => {
              const newT = report.tickers.filter(t => !diff.prevTickers.has(t.ticker)).length
              const newP = report.tickers.flatMap(t => t.puts).filter(p => !diff.prevContracts.has(p.contract)).length
              const prevLabel = diff.prevReportId ? formatTimestamp(diff.prevReportId.replace('put-scan-', '')) : ''
              const parts = [
                newT > 0 && `${newT} new ticker${newT !== 1 ? 's' : ''}`,
                newP > 0 && `${newP} new put${newP !== 1 ? 's' : ''}`,
              ].filter(Boolean)
              return (
                <p className="text-xs text-muted-foreground px-0.5">
                  vs <span className="font-mono">{prevLabel}</span>
                  {' — '}
                  {parts.length > 0
                    ? parts.map((p, i) => (
                        <span key={i}>
                          {i > 0 && ', '}
                          <span className="font-semibold text-gain">{p}</span>
                        </span>
                      ))
                    : PUTS_PAGE.noNewItems
                  }
                </p>
              )
            })()}
          </div>
        </div>

        {(report || !error) && (
          <>
            {/* Hero cards */}
            <div className="mb-8">
              <HeroCardDeck
                loading={!report}
                cards={report ? [
                  { option: report.heroes.short,    movePct: report.heroes.short?.gain_pct    ?? 0, moveLabel: '(1Y)', label: HERO_CARD.short.label,    icon: HERO_CARD.short.icon,    heroRowId: 'hero-short'    },
                  { option: report.heroes.long,     movePct: report.heroes.long?.gain_pct     ?? 0, moveLabel: '(1Y)', label: HERO_CARD.long.label,     icon: HERO_CARD.long.icon,     heroRowId: 'hero-long'     },
                  { option: report.heroes.moonshot, movePct: report.heroes.moonshot?.gain_pct ?? 0, moveLabel: '(1Y)', label: HERO_CARD.moonshot.label, icon: HERO_CARD.moonshot.icon, heroRowId: 'hero-moonshot' },
                ] : []}
                onHeroClick={scrollToHero}
                desktopGrid
              />
            </div>

            {/* Toolbar */}
            <div className="flex justify-end gap-2 mb-0">
              <PutsFiltersSheet />
              {hasNewItems && diff.prevContracts.size > 0 && (
                <Button variant={newOnly ? 'secondary' : 'outline'} size="sm"
                  onClick={() => setNewOnly(v => !v)}>
                  {PUTS_PAGE.newOnly}
                </Button>
              )}
              <Button variant="outline" size="sm"
                onClick={() => setExpansion(p => ({ open: true,  v: (p?.v ?? 0) + 1 }))}>
                {PUTS_PAGE.expandAll}
              </Button>
              <Button variant="outline" size="sm"
                onClick={() => setExpansion(p => ({ open: false, v: (p?.v ?? 0) + 1 }))}>
                {PUTS_PAGE.collapseAll}
              </Button>
            </div>

            {/* Ticker tabs */}
            <div className="border-b border-border mb-6 mt-3">
              <div className="overflow-x-auto overflow-y-hidden">
                <div className="flex min-w-max">
                  {visibleTickers.map(t => {
                    const isActive    = t.ticker === activeTicker?.ticker
                    const isNewTicker = diff.prevTickers.size > 0 && !diff.prevTickers.has(t.ticker)
                    const newPuts     = diff.prevContracts.size > 0
                      ? t.puts.filter(p => !diff.prevContracts.has(p.contract)).length
                      : 0
                    return (
                      <button
                        key={t.ticker}
                        id={`ticker-tab-${t.ticker}`}
                        className={cn(
                          "flex items-center gap-1.5 px-3 py-2.5 text-sm whitespace-nowrap",
                          "border-b-2 -mb-px transition-colors",
                          isActive
                            ? "border-primary text-foreground font-semibold"
                            : "border-transparent text-muted-foreground hover:text-foreground hover:border-border",
                        )}
                        onClick={() => setSelectedTicker(t.ticker)}
                      >
                        {t.ticker}
                        <span className={cn("text-xs font-normal", t.gain_pct >= 0 ? "text-gain" : "text-loss")}>
                          {t.gain_pct >= 0 ? '+' : ''}{Math.round(t.gain_pct)}% (1Y)
                        </span>
                        {isNewTicker && (
                          <Badge variant="success" className="text-[9px] py-0 px-1 h-4 leading-none">NEW</Badge>
                        )}
                        {!isNewTicker && newPuts > 0 && (
                          <Badge variant="success" className="text-[9px] py-0 px-1 h-4 leading-none">{newPuts}</Badge>
                        )}
                      </button>
                    )
                  })}
                </div>
              </div>
            </div>

            {/* Active ticker detail */}
            {activeTicker && (
              <TickerCard
                key={activeTicker.ticker}
                ticker={activeTicker.ticker}
                currentPrice={activeTicker.current_price}
                options={activeTicker.puts}
                optionLabel="put"
                columns={OPTIONS_TABLE.columns}
                getBreakeven={(p: Put) => p.breakeven_drop_pct}
                shortHero={{ contract: shortHero, rowId: 'hero-short' }}
                longHero={{ contract: longHero, rowId: 'hero-long' }}
                moonshotHero={{ contract: moonshotHero, rowId: 'hero-moonshot' }}
                prevContracts={diff.prevContracts}
                prevTickers={diff.prevTickers}
                newOnly={newOnly}
                expansionOverride={expansion}
              />
            )}
          </>
        )}
      </div>

    </div>
  )
}
