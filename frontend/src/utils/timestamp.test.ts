import { describe, it, expect } from 'vitest'
import { formatTimestamp, getScanLabel } from './timestamp'

describe('getScanLabel', () => {
  it('returns Morning Data for the 9:35 AM ET open scan (UTC 13:35 in summer)', () => {
    // Regression: label must reflect the report timestamp, not the current time of day
    expect(getScanLabel('2026-05-09_13-35')).toBe('Morning Data')
  })

  it('returns Midday Data for the 12:00 PM ET midday scan (UTC 16:00 in summer)', () => {
    expect(getScanLabel('2026-05-09_16-00')).toBe('Midday Data')
  })

  it('returns Morning Data for the 9:35 AM ET open scan in winter (EST, UTC 14:35)', () => {
    expect(getScanLabel('2026-01-09_14-35')).toBe('Morning Data')
  })

  it('returns Midday Data for the 12:00 PM ET midday scan in winter (EST, UTC 17:00)', () => {
    expect(getScanLabel('2026-01-09_17-00')).toBe('Midday Data')
  })

  it('returns Midday Data for a malformed timestamp', () => {
    expect(getScanLabel('bad')).toBe('Midday Data')
  })
})

describe('formatTimestamp', () => {
  it('returns raw string when missing underscore separator', () => {
    expect(formatTimestamp('2026-05-09')).toBe('2026-05-09')
  })

  it('returns raw string when time part is missing', () => {
    expect(formatTimestamp('_')).toBe('_')
  })

  it('returns raw string when date part is invalid', () => {
    expect(formatTimestamp('not-a-date_12-00')).toBe('not-a-date_12-00')
  })

  it('returns raw string for empty string', () => {
    expect(formatTimestamp('')).toBe('')
  })

  it('parses UTC timestamp and returns formatted string', () => {
    // 2026-05-09T18:59:00Z → 2:59 PM EDT (UTC-4 in summer)
    const result = formatTimestamp('2026-05-09_18-59')
    expect(result).toContain('2026')
    expect(result).toContain('May')
    expect(result).toContain('9')
    expect(result).toMatch(/EDT|EST/)
  })

  it('includes timezone name in output', () => {
    const result = formatTimestamp('2026-01-15_14-30')
    expect(result).toMatch(/EDT|EST/)
  })

  it('handles midnight UTC correctly', () => {
    const result = formatTimestamp('2026-06-01_00-00')
    expect(result).toContain('2026')
    expect(result).toMatch(/EDT|EST/)
  })

  it('handles single-digit hour correctly', () => {
    const result = formatTimestamp('2026-05-09_09-05')
    expect(result).toContain('2026')
  })

  it('handles end of day timestamp', () => {
    const result = formatTimestamp('2026-05-09_23-59')
    expect(result).toContain('2026')
  })

  it('returns raw string for invalid date like 2026-13-99', () => {
    // Month 13 is invalid — new Date() returns NaN
    expect(formatTimestamp('2026-13-99_12-00')).toBe('2026-13-99_12-00')
  })
})
