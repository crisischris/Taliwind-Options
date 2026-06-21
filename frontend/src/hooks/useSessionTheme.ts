import { useState } from 'react'
import { themesForPage } from '@/constants/themes'

export function useSessionTheme(page: 'puts' | 'calls'): [string, (id: string) => void] {
  const key = `selectedTheme_${page}`
  const [themeId, setThemeId] = useState(() => {
    const stored = sessionStorage.getItem(key)
    const themes = themesForPage(page)
    return themes.some(t => t.id === stored) ? stored! : themes[0].id
  })

  function setTheme(id: string) {
    sessionStorage.setItem(key, id)
    setThemeId(id)
  }

  return [themeId, setTheme]
}
