import { useState } from 'react'
import { ChevronDown } from 'lucide-react'
import { cn } from '@/lib/utils'
import { themesForPage, type ThemeDefinition } from '@/constants/themes'
import { Badge } from '@/components/ui/badge'

interface Props {
  page: 'puts' | 'calls'
}

function getInitialThemeId(page: 'puts' | 'calls', themes: ThemeDefinition[]): string {
  const stored = localStorage.getItem(`selectedTheme_${page}`)
  return themes.find(t => t.id === stored)?.id ?? themes[0].id
}

export default function ThemePanel({ page }: Props) {
  const themes = themesForPage(page)
  const [selectedId, setSelectedId] = useState(() => getInitialThemeId(page, themes))
  const [expanded, setExpanded] = useState(false)

  const theme = themes.find(t => t.id === selectedId) ?? themes[0]

  function select(id: string) {
    setSelectedId(id)
    setExpanded(false)
    localStorage.setItem(`selectedTheme_${page}`, id)
  }

  return (
    <div className="border-b bg-muted/20">
      <div className="mx-auto max-w-5xl px-4 sm:px-8">
        {/* Theme pills */}
        <div className="flex items-center gap-2 py-3">
          <span className="text-xs font-medium text-muted-foreground mr-1 shrink-0">Theme</span>
          <div className="flex flex-wrap gap-2">
            {themes.map(t => (
              <button
                key={t.id}
                onClick={() => select(t.id)}
                className={cn(
                  'inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-medium transition-colors',
                  selectedId === t.id
                    ? 'border-primary bg-primary text-primary-foreground'
                    : 'border-border bg-background text-foreground hover:bg-muted',
                )}
              >
                <span className="leading-none">{t.icon}</span>
                {t.name}
                {t.stub && (
                  <Badge variant="outline" className="ml-0.5 h-4 px-1 text-[10px] font-normal">
                    Soon
                  </Badge>
                )}
              </button>
            ))}
          </div>
        </div>

        {/* Collapsible thesis */}
        <button
          onClick={() => setExpanded(e => !e)}
          aria-expanded={expanded}
          className="flex w-full items-center gap-3 pb-3 text-left"
        >
          <span className="text-base leading-none">{theme.icon}</span>
          <div className="flex min-w-0 flex-1 flex-col sm:flex-row sm:items-center sm:gap-2">
            <span className="text-sm font-semibold">{theme.name}</span>
            <span className="truncate text-xs text-muted-foreground sm:text-sm">{theme.tagline}</span>
          </div>
          <ChevronDown
            className={cn(
              'h-4 w-4 shrink-0 text-muted-foreground transition-transform duration-200',
              expanded && 'rotate-180',
            )}
          />
        </button>

        {expanded && (
          <div className="pb-4 pl-7">
            <p className="text-sm leading-relaxed text-muted-foreground">{theme.thesis}</p>
            {theme.stub && (
              <p className="mt-2 text-xs text-muted-foreground/60 italic">
                Scanner for this theme is in development — signals coming soon.
              </p>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
