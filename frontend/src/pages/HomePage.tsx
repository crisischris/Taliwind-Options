import { useState } from 'react'
import { TrendingUp, TrendingDown } from 'lucide-react'
import { useManifest, useReport } from '@/hooks/useReport'
import { usePageMeta } from '@/hooks/usePageMeta'
import { Button } from '@/components/ui/button'
import { HERO_CARD, HOME_PAGE, PAGE_META } from '@/constants/strings'
import { track } from '@/lib/analytics'
import HeroCardDeck from '@/components/HeroCardDeck'
import ThemeSelect from '@/components/ThemeSelect'
import type { Page } from '@/components/Navbar'
import type { DeckCard } from '@/components/HeroCardDeck'

interface Props {
  onNavigate: (page: Page, heroRowId?: string) => void
}

export default function HomePage({ onNavigate }: Props) {
  usePageMeta(PAGE_META.home.title, PAGE_META.home.description)

  const [callsThemeId, setCallsThemeId] = useState('ai-momentum')
  const [putsThemeId,  setPutsThemeId]  = useState('mean-reversion')

  const { manifest: putsManifest, error: putsError } = useManifest('puts', putsThemeId)
  const { manifest: callsManifest, error: callsError } = useManifest('calls', callsThemeId)

  const putsId  = putsManifest[0]?.id  ?? null
  const callsId = callsManifest[0]?.id ?? null

  const { report: putsReport }  = useReport('puts',  putsId,  putsManifest,  putsThemeId)
  const { report: callsReport } = useReport('calls', callsId, callsManifest, callsThemeId)

  const callsCards: DeckCard[] = callsReport ? [
    { option: callsReport.heroes.short,    movePct: callsReport.heroes.short?.move_pct    ?? 0, moveLabel: callsReport.heroes.short?.move_label    ?? '', label: HERO_CARD.short.label,    icon: HERO_CARD.short.icon,    heroRowId: 'hero-call-short'    },
    { option: callsReport.heroes.long,     movePct: callsReport.heroes.long?.move_pct     ?? 0, moveLabel: callsReport.heroes.long?.move_label     ?? '', label: HERO_CARD.long.label,     icon: HERO_CARD.long.icon,     heroRowId: 'hero-call-long'     },
    { option: callsReport.heroes.moonshot, movePct: callsReport.heroes.moonshot?.move_pct ?? 0, moveLabel: callsReport.heroes.moonshot?.move_label ?? '', label: HERO_CARD.moonshot.label, icon: HERO_CARD.moonshot.icon, heroRowId: 'hero-call-moonshot' },
  ] : []

  const putsCards: DeckCard[] = putsReport ? [
    { option: putsReport.heroes.short,    movePct: putsReport.heroes.short?.move_pct    ?? 0, moveLabel: putsReport.heroes.short?.move_label    ?? '', label: HERO_CARD.short.label,    icon: HERO_CARD.short.icon,    heroRowId: 'hero-short'    },
    { option: putsReport.heroes.long,     movePct: putsReport.heroes.long?.move_pct     ?? 0, moveLabel: putsReport.heroes.long?.move_label     ?? '', label: HERO_CARD.long.label,     icon: HERO_CARD.long.icon,     heroRowId: 'hero-long'     },
    { option: putsReport.heroes.moonshot, movePct: putsReport.heroes.moonshot?.move_pct ?? 0, moveLabel: putsReport.heroes.moonshot?.move_label ?? '', label: HERO_CARD.moonshot.label, icon: HERO_CARD.moonshot.icon, heroRowId: 'hero-moonshot' },
  ] : []

  return (
    <div className="p-4 sm:p-8">
      <div className="max-w-7xl mx-auto">

        <div className="mb-10">
          <p className="text-muted-foreground">{HOME_PAGE.subtitle}</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-10">

          <section aria-label={HOME_PAGE.callsHeading}>
            <div className="mb-4">
              <div className="flex items-center justify-between">
                <h2 className="flex items-center gap-2 text-xl font-bold">
                  <TrendingUp aria-hidden="true" className="h-5 w-5 text-primary" />
                  {HOME_PAGE.callsHeading}
                </h2>
                <Button variant="outline" size="sm" onClick={() => { track('view_all_clicked', { base: 'calls' }); onNavigate('calls') }}>
                  {HOME_PAGE.viewAll}
                </Button>
              </div>
              <div className="mt-2">
                <ThemeSelect page="calls" value={callsThemeId} onValueChange={setCallsThemeId} showInfo={false} />
              </div>
            </div>
            {callsError  && <p className="text-muted-foreground">{HOME_PAGE.callsEmpty}</p>}
            {!callsError && <HeroCardDeck loading={!callsReport} cards={callsCards} onHeroClick={rowId => onNavigate('calls', rowId)} />}
          </section>

          <section aria-label={HOME_PAGE.putsHeading}>
            <div className="mb-4">
              <div className="flex items-center justify-between">
                <h2 className="flex items-center gap-2 text-xl font-bold">
                  <TrendingDown aria-hidden="true" className="h-5 w-5 text-primary" />
                  {HOME_PAGE.putsHeading}
                </h2>
                <Button variant="outline" size="sm" onClick={() => { track('view_all_clicked', { base: 'puts' }); onNavigate('puts') }}>
                  {HOME_PAGE.viewAll}
                </Button>
              </div>
              <div className="mt-2">
                <ThemeSelect page="puts" value={putsThemeId} onValueChange={setPutsThemeId} showInfo={false} />
              </div>
            </div>
            {putsError  && <p className="text-muted-foreground">{HOME_PAGE.putsEmpty}</p>}
            {!putsError && <HeroCardDeck loading={!putsReport} cards={putsCards} onHeroClick={rowId => onNavigate('puts', rowId)} />}
          </section>

        </div>
      </div>
    </div>
  )
}
