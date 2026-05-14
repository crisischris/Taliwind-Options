import { describe, it, expect } from 'vitest'
import { beCls, ivCls, probCls } from './colors'

describe('beCls', () => {
  it('returns text-gain below 25', () => {
    expect(beCls(0)).toBe('text-gain')
    expect(beCls(24.9)).toBe('text-gain')
  })

  it('returns text-caution between 25 and 49', () => {
    expect(beCls(25)).toBe('text-caution')
    expect(beCls(49.9)).toBe('text-caution')
  })

  it('returns text-loss at 50 and above', () => {
    expect(beCls(50)).toBe('text-loss')
    expect(beCls(100)).toBe('text-loss')
  })

  it('handles boundary at 25 exactly', () => {
    expect(beCls(24.999)).toBe('text-gain')
    expect(beCls(25)).toBe('text-caution')
  })

  it('handles boundary at 50 exactly', () => {
    expect(beCls(49.999)).toBe('text-caution')
    expect(beCls(50)).toBe('text-loss')
  })
})

describe('ivCls', () => {
  it('returns text-gain below 1.0', () => {
    expect(ivCls(0)).toBe('text-gain')
    expect(ivCls(0.99)).toBe('text-gain')
  })

  it('returns text-caution between 1.0 and 1.49', () => {
    expect(ivCls(1.0)).toBe('text-caution')
    expect(ivCls(1.49)).toBe('text-caution')
  })

  it('returns text-loss at 1.5 and above', () => {
    expect(ivCls(1.5)).toBe('text-loss')
    expect(ivCls(3.0)).toBe('text-loss')
  })

  it('handles boundary at 1.0 exactly', () => {
    expect(ivCls(0.999)).toBe('text-gain')
    expect(ivCls(1.0)).toBe('text-caution')
  })

  it('handles boundary at 1.5 exactly', () => {
    expect(ivCls(1.499)).toBe('text-caution')
    expect(ivCls(1.5)).toBe('text-loss')
  })
})

describe('probCls', () => {
  it('returns text-muted-foreground below 0.10', () => {
    expect(probCls(0)).toBe('text-muted-foreground')
    expect(probCls(0.09)).toBe('text-muted-foreground')
  })

  it('returns text-caution between 0.10 and 0.24', () => {
    expect(probCls(0.10)).toBe('text-caution')
    expect(probCls(0.24)).toBe('text-caution')
  })

  it('returns text-gain at 0.25 and above', () => {
    expect(probCls(0.25)).toBe('text-gain')
    expect(probCls(1.0)).toBe('text-gain')
  })

  it('handles boundary at 0.10 exactly', () => {
    expect(probCls(0.099)).toBe('text-muted-foreground')
    expect(probCls(0.10)).toBe('text-caution')
  })

  it('handles boundary at 0.25 exactly', () => {
    expect(probCls(0.249)).toBe('text-caution')
    expect(probCls(0.25)).toBe('text-gain')
  })
})
