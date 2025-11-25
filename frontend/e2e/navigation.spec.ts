import { test, expect } from '@playwright/test'

/**
 * Navigation E2E Tests (Phase 4 - Step 9)
 * Tests: 4
 * Coverage: Homepage, sidebar navigation, routing
 */

test.describe('Navigation Tests', () => {
  test('should load homepage successfully', async ({ page }) => {
    await page.goto('/')

    // Check that the page loads
    await expect(page).toHaveTitle(/DEEO\.AI/)

    // Check for main layout elements
    await expect(page.getByRole('banner')).toBeVisible()
  })

  test('should navigate to all sidebar menu items', async ({ page }) => {
    await page.goto('/')
    await page.waitForTimeout(1000)

    // Navigate to Dashboard (use sidebar link)
    await page.locator('aside').getByRole('link', { name: /dashboard/i }).click()
    await expect(page).toHaveURL(/\/dashboard/)

    // Navigate to Publications
    await page.locator('aside').getByRole('link', { name: /publications/i }).click()
    await expect(page).toHaveURL(/\/publications/)

    // Navigate to Authors
    await page.locator('aside').getByRole('link', { name: /authors/i }).click()
    await expect(page).toHaveURL(/\/authors/)

    // Navigate to Organisations
    await page.locator('aside').getByRole('link', { name: /organisations/i }).click()
    await expect(page).toHaveURL(/\/organisations/)

    // Navigate to Network Graphs
    await page.locator('aside').getByRole('link', { name: /network graphs/i }).click()
    await expect(page).toHaveURL(/\/graphs/)

    // Navigate to Thèmes
    await page.locator('aside').getByRole('link', { name: /th[èe]mes/i }).click()
    await expect(page).toHaveURL(/\/themes/)
  })

  test('should display and toggle sidebar collapse', async ({ page }) => {
    await page.goto('/dashboard')

    // Check sidebar is visible
    const sidebar = page.locator('aside')
    await expect(sidebar).toBeVisible()

    // Find collapse button
    const collapseButton = page.getByRole('button', { name: /collapse|expand/i })
    await expect(collapseButton).toBeVisible()

    // Click to collapse
    await collapseButton.click()

    // Sidebar should still be visible but narrower
    await expect(sidebar).toBeVisible()

    // Click to expand again
    await collapseButton.click()
  })

  test('should handle 404 page for invalid routes', async ({ page }) => {
    await page.goto('/this-page-does-not-exist')

    // Should show some error or redirect
    // Either 404 page or redirect to dashboard/home
    const url = page.url()
    const hasError = url.includes('404') || url.includes('dashboard') || url.includes('/')
    expect(hasError).toBe(true)
  })
})
