import path from "path"
import { defineConfig } from 'vitest/config'
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
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./src/test/setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'lcov'],
      include: ['src/utils/**', 'src/hooks/**'],
      thresholds: { lines: 90, branches: 90 },
    },
  },
})
