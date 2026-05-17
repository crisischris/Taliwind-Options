import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import posthog from 'posthog-js'
import './index.css'
import App from './App.tsx'

posthog.init('phc_BMimCo8jpciMy2UWMub2VA5e8UA7iVuk9fRJAhALh7sR', {
  api_host: 'https://us.i.posthog.com',
  capture_pageview: false,  // fired manually on hash-based SPA navigation
  capture_pageleave: true,
})

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
