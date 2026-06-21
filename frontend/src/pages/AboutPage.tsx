import { useState } from 'react'
import { ChevronDown } from 'lucide-react'
import { Collapsible, CollapsibleTrigger, CollapsibleContent } from '@/components/ui/collapsible'
import { cn } from '@/lib/utils'
import { themesForPage, type ThemeDefinition } from '@/constants/themes'
import { ABOUT_PAGE, FILTERS_SHEET, PAGE_META } from '@/constants/strings'
import { usePageMeta } from '@/hooks/usePageMeta'

function ThemeColumn({ title, page }: { title: string; page: 'puts' | 'calls' }) {
  const themes = themesForPage(page)
  const [selectedId, setSelectedId] = useState(themes[0].id)
  const [open, setOpen] = useState(true)
  const selected = themes.find(t => t.id === selectedId) ?? themes[0]

  return (
    <Collapsible open={open} onOpenChange={setOpen}>
      <CollapsibleTrigger className="flex w-full items-center justify-between pb-2 border-b border-border mb-4 lg:cursor-default group">
        <h2 className="text-xl font-bold">{title}</h2>
        <ChevronDown
          aria-hidden="true"
          className={cn(
            'h-4 w-4 text-muted-foreground transition-transform duration-200 lg:hidden',
            open && 'rotate-180',
          )}
        /></CollapsibleTrigger>

      <CollapsibleContent>
        <div className="flex flex-wrap gap-2 mb-8">
          {themes.map(t => (
            <button
              key={t.id}
              onClick={() => setSelectedId(t.id)}
              className={cn(
                'flex items-center gap-1.5 rounded-full border px-3 py-1 text-sm font-medium transition-colors',
                selectedId === t.id
                  ? 'border-primary bg-primary text-primary-foreground'
                  : 'border-border hover:bg-muted',
              )}
            >
              {t.name}
            </button>
          ))}
        </div>

        <ThemeDetail theme={selected} />
      </CollapsibleContent>
    </Collapsible>
  )
}

function ThemeDetail({ theme }: { theme: ThemeDefinition }) {
  return (
    <div>
      <h3 className="text-base font-semibold mb-1">{FILTERS_SHEET.thesisHeading}</h3>
      <p className="text-muted-foreground leading-relaxed mb-8">{theme.thesis}</p>

      {theme.judgementCalls && (
        <>
          <h3 className="text-base font-semibold mb-1">{FILTERS_SHEET.judgementCallsHeading}</h3>
          <p className="text-muted-foreground text-sm mb-4">{theme.judgementCalls.intro}</p>
          <ul className="space-y-3">
            {theme.judgementCalls.rules.map(r => (
              <li key={r.rule} className="flex gap-3 text-sm">
                <span className="font-medium text-foreground shrink-0 w-48">{r.rule}</span>
                <span className="text-muted-foreground">{r.detail}</span>
              </li>
            ))}
          </ul>
        </>
      )}
    </div>
  )
}

export default function AboutPage() {
  usePageMeta(PAGE_META.about.title, PAGE_META.about.description)

  return (
    <div className="p-4 sm:p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold mb-4">{ABOUT_PAGE.title}</h1>
        <p className="text-muted-foreground leading-relaxed mb-10 max-w-2xl">{ABOUT_PAGE.intro}</p>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
          <ThemeColumn title="Call Themes" page="calls" />
          <ThemeColumn title="Put Themes"  page="puts" />
        </div>
      </div>
    </div>
  )
}
