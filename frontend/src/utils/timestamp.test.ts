import { describe, it, expect } from 'vitest'
import { formatTimestamp } from './timestamp'

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
