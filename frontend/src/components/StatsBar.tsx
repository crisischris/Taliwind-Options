import { Info } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { TooltipProvider, Tooltip, TooltipTrigger, TooltipContent } from "@/components/ui/tooltip"
import type { Summary } from "@/types/report"
import { STATS_BAR } from "@/constants/strings"

interface Props {
  summary: Summary
  onShowTickers: () => void
}

interface StatProps {
  label: string
  value: number
  description: string
  action?: React.ReactNode
}

function Stat({ label, value, description, action }: StatProps) {
  return (
    <div className="flex flex-col gap-1 p-4 sm:p-6 flex-1">
      <div className="flex items-center justify-between">
        <p className="text-sm text-muted-foreground">{label}</p>
        {action}
      </div>
      <p className="text-3xl font-bold">{value}</p>
      <p className="text-xs text-muted-foreground">{description}</p>
    </div>
  )
}

export default function StatsBar({ summary, onShowTickers }: Props) {
  return (
    <Card className="flex flex-col sm:flex-row divide-y sm:divide-y-0 sm:divide-x mb-6">
      <Stat
        label={STATS_BAR.tickersFlagged.label}
        value={summary.tickers_flagged}
        description={STATS_BAR.tickersFlagged.description}
        action={
          <TooltipProvider delayDuration={0}>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button variant="ghost" size="icon" className="h-6 w-6" onClick={onShowTickers}>
                  <Info className="h-4 w-4" />
                </Button>
              </TooltipTrigger>
              <TooltipContent>Click to see flagged tickers</TooltipContent>
            </Tooltip>
          </TooltipProvider>
        }
      />
      <Stat label={STATS_BAR.shortPuts.label} value={summary.short_puts}  description={STATS_BAR.shortPuts.description} />
      <Stat label={STATS_BAR.longPuts.label}  value={summary.long_puts}   description={STATS_BAR.longPuts.description} />
    </Card>
  )
}
