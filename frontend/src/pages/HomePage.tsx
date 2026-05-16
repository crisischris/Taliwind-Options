import { useState } from 'react'
import { TrendingUp, TrendingDown, ChevronLeft, ChevronRight } from 'lucide-react'
import { useManifest, useReport } from '@/hooks/useReport'
import HeroCard from '@/components/HeroCard'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { HERO_CARD, HOME_PAGE } from '@/constants/strings'
import type { Page } from '@/components/Navbar'
import type { BaseHeroOption } from '@/components/HeroCard'

interface Props {
  onNavigate: (page: Page, heroRowId?: string) => void
}

interface DeckCard {
  option: BaseHeroOption | null
  movePct: number
  moveLabel: string
  label: string
  icon: string
  heroRowId: string
}

function HeroCardDeck({ cards, onHeroClick }: { cards: DeckCard[]; onHeroClick: (heroRowId: string) => void }) {
  const [active, setActive] = useState(0)
  const prev = () => setActive(i => (i - 1 + cards.length) % cards.length)
  const next = () => setActive(i => (i + 1) % cards.length)

  return (
    <div>
      {/* pb/pr gives offset silhouettes room to show below/right the front card */}
      <div className="pb-7 pr-7">
        <div className="relative">
          {/* Silhouettes: solid bg-card + gold border only — zero transparency */}
          {cards.length > 2 && (
            <div className="absolute inset-0 rounded-lg border-2 border-gold/40 bg-card pointer-events-none"
              style={{ transform: 'translate(28px, 28px)', zIndex: 1 }} />
          )}
          {cards.length > 1 && (
            <div className="absolute inset-0 rounded-lg border-2 border-gold/40 bg-card pointer-events-none"
              style={{ transform: 'translate(14px, 14px)', zIndex: 2 }} />
          )}
          {/* Opaque backing layer so the HeroCard gradient has no bleed-through */}
          <div className="relative rounded-lg bg-card" style={{ zIndex: 3 }}>
            <HeroCard {...cards[active]} onScrollTo={onHeroClick} />
          </div>
        </div>
      </div>

      {cards.length > 1 && (
        <div className="flex items-center justify-center gap-3 mt-2">
          <button
            onClick={prev}
            className={cn(
              'rounded-full border border-border p-1.5 transition-colors',
              'hover:bg-accent hover:border-accent-foreground/20',
            )}
            aria-label="Previous"
          >
            <ChevronLeft className="h-4 w-4 text-muted-foreground" />
          </button>
          <span className="text-xs text-muted-foreground tabular-nums w-8 text-center">
            {active + 1} / {cards.length}
          </span>
          <button
            onClick={next}
            className={cn(
              'rounded-full border border-border p-1.5 transition-colors',
              'hover:bg-accent hover:border-accent-foreground/20',
            )}
            aria-label="Next"
          >
            <ChevronRight className="h-4 w-4 text-muted-foreground" />
          </button>
        </div>
      )}
    </div>
  )
}

export default function HomePage({ onNavigate }: Props) {
  const { manifest: putsManifest, error: putsError } = useManifest('puts')
  const { manifest: callsManifest, error: callsError } = useManifest('calls')

  const putsId  = putsManifest[0]?.id  ?? null
  const callsId = callsManifest[0]?.id ?? null

  const { report: putsReport }  = useReport('puts',  putsId,  putsManifest)
  const { report: callsReport } = useReport('calls', callsId, callsManifest)

  const callsCards: DeckCard[] = callsReport ? [
    { option: callsReport.heroes.short,    movePct: callsReport.heroes.short?.momentum_pct    ?? 0, moveLabel: '90d', label: HERO_CARD.short.label,    icon: HERO_CARD.short.icon,    heroRowId: 'hero-call-short'    },
    { option: callsReport.heroes.long,     movePct: callsReport.heroes.long?.momentum_pct     ?? 0, moveLabel: '90d', label: HERO_CARD.long.label,     icon: HERO_CARD.long.icon,     heroRowId: 'hero-call-long'     },
    { option: callsReport.heroes.moonshot, movePct: callsReport.heroes.moonshot?.momentum_pct ?? 0, moveLabel: '90d', label: HERO_CARD.moonshot.label, icon: HERO_CARD.moonshot.icon, heroRowId: 'hero-call-moonshot' },
  ] : []

  const putsCards: DeckCard[] = putsReport ? [
    { option: putsReport.heroes.short,    movePct: putsReport.heroes.short?.gain_pct    ?? 0, moveLabel: '(1Y)', label: HERO_CARD.short.label,    icon: HERO_CARD.short.icon,    heroRowId: 'hero-short'    },
    { option: putsReport.heroes.long,     movePct: putsReport.heroes.long?.gain_pct     ?? 0, moveLabel: '(1Y)', label: HERO_CARD.long.label,     icon: HERO_CARD.long.icon,     heroRowId: 'hero-long'     },
    { option: putsReport.heroes.moonshot, movePct: putsReport.heroes.moonshot?.gain_pct ?? 0, moveLabel: '(1Y)', label: HERO_CARD.moonshot.label, icon: HERO_CARD.moonshot.icon, heroRowId: 'hero-moonshot' },
  ] : []

  return (
    <div className="p-4 sm:p-8">
      <div className="max-w-7xl mx-auto">

        <div className="mb-10">
          <p className="text-muted-foreground">{HOME_PAGE.subtitle}</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-10">

          <section>
            <div className="flex items-center justify-between mb-6">
              <h2 className="flex items-center gap-2 text-xl font-bold">
                <TrendingUp className="h-5 w-5 text-primary" />
                {HOME_PAGE.callsHeading}
              </h2>
              <Button variant="outline" size="sm" onClick={() => onNavigate('calls')}>
                {HOME_PAGE.viewAll}
              </Button>
            </div>
            {callsError  && <p className="text-muted-foreground">{HOME_PAGE.callsEmpty}</p>}
            {!callsError && !callsReport && <p className="text-muted-foreground">{HOME_PAGE.loading}</p>}
            {!callsError && callsReport  && <HeroCardDeck cards={callsCards} onHeroClick={rowId => onNavigate('calls', rowId)} />}
          </section>

          <section>
            <div className="flex items-center justify-between mb-6">
              <h2 className="flex items-center gap-2 text-xl font-bold">
                <TrendingDown className="h-5 w-5 text-primary" />
                {HOME_PAGE.putsHeading}
              </h2>
              <Button variant="outline" size="sm" onClick={() => onNavigate('puts')}>
                {HOME_PAGE.viewAll}
              </Button>
            </div>
            {putsError  && <p className="text-muted-foreground">{HOME_PAGE.putsEmpty}</p>}
            {!putsError && !putsReport && <p className="text-muted-foreground">{HOME_PAGE.loading}</p>}
            {!putsError && putsReport  && <HeroCardDeck cards={putsCards} onHeroClick={rowId => onNavigate('puts', rowId)} />}
          </section>

        </div>
      </div>
    </div>
  )
}
