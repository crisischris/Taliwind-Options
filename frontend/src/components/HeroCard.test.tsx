import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import HeroCard from './HeroCard'
import type { BaseHeroOption } from './HeroCard'

const OPTION: BaseHeroOption = {
  contract:        'AAPL261219C00250000',
  ticker:          'AAPL',
  current_price:   200,
  return_multiple: 150,
  prob_itm:        0.08,
  ask:             2.5,
  strike:          250,
  expiry:          '2026-12-19',
  iv:              0.45,
}

const BASE_PROPS = {
  movePct:    35,
  moveLabel:  '90d',
  label:      'Best Short-Dated',
  icon:       '⚡',
  emptyLabel: 'No qualifying short-dated option found this session',
  heroRowId:  'hero-short',
  onScrollTo: vi.fn(),
}

describe('HeroCard', () => {
  it('renders option data when option is provided', () => {
    render(<HeroCard {...BASE_PROPS} option={OPTION} />)
    expect(screen.getByText('AAPL')).toBeInTheDocument()
    expect(screen.getByText('150x')).toBeInTheDocument()
    expect(screen.getByText('Best Short-Dated')).toBeInTheDocument()
  })

  it('calls onScrollTo when clicked', () => {
    const onScrollTo = vi.fn()
    render(<HeroCard {...BASE_PROPS} option={OPTION} onScrollTo={onScrollTo} />)
    fireEvent.click(screen.getByRole('button'))
    expect(onScrollTo).toHaveBeenCalledWith('hero-short')
  })

  it('renders empty state when option is null', () => {
    render(<HeroCard {...BASE_PROPS} option={null} />)
    expect(screen.getByText('Best Short-Dated')).toBeInTheDocument()
    expect(screen.getByText('No qualifying short-dated option found this session')).toBeInTheDocument()
    expect(screen.queryByRole('button')).not.toBeInTheDocument()
  })

  it('empty state does not show ticker data', () => {
    render(<HeroCard {...BASE_PROPS} option={null} />)
    expect(screen.queryByText('AAPL')).not.toBeInTheDocument()
    expect(screen.queryByText('150x')).not.toBeInTheDocument()
  })
})
