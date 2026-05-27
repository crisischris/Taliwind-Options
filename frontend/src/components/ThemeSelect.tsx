import { useState, useRef, useEffect } from 'react'
import { Info } from 'lucide-react'
import { themesForPage, type ThemeDefinition } from '@/constants/themes'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectSeparator,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { TooltipProvider, Tooltip, TooltipTrigger, TooltipContent } from '@/components/ui/tooltip'

interface Props {
  page: 'puts' | 'calls'
  value: string
  onValueChange: (id: string) => void
  showInfo?: boolean
}

function ThemeInfoTip({ theme }: { theme: ThemeDefinition }) {
  const [open, setOpen] = useState(false)
  const pinned = useRef(false)
  const closeTimer = useRef<ReturnType<typeof setTimeout> | null>(null)
  const triggerRef = useRef<HTMLButtonElement>(null)

  useEffect(() => {
    if (!open) return
    function onDocPointerDown(e: PointerEvent) {
      if (!triggerRef.current?.contains(e.target as Node)) {
        pinned.current = false
        setOpen(false)
      }
    }
    document.addEventListener('pointerdown', onDocPointerDown)
    return () => document.removeEventListener('pointerdown', onDocPointerDown)
  }, [open])

  // Reset when theme changes (eslint-disable: resetting tooltip state on prop change is intentional)
  // eslint-disable-next-line react-hooks/set-state-in-effect
  useEffect(() => { pinned.current = false; setOpen(false) }, [theme.id])

  function onOpenChange(val: boolean) {
    if (pinned.current) return
    if (!val) {
      closeTimer.current = setTimeout(() => setOpen(false), 100)
    } else {
      if (closeTimer.current) clearTimeout(closeTimer.current)
      setOpen(true)
    }
  }

  function onClick(e: React.MouseEvent) {
    e.stopPropagation()
    if (closeTimer.current) clearTimeout(closeTimer.current)
    if (pinned.current) {
      pinned.current = false
      setOpen(false)
    } else {
      pinned.current = true
      setOpen(true)
    }
  }

  return (
    <Tooltip open={open} onOpenChange={onOpenChange}>
      <TooltipTrigger
        ref={triggerRef}
        type="button"
        className="inline-flex items-center cursor-pointer focus:outline-none"
        onClick={onClick}
        aria-label={`About ${theme.name}`}
      >
        <Info className="h-3.5 w-3.5 text-muted-foreground opacity-50 hover:opacity-100 transition-opacity" />
      </TooltipTrigger>
      <TooltipContent side="bottom" align="start" className="max-w-[300px] space-y-1.5">
        <p className="font-semibold text-foreground">{theme.name}</p>
        <p className="text-muted-foreground">{theme.tagline}</p>
        <p className="leading-relaxed">{theme.thesis}</p>
      </TooltipContent>
    </Tooltip>
  )
}

export default function ThemeSelect({ page, value, onValueChange, showInfo = true }: Props) {
  const themes = themesForPage(page)

  const liveThemes = themes.filter(t => !t.stub)
  const stubThemes = themes.filter(t => t.stub)
  const selectedTheme = themes.find(t => t.id === value) ?? themes[0]

  return (
    <TooltipProvider delayDuration={300}>
      <div className="flex items-center gap-1.5">
        <Select value={value} onValueChange={onValueChange}>
          <SelectTrigger className="h-7 w-auto gap-1 rounded-full border-border bg-transparent px-3 text-xs font-medium shadow-none hover:bg-muted focus:ring-0">
            <span className="text-muted-foreground">Theme:</span>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {liveThemes.map(t => (
              <SelectItem key={t.id} value={t.id}>{t.name}</SelectItem>
            ))}
            {stubThemes.length > 0 && (
              <>
                <SelectSeparator />
                {stubThemes.map(t => (
                  <SelectItem key={t.id} value={t.id} className="text-muted-foreground">
                    {t.name}
                    <span className="ml-2 text-[10px] font-medium uppercase tracking-wide">Soon</span>
                  </SelectItem>
                ))}
              </>
            )}
          </SelectContent>
        </Select>
        {showInfo && <ThemeInfoTip theme={selectedTheme} />}
      </div>
    </TooltipProvider>
  )
}
