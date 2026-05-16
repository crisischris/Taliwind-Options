import { test, expect } from '@playwright/test'
import { mockReports, PUT_TICKER_AAPL, PUT_TICKER_MSFT, CALL_TICKER_NVDA } from './fixtures'
import {
  HERO_CARD,
  PUTS_PAGE,
  CALLS_PAGE,
  HOME_PAGE,
  FILTERS_SHEET,
  METHODOLOGY,
  CALLS_METHODOLOGY,
} from '../src/constants/strings'

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
  await expect(page.locator('select option')).toHaveCount(1)
})

test('puts ticker tab switches active ticker', async ({ page }) => {
  await page.goto('/#puts')
  await page.getByRole('button', { name: new RegExp(PUT_TICKER_MSFT.ticker) }).click()
  await expect(page.getByRole('cell', { name: PUT_TICKER_MSFT.puts[0].expiry })).toBeVisible()
})

test('puts expand/collapse all buttons work', async ({ page }) => {
  await page.goto('/#puts')
  await page.getByRole('button', { name: PUTS_PAGE.collapseAll }).click()
  await expect(page.getByRole('button', { name: PUTS_PAGE.expandAll })).toBeVisible()
  await page.getByRole('button', { name: PUTS_PAGE.expandAll }).click()
  await expect(page.getByRole('cell', { name: PUT_TICKER_AAPL.puts[0].expiry })).toBeVisible()
})

test('puts filters sheet opens with methodology', async ({ page }) => {
  await page.goto('/#puts')
  await page.getByRole('button', { name: FILTERS_SHEET.triggerLabel }).click()
  await expect(page.getByText(METHODOLOGY.trigger)).toBeVisible()
  await expect(page.getByRole('heading', { name: METHODOLOGY.thesis.heading })).toBeVisible()
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
  await expect(page.getByText(CALLS_METHODOLOGY.trigger)).toBeVisible()
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
