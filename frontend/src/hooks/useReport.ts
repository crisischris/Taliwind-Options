import { useState, useEffect } from 'react'
import type { ManifestEntry, PutsReport, CallsReport } from '../types/report'

export interface ReportDiff {
  prevContracts: Set<string>
  prevTickers: Set<string>
  prevReportId: string | null
}

const EMPTY_DIFF: ReportDiff = {
  prevContracts: new Set(),
  prevTickers: new Set(),
  prevReportId: null,
}

// ── Module-level cache ────────────────────────────────────────────────────────
// Survives React unmount/remount so navigating back to a page is instant.
// TTL ensures stale manifests and reports are refreshed within 10 minutes,
// which covers the gap between the two daily scanner runs.

const CACHE_TTL_MS = 10 * 60 * 1000

interface CacheEntry { data: unknown; ts: number }

const cache = new Map<string, CacheEntry>()

function getCache<T>(key: string): T | null {
  const entry = cache.get(key)
  if (!entry) return null
  if (Date.now() - entry.ts > CACHE_TTL_MS) { cache.delete(key); return null }
  return entry.data as T
}

function setCache(key: string, data: unknown) {
  cache.set(key, { data, ts: Date.now() })
}

export function clearReportCache() { cache.clear() }

function cachedFetch<T>(url: string, signal: AbortSignal): Promise<T> {
  const hit = getCache<T>(url)
  if (hit !== null) return Promise.resolve(hit)
  return fetch(url, { signal }).then(r => r.json()).then((data: T) => { setCache(url, data); return data })
}

function buildDiff(
  prev: PutsReport | CallsReport | null,
  prevEntry: ManifestEntry | null,
): ReportDiff {
  if (!prev || !prevEntry) return EMPTY_DIFF
  const tickers: { ticker: string; puts?: { contract: string }[]; calls?: { contract: string }[] }[] =
    (prev as unknown as { tickers: { ticker: string; puts?: { contract: string }[]; calls?: { contract: string }[] }[] }).tickers
  return {
    prevContracts: new Set(tickers.flatMap(t => (t.puts ?? t.calls ?? []).map(o => o.contract))),
    prevTickers:   new Set(tickers.map(t => t.ticker)),
    prevReportId:  prevEntry.id,
  }
}

// ── Hooks ─────────────────────────────────────────────────────────────────────

export function useManifest(base: 'puts' | 'calls') {
  const [manifest, setManifest] = useState<ManifestEntry[]>(
    () => getCache<ManifestEntry[]>(`${base}/manifest.json`) ?? []
  )
  const [error, setError] = useState(false)

  useEffect(() => {
    const url = `${base}/manifest.json`
    if (getCache<ManifestEntry[]>(url)) return
    fetch(url, { cache: 'no-cache' })
      .then(r => r.json())
      .then((data: ManifestEntry[]) => { setCache(url, data); setManifest(data) })
      .catch(() => setError(true))
  }, [base])

  return { manifest, error }
}

export function useReport(base: 'puts',  id: string | null, manifest: ManifestEntry[]): { report: PutsReport  | null; diff: ReportDiff; loading: boolean }
export function useReport(base: 'calls', id: string | null, manifest: ManifestEntry[]): { report: CallsReport | null; diff: ReportDiff; loading: boolean }
export function useReport(base: 'puts' | 'calls', id: string | null, manifest: ManifestEntry[]): { report: PutsReport | CallsReport | null; diff: ReportDiff; loading: boolean }
export function useReport(base: 'puts' | 'calls', id: string | null, manifest: ManifestEntry[]) {
  const [report, setReport]   = useState<PutsReport | CallsReport | null>(null)
  const [diff, setDiff]       = useState<ReportDiff>(EMPTY_DIFF)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!id) return

    const reportUrl = `${base}/${id}.json`
    const idx       = manifest.findIndex(m => m.id === id)
    const prevEntry = manifest[idx + 1] ?? null
    const prevUrl   = prevEntry ? `${base}/${prevEntry.id}.json` : null

    // Serve from cache instantly — no loading state, no network call
    const cachedReport = getCache<PutsReport | CallsReport>(reportUrl)
    if (cachedReport) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setReport(cachedReport)
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setDiff(buildDiff(prevUrl ? getCache<PutsReport | CallsReport>(prevUrl) : null, prevEntry))
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setLoading(false)
      return
    }

    setLoading(true)
    const controller = new AbortController()
    const { signal } = controller

    const reportReq = cachedFetch<PutsReport | CallsReport>(reportUrl, signal)
    const prevReq   = prevUrl
      ? cachedFetch<PutsReport | CallsReport>(prevUrl, signal).catch(() => null)
      : Promise.resolve(null)

    Promise.all([reportReq, prevReq])
      .then(([data, prev]) => {
        setReport(data)
        setDiff(buildDiff(prev, prevEntry))
        setLoading(false)
      })
      .catch(e => { if ((e as Error)?.name !== 'AbortError') setLoading(false) })

    return () => controller.abort()
  }, [id, base, manifest])

  return { report, diff, loading }
}
