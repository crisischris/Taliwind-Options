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

export interface Ticker {
  ticker: string
  gain_pct: number
  current_price: number
  puts: Put[]
}

export interface Heroes {
  short: (Put & { gain_pct: number; current_price: number }) | null
  long:  (Put & { gain_pct: number; current_price: number }) | null
  moonshot: (Put & { gain_pct: number; current_price: number }) | null
}

export interface Summary {
  tickers_flagged: number
  short_puts: number
  long_puts: number
}

export interface Report {
  id: string
  generated_at: string
  summary: Summary
  heroes: Heroes
  tickers: Ticker[]
}

export interface ManifestEntry {
  id: string
  generated_at: string
  tickers_flagged: number
  short_puts: number
  long_puts: number
}
