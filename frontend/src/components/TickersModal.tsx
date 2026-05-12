import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Button } from "@/components/ui/button"
import { TICKERS_MODAL } from "@/constants/strings"
import type { Ticker } from "@/types/report"

interface Props {
  tickers: Ticker[]
  onClose: () => void
}

export default function TickersModal({ tickers, onClose }: Props) {
  return (
    <Dialog open onOpenChange={open => !open && onClose()}>
      <DialogContent className="max-w-sm">
        <DialogHeader>
          <DialogTitle>{TICKERS_MODAL.title}</DialogTitle>
        </DialogHeader>

        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>{TICKERS_MODAL.colTicker}</TableHead>
              <TableHead>{TICKERS_MODAL.colYtdGain}</TableHead>
              <TableHead>{TICKERS_MODAL.colPutsFound}</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {tickers.map(t => {
              const shortCount = t.puts.filter(p => p.term === 'short').length
              const longCount  = t.puts.filter(p => p.term === 'long').length
              const sign       = t.gain_pct >= 0 ? '+' : ''
              return (
                <TableRow key={t.ticker}>
                  <TableCell className="font-bold">{t.ticker}</TableCell>
                  <TableCell className="text-gain">{sign}{Math.round(t.gain_pct)}%</TableCell>
                  <TableCell className="text-muted-foreground">{shortCount}s / {longCount}l</TableCell>
                </TableRow>
              )
            })}
          </TableBody>
        </Table>

        <div className="flex justify-end pt-2">
          <Button variant="outline" size="sm" onClick={onClose}>{TICKERS_MODAL.close}</Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}
