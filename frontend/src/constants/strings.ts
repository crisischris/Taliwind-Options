export const APP_NAME = 'Tailwind Options'

export const NAVBAR = {
  home:  'Home',
  calls: 'Calls',
  puts:  'Puts',
  about: 'About',
} as const


// Shared between puts and calls ticker cards — labels and icons are identical
export const TICKER_CARD = {
  short:       { label: '⚡ Short-Dated < 6 months'       },
  long:        { label: '🚀 Long-Dated / LEAPs 6+ months' },
  moonshot:    { label: '🎰 Moonshots — return only'      },
  expand:      'expand',
  collapse:    'collapse',
  priceAtScan: 'Price at Scan',
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
  triggerLabel:            'Filters',
  premiumLabel:            'Filters',
  premiumBadge:            'COMING SOON',
  getPremium:              'Coming Soon',
  comingSoon:              'Coming soon',
  thesisHeading:           'The Thesis',
  judgementCallsHeading:   'Judgement Calls',
  putsMethodologyTrigger:  'How are these puts selected?',
  callsMethodologyTrigger: 'How are these calls selected?',
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

export const PUTS_PAGE  = { title: 'Puts',  ...REPORT_PAGE_BASE } as const
export const CALLS_PAGE = { title: 'Calls', ...REPORT_PAGE_BASE } as const


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

// SEO: per-page title and meta description. Title is set via usePageMeta on each page transition
// so Googlebot (which executes JS) sees distinct titles; social crawlers use the static
// fallbacks in index.html. Descriptions should be 140-160 characters for full snippet display.
export const PAGE_META = {
  home: {
    title:       'Tailwind Options',
    description: 'Twice-daily scans for asymmetric options plays — cheap OTM puts on extreme gainers and cheap calls on momentum names from S&P 500, NASDAQ 100, and leading thematic ETFs.',
  },
  puts: {
    title:       'Put Report | Tailwind Options',
    description: 'Cheap out-of-the-money puts on S&P 500 and NASDAQ 100 stocks up 500%+ over the past year. Scored by return multiple × probability ITM.',
  },
  calls: {
    title:       'Call Report | Tailwind Options',
    description: 'Cheap out-of-the-money calls on momentum names held across ARKK, SMH, AIQ, BOTZ, and other thematic ETFs. Scored by return multiple × probability ITM.',
  },
  about: {
    title:       'About | Tailwind Options',
    description: 'How Tailwind Options works — scanner methodology, judgement calls, and the thesis behind cheap asymmetric options plays on extreme gainers and momentum names.',
  },
} as const

export const ABOUT_PAGE = {
  title: 'About',
  intro: `${APP_NAME} runs twice-daily scans to surface asymmetric options plays across many macro or micro themes. Scans run at market open and midday ET. Reports are compared across runs to highlight what's new.`,
} as const
