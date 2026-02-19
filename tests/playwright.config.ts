import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './tests',
  testMatch: /e2e-.*\.spec\.ts/,
  timeout: 30000,
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: 0,
  workers: 1,
  reporter: [['html', { outputFolder: 'playwright-report' }], ['list']],
  use: {
    baseURL: process.env.P09_H5_URL || 'http://localhost:10087',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    viewport: { width: 375, height: 667 },
  },
  projects: [{ name: 'chromium', use: { ...devices['Pixel 5'] } }],
  // 需先手动启动: cd frontend && npm run dev:h5:local
  webServer: undefined,
})
