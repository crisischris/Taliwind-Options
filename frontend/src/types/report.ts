export interface Put {
  contract: string
  ticker: string
  expiry: string
  strike: number
  ask: number
  return_multiple: number
  prob_itm: number
  breakeven_drop_pct: number
  iv: number
  open_interest: number
  volume: number | null
  term: 'short' | 'long' | 'moonshot'
  // present on hero puts only
  gain_pct?: number
  current_price?: number
}

export interface PutTicker {
  ticker: string
  gain_pct: number
  current_price: number
  puts: Put[]
}

export interface PutHeroes {
  short: (Put & { gain_pct: number; current_price: number }) | null
  long:  (Put & { gain_pct: number; current_price: number }) | null
  moonshot: (Put & { gain_pct: number; current_price: number }) | null
}

export interface Call {
  contract: string
  ticker: string
  expiry: string
  strike: number
  ask: number
  return_multiple: number
  prob_itm: number
  breakeven_rise_pct: number
  iv: number
  open_interest: number
  volume: number | null
  term: 'short' | 'long' | 'moonshot'
  // present on hero calls only
  momentum_pct?: number
  current_price?: number
}

export interface CallTicker {
  ticker: string
  momentum_pct: number
  current_price: number
  calls: Call[]
}

export interface CallHeroes {
  short: (Call & { momentum_pct: number; current_price: number }) | null
  long:  (Call & { momentum_pct: number; current_price: number }) | null
  moonshot: (Call & { momentum_pct: number; current_price: number }) | null
}

export interface PutsSummary {
  tickers_flagged: number
  short_puts: number
  long_puts: number
  moonshot_puts: number
}

export interface CallsSummary {
  tickers_flagged: number
  short_calls: number
  long_calls: number
  moonshot_calls: number
}

export interface PutsReport {
  id: string
  generated_at: string
  summary: PutsSummary
  heroes: PutHeroes
  tickers: PutTicker[]
}

export interface CallsReport {
  id: string
  generated_at: string
  summary: CallsSummary
  heroes: CallHeroes
  tickers: CallTicker[]
}

export interface ManifestEntry {
  id: string
  generated_at: string
  tickers_flagged: number
  short_puts?: number
  long_puts?: number
  moonshot_puts?: number
  short_calls?: number
  long_calls?: number
  moonshot_calls?: number
}
