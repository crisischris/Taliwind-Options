import { describe, it, expect, vi, afterEach } from 'vitest'
import { renderHook, waitFor, act } from '@testing-library/react'
import { useManifest, useReport, clearReportCache } from './useReport'
import type { ManifestEntry, PutsReport } from '../types/report'

// ── test data ─────────────────────────────────────────────────────────────────

const MANIFEST: ManifestEntry[] = [
  { id: 'put-scan-2026-05-14_09-31', generated_at: '2026-05-14_09-31', tickers_flagged: 3, short_puts: 10, long_puts: 5 },
  { id: 'put-scan-2026-05-13_09-31', generated_at: '2026-05-13_09-31', tickers_flagged: 2, short_puts: 8, long_puts: 4 },
]

const REPORT: PutsReport = {
  id: 'put-scan-2026-05-14_09-31',
  generated_at: '2026-05-14_09-31',
  summary: { tickers_flagged: 3, short_puts: 10, long_puts: 5, moonshot_puts: 0 },
  heroes: { short: null, long: null, moonshot: null },
  tickers: [
    {
      ticker: 'AAPL',
      theme_id: 'mean-reversion',
      move_pct: 600,
      move_label: '1Y',
      gain_pct: 600,
      current_price: 200,
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
    },
  ],
}

const PREV_REPORT: PutsReport = {
  ...REPORT,
  id: 'put-scan-2026-05-13_09-31',
  generated_at: '2026-05-13_09-31',
  tickers: [
    {
      ticker: 'MSFT',
      theme_id: 'mean-reversion',
      move_pct: 550,
      move_label: '1Y',
      gain_pct: 550,
      current_price: 300,
      puts: [
        {
          contract: 'MSFT261219P00250000',
          ticker: 'MSFT',
          expiry: '2026-12-19',
          strike: 250,
          ask: 2.0,
          return_multiple: 125,
          prob_itm: 0.10,
          breakeven_drop_pct: 17.0,
          iv: 0.6,
          open_interest: 30,
          volume: 5,
          term: 'long',
        },
      ],
    },
  ],
}

// ── helpers ───────────────────────────────────────────────────────────────────

function mockFetch(responses: Record<string, unknown>) {
  vi.stubGlobal('fetch', vi.fn((url: string) => {
    const key = Object.keys(responses).find(k => url.includes(k))
    if (key !== undefined) {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve(responses[key]),
      })
    }
    return Promise.reject(new Error(`Unexpected fetch: ${url}`))
  }))
}

// ── useManifest ───────────────────────────────────────────────────────────────

describe('useManifest', () => {
  afterEach(() => { clearReportCache(); vi.unstubAllGlobals() })

  it('fetches manifest with cache: no-cache', async () => {
    mockFetch({ 'mean-reversion/manifest.json': MANIFEST })
    renderHook(() => useManifest('puts', 'mean-reversion'))
    await waitFor(() => expect(vi.mocked(fetch)).toHaveBeenCalledWith(
      expect.stringContaining('mean-reversion/manifest.json'),
      { cache: 'no-cache' }
    ))
  })

  it('returns manifest on success', async () => {
    mockFetch({ 'mean-reversion/manifest.json': MANIFEST })
    const { result } = renderHook(() => useManifest('puts', 'mean-reversion'))
    await waitFor(() => expect(result.current.manifest).toHaveLength(2))
    expect(result.current.error).toBe(false)
    expect(result.current.manifest[0].id).toBe('put-scan-2026-05-14_09-31')
  })

  it('sets error on fetch failure', async () => {
    vi.stubGlobal('fetch', vi.fn(() => Promise.reject(new Error('network error'))))
    const { result } = renderHook(() => useManifest('puts', 'mean-reversion'))
    await waitFor(() => expect(result.current.error).toBe(true))
    expect(result.current.manifest).toHaveLength(0)
  })

  it('sets error on non-ok response', async () => {
    vi.stubGlobal('fetch', vi.fn(() => Promise.resolve({
      ok: false,
      json: () => Promise.reject(new Error('bad json')),
    })))
    const { result } = renderHook(() => useManifest('puts', 'mean-reversion'))
    await waitFor(() => expect(result.current.error).toBe(true))
  })

  it('starts with empty manifest', () => {
    vi.stubGlobal('fetch', vi.fn(() => new Promise(() => {}))) // never resolves
    const { result } = renderHook(() => useManifest('puts', 'mean-reversion'))
    expect(result.current.manifest).toHaveLength(0)
    expect(result.current.error).toBe(false)
  })
})

// ── useReport ─────────────────────────────────────────────────────────────────

describe('useReport', () => {
  afterEach(() => { clearReportCache(); vi.unstubAllGlobals() })

  it('does nothing when id is null', async () => {
    vi.stubGlobal('fetch', vi.fn())
    const { result } = renderHook(() => useReport('puts', null, MANIFEST, 'mean-reversion'))
    await act(async () => {})
    expect(result.current.report).toBeNull()
    expect(vi.mocked(fetch)).not.toHaveBeenCalled()
  })

  it('loads report and prev report', async () => {
    mockFetch({
      'put-scan-2026-05-14_09-31.json': REPORT,
      'put-scan-2026-05-13_09-31.json': PREV_REPORT,
    })
    const { result } = renderHook(() => useReport('puts', 'put-scan-2026-05-14_09-31', MANIFEST, 'mean-reversion'))
    await waitFor(() => expect(result.current.report).not.toBeNull())

    expect(result.current.report?.id).toBe('put-scan-2026-05-14_09-31')
    expect(result.current.diff.prevReportId).toBe('put-scan-2026-05-13_09-31')
    expect(result.current.diff.prevTickers.has('MSFT')).toBe(true)
    expect(result.current.diff.prevContracts.has('MSFT261219P00250000')).toBe(true)
  })

  it('sets empty diff when there is no previous report', async () => {
    mockFetch({ 'put-scan-2026-05-13_09-31.json': PREV_REPORT })
    // Only one entry in manifest — no prev
    const { result } = renderHook(() =>
      useReport('puts', 'put-scan-2026-05-13_09-31', [MANIFEST[1]], 'mean-reversion')
    )
    await waitFor(() => expect(result.current.report).not.toBeNull())
    expect(result.current.diff.prevReportId).toBeNull()
    expect(result.current.diff.prevContracts.size).toBe(0)
    expect(result.current.diff.prevTickers.size).toBe(0)
  })

  it('handles prev report fetch failure gracefully', async () => {
    vi.stubGlobal('fetch', vi.fn((url: string) => {
      if (url.includes('2026-05-14')) {
        return Promise.resolve({ ok: true, json: () => Promise.resolve(REPORT) })
      }
      return Promise.reject(new Error('prev fetch failed'))
    }))

    const { result } = renderHook(() => useReport('puts', 'put-scan-2026-05-14_09-31', MANIFEST, 'mean-reversion'))
    await waitFor(() => expect(result.current.report).not.toBeNull())
    expect(result.current.report?.id).toBe('put-scan-2026-05-14_09-31')
    expect(result.current.diff.prevReportId).toBeNull()
  })

  it('resets when id changes', async () => {
    mockFetch({
      'put-scan-2026-05-14_09-31.json': REPORT,
      'put-scan-2026-05-13_09-31.json': PREV_REPORT,
    })

    const { result, rerender } = renderHook(
      ({ id }: { id: string }) => useReport('puts', id, MANIFEST, 'mean-reversion'),
      { initialProps: { id: 'put-scan-2026-05-14_09-31' } }
    )
    await waitFor(() => expect(result.current.report?.id).toBe('put-scan-2026-05-14_09-31'))

    rerender({ id: 'put-scan-2026-05-13_09-31' })
    await waitFor(() => expect(result.current.report?.id).toBe('put-scan-2026-05-13_09-31'))
  })

  it('sets loading true during fetch', async () => {
    let resolveReport!: (v: unknown) => void
    const reportPromise = new Promise(r => { resolveReport = r })

    vi.stubGlobal('fetch', vi.fn(() => Promise.resolve({
      ok: true,
      json: () => reportPromise,
    })))

    const { result } = renderHook(() => useReport('puts', 'put-scan-2026-05-14_09-31', MANIFEST, 'mean-reversion'))
    expect(result.current.loading).toBe(true)

    act(() => resolveReport(REPORT))
    await waitFor(() => expect(result.current.loading).toBe(false))
  })
})
