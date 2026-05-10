import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    // proxy JSON report files to the local Python report server
    proxy: {
      '/manifest.json': 'http://localhost:8765',
      '/put-scan-': { target: 'http://localhost:8765', rewrite: p => p },
    },
  },
})
