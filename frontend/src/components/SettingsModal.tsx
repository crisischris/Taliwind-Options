import { Moon, Sun } from "lucide-react"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Switch } from "@/components/ui/switch"
import { SETTINGS } from "@/constants/strings"

type Theme = 'dark' | 'light'

interface Props {
  theme: Theme
  onToggle: () => void
  onClose: () => void
}

export default function SettingsModal({ theme, onToggle, onClose }: Props) {
  return (
    <Dialog open onOpenChange={open => !open && onClose()}>
      <DialogContent className="max-w-sm">
        <DialogHeader>
          <DialogTitle>{SETTINGS.title}</DialogTitle>
        </DialogHeader>

        <div className="flex items-center justify-between py-2">
          <div className="flex items-center gap-3">
            {theme === 'dark' ? <Moon className="h-4 w-4" /> : <Sun className="h-4 w-4" />}
            <div>
              <p className="text-sm font-medium">{SETTINGS.appearance}</p>
              <p className="text-xs text-muted-foreground">{theme === 'dark' ? SETTINGS.dark : SETTINGS.light}</p>
            </div>
          </div>
          <Switch checked={theme === 'dark'} onCheckedChange={onToggle} />
        </div>
      </DialogContent>
    </Dialog>
  )
}

export type { Theme }
