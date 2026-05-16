import { useState, useEffect, useCallback, useRef } from 'react'
import { formatTimestamp, getScanLabel } from '@/utils/timestamp'
import { useManifest, useReport } from '@/hooks/useReport'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'
import { CALLS_PAGE, HERO_CARD, CALLS_OPTIONS_TABLE } from '@/constants/strings'
import HeroCardDeck from '@/components/HeroCardDeck'
import ScanBadge from '@/components/ScanBadge'
import TickerCard, { type ExpansionOverride } from '@/components/TickerCard'
import CallsFiltersSheet from '@/components/CallsFiltersSheet'
import type { Call } from '@/types/report'

export default function CallsPage() {
  const pendingHeroRef = useRef<string | null>(location.hash.slice(1).split(';')[1] ?? null)
  const { manifest, error } = useManifest('calls')
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

  const { report, diff } = useReport('calls', selectedId, manifest)

  const scrollToHero = useCallback((heroRowId: string) => {
    if (report) {
      const heroTicker =
        heroRowId === 'hero-call-short'    ? report.heroes.short?.ticker
        : heroRowId === 'hero-call-long'   ? report.heroes.long?.ticker
        : report.heroes.moonshot?.ticker
      if (heroTicker) setSelectedTicker(heroTicker)
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
      rowId === 'hero-call-short'  ? report.heroes.short?.ticker
      : rowId === 'hero-call-long' ? report.heroes.long?.ticker
      : report.heroes.moonshot?.ticker
    setExpansion(p => ({ open: true, v: (p?.v ?? 0) + 1 }))
    setTimeout(() => {
      if (heroTicker) setSelectedTicker(heroTicker)
      setTimeout(() => {
        const row = document.getElementById(rowId)
        if (!row) return
        row.scrollIntoView({ behavior: 'smooth', block: 'center' })
        row.classList.remove('hero-flash')
        void row.offsetWidth
        row.classList.add('hero-flash')
        location.hash = 'calls'
      }, 150)
    }, 0)
  }, [report])

  const shortHero    = report?.heroes.short?.contract    ?? ''
  const longHero     = report?.heroes.long?.contract     ?? ''
  const moonshotHero = report?.heroes.moonshot?.contract ?? ''

  const visibleTickers = report
    ? report.tickers.filter(t => {
        if (!newOnly) return true
        const isNew    = diff.prevTickers.size > 0 && !diff.prevTickers.has(t.ticker)
        const hasNew   = diff.prevContracts.size > 0 && t.calls.some(c => !diff.prevContracts.has(c.contract))
        return isNew || hasNew
      })
    : []

  const activeTicker = visibleTickers.find(t => t.ticker === selectedTicker) ?? visibleTickers[0] ?? null

  useEffect(() => {
    if (activeTicker && activeTicker.ticker !== selectedTicker) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setSelectedTicker(activeTicker.ticker)
    }
  }, [activeTicker, selectedTicker])

  const hasNewItems = report
    ? report.tickers.some(t => {
        const isNew  = diff.prevTickers.size > 0 && !diff.prevTickers.has(t.ticker)
        const hasNew = diff.prevContracts.size > 0 && t.calls.some(c => !diff.prevContracts.has(c.contract))
        return isNew || hasNew
      })
    : false

  if (error) {
    return (
      <div className="flex items-center justify-center py-32">
        <p className="text-muted-foreground">{CALLS_PAGE.empty}</p>
      </div>
    )
  }

  return (
    <div className="p-4 sm:p-8">
      <div className="max-w-7xl mx-auto">

        {/* Page header */}
        <div className="mb-8 flex flex-col sm:flex-row sm:items-start justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">{CALLS_PAGE.title}</h1>
            <div className="flex items-center gap-2 text-muted-foreground text-sm mt-1">
              {report && <ScanBadge />}
              {report ? `Generated ${formatTimestamp(report.generated_at)}` : CALLS_PAGE.loading}
            </div>
          </div>
          <div className="flex flex-col gap-1 w-full sm:w-80 shrink-0">
            <select
              className={cn(
                'rounded-md border border-input bg-card text-sm px-3 py-1.5',
                'w-full focus:outline-none focus:ring-2 focus:ring-ring',
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
              const newC = report.tickers.flatMap(t => t.calls).filter(c => !diff.prevContracts.has(c.contract)).length
              const prevLabel = diff.prevReportId ? formatTimestamp(diff.prevReportId.replace('call-scan-', '')) : ''
              const parts = [
                newT > 0 && `${newT} new ticker${newT !== 1 ? 's' : ''}`,
                newC > 0 && `${newC} new call${newC !== 1 ? 's' : ''}`,
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
                    : CALLS_PAGE.noNewItems
                  }
                </p>
              )
            })()}
          </div>
        </div>

        {report && (
          <>
            {/* Hero cards */}
            <div className="mb-8">
              <HeroCardDeck
                cards={[
                  { option: report.heroes.short,    movePct: report.heroes.short?.momentum_pct    ?? 0, moveLabel: '90d', label: HERO_CARD.short.label,    icon: HERO_CARD.short.icon,    heroRowId: 'hero-call-short'    },
                  { option: report.heroes.long,     movePct: report.heroes.long?.momentum_pct     ?? 0, moveLabel: '90d', label: HERO_CARD.long.label,     icon: HERO_CARD.long.icon,     heroRowId: 'hero-call-long'     },
                  { option: report.heroes.moonshot, movePct: report.heroes.moonshot?.momentum_pct ?? 0, moveLabel: '90d', label: HERO_CARD.moonshot.label, icon: HERO_CARD.moonshot.icon, heroRowId: 'hero-call-moonshot' },
                ]}
                onHeroClick={scrollToHero}
              />
            </div>

            {/* Toolbar */}
            <div className="flex justify-end gap-2 mb-0">
              <CallsFiltersSheet />
              {hasNewItems && diff.prevContracts.size > 0 && (
                <Button variant={newOnly ? 'secondary' : 'outline'} size="sm"
                  onClick={() => setNewOnly(v => !v)}>
                  {CALLS_PAGE.newOnly}
                </Button>
              )}
              <Button variant="outline" size="sm"
                onClick={() => setExpansion(p => ({ open: true,  v: (p?.v ?? 0) + 1 }))}>
                {CALLS_PAGE.expandAll}
              </Button>
              <Button variant="outline" size="sm"
                onClick={() => setExpansion(p => ({ open: false, v: (p?.v ?? 0) + 1 }))}>
                {CALLS_PAGE.collapseAll}
              </Button>
            </div>

            {/* Ticker tabs */}
            <div className="border-b border-border mb-6 mt-3">
              <div className="overflow-x-auto overflow-y-hidden">
                <div className="flex min-w-max">
                  {visibleTickers.map(t => {
                    const isActive    = t.ticker === activeTicker?.ticker
                    const isNewTicker = diff.prevTickers.size > 0 && !diff.prevTickers.has(t.ticker)
                    const newCalls    = diff.prevContracts.size > 0
                      ? t.calls.filter(c => !diff.prevContracts.has(c.contract)).length
                      : 0
                    return (
                      <button
                        key={t.ticker}
                        className={cn(
                          'flex items-center gap-1.5 px-3 py-2.5 text-sm whitespace-nowrap',
                          'border-b-2 -mb-px transition-colors',
                          isActive
                            ? 'border-primary text-foreground font-semibold'
                            : 'border-transparent text-muted-foreground hover:text-foreground hover:border-border',
                        )}
                        onClick={() => setSelectedTicker(t.ticker)}
                      >
                        {t.ticker}
                        <span className="text-xs font-normal text-gain">
                          +{Math.round(t.momentum_pct)}% (90d)
                        </span>
                        {isNewTicker && (
                          <Badge variant="success" className="text-[9px] py-0 px-1 h-4 leading-none">NEW</Badge>
                        )}
                        {!isNewTicker && newCalls > 0 && (
                          <Badge variant="success" className="text-[9px] py-0 px-1 h-4 leading-none">{newCalls}</Badge>
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
                options={activeTicker.calls}
                optionLabel="call"
                columns={CALLS_OPTIONS_TABLE.columns}
                getBreakeven={(c: Call) => c.breakeven_rise_pct}
                shortHero={{ contract: shortHero, rowId: 'hero-call-short' }}
                longHero={{ contract: longHero, rowId: 'hero-call-long' }}
                moonshotHero={{ contract: moonshotHero, rowId: 'hero-call-moonshot' }}
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
