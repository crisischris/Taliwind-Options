import { useManifest, usePutsReport, useCallsReport } from '@/hooks/useReport'
import HeroCard from '@/components/HeroCard'
import CallsHeroCard from '@/components/CallsHeroCard'
import { Button } from '@/components/ui/button'
import { HERO_CARD, CALLS_HERO_CARD, HOME_PAGE } from '@/constants/strings'
import type { Page } from '@/components/Navbar'

interface Props {
  onNavigate: (page: Page) => void
}

export default function HomePage({ onNavigate }: Props) {
  const { manifest: putsManifest, error: putsError } = useManifest('puts')
  const { manifest: callsManifest, error: callsError } = useManifest('calls')

  const putsId  = putsManifest[0]?.id  ?? null
  const callsId = callsManifest[0]?.id ?? null

  const { report: putsReport } = usePutsReport(putsId, putsManifest)
  const { report: callsReport } = useCallsReport(callsId, callsManifest)

  // HeroCard/CallsHeroCard normally scroll to the detail row on click; no detail rows exist on
  // the home page so the callback is intentionally a no-op.
  const noop = () => {}

  return (
    <div className="p-4 sm:p-8">
      <div className="max-w-7xl mx-auto">

        {/* Page header */}
        <div className="mb-10">
          <p className="text-muted-foreground">{HOME_PAGE.subtitle}</p>
        </div>

        {/* Calls section */}
        <section className="mb-12">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold">{HOME_PAGE.callsHeading}</h2>
            <Button variant="outline" size="sm" onClick={() => onNavigate('calls')}>
              {HOME_PAGE.viewAll}
            </Button>
          </div>

          {callsError && <p className="text-muted-foreground">{HOME_PAGE.callsEmpty}</p>}

          {!callsError && callsReport && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <CallsHeroCard call={callsReport.heroes.short}    label={CALLS_HERO_CARD.short.label}    icon={CALLS_HERO_CARD.short.icon}    heroRowId="hero-short"    onScrollTo={noop} />
              <CallsHeroCard call={callsReport.heroes.long}     label={CALLS_HERO_CARD.long.label}     icon={CALLS_HERO_CARD.long.icon}     heroRowId="hero-long"     onScrollTo={noop} />
              <CallsHeroCard call={callsReport.heroes.moonshot} label={CALLS_HERO_CARD.moonshot.label} icon={CALLS_HERO_CARD.moonshot.icon} heroRowId="hero-moonshot" onScrollTo={noop} />
            </div>
          )}

          {!callsError && !callsReport && <p className="text-muted-foreground">{HOME_PAGE.loading}</p>}
        </section>

        {/* Puts section */}
        <section>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold">{HOME_PAGE.putsHeading}</h2>
            <Button variant="outline" size="sm" onClick={() => onNavigate('puts')}>
              {HOME_PAGE.viewAll}
            </Button>
          </div>

          {putsError && <p className="text-muted-foreground">{HOME_PAGE.putsEmpty}</p>}

          {!putsError && putsReport && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <HeroCard put={putsReport.heroes.short}    label={HERO_CARD.short.label}    icon={HERO_CARD.short.icon}    heroRowId="hero-short"    onScrollTo={noop} />
              <HeroCard put={putsReport.heroes.long}     label={HERO_CARD.long.label}     icon={HERO_CARD.long.icon}     heroRowId="hero-long"     onScrollTo={noop} />
              <HeroCard put={putsReport.heroes.moonshot} label={HERO_CARD.moonshot.label} icon={HERO_CARD.moonshot.icon} heroRowId="hero-moonshot" onScrollTo={noop} />
            </div>
          )}

          {!putsError && !putsReport && <p className="text-muted-foreground">{HOME_PAGE.loading}</p>}
        </section>

      </div>
    </div>
  )
}
