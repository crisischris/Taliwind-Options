import type { Page } from '@playwright/test'

export const PUT_TICKER_AAPL = {
  ticker: 'AAPL',
  gain_pct: 620,
  current_price: 210.5,
  puts: [
    {
      contract: 'AAPL261219P00150000',
      ticker: 'AAPL',
      expiry: '2026-12-19',
      strike: 150,
      ask: 3.0,
      return_multiple: 50,
      prob_itm: 0.15,
      breakeven_drop_pct: 23.5,
      iv: 0.8,
      open_interest: 50,
      volume: 10,
      term: 'short',
    },
  ],
}

export const PUT_TICKER_MSFT = {
  ticker: 'MSFT',
  gain_pct: 510,
  current_price: 320.0,
  puts: [
    {
      contract: 'MSFT270619P00250000',
      ticker: 'MSFT',
      expiry: '2027-06-19',
      strike: 250,
      ask: 4.5,
      return_multiple: 55,
      prob_itm: 0.12,
      breakeven_drop_pct: 21.0,
      iv: 0.75,
      open_interest: 30,
      volume: 5,
      term: 'long',
    },
  ],
}

const PUTS_MANIFEST = [
  { id: 'put-scan-2026-05-14_09-31', generated_at: '2026-05-14_09-31', tickers_flagged: 2 },
]

const PUTS_REPORT = {
  id: 'put-scan-2026-05-14_09-31',
  generated_at: '2026-05-14_09-31',
  summary: { tickers_flagged: 2, short_puts: 1, long_puts: 1, moonshot_puts: 0 },
  heroes: {
    short: { ...PUT_TICKER_AAPL.puts[0], gain_pct: 620, current_price: 210.5 },
    long:  { ...PUT_TICKER_MSFT.puts[0], gain_pct: 510, current_price: 320.0 },
    moonshot: null,
  },
  tickers: [PUT_TICKER_AAPL, PUT_TICKER_MSFT],
}

export const CALL_TICKER_NVDA = {
  ticker: 'NVDA',
  momentum_pct: 42,
  current_price: 880.0,
  calls: [
    {
      contract: 'NVDA261219C01000000',
      ticker: 'NVDA',
      expiry: '2026-12-19',
      strike: 1000,
      ask: 12.0,
      return_multiple: 83,
      prob_itm: 0.18,
      breakeven_rise_pct: 15.2,
      iv: 0.65,
      open_interest: 200,
      volume: 40,
      term: 'short',
    },
  ],
}

const CALLS_MANIFEST = [
  { id: 'call-scan-2026-05-14_09-31', generated_at: '2026-05-14_09-31', tickers_flagged: 1 },
]

const CALLS_REPORT = {
  id: 'call-scan-2026-05-14_09-31',
  generated_at: '2026-05-14_09-31',
  summary: { tickers_flagged: 1, short_calls: 1, long_calls: 0, moonshot_calls: 0 },
  heroes: {
    short: { ...CALL_TICKER_NVDA.calls[0], momentum_pct: 42, current_price: 880.0 },
    long:  null,
    moonshot: null,
  },
  tickers: [CALL_TICKER_NVDA],
}

export async function mockReports(page: Page) {
  await page.route('**/puts/**', async route => {
    const url = route.request().url()
    await route.fulfill({ json: url.includes('manifest') ? PUTS_MANIFEST : PUTS_REPORT })
  })
  await page.route('**/calls/**', async route => {
    const url = route.request().url()
    await route.fulfill({ json: url.includes('manifest') ? CALLS_MANIFEST : CALLS_REPORT })
  })
}

export async function mockEmptyReports(page: Page) {
  await page.route('**/puts/**',  route => route.fulfill({ json: [] }))
  await page.route('**/calls/**', route => route.fulfill({ json: [] }))
}
