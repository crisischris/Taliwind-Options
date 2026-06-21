import { test, expect } from '@playwright/test'
import { mockReports, mockReportsWithDiff, PUT_TICKER_AAPL, PUT_TICKER_MSFT, CALL_TICKER_NVDA } from './fixtures'
import {
  HERO_CARD,
  PUTS_PAGE,
  CALLS_PAGE,
  HOME_PAGE,
  FILTERS_SHEET,
} from '../src/constants/strings'

// ── New Only + hero click bug fix ─────────────────────────────────────────────

test('hero card click clears new only filter and shows ticker', async ({ page }) => {
  await mockReportsWithDiff(page)
  await page.goto('/#puts')

  // New Only button appears once diff data loads
  const newOnlyBtn = page.getByRole('button', { name: PUTS_PAGE.newOnly })
  await expect(newOnlyBtn).toBeVisible()
  await newOnlyBtn.click()

  // MSFT is new; AAPL is not — only MSFT tab visible
  await expect(page.getByRole('tab', { name: new RegExp(PUT_TICKER_MSFT.ticker) })).toBeVisible()
  await expect(page.getByRole('tab', { name: new RegExp(PUT_TICKER_AAPL.ticker) })).not.toBeVisible()

  // Click the short hero (AAPL) — should clear newOnly
  await page.locator('.md\\:grid').getByText(HERO_CARD.short.label).click()

  // newOnly cleared: AAPL tab now visible
  await expect(page.getByRole('tab', { name: new RegExp(PUT_TICKER_AAPL.ticker) })).toBeVisible()
})

test.beforeEach(async ({ page }) => {
  await mockReports(page)
})

// ── Puts page ─────────────────────────────────────────────────────────────────

test('puts page renders hero cards', async ({ page }) => {
  await page.goto('/#puts')
  await expect(page.locator('.md\\:grid').getByText(HERO_CARD.short.label)).toBeVisible()
})

test('puts page renders ticker tabs', async ({ page }) => {
  await page.goto('/#puts')
  await expect(page.getByRole('button', { name: new RegExp(PUT_TICKER_AAPL.ticker) })).toBeVisible()
  await expect(page.getByRole('button', { name: new RegExp(PUT_TICKER_MSFT.ticker) })).toBeVisible()
})

test('puts page report selector shows scan entry', async ({ page }) => {
  await page.goto('/#puts')
  // fixture timestamp 09:31 UTC = 5:31 AM ET → Morning label shown in the select trigger
  await expect(page.getByText(/Morning|Midday/).first()).toBeVisible()
})

test('puts ticker tab switches active ticker', async ({ page }) => {
  await page.goto('/#puts')
  await page.getByRole('button', { name: new RegExp(PUT_TICKER_MSFT.ticker) }).click()
  await expect(page.getByRole('cell', { name: PUT_TICKER_MSFT.puts[0].expiry })).toBeVisible()
})

test('puts expand/collapse all buttons work', async ({ page }) => {
  await page.goto('/#puts')
  await page.getByRole('button', { name: PUTS_PAGE.collapseAll, exact: true }).click()
  await expect(page.getByRole('button', { name: PUTS_PAGE.expandAll, exact: true })).toBeVisible()
  await page.getByRole('button', { name: PUTS_PAGE.expandAll, exact: true }).click()
  await expect(page.getByRole('cell', { name: PUT_TICKER_AAPL.puts[0].expiry })).toBeVisible()
})

test('puts filters sheet opens with methodology', async ({ page }) => {
  await page.goto('/#puts')
  await page.getByRole('button', { name: FILTERS_SHEET.triggerLabel }).click()
  await expect(page.getByText(FILTERS_SHEET.putsMethodologyTrigger)).toBeVisible()
  await expect(page.getByRole('heading', { name: FILTERS_SHEET.thesisHeading })).toBeVisible()
})

// ── Calls page ────────────────────────────────────────────────────────────────

test('calls page renders hero card', async ({ page }) => {
  await page.goto('/#calls')
  await expect(page.locator('.md\\:grid').getByText(HERO_CARD.short.label)).toBeVisible()
})

test('calls page renders ticker tab', async ({ page }) => {
  await page.goto('/#calls')
  await expect(page.getByRole('button', { name: new RegExp(CALL_TICKER_NVDA.ticker) })).toBeVisible()
})

test('calls filters sheet opens with methodology', async ({ page }) => {
  await page.goto('/#calls')
  await page.getByRole('button', { name: FILTERS_SHEET.triggerLabel }).click()
  await expect(page.getByText(FILTERS_SHEET.callsMethodologyTrigger)).toBeVisible()
})

// ── Home page with data ───────────────────────────────────────────────────────

test('home page shows hero cards when data loads', async ({ page }) => {
  await page.goto('/')
  await expect(page.getByText(HERO_CARD.short.label).first()).toBeVisible()
})

test('home page view all navigates to calls', async ({ page }) => {
  await page.goto('/')
  await page.getByRole('button', { name: HOME_PAGE.viewAll }).first().click()
  await expect(page.getByRole('heading', { name: CALLS_PAGE.title })).toBeVisible()
})

test('home page view all navigates to puts', async ({ page }) => {
  await page.goto('/')
  await page.getByRole('button', { name: HOME_PAGE.viewAll }).nth(1).click()
  await expect(page.getByRole('heading', { name: PUTS_PAGE.title })).toBeVisible()
})
