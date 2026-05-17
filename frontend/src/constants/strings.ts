export const APP_NAME = 'Tailwind Options'

export const NAVBAR = {
  home:  'Home',
  calls: 'Calls',
  puts:  'Puts',
  about: 'About',
} as const

export const SETTINGS = {
  title:      'Settings',
  appearance: 'Appearance',
  dark:       'Dark mode',
  light:      'Light mode',
} as const

// Shared between puts and calls ticker cards — labels and icons are identical
export const TICKER_CARD = {
  short:    { label: '⚡ Short-Dated < 6 months'       },
  long:     { label: '🚀 Long-Dated / LEAPs 6+ months' },
  moonshot: { label: '🎰 Moonshots — return only'      },
  expand:   'expand',
  collapse: 'collapse',
} as const

const SHARED_OPTION_COLUMNS = [
  { key: 'return_multiple', label: 'Return',        tip: 'Strike price divided by ask price. Options are ranked by Return x Prob ITM combined.' },
  { key: 'prob_itm',        label: 'Prob ITM',      tip: 'Black-Scholes risk-neutral probability this option expires in-the-money.' },
  { key: 'expiry',          label: 'Expiry',        tip: 'Option expiration date.' },
  { key: 'strike',          label: 'Strike',        tip: 'The price the stock must reach for this option to have intrinsic value at expiry.' },
  { key: 'ask',             label: 'Ask',           tip: 'Current asking price per share. One contract = 100 shares, so multiply by 100 for total cost.' },
  { key: 'contract_cost',   label: 'Contract Cost', tip: 'Total cost of one contract in USD (ask x 100 shares). This is the actual cash outlay.' },
  { key: 'cost_pct',        label: 'Cost %',        tip: "Ask as a percentage of the current stock price. How much you are risking relative to the stock's value." },
]

const SHARED_OPTION_COLUMNS_AFTER = [
  { key: 'iv',            label: 'IV',       tip: "Implied Volatility — the market's annualised expected price swing baked into the option price." },
  { key: 'open_interest', label: 'Open Int', tip: 'Open Interest — total number of outstanding contracts. Higher = more liquid.' },
  { key: 'volume',        label: 'Volume',   tip: 'Contracts traded today. A real-time liquidity signal.' },
]

export const OPTIONS_TABLE = {
  columns: [
    ...SHARED_OPTION_COLUMNS,
    { key: 'breakeven_drop_pct', label: 'BE Drop', tip: 'Breakeven drop — how far the stock must fall for you to break even at expiry (strike minus ask, expressed as % below current price).' },
    ...SHARED_OPTION_COLUMNS_AFTER,
  ],
}

export const CALLS_OPTIONS_TABLE = {
  columns: [
    ...SHARED_OPTION_COLUMNS,
    { key: 'breakeven_rise_pct', label: 'BE Rise', tip: 'Breakeven rise — how far the stock must rise for you to break even at expiry (strike plus ask, expressed as % above current price).' },
    ...SHARED_OPTION_COLUMNS_AFTER,
  ],
}

// Shared between puts and calls hero cards — labels, icons, and stat names are identical
export const HERO_CARD = {
  short:    { label: 'Best Short-Dated',           icon: '⚡' },
  long:     { label: 'Best Long-Dated / LEAP',     icon: '🚀' },
  moonshot: { label: 'Top Moonshot — return only', icon: '🎰' },
  stats: {
    returnMultiple: 'Return Multiple',
    probItm:        'Prob ITM',
    askPerShare:    'Ask / Share',
    contractCost:   'Contract Cost',
    strike:         'Strike',
    expiry:         'Expiry',
    iv:             'IV',
  },
} as const

// Shared between puts and calls filters sheets
export const FILTERS_SHEET = {
  triggerLabel: 'Filters',
  premiumLabel: 'Filters',
  premiumBadge: 'PREMIUM',
  getPremium:   'Get Premium',
  comingSoon:   'Premium coming soon',
} as const

// Shared page strings — only titles differ between puts and calls
const REPORT_PAGE_BASE = {
  loading:     'Loading…',
  empty:       'No reports found — run the scanner to generate one.',
  newOnly:     'New Only',
  expandAll:   'Expand All',
  collapseAll: 'Collapse All',
  noNewItems:  'no new items',
} as const

export const PUTS_PAGE  = { title: 'Put Report',  ...REPORT_PAGE_BASE } as const
export const CALLS_PAGE = { title: 'Call Report', ...REPORT_PAGE_BASE } as const

export const METHODOLOGY = {
  trigger: 'How are these puts selected?',
  thesis: {
    heading: 'The Thesis',
    body: 'Stocks with 500%+ trailing 12-month gains tend to mean-revert. The move may be fundamental, but the options market regularly underprices downside risk on extreme gainers. This scanner finds those names and surfaces cheap out-of-the-money puts on them. The setup is asymmetric. Small premium at risk, large payoff if the correction plays out.',
  },
  judgementCalls: {
    heading: 'Judgement Calls',
    intro: 'These are the rules baked into the scanner. Each one is a deliberate choice, not a given:',
    rules: [
      { rule: 'Universe', detail: 'S&P 500 and NASDAQ 100 constituents only — liquid, well-known names where options markets are active.' },
      { rule: '500%+ over 1 year', detail: 'The stock must have appreciated at least 500% over the trailing 12 months. Below that threshold the mean-reversion thesis is weaker.' },
      { rule: 'Out-of-the-money puts only', detail: 'We want cheap optionality on a correction, not intrinsic value. ITM puts are excluded.' },
      { rule: 'Expiry between 60 and 1,000 DTE', detail: 'Too short and there is no time for the thesis to play out. Too long and pricing becomes speculative. The sweet spot is roughly 2 months to 3 years out.' },
      { rule: 'Ask ≤ 5% of stock price', detail: 'Keeps the cost-of-insurance sensible. A put that costs more than 5% of the underlying is already pricing in meaningful downside.' },
      { rule: 'Implied volatility ≤ 200%', detail: 'Extremely high IV means the market is already pricing in a crash. We want names where the put is still relatively cheap.' },
      { rule: 'Minimum liquidity', detail: 'Open interest ≥ 10, or any volume traded today, or a recorded last price. Catches thinly-traded LEAPs that are still quote-able.' },
      { rule: 'Scored by return × prob ITM', detail: 'Puts are ranked by return multiple (strike ÷ ask) multiplied by Black-Scholes probability of expiring in-the-money. This balances raw upside against realistic odds.' },
      { rule: 'Top 10 per bucket', detail: 'Short-dated (< 6 months) and long-dated / LEAPs (6+ months) are capped at 10 each, sorted by score. Moonshots — the top 5 by raw return multiple — are surfaced separately.' },
    ],
  },
} as const

export const CALLS_METHODOLOGY = {
  trigger: 'How are these calls selected?',
  thesis: {
    heading: 'The Thesis',
    body: 'Macro tailwinds in AI, space, and disruptive tech create asymmetric upside in smaller, lesser-known names. This scanner finds tickers held across leading thematic ETFs — ARKK, ARKX, ARKQ, SMH, AIQ, BOTZ, and ROKT — that are showing strong 90-day momentum, and surfaces cheap out-of-the-money calls on them. The setup is a trend-continuation bet — small premium at risk, large payoff if the run extends.',
  },
  judgementCalls: {
    heading: 'Judgement Calls',
    intro: 'These are the rules baked into the scanner. Each one is a deliberate choice, not a given:',
    rules: [
      { rule: 'Universe', detail: 'Tickers held across ARKK, ARKX, ARKQ, SMH, AIQ, BOTZ, and ROKT ETFs — a cross-section of AI, semiconductors, robotics, and space plays. Holdings are fetched daily via Yahoo Finance and cached.' },
      { rule: '15%+ momentum in 90 days', detail: 'The ticker must be up at least 15% over the trailing 90 days. This confirms the trend is live before we look for calls.' },
      { rule: 'Out-of-the-money calls only', detail: 'We want cheap optionality on a continuation move, not intrinsic value. ITM calls are excluded.' },
      { rule: 'Expiry between 60 and 365 DTE', detail: 'Long enough for the thesis to play out. LEAPs are included — macro trends take time.' },
      { rule: 'Ask ≤ 4% of stock price', detail: 'Keeps premium cost manageable. These are momentum names with naturally higher volatility, so we allow slightly more than the put scanner.' },
      { rule: 'Implied volatility ≤ 150%', detail: 'High-momentum stocks carry high IV. We accept up to 150% — above that the market is already pricing in a parabolic move.' },
      { rule: 'Minimum liquidity', detail: 'Open interest ≥ 10, or any volume traded today, or a recorded last price.' },
      { rule: 'Scored by return × prob ITM', detail: 'Calls are ranked by return multiple (strike ÷ ask) multiplied by Black-Scholes probability of expiring in-the-money. This balances raw upside against realistic odds.' },
      { rule: 'Top 10 per bucket', detail: 'Short-dated (< 6 months) and long-dated / LEAPs (6+ months) are capped at 10 each, sorted by score. Moonshots — the top 5 by raw return multiple — are surfaced separately.' },
    ],
  },
} as const

export const HOME_PAGE = {
  subtitle:     'Twice-daily scans for asymmetric options plays — extreme gainers ripe for puts, momentum names primed for calls.',
  putsHeading:  'Top Put Plays Identified',
  callsHeading: 'Top Call Plays Identified',
  viewAll:      'View all →',
  loading:      'Loading…',
  putsEmpty:    'No put reports found.',
  callsEmpty:   'No call reports found.',
} as const

export const FOOTER = {
  notFinancialAdvice: 'Not financial advice.',
  mobileDisclaimer:   'Options trading involves significant risk and is not suitable for all investors.',
} as const

export const ABOUT_PAGE = {
  title: 'About',
  intro: `${APP_NAME} runs twice-daily scans to surface asymmetric options plays — cheap out-of-the-money puts on extreme gainers, and cheap calls on momentum names. Scans run at market open and midday ET. Reports are compared across runs to highlight what's new.`,
} as const
