import React, { useState, useEffect, useCallback, useRef, type ComponentType } from 'react'
import { track } from '@/lib/analytics'
import { formatTimestamp, getScanLabel } from '@/utils/timestamp'
import { useManifest, useReport } from '@/hooks/useReport'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { SunriseIcon, MiddayIcon } from '@/components/ScanBadge'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { cn } from '@/lib/utils'
import { HERO_CARD, PAGE_META } from '@/constants/strings'
import { usePageMeta } from '@/hooks/usePageMeta'
import HeroCardDeck from '@/components/HeroCardDeck'
import TickerCard, { type ExpansionOverride } from '@/components/TickerCard'
import type { BaseHeroOption } from '@/components/HeroCard'
import type { PutTicker, CallTicker, BaseOption } from '@/types/report'

type AnyTicker = PutTicker | CallTicker
type HeroMap   = Record<'short' | 'long' | 'moonshot', { ticker: string; contract: string } | null>

const HERO_TERMS = ['short', 'long', 'moonshot'] as const

export interface ScanConfig {
  base:          'puts' | 'calls'
  heroIdPrefix:  string
  moveLabel:     string
  themeSelector: React.ReactNode
  strings: {
    title:       string
    loading:     string
    empty:       string
    newOnly:     string
    expandAll:   string
    collapseAll: string
    noNewItems:  string
  }
  columns:       readonly { key: string; label: string; tip: string }[]
  FiltersSheet:  ComponentType
  getOptions:    (t: AnyTicker) => BaseOption[]
  getMovePct:    (t: AnyTicker) => number
  getHeroMovePct:(h: BaseHeroOption | null) => number
  getBreakeven:  (o: BaseOption) => number
}

function scrollTickerTabIntoView(ticker: string) {
  document.getElementById(`ticker-tab-${ticker}`)
    ?.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' })
}

function flashRow(rowId: string) {
  const row = document.getElementById(rowId)
  if (!row) return
  row.scrollIntoView({ behavior: 'smooth', block: 'center' })
  row.classList.remove('hero-flash')
  void row.offsetWidth
  row.classList.add('hero-flash')
}

export default function ReportPage({ config }: { config: ScanConfig }) {
  const { base, heroIdPrefix, moveLabel, strings } = config

  usePageMeta(PAGE_META[base].title, PAGE_META[base].description)

  const pendingHeroRef = useRef<string | null>(location.hash.slice(1).split(';')[1] ?? null)
  const { manifest, error } = useManifest(base)
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

  const { report, diff } = useReport(base, selectedId, manifest)

  const scrollToHero = useCallback((heroRowId: string) => {
    track('hero_card_clicked', { base, term: heroRowId.replace(`hero-${heroIdPrefix}`, '') })
    setNewOnly(false)
    if (report) {
      const term = heroRowId.replace(`hero-${heroIdPrefix}`, '') as typeof HERO_TERMS[number]
      const heroTicker = (report.heroes as unknown as HeroMap)[term]?.ticker
      if (heroTicker) {
        setSelectedTicker(heroTicker)
        scrollTickerTabIntoView(heroTicker)
      }
    }
    setExpansion(p => ({ open: true, v: (p?.v ?? 0) + 1 }))
    setTimeout(() => flashRow(heroRowId), 50)
  }, [report, heroIdPrefix])

  // On first load from a deep-link hash (format: #puts;hero-short), scroll to the named hero row.
  // useRef so consuming the pending value doesn't trigger a re-render.
  useEffect(() => {
    if (!pendingHeroRef.current || !report) return
    const rowId = pendingHeroRef.current
    pendingHeroRef.current = null
    const term = rowId.replace(`hero-${heroIdPrefix}`, '') as typeof HERO_TERMS[number]
    const heroTicker = (report.heroes as unknown as HeroMap)[term]?.ticker
    setExpansion(p => ({ open: true, v: (p?.v ?? 0) + 1 }))
    setTimeout(() => {
      if (heroTicker) {
        setSelectedTicker(heroTicker)
        scrollTickerTabIntoView(heroTicker)
      }
      setTimeout(() => {
        flashRow(rowId)
        location.hash = base
      }, 150)
    }, 0)
  }, [report, heroIdPrefix, base])

  const heroes       = report?.heroes as unknown as HeroMap | undefined
  const shortHero    = heroes?.short?.contract    ?? ''
  const longHero     = heroes?.long?.contract     ?? ''
  const moonshotHero = heroes?.moonshot?.contract ?? ''

  const allTickers    = report ? (report.tickers as AnyTicker[]) : []
  // scanLabel is derived per-report from generated_at so morning/midday is accurate regardless of when the page is viewed

  function tickerHasNewContent(t: AnyTicker) {
    const isNew       = diff.prevTickers.size > 0 && !diff.prevTickers.has(t.ticker)
    const hasNewOption = diff.prevContracts.size > 0 && config.getOptions(t).some(o => !diff.prevContracts.has(o.contract))
    return isNew || hasNewOption
  }

  const hasNewItems    = allTickers.some(tickerHasNewContent)
  const visibleTickers = newOnly ? allTickers.filter(tickerHasNewContent) : allTickers
  const activeTicker   = visibleTickers.find(t => t.ticker === selectedTicker) ?? visibleTickers[0] ?? null

  useEffect(() => {
    if (activeTicker && activeTicker.ticker !== selectedTicker) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setSelectedTicker(activeTicker.ticker)
    }
  }, [activeTicker, selectedTicker])

  const optLabel = base === 'puts' ? 'put' : 'call'

  const heroCards = report
    ? HERO_TERMS.map(term => ({
        option:    (report.heroes as unknown as HeroMap)[term] as BaseHeroOption | null,
        movePct:   config.getHeroMovePct((report.heroes as unknown as HeroMap)[term] as BaseHeroOption | null),
        moveLabel,
        label:     HERO_CARD[term].label,
        icon:      HERO_CARD[term].icon,
        heroRowId: `hero-${heroIdPrefix}${term}`,
      }))
    : []

  if (error) {
    return (
      <div className="flex items-center justify-center py-32">
        <p className="text-muted-foreground">{strings.empty}</p>
      </div>
    )
  }

  return (
    <div className="p-4 sm:p-8">
      <div className="max-w-7xl mx-auto">

        <div className="mb-8">
          <h1 className="text-3xl font-bold tracking-tight">{strings.title}</h1>
          <div className="flex items-center gap-2 mt-2">
            {config.themeSelector}
          </div>
          <div className="flex items-center gap-2 mt-1.5">
            {selectedId === manifest[0]?.id && <Badge variant="outline" className="text-xs font-medium">Latest</Badge>}
            {(() => {
              const sel = manifest.find(r => r.id === selectedId)
              const isMorning = sel ? getScanLabel(sel.generated_at) === 'Morning Data' : true
              return (
                <Select
                  value={selectedId ?? ''}
                  onValueChange={id => { track('report_selected', { base, report_id: id }); selectReport(id) }}
                >
                  <SelectTrigger className={cn(
                    'h-7 w-auto gap-1.5 rounded-full border px-3 text-xs font-medium shadow-none focus:ring-0',
                    isMorning
                      ? 'border-gold/40 bg-gold/10 text-gold hover:bg-gold/20'
                      : 'border-border bg-transparent hover:bg-muted',
                  )}>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {manifest.slice(0, 8).map(r => {
                      const morning = getScanLabel(r.generated_at) === 'Morning Data'
                      return (
                        <SelectItem key={r.id} value={r.id}>
                          <span className="flex items-center gap-1.5">
                            {morning
                              ? <SunriseIcon aria-hidden="true" className="h-3 w-auto text-gold" />
                              : <MiddayIcon  aria-hidden="true" className="h-3 w-auto text-muted-foreground" />}
                            {getScanLabel(r.generated_at).replace(' Data', '')} — {formatTimestamp(r.generated_at)}
                          </span>
                        </SelectItem>
                      )
                    })}
                  </SelectContent>
                </Select>
              )
            })()}
          </div>
        </div>

        {(report || !error) && (
          <>
            <div className="mb-8">
              <HeroCardDeck
                loading={!report}
                cards={heroCards}
                onHeroClick={scrollToHero}
                desktopGrid
              />
            </div>

            <div className="flex justify-end gap-2 mb-0">
              <config.FiltersSheet />
              {hasNewItems && diff.prevContracts.size > 0 && (
                <Button variant={newOnly ? 'secondary' : 'outline'} size="sm"
                  aria-pressed={newOnly}
                  onClick={() => { track('new_only_toggled', { base, enabled: !newOnly }); setNewOnly(v => !v) }}>
                  {strings.newOnly}
                </Button>
              )}
              <Button variant="outline" size="sm"
                onClick={() => { track('expand_all_clicked', { base }); setExpansion(p => ({ open: true,  v: (p?.v ?? 0) + 1 })) }}>
                {strings.expandAll}
              </Button>
              <Button variant="outline" size="sm"
                onClick={() => { track('collapse_all_clicked', { base }); setExpansion(p => ({ open: false, v: (p?.v ?? 0) + 1 })) }}>
                {strings.collapseAll}
              </Button>
            </div>

            <div className="border-b border-border mb-6 mt-3">
              <div className="overflow-x-auto overflow-y-hidden">
                <div role="tablist" aria-label="Tickers" className="flex min-w-max">
                  {visibleTickers.map(t => {
                    const isActive    = t.ticker === activeTicker?.ticker
                    const isNewTicker = diff.prevTickers.size > 0 && !diff.prevTickers.has(t.ticker)
                    const newCount    = diff.prevContracts.size > 0
                      ? config.getOptions(t).filter(o => !diff.prevContracts.has(o.contract)).length
                      : 0
                    const movePct = config.getMovePct(t)
                    return (
                      <button
                        key={t.ticker}
                        role="tab"
                        id={`ticker-tab-${t.ticker}`}
                        aria-selected={isActive}
                        aria-controls="ticker-panel"
                        className={cn(
                          'flex items-center gap-1.5 px-3 py-2.5 text-sm whitespace-nowrap',
                          'border-b-2 -mb-px transition-colors',
                          isActive
                            ? 'border-primary text-foreground font-semibold'
                            : 'border-transparent text-muted-foreground hover:text-foreground hover:border-border',
                        )}
                        onClick={() => { track('ticker_tab_clicked', { base, ticker: t.ticker }); setSelectedTicker(t.ticker) }}
                      >
                        {t.ticker}
                        <span className={cn('text-xs font-normal', movePct >= 0 ? 'text-gain' : 'text-loss')}>
                          {movePct >= 0 ? '+' : ''}{Math.round(movePct)}% {moveLabel}
                        </span>
                        {isNewTicker && (
                          <Badge variant="success" className="text-[9px] py-0 px-1 h-4 leading-none">NEW</Badge>
                        )}
                        {!isNewTicker && newCount > 0 && (
                          <Badge variant="success" className="text-[9px] py-0 px-1 h-4 leading-none">{newCount}</Badge>
                        )}
                      </button>
                    )
                  })}
                </div>
              </div>
            </div>

            {activeTicker && (
              <div
                role="tabpanel"
                id="ticker-panel"
                aria-labelledby={`ticker-tab-${activeTicker.ticker}`}
              >
              <TickerCard
                key={activeTicker.ticker}
                ticker={activeTicker.ticker}
                companyName={activeTicker.company_name}
                currentPrice={activeTicker.current_price}
                options={config.getOptions(activeTicker)}
                optionLabel={optLabel}
                columns={config.columns}
                getBreakeven={config.getBreakeven}
                shortHero={{ contract: shortHero, rowId: `hero-${heroIdPrefix}short` }}
                longHero={{ contract: longHero,   rowId: `hero-${heroIdPrefix}long` }}
                moonshotHero={{ contract: moonshotHero, rowId: `hero-${heroIdPrefix}moonshot` }}
                prevContracts={diff.prevContracts}
                prevTickers={diff.prevTickers}
                newOnly={newOnly}
                expansionOverride={expansion}
              />
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}
