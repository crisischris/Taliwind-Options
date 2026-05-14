import { useState, useEffect } from 'react'
import type { ManifestEntry, Report } from '../types/report'

export interface DiffSets {
  prevContracts: Set<string>
  prevTickers: Set<string>
  prevReportId: string | null
}

const EMPTY_DIFF: DiffSets = { prevContracts: new Set(), prevTickers: new Set(), prevReportId: null }

export function useManifest() {
  const [manifest, setManifest] = useState<ManifestEntry[]>([])
  const [error, setError] = useState(false)

  useEffect(() => {
    fetch('manifest.json')
      .then(r => r.json())
      .then(setManifest)
      .catch(() => setError(true))
  }, [])

  return { manifest, error }
}

export function useReport(id: string | null, manifest: ManifestEntry[]) {
  const [report, setReport] = useState<Report | null>(null)
  const [diff, setDiff] = useState<DiffSets>(EMPTY_DIFF)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!id) return
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setLoading(true)

    const idx = manifest.findIndex(m => m.id === id)
    const prevEntry = manifest[idx + 1] ?? null

    const reportReq = fetch(`${id}.json`).then(r => r.json() as Promise<Report>)
    const prevReq = prevEntry
      ? fetch(`${prevEntry.id}.json`)
          .then(r => r.json() as Promise<Report>)
          .catch(() => null)
      : Promise.resolve(null)

    Promise.all([reportReq, prevReq]).then(([data, prev]) => {
      setReport(data)
      if (prev) {
        setDiff({
          prevContracts: new Set(prev.tickers.flatMap(t => t.puts.map(p => p.contract))),
          prevTickers: new Set(prev.tickers.map(t => t.ticker)),
          prevReportId: prevEntry!.id,
        })
      } else {
        setDiff(EMPTY_DIFF)
      }
      setLoading(false)
    })
  }, [id, manifest])

  return { report, diff, loading }
}
