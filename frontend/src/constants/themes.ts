export interface JudgementCall {
  rule:   string
  detail: string
}

export interface ThemeDefinition {
  id:       string
  name:     string
  shortName: string
  tagline:  string
  thesis:   string
  icon:     string
  page:     'puts' | 'calls'
  stub?:    boolean
  judgementCalls?: {
    intro: string
    rules: JudgementCall[]
  }
}

export const THEMES: ThemeDefinition[] = [
  // ── Puts themes ──────────────────────────────────────────────────────────
  {
    id:        'mean-reversion',
    name:      'Mean Reversion',
    shortName: 'Mean Rev.',
    tagline:   'Cheap OTM puts on extreme gainers',
    thesis:
      'Stocks with 500%+ trailing 12-month gains tend to mean-revert. The move may be fundamental, but the options market regularly underprices downside risk on extreme gainers. This scanner finds those names and surfaces cheap out-of-the-money puts on them. The setup is asymmetric — small premium at risk, large payoff if the correction plays out.',
    icon: '📉',
    page: 'puts',
    judgementCalls: {
      intro: 'These are the rules baked into the scanner. Each one is a deliberate choice, not a given:',
      rules: [
        { rule: 'Universe',                 detail: 'S&P 500 and NASDAQ 100 constituents only — liquid, well-known names where options markets are active.' },
        { rule: '500%+ over 1 year',        detail: 'The stock must have appreciated at least 500% over the trailing 12 months. Below that threshold the mean-reversion thesis is weaker.' },
        { rule: 'Out-of-the-money puts only', detail: 'We want cheap optionality on a correction, not intrinsic value. ITM puts are excluded.' },
        { rule: 'Expiry between 60 and 1,000 DTE', detail: 'Too short and there is no time for the thesis to play out. Too long and pricing becomes speculative. The sweet spot is roughly 2 months to 3 years out.' },
        { rule: 'Ask ≤ 5% of stock price',  detail: 'Keeps the cost-of-insurance sensible. A put that costs more than 5% of the underlying is already pricing in meaningful downside.' },
        { rule: 'Implied volatility ≤ 200%', detail: 'Extremely high IV means the market is already pricing in a crash. We want names where the put is still relatively cheap.' },
        { rule: 'Minimum liquidity',        detail: 'Open interest ≥ 10, or any volume traded today, or a recorded last price. Catches thinly-traded LEAPs that are still quote-able.' },
        { rule: 'Scored by return × prob ITM', detail: 'Puts are ranked by return multiple (strike ÷ ask) multiplied by Black-Scholes probability of expiring in-the-money. This balances raw upside against realistic odds.' },
        { rule: 'Top 10 per bucket',        detail: 'Short-dated (< 6 months) and long-dated / LEAPs (6+ months) are capped at 10 each, sorted by score. Moonshots — the top 5 by raw return multiple — are surfaced separately.' },
      ],
    },
  },
  {
    id:        'earnings-fades',
    name:      'Earnings Fades',
    shortName: 'Earnings',
    tagline:   'OTM puts on post-earnings gap-ups',
    thesis:
      'Stocks that gap up sharply on earnings often retrace as the initial excitement fades and the market revisits forward guidance. This scanner targets names that popped more than 15% on their last release and surfaces cheap OTM puts ahead of the next catalyst — a contrarian bet that the market overreacted to the print.',
    icon: '📊',
    page: 'puts',
    stub: true,
  },

  // ── Calls themes ─────────────────────────────────────────────────────────
  {
    id:        'ai-momentum',
    name:      'AI Momentum',
    shortName: 'AI Mom.',
    tagline:   'Cheap calls on AI and AI-adjacent names',
    thesis:
      'Macro tailwinds in AI, space, and disruptive tech create asymmetric upside in smaller, lesser-known names. This scanner finds tickers held across leading thematic ETFs — ARKK, ARKX, ARKQ, SMH, AIQ, BOTZ, and ROKT — that are showing strong 90-day momentum, and surfaces cheap out-of-the-money calls on them. The setup is a trend-continuation bet — small premium at risk, large payoff if the run extends.',
    icon: '🚀',
    page: 'calls',
    judgementCalls: {
      intro: 'These are the rules baked into the scanner. Each one is a deliberate choice, not a given:',
      rules: [
        { rule: 'Universe',                 detail: 'Tickers held across ARKK, ARKX, ARKQ, SMH, AIQ, BOTZ, and ROKT ETFs — a cross-section of AI, semiconductors, robotics, and space plays. Holdings are fetched daily via Yahoo Finance and cached.' },
        { rule: '15%+ momentum in 90 days', detail: 'The ticker must be up at least 15% over the trailing 90 days. This confirms the trend is live before we look for calls.' },
        { rule: 'Out-of-the-money calls only', detail: 'We want cheap optionality on a continuation move, not intrinsic value. ITM calls are excluded.' },
        { rule: 'Expiry between 60 and 365 DTE', detail: 'Long enough for the thesis to play out. LEAPs are included — macro trends take time.' },
        { rule: 'Ask ≤ 4% of stock price',  detail: 'Keeps premium cost manageable. These are momentum names with naturally higher volatility, so we allow slightly more than the put scanner.' },
        { rule: 'Implied volatility ≤ 150%', detail: 'High-momentum stocks carry high IV. We accept up to 150% — above that the market is already pricing in a parabolic move.' },
        { rule: 'Minimum liquidity',        detail: 'Open interest ≥ 10, or any volume traded today, or a recorded last price.' },
        { rule: 'Scored by return × prob ITM', detail: 'Calls are ranked by return multiple (strike ÷ ask) multiplied by Black-Scholes probability of expiring in-the-money. This balances raw upside against realistic odds.' },
        { rule: 'Top 10 per bucket',        detail: 'Short-dated (< 6 months) and long-dated / LEAPs (6+ months) are capped at 10 each, sorted by score. Moonshots — the top 5 by raw return multiple — are surfaced separately.' },
      ],
    },
  },
  {
    id:        'biotech-breakouts',
    name:      'Biotech Breakouts',
    shortName: 'Biotech',
    tagline:   'Cheap calls on biotech names near catalyst events',
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
