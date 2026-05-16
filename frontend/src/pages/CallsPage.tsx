import { CALLS_OPTIONS_TABLE, CALLS_PAGE } from '@/constants/strings'
import CallsFiltersSheet from '@/components/CallsFiltersSheet'
import ReportPage, { type ScanConfig } from '@/pages/ReportPage'
import type { Call, CallTicker } from '@/types/report'

const CONFIG: ScanConfig = {
  base:          'calls',
  heroIdPrefix:  'call-',
  moveLabel:     '90d',
  strings:       CALLS_PAGE,
  columns:       CALLS_OPTIONS_TABLE.columns,
  FiltersSheet:  CallsFiltersSheet,
  getOptions:    t => (t as CallTicker).calls,
  getMovePct:    t => (t as CallTicker).momentum_pct,
  getHeroMovePct: h => (h as unknown as { momentum_pct: number } | null)?.momentum_pct ?? 0,
  getBreakeven:  o => (o as Call).breakeven_rise_pct,
}

export default function CallsPage() {
  return <ReportPage config={CONFIG} />
}
