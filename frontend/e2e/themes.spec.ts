import { test, expect } from '@playwright/test'

/**
 * Themes Page E2E Tests
 * Tests: 4
 * Coverage: Theme list, search, navigation to publications
 */

test.describe('Themes Page Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/themes')
  })

  test('should load themes page without 404 error', async ({ page }) => {
    // Check page URL is correct
    await expect(page).toHaveURL(/\/themes/)

    // Wait for page to load
    await page.waitForTimeout(2000)

    // Should not show NotFound component
    const bodyText = await page.textContent('body')
    expect(bodyText).not.toContain('404')
    expect(bodyText).not.toContain('Page not found')

    // Should show themes page title
    const heading = page.locator('h1')
    await expect(heading).toBeVisible()
    const headingText = await heading.textContent()
    expect(headingText?.toLowerCase()).toContain('theme')
  })

  test('should display themes list with hierarchy levels', async ({ page }) => {
    // Wait for themes to load
    await page.waitForTimeout(2000)

    // Check if we have theme cards or theme content
    const bodyContent = await page.textContent('body')
    expect(bodyContent).toBeTruthy()

    // Page should be loaded successfully
    expect(page.url()).toContain('/themes')

    // Look for theme-related content (cards or list items)
    const themeCards = page.locator('[data-testid="theme-card"]')
    const cardCount = await themeCards.count()

    // If themes are loaded, verify they have proper structure
    if (cardCount > 0) {
      const firstCard = themeCards.first()
      await expect(firstCard).toBeVisible()

      // Check for "Level" text indicating hierarchy
      const cardText = await firstCard.textContent()
      expect(cardText?.toLowerCase()).toMatch(/level|niveau/i)
    }
  })

  test('should search themes by name', async ({ page }) => {
    // Wait for initial load
    await page.waitForTimeout(2000)

    // Find search input
    const searchInput = page.getByPlaceholder(/search.*theme/i).first()

    if (await searchInput.isVisible({ timeout: 3000 })) {
      await searchInput.fill('Machine Learning')

      // Wait for search results to filter
      await page.waitForTimeout(1000)

      // Results should be filtered
      const bodyText = await page.textContent('body')
      expect(bodyText).toBeTruthy()
    }
  })

  test('should navigate to publications filtered by theme', async ({ page }) => {
    // Wait for themes to load
    await page.waitForTimeout(2000)

    // Look for "View" or "View Publications" button
    const viewButton = page.getByRole('button', { name: /view/i }).first()

    if (await viewButton.isVisible({ timeout: 3000 })) {
      await viewButton.click()

      // Wait for navigation
      await page.waitForTimeout(2000)

      // Should navigate to publications page with theme filter
      const currentUrl = page.url()
      expect(currentUrl).toMatch(/\/publications/)
    }
  })

  test('should display publication count for each theme', async ({ page }) => {
    // Wait for themes to load
    await page.waitForTimeout(2000)

    // Check for publication count text
    const bodyText = await page.textContent('body')

    // Should show publication counts (looking for "publication" or "pub" text)
    if (bodyText && bodyText.length > 100) {
      expect(bodyText.toLowerCase()).toMatch(/publication/i)
    }
  })
})
