import { Lock } from 'lucide-react'

export function Label({ children }: { children: React.ReactNode }) {
  return <p className="text-sm font-semibold mb-1">{children}</p>
}

export function Hint({ children }: { children: React.ReactNode }) {
  return <p className="text-xs text-muted-foreground leading-relaxed">{children}</p>
}

export function FixedRule({ rule, detail }: { rule: string; detail: string }) {
  return (
    <li className="border-l-2 border-border pl-3">
      <div className="flex items-center gap-1.5 mb-0.5">
        <Label>{rule}</Label>
        <Lock className="h-3 w-3 text-muted-foreground/50" />
      </div>
      <Hint>{detail}</Hint>
    </li>
  )
}

export interface EditableRuleProps {
  rule: string
  detail: string
  children: React.ReactNode
}

export function EditableRule({ rule, detail, children }: EditableRuleProps) {
  return (
    <li className="border-l-2 border-primary/40 pl-3 space-y-2">
      <Label>{rule}</Label>
      {children}
      <Hint>{detail}</Hint>
    </li>
  )
}

export function NumberInput({
  value, onChange, min, max, unit = '',
}: {
  value: number; onChange: (v: number) => void; min: number; max: number; unit?: string
}) {
  return (
    <div className="flex items-center gap-2">
      <input
        type="range"
        min={min} max={max}
        value={value}
        onChange={e => onChange(Number(e.target.value))}
        className="flex-1 accent-primary h-1.5"
      />
      <span className="text-sm font-mono w-20 text-right tabular-nums">
        {value.toLocaleString()}{unit}
      </span>
    </div>
  )
}
