import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { HERO_CARD } from "@/constants/strings"
import { ivCls, probCls } from "@/utils/colors"
import type { Put } from "@/types/report"

interface HeroPut extends Put {
  gain_pct: number
  current_price: number
}

interface Props {
  put: HeroPut | null
  label: string
  icon: string
  heroRowId: string
  onScrollTo: (id: string) => void
}

export default function HeroCard({ put, label, icon, heroRowId, onScrollTo }: Props) {
  if (!put) return null
  const contractCost = put.ask * 100

  return (
    <Card
      className="border-2 border-gold/40 bg-gradient-to-br from-gold/10 to-card shadow-lg shadow-gold/10 cursor-pointer hover:border-gold/60 transition-colors"
      onClick={() => onScrollTo(heroRowId)}
    >
      <CardContent className="p-5">
        <div className="flex items-center gap-3 mb-2">
          <span className="text-2xl">{icon}</span>
          <p className="text-xs font-semibold uppercase tracking-widest text-gold/80">{label}</p>
        </div>

        <div className="flex flex-wrap items-baseline gap-4 mb-4">
          <span className="text-gold text-5xl font-black tracking-tight">{put.ticker}</span>
          <Badge variant="gold" className="text-sm font-semibold">
            +{Math.round(put.gain_pct)}% (1Y)
          </Badge>
          <span className="text-muted-foreground text-sm">@ ${put.current_price.toFixed(2)}</span>
        </div>

        <div className="flex flex-wrap gap-6">
          <div>
            <div className="text-gold text-4xl font-black">{Math.round(put.return_multiple)}x</div>
            <div className="text-muted-foreground text-xs uppercase tracking-wide mt-1">{HERO_CARD.stats.returnMultiple}</div>
          </div>
          <div>
            <div className={`${probCls(put.prob_itm)} text-4xl font-black`}>
              {(put.prob_itm * 100).toFixed(1)}%
            </div>
            <div className="text-muted-foreground text-xs uppercase tracking-wide mt-1">{HERO_CARD.stats.probItm}</div>
          </div>

          <div className="hidden sm:block w-px bg-border self-stretch mx-2" />

          <div>
            <div className="text-gain text-2xl font-bold">${put.ask.toFixed(2)}</div>
            <div className="text-muted-foreground text-xs uppercase tracking-wide mt-1">{HERO_CARD.stats.askPerShare}</div>
          </div>
          <div>
            <div className="text-gain text-2xl font-bold">
              ${contractCost.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </div>
            <div className="text-muted-foreground text-xs uppercase tracking-wide mt-1">{HERO_CARD.stats.contractCost}</div>
          </div>
          <div>
            <div className="text-2xl font-bold">${Math.round(put.strike)}</div>
            <div className="text-muted-foreground text-xs uppercase tracking-wide mt-1">{HERO_CARD.stats.strike}</div>
          </div>
          <div>
            <div className="text-2xl font-bold">{put.expiry}</div>
            <div className="text-muted-foreground text-xs uppercase tracking-wide mt-1">{HERO_CARD.stats.expiry}</div>
          </div>
          <div>
            <div className={`${ivCls(put.iv)} text-2xl font-bold`}>{(put.iv * 100).toFixed(0)}%</div>
            <div className="text-muted-foreground text-xs uppercase tracking-wide mt-1">{HERO_CARD.stats.iv}</div>
          </div>
        </div>

        <div className="mt-3 font-mono text-xs text-muted-foreground/40">{put.contract}</div>
      </CardContent>
    </Card>
  )
}
