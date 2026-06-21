import { describe, it, expect, afterEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useSessionTheme } from './useSessionTheme'

afterEach(() => {
  sessionStorage.clear()
})

describe('useSessionTheme', () => {
  it('returns the default puts theme when sessionStorage is empty', () => {
    const { result } = renderHook(() => useSessionTheme('puts'))
    expect(result.current[0]).toBe('mean-reversion')
  })

  it('returns the default calls theme when sessionStorage is empty', () => {
    const { result } = renderHook(() => useSessionTheme('calls'))
    expect(result.current[0]).toBe('ai-momentum')
  })

  it('restores a previously stored theme from sessionStorage', () => {
    sessionStorage.setItem('selectedTheme_puts', 'broken-momentum')
    const { result } = renderHook(() => useSessionTheme('puts'))
    expect(result.current[0]).toBe('broken-momentum')
  })

  it('writes the new theme to sessionStorage when updated', () => {
    const { result } = renderHook(() => useSessionTheme('puts'))
    act(() => result.current[1]('valuation-gravity'))
    expect(sessionStorage.getItem('selectedTheme_puts')).toBe('valuation-gravity')
    expect(result.current[0]).toBe('valuation-gravity')
  })

  it('falls back to the default when the stored value is an invalid theme ID', () => {
    sessionStorage.setItem('selectedTheme_calls', 'not-a-real-theme')
    const { result } = renderHook(() => useSessionTheme('calls'))
    expect(result.current[0]).toBe('ai-momentum')
  })

  it('keeps puts and calls storage keys independent', () => {
    sessionStorage.setItem('selectedTheme_puts', 'broken-momentum')
    const { result: putsResult }  = renderHook(() => useSessionTheme('puts'))
    const { result: callsResult } = renderHook(() => useSessionTheme('calls'))
    expect(putsResult.current[0]).toBe('broken-momentum')
    expect(callsResult.current[0]).toBe('ai-momentum')
  })

  it('does not persist a theme update to the other page key', () => {
    const { result } = renderHook(() => useSessionTheme('calls'))
    act(() => result.current[1]('52-week-breakouts'))
    expect(sessionStorage.getItem('selectedTheme_puts')).toBeNull()
  })
})
