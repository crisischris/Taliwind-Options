export interface ThemeDefinition {
  id: string
  name: string
  shortName: string  // compact label for BottomNav
  tagline: string    // one-line descriptor shown in collapsed banner header
  thesis: string     // full paragraph shown when banner is expanded
  icon: string
  page: 'puts' | 'calls'
  stub?: boolean     // scanner not yet built — show coming-soon state
}

export const THEMES: ThemeDefinition[] = [
  // ── Puts themes ──────────────────────────────────────────────────────────
  {
    id: 'mean-reversion',
    name: 'Mean Reversion',
    shortName: 'Mean Rev.',
    tagline: 'Cheap OTM puts on extreme gainers',
    thesis:
      'Stocks with 500%+ trailing 12-month gains tend to mean-revert. The move may be fundamental, but the options market regularly underprices downside risk on extreme gainers. This scanner finds those names and surfaces cheap out-of-the-money puts on them. The setup is asymmetric — small premium at risk, large payoff if the correction plays out.',
    icon: '📉',
    page: 'puts',
  },
  {
    id: 'earnings-fades',
    name: 'Earnings Fades',
    shortName: 'Earnings',
    tagline: 'OTM puts on post-earnings gap-ups',
    thesis:
      'Stocks that gap up sharply on earnings often retrace as the initial excitement fades and the market revisits forward guidance. This scanner targets names that popped more than 15% on their last release and surfaces cheap OTM puts ahead of the next catalyst — a contrarian bet that the market overreacted to the print.',
    icon: '📊',
    page: 'puts',
    stub: true,
  },

  // ── Calls themes ─────────────────────────────────────────────────────────
  {
    id: 'ai-momentum',
    name: 'AI Momentum',
    shortName: 'AI Mom.',
    tagline: 'Cheap calls on AI and AI-adjacent names',
    thesis:
      'Macro tailwinds in AI, space, and disruptive tech create asymmetric upside in smaller, lesser-known names. This scanner finds tickers held across leading thematic ETFs — ARKK, ARKX, ARKQ, SMH, AIQ, BOTZ, and ROKT — that are showing strong 90-day momentum, and surfaces cheap out-of-the-money calls on them. The setup is a trend-continuation bet — small premium at risk, large payoff if the run extends.',
    icon: '🚀',
    page: 'calls',
  },
  {
    id: 'biotech-breakouts',
    name: 'Biotech Breakouts',
    shortName: 'Biotech',
    tagline: 'Cheap calls on biotech names near catalyst events',
    thesis:
      'Binary events — FDA decisions, Phase 3 readouts, PDUFA dates — create explosive upside potential in biotech. This scanner identifies names with upcoming catalyst windows and surfaces cheap OTM calls that offer asymmetric upside if the trial succeeds or approval comes through. One approval can move a small-cap 10x overnight.',
    icon: '🧬',
    page: 'calls',
    stub: true,
  },
]

export function themesForPage(page: 'puts' | 'calls'): ThemeDefinition[] {
  return THEMES.filter(t => t.page === page)
}

export function themeForPage(page: 'puts' | 'calls'): ThemeDefinition {
  return THEMES.find(t => t.page === page && !t.stub)!
}

export function themeById(id: string): ThemeDefinition | undefined {
  return THEMES.find(t => t.id === id)
}
