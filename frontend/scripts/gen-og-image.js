// SEO: generates the Open Graph image (og-image.png) used in social link previews.
// Renders an HTML layout at 1200x630 via Playwright and saves it to public/.
// Run: node scripts/gen-og-image.js

import { chromium } from 'playwright'
import { fileURLToPath } from 'url'
import { dirname, join } from 'path'

const __dirname = dirname(fileURLToPath(import.meta.url))
const outPath = join(__dirname, '../public/og-image.png')

const html = `<!doctype html>
<html>
<head>
<meta charset="UTF-8" />
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }

  body {
    width: 1200px;
    height: 630px;
    background: #0a0f0d;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    position: relative;
  }

  /* Subtle radial glow behind the logo */
  .glow {
    position: absolute;
    width: 600px;
    height: 600px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(0,184,156,0.12) 0%, transparent 70%);
    left: 50%;
    top: 50%;
    transform: translate(-50%, -50%);
    pointer-events: none;
  }

  /* Thin green accent bar along the top */
  .top-bar {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: #00b89c;
  }

  .content {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 28px;
    position: relative;
    z-index: 1;
  }

  /* Logo — same SVG as favicon, scaled up */
  .logo {
    width: 120px;
    height: 120px;
  }

  .text-block {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 14px;
  }

  .app-name {
    font-size: 64px;
    font-weight: 700;
    letter-spacing: -1.5px;
    color: #ffffff;
  }

  .tagline {
    font-size: 22px;
    font-weight: 400;
    color: rgba(255,255,255,0.55);
    max-width: 680px;
    text-align: center;
    line-height: 1.45;
  }

  /* Pill badge */
  .badge {
    margin-top: 8px;
    padding: 6px 18px;
    border-radius: 9999px;
    border: 1px solid rgba(0,184,156,0.45);
    color: #00b89c;
    font-size: 14px;
    font-weight: 500;
    letter-spacing: 0.5px;
  }
</style>
</head>
<body>
  <div class="top-bar"></div>
  <div class="glow"></div>
  <div class="content">
    <svg class="logo" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
      <rect width="100" height="100" rx="22" fill="#00b89c"/>
      <rect x="16" y="58" width="18" height="28" rx="4" fill="rgba(255,255,255,0.32)"/>
      <rect x="41" y="40" width="18" height="46" rx="4" fill="rgba(255,255,255,0.62)"/>
      <rect x="66" y="18" width="18" height="68" rx="4" fill="#ffffff"/>
    </svg>
    <div class="text-block">
      <div class="app-name">Tailwind Options</div>
      <div class="tagline">Asymmetric options plays — cheap puts on extreme gainers, cheap calls on momentum names.</div>
      <div class="badge">tailwindoptions.com</div>
    </div>
  </div>
</body>
</html>`

const browser = await chromium.launch()
const page = await browser.newPage()
await page.setViewportSize({ width: 1200, height: 630 })
await page.setContent(html, { waitUntil: 'domcontentloaded' })
await page.screenshot({ path: outPath, type: 'png' })
await browser.close()

console.log(`og-image.png written to ${outPath}`)
