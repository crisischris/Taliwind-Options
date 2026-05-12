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

export const METHODOLOGY = {
  trigger: 'How is this report generated?',
  thesis: {
    heading: 'The Thesis',
    body: 'Stocks with 500%+ YTD gains tend to mean-revert. The move may be fundamental, but the options market regularly underprices downside risk on extreme gainers. This scanner finds those names and surfaces cheap out-of-the-money puts on them. The setup is asymmetric. Small premium at risk, large payoff if the correction plays out.',
  },
  judgementCalls: {
    heading: 'Judgement Calls',
    intro: 'These are the rules baked into the scanner. Each one is a deliberate choice, not a given:',
    rules: [
      { rule: 'Universe', detail: 'S&P 500 and NASDAQ 100 constituents only — liquid, well-known names where options markets are active.' },
      { rule: '500%+ YTD gain', detail: 'The stock must have appreciated at least 500% over the trailing 12 months. Below that threshold the mean-reversion thesis is weaker.' },
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
