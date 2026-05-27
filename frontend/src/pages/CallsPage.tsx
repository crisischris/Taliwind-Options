import { CALLS_OPTIONS_TABLE, CALLS_PAGE } from '@/constants/strings'
import ReportPage, { type ScanConfig } from '@/pages/ReportPage'
import type { Call, CallTicker } from '@/types/report'

const CONFIG: ScanConfig = {
  base:         'calls',
  strings:      CALLS_PAGE,
  columns:      CALLS_OPTIONS_TABLE.columns,
  getOptions:   t => (t as CallTicker).calls,
  getBreakeven: o => (o as Call).breakeven_rise_pct,
}

export default function CallsPage() {
  return <ReportPage config={CONFIG} />
}
