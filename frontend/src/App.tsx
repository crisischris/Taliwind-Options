import { useState, useEffect } from 'react'
import Navbar, { type Page } from './components/Navbar'
import SettingsModal, { type Theme } from './components/SettingsModal'
import PutsPage from './pages/PutsPage'
import CallsPage from './pages/CallsPage'
import AboutPage from './pages/AboutPage'
import Footer from './components/Footer'

function getInitialTheme(): Theme {
  const stored = localStorage.getItem('theme')
  if (stored === 'light') return 'light'
  return 'dark'
}

export default function App() {
  const [page, setPage]             = useState<Page>('puts')
  const [theme, setTheme]           = useState<Theme>(getInitialTheme)
  const [showSettings, setSettings] = useState(false)

  useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark')
  }, [theme])

  function toggleTheme() {
    const next: Theme = theme === 'dark' ? 'light' : 'dark'
    setTheme(next)
    localStorage.setItem('theme', next)
  }

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <Navbar current={page} onChange={setPage} onOpenSettings={() => setSettings(true)} />
      <main className="flex-1">
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
