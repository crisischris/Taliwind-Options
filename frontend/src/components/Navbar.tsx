import React from 'react'
import { Sun, Moon, TrendingUp, TrendingDown } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { APP_NAME, NAVBAR } from '@/constants/strings'
import { track } from '@/lib/analytics'
import logoLight from '@/assets/tailwind-options-logo.svg'
import logoDark from '@/assets/tailwind-options-logo-dark.svg'
type Theme = 'dark' | 'light'
type Page  = 'home' | 'puts' | 'calls' | 'about'

interface Props {
  current: Page
  onChange: (page: Page) => void
  theme: Theme
  onToggleTheme: () => void
}

const LINKS: { id: Page; label: string; icon?: React.ReactNode }[] = [
  { id: 'home',  label: NAVBAR.home  },
  { id: 'calls', label: NAVBAR.calls, icon: <TrendingUp  className="h-3.5 w-3.5 text-primary" /> },
  { id: 'puts',  label: NAVBAR.puts,  icon: <TrendingDown className="h-3.5 w-3.5 text-primary" /> },
  { id: 'about', label: NAVBAR.about },
]

export default function Navbar({ current, onChange, theme, onToggleTheme }: Props) {
  const ThemeIcon = theme === 'dark' ? Sun : Moon

  return (
    <header className="sticky top-0 z-40 w-full border-b bg-card shadow-sm">
      <div className="flex h-16 items-center px-4 sm:px-8">
        <button
          className="mr-auto hover:opacity-80 transition-opacity"
          onClick={() => onChange('home')}
          aria-label={`${APP_NAME} home`}
        >
          <img src={logoLight} alt={APP_NAME} className="h-12 dark:hidden" />
          <img src={logoDark}  alt={APP_NAME} className="h-12 hidden dark:block" />
        </button>

        {/* Desktop nav */}
        <nav className="hidden sm:flex items-center gap-1">
          {LINKS.map(({ id, label, icon }) => (
            <Button
              key={id}
              variant={current === id ? 'secondary' : 'ghost'}
              size="sm"
              onClick={() => { track('nav_clicked', { page: id, nav: 'top' }); onChange(id) }}
              className="flex items-center gap-1.5"
            >
              {icon}
              {label}
            </Button>
          ))}
          <span className="w-px h-5 bg-border mx-1" />
          <Button
            variant="ghost"
            size="icon"
            onClick={() => { track('theme_toggled', { theme: theme === 'dark' ? 'light' : 'dark' }); onToggleTheme() }}
            aria-label={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
          >
            <ThemeIcon className="h-4 w-4" />
          </Button>
        </nav>

        {/* Mobile: theme toggle only — nav is in BottomNav */}
        <div className="flex sm:hidden">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => { track('theme_toggled', { theme: theme === 'dark' ? 'light' : 'dark' }); onToggleTheme() }}
            aria-label={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
          >
            <ThemeIcon className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </header>
  )
}

export type { Page }
