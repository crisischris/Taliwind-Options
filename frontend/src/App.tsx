import { useState, useEffect } from 'react'
import Navbar, { type Page } from './components/Navbar'
import SettingsModal, { type Theme } from './components/SettingsModal'
import HomePage from './pages/HomePage'
import PutsPage from './pages/PutsPage'
import CallsPage from './pages/CallsPage'
import AboutPage from './pages/AboutPage'
import Footer from './components/Footer'

function getInitialTheme(): Theme {
  const stored = localStorage.getItem('theme')
  if (stored === 'light') return 'light'
  return 'dark'
}

function pageFromHash(): Page {
  const hash = location.hash.slice(1)
  // PutsPage/CallsPage write report IDs (e.g. "put-scan-2026-05-15_15-35") into the hash for
  // deep-linking specific reports. Recognise those prefixes so sharing a report URL still lands
  // on the right page.
  if (hash === 'puts'  || hash.startsWith('put-scan-'))  return 'puts'
  if (hash === 'calls' || hash.startsWith('call-scan-')) return 'calls'
  if (hash === 'about') return 'about'
  return 'home'
}

function navigate(page: Page) {
  location.hash = page === 'home' ? '' : page
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

  function goTo(page: Page) {
    navigate(page)
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
      <main className="flex-1">
        {page === 'home'  && <HomePage onNavigate={goTo} />}
        {page === 'puts'  && <PutsPage />}
        {page === 'calls' && <CallsPage />}
        {page === 'about' && <AboutPage />}
      </main>
      <Footer />
      {showSettings && (
        <SettingsModal theme={theme} onToggle={toggleTheme} onClose={() => setSettings(false)} />
      )}
    </div>
  )
}
