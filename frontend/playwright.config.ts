import { defineConfig, devices } from '@playwright/test'

/**
 * Playwright Configuration for DEEO.AI E2E Tests
 * Phase 4 - Step 9: Complete E2E Testing
 */
export default defineConfig({
  testDir: './e2e',

  // Test timeout (30 seconds per test)
  timeout: 30000,

  // Fail build on CI if tests fail
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,

  // Reporter configuration
  reporter: [
    ['html', { outputFolder: 'playwright-report' }],
    ['list'],
  ],

  // Shared test configuration
  use: {
    // Base URL for navigation
    baseURL: 'http://localhost:5173',

    // Screenshot on failure
    screenshot: 'only-on-failure',

    // Video on first retry
    video: 'retain-on-failure',

    // Trace on first retry
    trace: 'on-first-retry',
  },

  // Configure projects for different browsers
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],

  // Web server configuration
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:5173',
    reuseExistingServer: !process.env.CI,
    timeout: 120000,
  },
})
