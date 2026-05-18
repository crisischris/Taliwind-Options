import { Home, TrendingUp, TrendingDown, Info } from 'lucide-react'
import { cn } from '@/lib/utils'
import { NAVBAR } from '@/constants/strings'
import { track } from '@/lib/analytics'
import type { Page } from '@/components/Navbar'

interface Props {
  current: Page
  onChange: (page: Page) => void
}

const ITEMS: { id: Page; label: string; icon: React.ReactNode }[] = [
  { id: 'home',  label: NAVBAR.home,  icon: <Home      className="h-5 w-5" /> },
  { id: 'calls', label: NAVBAR.calls, icon: <TrendingUp  className="h-5 w-5" /> },
  { id: 'puts',  label: NAVBAR.puts,  icon: <TrendingDown className="h-5 w-5" /> },
  { id: 'about', label: NAVBAR.about, icon: <Info      className="h-5 w-5" /> },
]

export default function BottomNav({ current, onChange }: Props) {
  return (
    <nav className="sm:hidden fixed bottom-0 inset-x-0 z-40 border-t bg-card">
      <div className="flex">
        {ITEMS.map(({ id, label, icon }) => (
          <button
            key={id}
            aria-current={current === id ? 'page' : undefined}
            onClick={() => { track('nav_clicked', { page: id, nav: 'bottom' }); onChange(id) }}
            className={cn(
              'flex flex-1 flex-col items-center gap-1 py-2 text-[10px] font-medium transition-colors',
              current === id ? 'text-primary' : 'text-muted-foreground',
            )}
          >
            <span aria-hidden="true">{icon}</span>
            {label}
          </button>
        ))}
      </div>
      {/* Safe area spacer for iPhone home indicator */}
      <div className="h-safe-bottom bg-card" style={{ height: 'env(safe-area-inset-bottom)' }} />
    </nav>
  )
}
