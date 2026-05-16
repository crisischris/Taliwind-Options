import { test, expect } from '@playwright/test'
import { mockEmptyReports } from './fixtures'
import {
  APP_NAME,
  NAVBAR,
  SETTINGS,
  HOME_PAGE,
  PUTS_PAGE,
  CALLS_PAGE,
  ABOUT_PAGE,
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
  // The bottom nav has `fixed` class; desktop nav has `hidden sm:flex`
  await expect(page.locator('nav.fixed')).toBeVisible()
})

test('mobile bottom nav navigates pages', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 })
  await page.locator('nav.fixed button', { hasText: NAVBAR.puts }).click()
  await expect(page.getByRole('heading', { name: PUTS_PAGE.title })).toBeVisible()
})

test('settings modal opens and closes', async ({ page }) => {
  await page.getByRole('button', { name: SETTINGS.title }).click()
  await expect(page.getByRole('dialog')).toBeVisible()
  await page.keyboard.press('Escape')
  await expect(page.getByRole('dialog')).not.toBeVisible()
})
