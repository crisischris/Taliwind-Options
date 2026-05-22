import { ABOUT_PAGE, METHODOLOGY, CALLS_METHODOLOGY, PAGE_META } from '@/constants/strings'
import { usePageMeta } from '@/hooks/usePageMeta'

function MethodologySection({ m }: { m: typeof METHODOLOGY | typeof CALLS_METHODOLOGY }) {
  return (
    <div className="mb-12">
      <h3 className="text-lg font-semibold mb-2">{m.thesis.heading}</h3>
      <p className="text-muted-foreground leading-relaxed mb-6">{m.thesis.body}</p>

      <h3 className="text-lg font-semibold mb-1">{m.judgementCalls.heading}</h3>
      <p className="text-muted-foreground text-sm mb-4">{m.judgementCalls.intro}</p>
      <ul className="space-y-3">
        {m.judgementCalls.rules.map(r => (
          <li key={r.rule} className="flex gap-3 text-sm">
            <span className="font-medium text-foreground shrink-0 w-48">{r.rule}</span>
            <span className="text-muted-foreground">{r.detail}</span>
          </li>
        ))}
      </ul>
    </div>
  )
}

export default function AboutPage() {
  usePageMeta(PAGE_META.about.title, PAGE_META.about.description)

  return (
    <div className="p-4 sm:p-8">
      <div className="max-w-7xl mx-auto py-16">
        <h1 className="text-3xl font-bold mb-4">{ABOUT_PAGE.title}</h1>
        <p className="text-muted-foreground leading-relaxed mb-10 max-w-2xl">{ABOUT_PAGE.intro}</p>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-10">
          <div>
            <h2 className="text-xl font-bold mb-6 pb-2 border-b border-border">Call Report</h2>
            <MethodologySection m={CALLS_METHODOLOGY} />
          </div>
          <div>
            <h2 className="text-xl font-bold mb-6 pb-2 border-b border-border">Put Report</h2>
            <MethodologySection m={METHODOLOGY} />
          </div>
        </div>
      </div>
    </div>
  )
}
