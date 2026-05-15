import React from "react"
import { Settings, TrendingUp, TrendingDown } from "lucide-react"
import { Button } from "@/components/ui/button"
import { APP_NAME, NAVBAR } from "@/constants/strings"
import logoLight from "@/assets/options-hunter-logo.svg"
import logoDark from "@/assets/options-hunter-logo-dark.svg"

type Page = 'home' | 'puts' | 'calls' | 'about'

interface Props {
  current: Page
  onChange: (page: Page) => void
  onOpenSettings: () => void
}

const LINKS: { id: Page; label: string; icon?: React.ReactNode }[] = [
  { id: 'home',  label: NAVBAR.home  },
  { id: 'calls', label: NAVBAR.calls, icon: <TrendingUp  className="h-3.5 w-3.5 text-primary" /> },
  { id: 'puts',  label: NAVBAR.puts,  icon: <TrendingDown className="h-3.5 w-3.5 text-primary" /> },
  { id: 'about', label: NAVBAR.about },
]

export default function Navbar({ current, onChange, onOpenSettings }: Props) {
  return (
    <header className="sticky top-0 z-40 w-full border-b bg-card shadow-sm">
      <div className="flex h-16 items-center px-4 sm:px-8">
        <button
          className="mr-auto hover:opacity-80 transition-opacity"
          onClick={() => onChange('home')}
          aria-label={`${APP_NAME} home`}
        >
          {/* CSS-only theme swap — no JS theme prop needed in Navbar */}
          <img src={logoLight} alt={APP_NAME} className="h-12 dark:hidden" />
          <img src={logoDark}  alt={APP_NAME} className="h-12 hidden dark:block" />
        </button>
        <nav className="flex items-center gap-1">
          {LINKS.map(({ id, label, icon }) => (
            <Button
              key={id}
              variant={current === id ? "secondary" : "ghost"}
              size="sm"
              onClick={() => onChange(id)}
              className="flex items-center gap-1.5"
            >
              {icon}
              {label}
            </Button>
          ))}
          <span className="w-px h-5 bg-border mx-1" />
          <Button variant="ghost" size="icon" onClick={onOpenSettings} aria-label="Settings">
            <Settings className="h-4 w-4" />
          </Button>
        </nav>
      </div>
    </header>
  )
}

export type { Page }
