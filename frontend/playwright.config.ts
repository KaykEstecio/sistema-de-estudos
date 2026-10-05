import { defineConfig } from '@playwright/test'

export default defineConfig({
  testDir: './e2e', timeout: 30000, fullyParallel: false, workers: 1, retries: 0,
  reporter: [['list'], ['json', { outputFile: 'test-results/results.json' }]], outputDir: 'test-results',
  use: { baseURL: 'http://127.0.0.1:4173', browserName: 'chromium', trace: 'off', video: 'off', screenshot: 'only-on-failure' },
  projects: [
    { name: 'controlled-desktop', testMatch: ['**/controlled.spec.ts', '**/theme.spec.ts'], use: { colorScheme: 'light', viewport: { width: 1440, height: 1000 } } },
    { name: 'controlled-mobile', testMatch: ['**/controlled.spec.ts', '**/theme.spec.ts'], use: { colorScheme: 'light', viewport: { width: 390, height: 844 } } },
    { name: 'real', testMatch: '**/real.spec.ts', use: { colorScheme: 'dark', viewport: { width: 1440, height: 1000 } } },
  ],
  webServer: process.env.CODETRACK_QA_SERVER_STARTED === '1' ? undefined : {
    command: 'npm run dev -- --port 4173 --strictPort', url: 'http://127.0.0.1:4173',
    reuseExistingServer: false, timeout: 30000,
  },
})
