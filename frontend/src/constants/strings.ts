export const APP = {
  brand: '📈 Options Hunter',
} as const

export const NAVBAR = {
  puts:  'Puts',
  calls: 'Calls',
  about: 'About',
} as const

export const STATS_BAR = {
  tickersFlagged: { label: 'Tickers Flagged',    description: '500%+ YTD gainers'          },
  shortPuts:      { label: 'Short-Dated Puts',   description: 'Under 6 months to expiry'   },
  longPuts:       { label: 'Long-Dated / LEAPs', description: '6+ months to expiry'        },
} as const

export const SETTINGS = {
  title:      'Settings',
  appearance: 'Appearance',
  dark:       'Dark mode',
  light:      'Light mode',
} as const

export const TICKER_CARD = {
  short:    { label: '⚡ Short-Dated < 6 months'       },
  long:     { label: '🚀 Long-Dated / LEAPs 6+ months' },
  moonshot: { label: '🎰 Moonshots — return only'      },
  expand:   'expand',
  collapse: 'collapse',
} as const

export const OPTIONS_TABLE = {
  columns: [
    { key: 'return_multiple',    label: 'Return',        tip: 'Strike price divided by ask price. If the stock hits the strike at expiry, you receive this many times your investment back.' },
    { key: 'prob_itm',           label: 'Prob ITM',      tip: 'Black-Scholes risk-neutral probability this put expires in-the-money. Options are ranked by Return x Prob ITM combined.' },
    { key: 'expiry',             label: 'Expiry',        tip: 'Option expiration date. The put must expire in-the-money to have intrinsic value.' },
    { key: 'strike',             label: 'Strike',        tip: 'The price the stock must fall below for this put to have intrinsic value at expiry.' },
    { key: 'ask',                label: 'Ask',           tip: 'Current asking price per share. One contract = 100 shares, so multiply by 100 for total cost.' },
    { key: 'contract_cost',      label: 'Contract Cost', tip: 'Total cost of one contract in USD (ask x 100 shares). This is the actual cash outlay.' },
    { key: 'cost_pct',           label: 'Cost %',        tip: "Ask as a percentage of the current stock price. How much you are risking relative to the stock's value." },
    { key: 'breakeven_drop_pct', label: 'BE Drop',       tip: 'Breakeven drop — how far the stock must fall for you to break even at expiry (strike minus ask, expressed as % below current price).' },
    { key: 'iv',                 label: 'IV',            tip: "Implied Volatility — the market's annualised expected price swing baked into the option price." },
    { key: 'open_interest',      label: 'Open Int',      tip: 'Open Interest — total number of outstanding contracts. Higher = more liquid.' },
    { key: 'volume',             label: 'Volume',        tip: 'Contracts traded today. A real-time liquidity signal.' },
  ],
} as const

export const TICKERS_MODAL = {
  title:        'Tickers Flagged',
  colTicker:    'Ticker',
  colYtdGain:   'YTD Gain',
  colPutsFound: 'Puts Found',
  close:        'Close',
} as const

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

export const PUTS_PAGE = {
  title:       'Put Scan Reports',
  loading:     'Loading…',
  empty:       'No reports found — run the scanner to generate one.',
  newOnly:     'New Only',
  expandAll:   'Expand All',
  collapseAll: 'Collapse All',
  noNewItems:  'no new items',
} as const

export const ABOUT_PAGE = {
  title: 'About',
  body1: 'Options Hunter is a daily scanner that finds S&P 500 and NASDAQ 100 stocks with extreme YTD gains and surfaces cheap out-of-the-money puts as potential mean-reversion plays.',
  body2: 'Scans run twice daily at market open and midday. Reports are stored and compared across runs to highlight new opportunities.',
} as const

export const CALLS_PAGE = {
  icon:       '📞',
  title:      'Calls',
  comingSoon: 'Coming soon.',
} as const
