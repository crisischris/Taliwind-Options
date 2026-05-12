import path from "path"
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: { "@": path.resolve(__dirname, "./src") },
  },
  server: {
    proxy: {
      '/manifest.json': 'http://localhost:8765',
      '/put-scan-': { target: 'http://localhost:8765', rewrite: p => p },
    },
  },
})
