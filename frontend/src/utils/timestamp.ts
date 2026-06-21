/**
 * Parses a Lambda-generated UTC timestamp string "2026-05-09_18-59"
 * and formats it in Eastern Time with timezone name shown.
 */

import scanSchedule from '@/config/scanSchedule.json'

function parseRawTimestamp(raw: string): Date | null {
  const [datePart, timePart] = raw.split('_')
  if (!datePart || !timePart) return null
  const [h, m] = timePart.split('-').map(Number)
  const date = new Date(`${datePart}T${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:00Z`)
  return isNaN(date.getTime()) ? null : date
}

export function getScanLabel(generatedAt: string): 'Morning Data' | 'Midday Data' {
  const date = parseRawTimestamp(generatedAt)
  if (!date) return 'Midday Data'
  const etHour = Number(new Intl.DateTimeFormat('en-US', {
    hour: 'numeric', hour12: false, timeZone: 'America/New_York',
  }).format(date)) % 24
  return etHour < scanSchedule.middayScanEt.hour ? 'Morning Data' : 'Midday Data'
}

export function formatTimestamp(raw: string): string {
  const date = parseRawTimestamp(raw)
  if (!date) return raw
  return date.toLocaleString('en-US', {
    month: 'short', day: 'numeric', year: 'numeric',
    hour: 'numeric', minute: '2-digit',
    timeZone: 'America/New_York',
    timeZoneName: 'short',
  })
}
