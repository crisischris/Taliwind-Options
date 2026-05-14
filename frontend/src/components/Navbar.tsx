import { Settings } from "lucide-react"
import { Button } from "@/components/ui/button"
import { APP, NAVBAR } from "@/constants/strings"

type Page = 'puts' | 'calls' | 'about'

interface Props {
  current: Page
  onChange: (page: Page) => void
  onOpenSettings: () => void
}

const LINKS: { id: Page; label: string }[] = [
  { id: 'puts',  label: NAVBAR.puts  },
  { id: 'calls', label: NAVBAR.calls },
  { id: 'about', label: NAVBAR.about },
]

export default function Navbar({ current, onChange, onOpenSettings }: Props) {
  return (
    <header className="sticky top-0 z-40 w-full border-b bg-card shadow-sm">
      <div className="flex h-14 items-center px-4 sm:px-8">
        <span className="text-base font-bold tracking-tight mr-auto">{APP.brand}</span>
        <nav className="flex items-center gap-1">
          {LINKS.map(({ id, label }) => (
            <Button
              key={id}
              variant={current === id ? "secondary" : "ghost"}
              size="sm"
              onClick={() => onChange(id)}
            >
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
