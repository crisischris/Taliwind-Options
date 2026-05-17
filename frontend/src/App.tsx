import { useState, useEffect } from 'react'
import posthog from 'posthog-js'
import { track } from './lib/analytics'
import Navbar, { type Page } from './components/Navbar'
import SettingsModal, { type Theme } from './components/SettingsModal'
import HomePage from './pages/HomePage'
import PutsPage from './pages/PutsPage'
import CallsPage from './pages/CallsPage'
import AboutPage from './pages/AboutPage'
import Footer from './components/Footer'
import BottomNav from './components/BottomNav'
import { FOOTER } from './constants/strings'

function getInitialTheme(): Theme {
  const stored = localStorage.getItem('theme')
  if (stored === 'light') return 'light'
  return 'dark'
}

// Hash format: "#page" or "#page;heroRowId" or "#put-scan-..." (report deep-link)
function pageFromHash(): Page {
  const segment = location.hash.slice(1).split(';')[0]
  if (segment === 'puts'  || segment.startsWith('put-scan-'))  return 'puts'
  if (segment === 'calls' || segment.startsWith('call-scan-')) return 'calls'
  if (segment === 'about') return 'about'
  return 'home'
}

function navigate(page: Page, heroRowId?: string) {
  if (page === 'home') { location.hash = ''; return }
  location.hash = heroRowId ? `${page};${heroRowId}` : page
}

export default function App() {
  const [page, setPage]             = useState<Page>(pageFromHash)
  const [theme, setTheme]           = useState<Theme>(getInitialTheme)
  const [showSettings, setSettings] = useState(false)

  useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark')
  }, [theme])

  useEffect(() => {
    posthog.capture('$pageview', { page })
  }, [page])

  useEffect(() => {
    function onHashChange() { setPage(pageFromHash()) }
    window.addEventListener('hashchange', onHashChange)
    return () => window.removeEventListener('hashchange', onHashChange)
  }, [])

  function goTo(page: Page, heroRowId?: string) {
    navigate(page, heroRowId)
    setPage(page)
  }

  function toggleTheme() {
    const next: Theme = theme === 'dark' ? 'light' : 'dark'
    track('theme_toggled', { theme: next })
    setTheme(next)
    localStorage.setItem('theme', next)
  }

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <Navbar current={page} onChange={goTo} onOpenSettings={() => { track('settings_opened'); setSettings(true) }} />
      <main className="flex-1 [overflow-x:clip]">
        {page === 'home'  && <HomePage onNavigate={goTo} />}
        {page === 'puts'  && <PutsPage />}
        {page === 'calls' && <CallsPage />}
        {page === 'about' && <AboutPage />}
        <div className="sm:hidden border-t border-border bg-muted/30 px-4 py-3 pb-16 text-center text-[11px] text-muted-foreground">
          <span className="font-medium">{FOOTER.notFinancialAdvice}</span>{' '}
          {FOOTER.mobileDisclaimer}
        </div>
      </main>
      <div className="hidden sm:block"><Footer /></div>
      <BottomNav current={page} onChange={goTo} />
      {showSettings && (
        <SettingsModal theme={theme} onToggle={toggleTheme} onClose={() => setSettings(false)} />
      )}
    </div>
  )
}
