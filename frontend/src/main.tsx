import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { APP_NAME } from './constants/strings'

// Set here so APP_NAME is the single source of truth — index.html title is intentionally blank
document.title = APP_NAME

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
