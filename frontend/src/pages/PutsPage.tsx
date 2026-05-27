import { OPTIONS_TABLE, PUTS_PAGE } from '@/constants/strings'
import ReportPage, { type ScanConfig } from '@/pages/ReportPage'
import type { Put, PutTicker } from '@/types/report'

const CONFIG: ScanConfig = {
  base:         'puts',
  strings:      PUTS_PAGE,
  columns:      OPTIONS_TABLE.columns,
  getOptions:   t => (t as PutTicker).puts,
  getBreakeven: o => (o as Put).breakeven_drop_pct,
}

export default function PutsPage() {
  return <ReportPage config={CONFIG} />
}
