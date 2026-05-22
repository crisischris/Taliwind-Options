import { useEffect } from 'react'

// SEO: updates document.title and the meta[name="description"] tag on each page transition.
// Googlebot executes JavaScript and picks these up during deferred rendering; social crawlers
// (Twitter, LinkedIn, iMessage) do not run JS so they fall back to the static tags in index.html.
export function usePageMeta(title: string, description: string): void {
  useEffect(() => {
    document.title = title
    document.querySelector<HTMLMetaElement>('meta[name="description"]')?.setAttribute('content', description)
  }, [title, description])
}
