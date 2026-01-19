import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright Configuration
 * E2E 테스트 설정
 */
export default defineConfig({
  testDir: './tests/e2e',

  /* 전체 테스트 타임아웃 */
  timeout: 30 * 1000,

  /* 각 테스트 expect 타임아웃 */
  expect: {
    timeout: 5000
  },

  /* 병렬 실행 설정 */
  fullyParallel: true,

  /* CI 환경에서 재시도 */
  retries: process.env.CI ? 2 : 0,

  /* 병렬 워커 수 */
  workers: process.env.CI ? 1 : undefined,

  /* 리포터 설정 */
  reporter: [
    ['html'],
    ['list'],
    ['json', { outputFile: 'test-results/results.json' }]
  ],

  /* 공통 설정 */
  use: {
    /* Base URL */
    baseURL: process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:3000',

    /* 스크린샷 */
    screenshot: 'only-on-failure',

    /* 비디오 */
    video: 'retain-on-failure',

    /* 트레이스 */
    trace: 'on-first-retry',

    /* 헤드리스 모드 */
    headless: process.env.CI ? true : false,
  },

  /* 프로젝트별 설정 */
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },

    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },

    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },

    /* 모바일 테스트 */
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },

    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 12'] },
    },
  ],

  /* 웹서버 설정 (테스트 시작 전 자동 실행) */
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000,
  },
});
