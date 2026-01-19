# R³ Diary System - Frontend E2E 테스트 가이드

## 목차

1. [개요](#개요)
2. [Playwright 설정](#playwright-설정)
3. [테스트 실행](#테스트-실행)
4. [테스트 작성](#테스트-작성)
5. [디버깅](#디버깅)
6. [CI/CD 연동](#cicd-연동)
7. [베스트 프랙티스](#베스트-프랙티스)

## 개요

R³ Diary System Frontend는 Playwright를 사용하여 End-to-End (E2E) 테스트를 수행합니다.

**테스트 범위**:
- 사용자 인증 플로우 (회원가입, 로그인)
- 프로필 설정
- 일간/월간/연간 콘텐츠 조회
- 사용자 기록 작성
- PDF 다운로드
- 반응형 디자인 검증
- 접근성 검증

## Playwright 설정

### 설치

```bash
cd frontend

# Playwright 설치
npm install -D @playwright/test

# 브라우저 설치
npx playwright install
```

### 설정 파일

`playwright.config.ts`에서 테스트 설정 관리:

```typescript
export default defineConfig({
  testDir: './tests/e2e',
  timeout: 30 * 1000,
  use: {
    baseURL: 'http://localhost:3000',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
    { name: 'webkit', use: { ...devices['Desktop Safari'] } },
    { name: 'Mobile Chrome', use: { ...devices['Pixel 5'] } },
    { name: 'Mobile Safari', use: { ...devices['iPhone 12'] } },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
});
```

## 테스트 실행

### 개발 서버와 함께 실행

```bash
# 모든 테스트 실행 (자동으로 dev 서버 시작)
npx playwright test

# UI 모드로 실행
npx playwright test --ui

# 특정 브라우저만
npx playwright test --project=chromium
npx playwright test --project=webkit
```

### 특정 테스트 파일 실행

```bash
# 특정 파일
npx playwright test example.spec.ts

# 특정 테스트
npx playwright test example.spec.ts -g "홈페이지가 로드되어야 함"
```

### 디버그 모드

```bash
# Headed 모드로 실행 (브라우저 표시)
npx playwright test --headed

# 특정 테스트 디버그
npx playwright test --debug

# 슬로우 모션
npx playwright test --slow-mo=1000
```

### 리포트 확인

```bash
# HTML 리포트 생성 및 열기
npx playwright show-report
```

## 테스트 작성

### 기본 구조

```typescript
import { test, expect } from '@playwright/test';

test.describe('기능 그룹', () => {
  test('테스트 케이스', async ({ page }) => {
    // 페이지 이동
    await page.goto('/');

    // 요소 찾기
    const button = page.getByRole('button', { name: /클릭/i });

    // 상호작용
    await button.click();

    // 검증
    await expect(page).toHaveURL('/success');
  });
});
```

### Locator 전략

```typescript
// Role 기반 (권장)
page.getByRole('button', { name: '로그인' })
page.getByRole('heading', { level: 1 })

// Text 기반
page.getByText('환영합니다')

// Label 기반 (폼 필드)
page.getByLabel('이메일')

// Test ID (마지막 수단)
page.getByTestId('submit-button')

// CSS Selector (비권장)
page.locator('.my-class')
```

### 사용자 플로우 예시

```typescript
test('완전한 회원가입 플로우', async ({ page }) => {
  // 1. 홈페이지 방문
  await page.goto('/');

  // 2. 회원가입 페이지로 이동
  await page.getByRole('link', { name: /회원가입/i }).click();

  // 3. 폼 작성
  await page.getByLabel(/이름/i).fill('테스트 사용자');
  await page.getByLabel(/이메일/i).fill('test@example.com');
  await page.getByLabel(/비밀번호/i).fill('password123');

  // 4. 제출
  await page.getByRole('button', { name: /회원가입/i }).click();

  // 5. 성공 확인
  await expect(page).toHaveURL(/profile/);
});
```

### 반응형 테스트

```typescript
test('모바일 화면 테스트', async ({ page }) => {
  // 뷰포트 설정
  await page.setViewportSize({ width: 375, height: 667 });

  await page.goto('/');

  // 모바일 메뉴 확인
  const mobileMenu = page.getByRole('button', { name: /메뉴/i });
  await expect(mobileMenu).toBeVisible();
});
```

### 접근성 테스트

```typescript
test('키보드 네비게이션', async ({ page }) => {
  await page.goto('/');

  // Tab으로 이동
  await page.keyboard.press('Tab');

  // 포커스된 요소 확인
  const focused = page.locator(':focus');
  await expect(focused).toBeVisible();

  // Enter로 활성화
  await page.keyboard.press('Enter');
});
```

## 디버깅

### Playwright Inspector

```bash
# Inspector로 디버그
npx playwright test --debug
```

**기능**:
- 단계별 실행
- Locator 테스트
- 스크린샷 캡처
- 네트워크 요청 확인

### 스크린샷

```typescript
test('스크린샷 캡처', async ({ page }) => {
  await page.goto('/');

  // 전체 페이지
  await page.screenshot({ path: 'screenshot.png' });

  // 특정 요소
  const element = page.locator('.my-element');
  await element.screenshot({ path: 'element.png' });
});
```

### 트레이스

```typescript
// playwright.config.ts
export default defineConfig({
  use: {
    trace: 'on-first-retry', // 첫 재시도 시 트레이스 기록
  },
});

// 트레이스 보기
npx playwright show-trace trace.zip
```

### Console 로그

```typescript
test('콘솔 로그 확인', async ({ page }) => {
  page.on('console', msg => {
    console.log('Browser:', msg.text());
  });

  await page.goto('/');
});
```

## CI/CD 연동

### GitHub Actions 예시

```yaml
# .github/workflows/frontend-e2e.yml
name: Frontend E2E Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'

    - name: Install dependencies
      run: |
        cd frontend
        npm ci

    - name: Install Playwright Browsers
      run: |
        cd frontend
        npx playwright install --with-deps

    - name: Run E2E tests
      run: |
        cd frontend
        npx playwright test

    - name: Upload test results
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: playwright-report
        path: frontend/playwright-report/
```

### Docker 환경

```dockerfile
# Dockerfile.test
FROM mcr.microsoft.com/playwright:v1.40.0-focal

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

CMD ["npx", "playwright", "test"]
```

```bash
# Docker로 테스트 실행
docker build -f Dockerfile.test -t playwright-tests .
docker run --rm playwright-tests
```

## 베스트 프랙티스

### 1. Test Isolation

```typescript
// ❌ 나쁜 예: 테스트 간 의존성
test('로그인', async ({ page }) => {
  // 로그인 코드
});

test('프로필 조회', async ({ page }) => {
  // 이전 테스트에서 로그인했다고 가정 (X)
});

// ✅ 좋은 예: 각 테스트 독립적
test('프로필 조회', async ({ page }) => {
  // 로그인 수행
  await login(page);
  // 프로필 조회
});
```

### 2. Fixtures 활용

```typescript
// fixtures.ts
import { test as base } from '@playwright/test';

export const test = base.extend({
  authenticatedPage: async ({ page }, use) => {
    // 로그인 수행
    await page.goto('/login');
    await page.getByLabel('이메일').fill('test@example.com');
    await page.getByLabel('비밀번호').fill('password');
    await page.getByRole('button', { name: '로그인' }).click();
    await use(page);
  },
});

// 테스트에서 사용
test('인증된 사용자', async ({ authenticatedPage }) => {
  await authenticatedPage.goto('/profile');
  // ...
});
```

### 3. Page Object Model

```typescript
// pages/LoginPage.ts
export class LoginPage {
  constructor(private page: Page) {}

  async goto() {
    await this.page.goto('/login');
  }

  async login(email: string, password: string) {
    await this.page.getByLabel('이메일').fill(email);
    await this.page.getByLabel('비밀번호').fill(password);
    await this.page.getByRole('button', { name: '로그인' }).click();
  }
}

// 테스트
test('로그인', async ({ page }) => {
  const loginPage = new LoginPage(page);
  await loginPage.goto();
  await loginPage.login('test@example.com', 'password');
});
```

### 4. 명시적 대기

```typescript
// ❌ 나쁜 예
await page.waitForTimeout(3000);

// ✅ 좋은 예
await page.waitForURL(/profile/);
await page.waitForSelector('[data-testid="content"]');
await expect(page.getByText('로딩 완료')).toBeVisible();
```

### 5. 네트워크 Mock

```typescript
test('API Mock', async ({ page }) => {
  // API 응답 Mock
  await page.route('**/api/daily/*', route => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        date: '2026-01-20',
        summary: 'Mock 콘텐츠',
      }),
    });
  });

  await page.goto('/today');
});
```

## 트러블슈팅

### 브라우저 설치 실패

```bash
# 권한 오류 시
sudo npx playwright install

# 특정 브라우저만
npx playwright install chromium
```

### 타임아웃 오류

```typescript
// 개별 테스트 타임아웃 증가
test('느린 테스트', async ({ page }) => {
  test.setTimeout(60000); // 60초
  // ...
});

// 전역 설정 (playwright.config.ts)
timeout: 60 * 1000
```

### CI에서 실패

```yaml
# Headless 모드 확인
- name: Run tests
  run: npx playwright test
  env:
    CI: true
```

## 참고 자료

- [Playwright 공식 문서](https://playwright.dev/)
- [Best Practices](https://playwright.dev/docs/best-practices)
- [Debugging](https://playwright.dev/docs/debug)
- [CI/CD](https://playwright.dev/docs/ci)
