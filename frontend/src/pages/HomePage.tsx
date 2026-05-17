import { TrendingUp, TrendingDown } from 'lucide-react'
import { useManifest, useReport } from '@/hooks/useReport'
import { Button } from '@/components/ui/button'
import { HERO_CARD, HOME_PAGE } from '@/constants/strings'
import { track } from '@/lib/analytics'
import HeroCardDeck from '@/components/HeroCardDeck'
import type { Page } from '@/components/Navbar'
import type { DeckCard } from '@/components/HeroCardDeck'

interface Props {
  onNavigate: (page: Page, heroRowId?: string) => void
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
              <Button variant="outline" size="sm" onClick={() => { track('view_all_clicked', { base: 'calls' }); onNavigate('calls') }}>
                {HOME_PAGE.viewAll}
              </Button>
            </div>
            {callsError  && <p className="text-muted-foreground">{HOME_PAGE.callsEmpty}</p>}
            {!callsError && <HeroCardDeck loading={!callsReport} cards={callsCards} onHeroClick={rowId => onNavigate('calls', rowId)} />}
          </section>

          <section>
            <div className="flex items-center justify-between mb-6">
              <h2 className="flex items-center gap-2 text-xl font-bold">
                <TrendingDown className="h-5 w-5 text-primary" />
                {HOME_PAGE.putsHeading}
              </h2>
              <Button variant="outline" size="sm" onClick={() => { track('view_all_clicked', { base: 'puts' }); onNavigate('puts') }}>
                {HOME_PAGE.viewAll}
              </Button>
            </div>
            {putsError  && <p className="text-muted-foreground">{HOME_PAGE.putsEmpty}</p>}
            {!putsError && <HeroCardDeck loading={!putsReport} cards={putsCards} onHeroClick={rowId => onNavigate('puts', rowId)} />}
          </section>

        </div>
      </div>
    </div>
  )
}
