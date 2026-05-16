import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { HERO_CARD } from '@/constants/strings'
import { ivCls, probCls } from '@/utils/colors'

export interface BaseHeroOption {
  contract: string
  ticker: string
  current_price: number
  return_multiple: number
  prob_itm: number
  ask: number
  strike: number
  expiry: string
  iv: number
}

interface Props {
  option: BaseHeroOption | null
  movePct: number
  moveLabel: string
  label: string
  icon: string
  heroRowId: string
  onScrollTo: (id: string) => void
}

export default function HeroCard({ option, movePct, moveLabel, label, icon, heroRowId, onScrollTo }: Props) {
  if (!option) return null
  const contractCost = option.ask * 100
  const returnStr = option.return_multiple >= 1000
    ? `${(option.return_multiple / 1000).toFixed(1)}K`
    : `${Math.round(option.return_multiple)}`

  return (
    <Card
      className="h-full border-2 border-gold/40 bg-gradient-to-br from-gold/10 to-card shadow-lg shadow-gold/10 cursor-pointer hover:border-gold/60 transition-colors"
      onClick={() => onScrollTo(heroRowId)}
    >
      <CardContent className="p-5 h-full flex flex-col">
        <div className="flex items-center gap-3 mb-2">
          <span className="text-2xl">{icon}</span>
          <p className="text-xs font-semibold uppercase tracking-widest text-gold/80">{label}</p>
        </div>

        <div className="flex flex-wrap items-baseline gap-4 mb-4">
          <span className="text-gold text-5xl font-black tracking-tight">{option.ticker}</span>
          <Badge variant="gold" className="text-sm font-semibold">
            +{Math.round(movePct)}% {moveLabel}
          </Badge>
          <span className="text-muted-foreground text-sm">@ ${option.current_price.toFixed(2)}</span>
        </div>

        <div className="flex flex-wrap gap-6 mt-auto">
          <div>
            <div className="text-gold text-4xl font-black">{returnStr}x</div>
            <div className="text-muted-foreground text-xs uppercase tracking-wide mt-1">{HERO_CARD.stats.returnMultiple}</div>
          </div>
          <div>
            <div className={`${probCls(option.prob_itm)} text-4xl font-black`}>
              {(option.prob_itm * 100).toFixed(1)}%
            </div>
            <div className="text-muted-foreground text-xs uppercase tracking-wide mt-1">{HERO_CARD.stats.probItm}</div>
          </div>

          <div className="hidden sm:block w-px bg-border self-stretch mx-2" />

          <div>
            <div className="text-gain text-2xl font-bold">${option.ask.toFixed(2)}</div>
            <div className="text-muted-foreground text-xs uppercase tracking-wide mt-1">{HERO_CARD.stats.askPerShare}</div>
          </div>
          <div>
            <div className="text-gain text-2xl font-bold">
              ${contractCost.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </div>
            <div className="text-muted-foreground text-xs uppercase tracking-wide mt-1">{HERO_CARD.stats.contractCost}</div>
          </div>
          <div>
            <div className="text-2xl font-bold">${Math.round(option.strike)}</div>
            <div className="text-muted-foreground text-xs uppercase tracking-wide mt-1">{HERO_CARD.stats.strike}</div>
          </div>
          <div>
            <div className="text-2xl font-bold">{option.expiry}</div>
            <div className="text-muted-foreground text-xs uppercase tracking-wide mt-1">{HERO_CARD.stats.expiry}</div>
          </div>
          <div>
            <div className={`${ivCls(option.iv)} text-2xl font-bold`}>{(option.iv * 100).toFixed(0)}%</div>
            <div className="text-muted-foreground text-xs uppercase tracking-wide mt-1">{HERO_CARD.stats.iv}</div>
          </div>
        </div>

        <div className="mt-3 font-mono text-xs text-muted-foreground/40">{option.contract}</div>
      </CardContent>
    </Card>
  )
}
