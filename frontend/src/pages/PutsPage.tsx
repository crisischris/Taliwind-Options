import { OPTIONS_TABLE, PUTS_PAGE } from '@/constants/strings'
import PutsFiltersSheet from '@/components/PutsFiltersSheet'
import ReportPage, { type ScanConfig } from '@/pages/ReportPage'
import ThemeSelect from '@/components/ThemeSelect'
import type { Put, PutTicker } from '@/types/report'

const CONFIG: ScanConfig = {
  base:          'puts',
  heroIdPrefix:  '',
  moveLabel:     '(1Y)',
  themeSelector: <ThemeSelect page="puts" />,
  strings:       PUTS_PAGE,
  columns:       OPTIONS_TABLE.columns,
  FiltersSheet:  PutsFiltersSheet,
  getOptions:    t => (t as PutTicker).puts,
  getMovePct:    t => (t as PutTicker).gain_pct,
  getHeroMovePct: h => (h as unknown as { gain_pct: number } | null)?.gain_pct ?? 0,
  getBreakeven:  o => (o as Put).breakeven_drop_pct,
}

export default function PutsPage() {
  return <ReportPage config={CONFIG} />
}
