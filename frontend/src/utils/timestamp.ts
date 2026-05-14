/**
 * Parses a Lambda-generated UTC timestamp string "2026-05-09_18-59"
 * and formats it in Eastern Time with timezone name shown.
 */
export function formatTimestamp(raw: string): string {
  const [datePart, timePart] = raw.split('_')
  if (!datePart || !timePart) return raw
  const [h, m] = timePart.split('-').map(Number)
  const date = new Date(`${datePart}T${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:00Z`)
  if (isNaN(date.getTime())) return raw
  return date.toLocaleString('en-US', {
    month: 'short', day: 'numeric', year: 'numeric',
    hour: 'numeric', minute: '2-digit',
    timeZone: 'America/New_York',
    timeZoneName: 'short',
  })
}
