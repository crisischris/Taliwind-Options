import { useState, useEffect, useRef } from 'react'
import { ChevronLeft, ChevronRight, Loader2 } from 'lucide-react'
import HeroCard from '@/components/HeroCard'
import { Skeleton } from '@/components/ui/skeleton'
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
  loading?: boolean
  // When true: desktop shows 3-col grid. When false (default): carousel on all sizes.
  desktopGrid?: boolean
}

function HeroCardSkeleton() {
  return (
    <div className="rounded-lg border-2 border-gold/20 p-5 space-y-4">
      <div className="flex items-center gap-3">
        <Skeleton className="h-7 w-7 rounded-full" />
        <Skeleton className="h-3 w-24" />
        <Loader2 className="ml-auto h-3.5 w-3.5 animate-spin text-muted-foreground/50" />
      </div>
      <div className="flex items-baseline gap-3">
        <Skeleton className="h-10 w-20" />
        <Skeleton className="h-5 w-16 rounded-full" />
      </div>
      <div className="flex gap-6 pt-2">
        <div className="space-y-2">
          <Skeleton className="h-9 w-14" />
          <Skeleton className="h-2.5 w-16" />
        </div>
        <div className="space-y-2">
          <Skeleton className="h-9 w-14" />
          <Skeleton className="h-2.5 w-16" />
        </div>
        <div className="space-y-2">
          <Skeleton className="h-6 w-12" />
          <Skeleton className="h-2.5 w-14" />
        </div>
        <div className="space-y-2">
          <Skeleton className="h-6 w-12" />
          <Skeleton className="h-2.5 w-14" />
        </div>
      </div>
    </div>
  )
}

function Carousel({ cards, onHeroClick }: { cards: DeckCard[]; onHeroClick: (id: string) => void }) {
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
    <div>
      {/* Scroll container with side arrows overlaid on desktop */}
      <div className="relative group">
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
          <>
            <button
              onClick={prev}
              aria-label="Previous"
              className={cn(
                'absolute left-3 top-1/2 -translate-y-1/2 z-10',
                'hidden md:flex items-center justify-center',
                'h-9 w-9 rounded-full',
                'bg-card/80 border border-border shadow-md backdrop-blur-sm',
                'opacity-0 group-hover:opacity-100 transition-opacity',
                'hover:bg-card hover:border-border/80',
              )}
            >
              <ChevronLeft className="h-4 w-4" />
            </button>
            <button
              onClick={next}
              aria-label="Next"
              className={cn(
                'absolute right-3 top-1/2 -translate-y-1/2 z-10',
                'hidden md:flex items-center justify-center',
                'h-9 w-9 rounded-full',
                'bg-card/80 border border-border shadow-md backdrop-blur-sm',
                'opacity-0 group-hover:opacity-100 transition-opacity',
                'hover:bg-card hover:border-border/80',
              )}
            >
              <ChevronRight className="h-4 w-4" />
            </button>
          </>
        )}
      </div>

      {/* Dot indicators + mobile arrows */}
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
  )
}

export default function HeroCardDeck({ cards, onHeroClick, loading = false, desktopGrid = false }: Props) {
  if (loading) {
    return desktopGrid ? (
      <>
        <div className="md:hidden px-2 py-1"><HeroCardSkeleton /></div>
        <div className="hidden md:grid grid-cols-3 gap-4">
          <HeroCardSkeleton /><HeroCardSkeleton /><HeroCardSkeleton />
        </div>
      </>
    ) : (
      <div className="px-2 py-1"><HeroCardSkeleton /></div>
    )
  }

  if (desktopGrid) {
    return (
      <>
        {/* Mobile: carousel */}
        <div className="md:hidden">
          <Carousel cards={cards} onHeroClick={onHeroClick} />
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

  // Carousel on all sizes (home page)
  return <Carousel cards={cards} onHeroClick={onHeroClick} />
}
