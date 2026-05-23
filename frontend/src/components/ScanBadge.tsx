import { Badge } from '@/components/ui/badge'
import { getScanLabel } from '@/utils/timestamp'

function SunriseIcon({ className, 'aria-hidden': ariaHidden }: { className?: string; 'aria-hidden'?: boolean | 'true' }) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 80" className={className} aria-hidden={ariaHidden}
      fill="none" stroke="currentColor" strokeLinecap="round">
      <line x1="10" y1="52" x2="90" y2="52" strokeWidth="2" />
      <path d="M22,52 A28,28 0 0,1 78,52" strokeWidth="2.5" />
      <line x1="50" y1="18" x2="50" y2="8" strokeWidth="2" />
      <line x1="72" y1="25" x2="78" y2="18" strokeWidth="2" />
      <line x1="28" y1="25" x2="22" y2="18" strokeWidth="2" />
      <line x1="82" y1="44" x2="92" y2="42" strokeWidth="2" />
      <line x1="18" y1="44" x2="8"  y2="42" strokeWidth="2" />
    </svg>
  )
}

function MiddayIcon({ className, 'aria-hidden': ariaHidden }: { className?: string; 'aria-hidden'?: boolean | 'true' }) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 90" className={className} aria-hidden={ariaHidden}
      fill="none" stroke="currentColor" strokeLinecap="round">
      <line x1="10" y1="68" x2="90" y2="68" strokeWidth="2" />
      <circle cx="50" cy="42" r="18" strokeWidth="2.5" />
      <line x1="50" y1="18" x2="50" y2="8"  strokeWidth="2" />
      <line x1="50" y1="66" x2="50" y2="68" strokeWidth="2" />
      <line x1="72" y1="42" x2="82" y2="42" strokeWidth="2" />
      <line x1="28" y1="42" x2="18" y2="42" strokeWidth="2" />
      <line x1="66" y1="29" x2="73" y2="22" strokeWidth="2" />
      <line x1="34" y1="29" x2="27" y2="22" strokeWidth="2" />
      <line x1="66" y1="55" x2="72" y2="62" strokeWidth="2" />
      <line x1="34" y1="55" x2="28" y2="62" strokeWidth="2" />
    </svg>
  )
}

export default function ScanBadge({ generatedAt }: { generatedAt: string }) {
  const label = getScanLabel(generatedAt)
  const isMorning = label === 'Morning Data'
  return (
    <Badge variant={isMorning ? 'gold' : 'secondary'} className="gap-1.5">
      {isMorning
        ? <SunriseIcon aria-hidden="true" className="h-3.5 w-auto" />
        : <MiddayIcon  aria-hidden="true" className="h-3.5 w-auto" />}
      {label}
    </Badge>
  )
}
