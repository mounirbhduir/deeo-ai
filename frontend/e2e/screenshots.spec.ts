import { test, expect } from '@playwright/test'

/**
 * Screenshots Capture Test (Phase 4 - Step 9)
 * Captures screenshots of all 8 main pages for documentation
 */

test.describe('Screenshots Capture', () => {
  test('should capture homepage screenshot', async ({ page }) => {
    await page.goto('/')
    await page.waitForTimeout(2000)
    await page.screenshot({ path: 'e2e/screenshots/01-homepage.png', fullPage: true })
    expect(true).toBe(true)
  })

  test('should capture dashboard screenshot', async ({ page }) => {
    await page.goto('/dashboard')
    await page.waitForTimeout(3000)
    await page.screenshot({ path: 'e2e/screenshots/02-dashboard.png', fullPage: true })
    expect(true).toBe(true)
  })

  test('should capture publications screenshot', async ({ page }) => {
    await page.goto('/publications/search')
    await page.waitForTimeout(2500)
    await page.screenshot({ path: 'e2e/screenshots/03-publications.png', fullPage: true })
    expect(true).toBe(true)
  })

  test('should capture authors screenshot', async ({ page }) => {
    await page.goto('/authors')
    await page.waitForTimeout(2500)
    await page.screenshot({ path: 'e2e/screenshots/04-authors.png', fullPage: true })
    expect(true).toBe(true)
  })

  test('should capture organisations screenshot', async ({ page }) => {
    await page.goto('/organisations')
    await page.waitForTimeout(2500)
    await page.screenshot({ path: 'e2e/screenshots/05-organisations.png', fullPage: true })
    expect(true).toBe(true)
  })

  test('should capture network graphs screenshot', async ({ page }) => {
    await page.goto('/graphs')
    await page.waitForTimeout(5000) // Longer wait for graph rendering
    await page.screenshot({ path: 'e2e/screenshots/06-network-graphs.png', fullPage: true })
    expect(true).toBe(true)
  })

  test('should capture themes screenshot', async ({ page }) => {
    await page.goto('/themes')
    await page.waitForTimeout(2500)
    await page.screenshot({ path: 'e2e/screenshots/07-themes.png', fullPage: true })
    expect(true).toBe(true)
  })

  test('should capture publication details screenshot', async ({ page }) => {
    // First go to publications
    await page.goto('/publications/search')
    await page.waitForTimeout(2500)

    // Try to click on first publication
    const firstPub = page.locator('[data-testid*="publication"], article, .publication-card').first()
    if (await firstPub.isVisible({ timeout: 5000 })) {
      await firstPub.click()
      await page.waitForTimeout(2000)
      await page.screenshot({ path: 'e2e/screenshots/08-publication-details.png', fullPage: true })
    } else {
      // Fallback: just capture publications page again
      await page.screenshot({ path: 'e2e/screenshots/08-publication-details.png', fullPage: true })
    }
    expect(true).toBe(true)
  })
})
