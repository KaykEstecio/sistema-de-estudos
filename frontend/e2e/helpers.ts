import { expect, test as base } from '@playwright/test'
import type { Page } from '@playwright/test'

export const test = base.extend<{ consoleHealth: void }>({
  consoleHealth: [async ({ page }, use) => {
    const errors: string[] = []
    page.on('pageerror', error => errors.push(error.message))
    page.on('console', message => {
      if (message.type() === 'error' && !/Failed to load resource: the server responded with a status of (401|404|409|503)/.test(message.text())) errors.push(message.text())
    })
    await use()
    expect(errors).toEqual([])
    expect(await page.locator('vite-error-overlay').count()).toBe(0)
  }, { auto: true }],
})
export { expect }
export async function login(page: Page, email: string, password: string) {
  await page.getByLabel('E-mail', { exact: true }).fill(email)
  await page.locator('input[autocomplete=current-password]').fill(password)
  await page.getByRole('button', { name: 'Entrar', exact: true }).click()
}
export async function noOverflow(page: Page) {
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true)
}
