import { test, expect } from '@playwright/test'
import { mockEmptyReports, mockReports } from './fixtures'
import {
  APP_NAME,
  NAVBAR,
  HOME_PAGE,
  PUTS_PAGE,
  CALLS_PAGE,
  ABOUT_PAGE,
  FOOTER,
} from '../src/constants/strings'

test.beforeEach(async ({ page }) => {
  await mockEmptyReports(page)
  await page.goto('/')
})

test('home page renders both scan sections', async ({ page }) => {
  await expect(page.getByRole('heading', { name: new RegExp(HOME_PAGE.callsHeading) })).toBeVisible()
  await expect(page.getByRole('heading', { name: new RegExp(HOME_PAGE.putsHeading) })).toBeVisible()
})

test('desktop navbar has all links', async ({ page }) => {
  await expect(page.getByRole('button', { name: NAVBAR.calls }).first()).toBeVisible()
  await expect(page.getByRole('button', { name: NAVBAR.puts }).first()).toBeVisible()
  await expect(page.getByRole('button', { name: NAVBAR.about }).first()).toBeVisible()
})

test('navigates to puts page via navbar', async ({ page }) => {
  await page.getByRole('button', { name: NAVBAR.puts }).first().click()
  await expect(page.getByRole('heading', { name: PUTS_PAGE.title })).toBeVisible()
  await expect(page).toHaveURL(/#puts/)
})

test('navigates to calls page via navbar', async ({ page }) => {
  await page.getByRole('button', { name: NAVBAR.calls }).first().click()
  await expect(page.getByRole('heading', { name: CALLS_PAGE.title })).toBeVisible()
  await expect(page).toHaveURL(/#calls/)
})

test('navigates to about page via navbar', async ({ page }) => {
  await page.getByRole('button', { name: NAVBAR.about }).first().click()
  await expect(page.getByRole('heading', { name: ABOUT_PAGE.title })).toBeVisible()
  await expect(page).toHaveURL(/#about/)
})

test('logo click returns to home from another page', async ({ page }) => {
  await page.getByRole('button', { name: NAVBAR.puts }).first().click()
  await expect(page.getByRole('heading', { name: PUTS_PAGE.title })).toBeVisible()
  await page.getByRole('button', { name: new RegExp(APP_NAME) }).click()
  await expect(page.getByRole('heading', { name: new RegExp(HOME_PAGE.callsHeading) })).toBeVisible()
})

test('hash routing goes directly to puts page', async ({ page }) => {
  await page.goto('/#puts')
  await expect(page.getByRole('heading', { name: PUTS_PAGE.title })).toBeVisible()
})

test('hash routing goes directly to calls page', async ({ page }) => {
  await page.goto('/#calls')
  await expect(page.getByRole('heading', { name: CALLS_PAGE.title })).toBeVisible()
})

test('mobile bottom nav is visible on small screen', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 })
  await expect(page.locator('nav.fixed')).toBeVisible()
})

test('mobile bottom nav navigates pages', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 })
  await page.locator('nav.fixed button', { hasText: NAVBAR.puts }).click()
  await expect(page.getByRole('heading', { name: PUTS_PAGE.title })).toBeVisible()
})

test('mobile disclaimer is visible on small screen', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 })
  await expect(page.locator('main').getByText(FOOTER.notFinancialAdvice)).toBeVisible()
})

test('theme toggle button switches dark/light mode', async ({ page }) => {
  const isDark = await page.evaluate(() => document.documentElement.classList.contains('dark'))
  const label = isDark ? 'Switch to light mode' : 'Switch to dark mode'
  await page.getByRole('button', { name: label }).first().click()
  const isDarkAfter = await page.evaluate(() => document.documentElement.classList.contains('dark'))
  expect(isDarkAfter).toBe(!isDark)
})

test('navigation scrolls to top of page', async ({ page }) => {
  await mockReports(page)
  await page.goto('/#puts')
  await page.evaluate(() => window.scrollTo(0, 500))
  await page.getByRole('button', { name: NAVBAR.calls }).first().click()
  const scrollY = await page.evaluate(() => window.scrollY)
  expect(scrollY).toBe(0)
})

test('about page shows call and put theme columns', async ({ page }) => {
  await page.getByRole('button', { name: NAVBAR.about }).first().click()
  await expect(page.getByRole('heading', { name: 'Call Themes' })).toBeVisible()
  await expect(page.getByRole('heading', { name: 'Put Themes' })).toBeVisible()
})

test('about page shows thesis for selected theme', async ({ page }) => {
  await page.getByRole('button', { name: NAVBAR.about }).first().click()
  await expect(page.getByText(/Macro tailwinds in AI/)).toBeVisible()
  await expect(page.getByText(/500%\+ trailing 12-month gains/)).toBeVisible()
})
