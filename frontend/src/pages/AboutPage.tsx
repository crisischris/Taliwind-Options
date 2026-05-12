import { ABOUT_PAGE } from '@/constants/strings'

export default function AboutPage() {
  return (
    <div className="p-4 sm:p-8">
      <div className="max-w-2xl mx-auto py-16">
        <h1 className="text-3xl font-bold mb-4">{ABOUT_PAGE.title}</h1>
        <p className="text-muted-foreground leading-relaxed">{ABOUT_PAGE.body1}</p>
        <p className="text-muted-foreground leading-relaxed mt-4">{ABOUT_PAGE.body2}</p>
      </div>
    </div>
  )
}
