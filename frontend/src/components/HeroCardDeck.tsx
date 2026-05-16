import { useState, useEffect, useRef } from 'react'
import { ChevronLeft, ChevronRight } from 'lucide-react'
import HeroCard from '@/components/HeroCard'
import { cn } from '@/lib/utils'
import type { BaseHeroOption } from '@/components/HeroCard'

export interface DeckCard {
  option: BaseHeroOption | null
  movePct: number
  moveLabel: string
  label: string
  icon: string
  heroRowId: string
}

interface Props {
  cards: DeckCard[]
  onHeroClick: (heroRowId: string) => void
}

export default function HeroCardDeck({ cards, onHeroClick }: Props) {
  const [active, setActive] = useState(0)
  const scrollRef = useRef<HTMLDivElement>(null)
  const cardRefs = useRef<(HTMLDivElement | null)[]>([])

  useEffect(() => {
    const root = scrollRef.current
    if (!root) return
    const observer = new IntersectionObserver(
      entries => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            const idx = cardRefs.current.indexOf(entry.target as HTMLDivElement)
            if (idx !== -1) setActive(idx)
          }
        }
      },
      { root, threshold: 0.6 },
    )
    cardRefs.current.forEach(el => el && observer.observe(el))
    return () => observer.disconnect()
  }, [cards])

  function scrollTo(idx: number) {
    cardRefs.current[idx]?.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'start' })
  }

  const prev = () => scrollTo((active - 1 + cards.length) % cards.length)
  const next = () => scrollTo((active + 1) % cards.length)

  return (
    <>
      {/* Mobile: swipeable scroll snap carousel */}
      <div className="md:hidden">
        <div
          ref={scrollRef}
          className="flex overflow-x-auto snap-x snap-mandatory scrollbar-none items-stretch"
        >
          {cards.map((card, i) => (
            <div
              key={card.heroRowId}
              ref={el => { cardRefs.current[i] = el }}
              className="snap-start flex-shrink-0 w-full px-2 py-1"
            >
              <HeroCard {...card} onScrollTo={onHeroClick} />
            </div>
          ))}
        </div>

        {cards.length > 1 && (
          <div className="flex items-center justify-center gap-3 mt-3">
            <button
              onClick={prev}
              className={cn(
                'rounded-full border border-border p-1.5 transition-colors',
                'hover:bg-accent hover:border-accent-foreground/20',
              )}
              aria-label="Previous"
            >
              <ChevronLeft className="h-4 w-4 text-muted-foreground" />
            </button>
            {cards.map((_, i) => (
              <button
                key={i}
                onClick={() => scrollTo(i)}
                aria-label={`Go to card ${i + 1}`}
                className={cn(
                  'rounded-full transition-all',
                  i === active ? 'w-4 h-1.5 bg-primary' : 'w-1.5 h-1.5 bg-border hover:bg-muted-foreground',
                )}
              />
            ))}
            <button
              onClick={next}
              className={cn(
                'rounded-full border border-border p-1.5 transition-colors',
                'hover:bg-accent hover:border-accent-foreground/20',
              )}
              aria-label="Next"
            >
              <ChevronRight className="h-4 w-4 text-muted-foreground" />
            </button>
          </div>
        )}
      </div>

      {/* Desktop: 3-column grid */}
      <div className="hidden md:grid grid-cols-3 gap-4">
        {cards.map(card => (
          <HeroCard key={card.heroRowId} {...card} onScrollTo={onHeroClick} />
        ))}
      </div>
    </>
  )
}
