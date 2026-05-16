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

export function useManifest(base: 'puts' | 'calls') {
  const [manifest, setManifest] = useState<ManifestEntry[]>([])
  const [error, setError] = useState(false)

  useEffect(() => {
    fetch(`${base}/manifest.json`)
      .then(r => r.json())
      .then(setManifest)
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
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setLoading(true)

    const controller = new AbortController()
    const { signal } = controller
    const idx       = manifest.findIndex(m => m.id === id)
    const prevEntry = manifest[idx + 1] ?? null

    const reportReq = fetch(`${base}/${id}.json`, { signal }).then(r => r.json())
    const prevReq   = prevEntry
      ? fetch(`${base}/${prevEntry.id}.json`, { signal }).then(r => r.json()).catch(() => null)
      : Promise.resolve(null)

    Promise.all([reportReq, prevReq])
      .then(([data, prev]) => {
        setReport(data)
        if (prev) {
          const tickers: { ticker: string; puts?: { contract: string }[]; calls?: { contract: string }[] }[] = prev.tickers
          setDiff({
            prevContracts: new Set(tickers.flatMap(t => (t.puts ?? t.calls ?? []).map(o => o.contract))),
            prevTickers:   new Set(tickers.map(t => t.ticker)),
            prevReportId:  prevEntry!.id,
          })
        } else {
          setDiff(EMPTY_DIFF)
        }
        setLoading(false)
      })
      .catch(e => { if ((e as Error)?.name !== 'AbortError') setLoading(false) })

    return () => controller.abort()
  }, [id, base, manifest])

  return { report, diff, loading }
}
