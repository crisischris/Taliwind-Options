import { CALLS_PAGE } from '@/constants/strings'

export default function CallsPage() {
  return (
    <div className="flex flex-col items-center justify-center py-32 gap-4">
      <span className="text-5xl">{CALLS_PAGE.icon}</span>
      <h1 className="text-2xl font-bold">{CALLS_PAGE.title}</h1>
      <p className="text-muted-foreground">{CALLS_PAGE.comingSoon}</p>
    </div>
  )
}
