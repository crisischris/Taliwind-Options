import { useState, useEffect } from 'react'
import type { ManifestEntry, PutsReport, CallsReport } from '../types/report'

export interface PutsDiff {
  prevPutContracts: Set<string>
  prevPutTickers: Set<string>
  prevReportId: string | null
}

export interface CallsDiff {
  prevCallContracts: Set<string>
  prevCallTickers: Set<string>
  prevReportId: string | null
}

const EMPTY_PUTS_DIFF: PutsDiff = {
  prevPutContracts: new Set(),
  prevPutTickers: new Set(),
  prevReportId: null,
}

const EMPTY_CALLS_DIFF: CallsDiff = {
  prevCallContracts: new Set(),
  prevCallTickers: new Set(),
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

export function usePutsReport(id: string | null, manifest: ManifestEntry[]) {
  const [report, setReport] = useState<PutsReport | null>(null)
  const [diff, setDiff] = useState<PutsDiff>(EMPTY_PUTS_DIFF)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!id) return
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setLoading(true)

    const idx = manifest.findIndex(m => m.id === id)
    const prevEntry = manifest[idx + 1] ?? null

    const reportReq = fetch(`puts/${id}.json`).then(r => r.json() as Promise<PutsReport>)
    const prevReq = prevEntry
      ? fetch(`puts/${prevEntry.id}.json`)
          .then(r => r.json() as Promise<PutsReport>)
          .catch(() => null)
      : Promise.resolve(null)

    Promise.all([reportReq, prevReq]).then(([data, prev]) => {
      setReport(data)
      if (prev) {
        setDiff({
          prevPutContracts: new Set(prev.tickers.flatMap(t => t.puts.map(p => p.contract))),
          prevPutTickers: new Set(prev.tickers.map(t => t.ticker)),
          prevReportId: prevEntry!.id,
        })
      } else {
        setDiff(EMPTY_PUTS_DIFF)
      }
      setLoading(false)
    })
  }, [id, manifest])

  return { report, diff, loading }
}

export function useCallsReport(id: string | null, manifest: ManifestEntry[]) {
  const [report, setReport] = useState<CallsReport | null>(null)
  const [diff, setDiff] = useState<CallsDiff>(EMPTY_CALLS_DIFF)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!id) return
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setLoading(true)

    const idx = manifest.findIndex(m => m.id === id)
    const prevEntry = manifest[idx + 1] ?? null

    const reportReq = fetch(`calls/${id}.json`).then(r => r.json() as Promise<CallsReport>)
    const prevReq = prevEntry
      ? fetch(`calls/${prevEntry.id}.json`)
          .then(r => r.json() as Promise<CallsReport>)
          .catch(() => null)
      : Promise.resolve(null)

    Promise.all([reportReq, prevReq]).then(([data, prev]) => {
      setReport(data)
      if (prev) {
        setDiff({
          prevCallContracts: new Set(prev.tickers.flatMap(t => t.calls.map(c => c.contract))),
          prevCallTickers: new Set(prev.tickers.map(t => t.ticker)),
          prevReportId: prevEntry!.id,
        })
      } else {
        setDiff(EMPTY_CALLS_DIFF)
      }
      setLoading(false)
    })
  }, [id, manifest])

  return { report, diff, loading }
}
