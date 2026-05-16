import { useState, useEffect } from 'react'
import Navbar, { type Page } from './components/Navbar'
import SettingsModal, { type Theme } from './components/SettingsModal'
import HomePage from './pages/HomePage'
import PutsPage from './pages/PutsPage'
import CallsPage from './pages/CallsPage'
import AboutPage from './pages/AboutPage'
import Footer from './components/Footer'
import BottomNav from './components/BottomNav'

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
    setTheme(next)
    localStorage.setItem('theme', next)
  }

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <Navbar current={page} onChange={goTo} onOpenSettings={() => setSettings(true)} />
      <main className="flex-1 pb-16 sm:pb-0 [overflow-x:clip]">
        {page === 'home'  && <HomePage onNavigate={goTo} />}
        {page === 'puts'  && <PutsPage />}
        {page === 'calls' && <CallsPage />}
        {page === 'about' && <AboutPage />}
      </main>
      <div className="hidden sm:block"><Footer /></div>
      <BottomNav current={page} onChange={goTo} />
      {showSettings && (
        <SettingsModal theme={theme} onToggle={toggleTheme} onClose={() => setSettings(false)} />
      )}
    </div>
  )
}
