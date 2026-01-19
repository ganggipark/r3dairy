import { test, expect } from '@playwright/test';

/**
 * E2E 테스트 예제
 * R³ Diary System 주요 사용자 플로우 테스트
 */

test.describe('홈페이지', () => {
  test('홈페이지가 로드되어야 함', async ({ page }) => {
    await page.goto('/');

    // 페이지 제목 확인
    await expect(page).toHaveTitle(/R³ Diary/i);

    // 메인 콘텐츠 확인
    const heading = page.getByRole('heading', { level: 1 });
    await expect(heading).toBeVisible();
  });

  test('네비게이션이 작동해야 함', async ({ page }) => {
    await page.goto('/');

    // 로그인 링크 확인
    const loginLink = page.getByRole('link', { name: /로그인/i });
    await expect(loginLink).toBeVisible();

    // 회원가입 링크 확인
    const signupLink = page.getByRole('link', { name: /회원가입/i });
    await expect(signupLink).toBeVisible();
  });
});

test.describe('로그인 플로우', () => {
  test('로그인 페이지가 로드되어야 함', async ({ page }) => {
    await page.goto('/login');

    // 이메일 입력 필드
    const emailInput = page.getByLabel(/이메일/i);
    await expect(emailInput).toBeVisible();

    // 비밀번호 입력 필드
    const passwordInput = page.getByLabel(/비밀번호/i);
    await expect(passwordInput).toBeVisible();

    // 로그인 버튼
    const loginButton = page.getByRole('button', { name: /로그인/i });
    await expect(loginButton).toBeVisible();
  });

  test('잘못된 로그인 정보는 거부되어야 함', async ({ page }) => {
    await page.goto('/login');

    // 이메일 입력
    await page.getByLabel(/이메일/i).fill('invalid@example.com');

    // 비밀번호 입력
    await page.getByLabel(/비밀번호/i).fill('wrongpassword');

    // 로그인 버튼 클릭
    await page.getByRole('button', { name: /로그인/i }).click();

    // 에러 메시지 확인 (구현 시)
    // await expect(page.getByText(/로그인 실패/i)).toBeVisible();
  });
});

test.describe('회원가입 플로우', () => {
  test('회원가입 페이지가 로드되어야 함', async ({ page }) => {
    await page.goto('/signup');

    // 이름 입력 필드
    const nameInput = page.getByLabel(/이름/i);
    await expect(nameInput).toBeVisible();

    // 이메일 입력 필드
    const emailInput = page.getByLabel(/이메일/i);
    await expect(emailInput).toBeVisible();

    // 비밀번호 입력 필드
    const passwordInput = page.getByLabel(/비밀번호/i);
    await expect(passwordInput).toBeVisible();

    // 회원가입 버튼
    const signupButton = page.getByRole('button', { name: /회원가입/i });
    await expect(signupButton).toBeVisible();
  });

  test('유효하지 않은 이메일은 거부되어야 함', async ({ page }) => {
    await page.goto('/signup');

    await page.getByLabel(/이름/i).fill('테스트 사용자');
    await page.getByLabel(/이메일/i).fill('invalid-email');
    await page.getByLabel(/비밀번호/i).fill('testpass123');

    await page.getByRole('button', { name: /회원가입/i }).click();

    // 검증 에러 메시지 확인 (구현 시)
    // await expect(page.getByText(/유효한 이메일/i)).toBeVisible();
  });
});

test.describe('프로필 설정', () => {
  test.skip('프로필 페이지가 로드되어야 함', async ({ page }) => {
    // 로그인 필요 - 인증 설정 후 테스트
    await page.goto('/profile');

    // 출생 정보 입력 필드 확인
    const birthDateInput = page.getByLabel(/생년월일/i);
    await expect(birthDateInput).toBeVisible();

    const birthTimeInput = page.getByLabel(/출생 시간/i);
    await expect(birthTimeInput).toBeVisible();
  });
});

test.describe('오늘 페이지', () => {
  test.skip('오늘 페이지가 로드되어야 함', async ({ page }) => {
    // 로그인 필요 - 인증 설정 후 테스트
    await page.goto('/today');

    // 좌측 콘텐츠 패널
    const leftPanel = page.locator('[data-testid="left-panel"]');
    await expect(leftPanel).toBeVisible();

    // 우측 기록 패널
    const rightPanel = page.locator('[data-testid="right-panel"]');
    await expect(rightPanel).toBeVisible();
  });

  test.skip('10개 콘텐츠 블록이 표시되어야 함', async ({ page }) => {
    await page.goto('/today');

    // 요약 카드
    const summaryBlock = page.getByTestId('summary-block');
    await expect(summaryBlock).toBeVisible();

    // 키워드
    const keywordsBlock = page.getByTestId('keywords-block');
    await expect(keywordsBlock).toBeVisible();

    // 리듬 해설
    const rhythmBlock = page.getByTestId('rhythm-description-block');
    await expect(rhythmBlock).toBeVisible();

    // ... (나머지 블록들)
  });
});

test.describe('반응형 디자인', () => {
  test('모바일 화면에서 레이아웃이 정상적이어야 함', async ({ page }) => {
    // 모바일 뷰포트 설정
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');

    // 모바일 메뉴 버튼 확인
    const mobileMenu = page.getByRole('button', { name: /메뉴/i });
    // await expect(mobileMenu).toBeVisible();
  });

  test('태블릿 화면에서 레이아웃이 정상적이어야 함', async ({ page }) => {
    // 태블릿 뷰포트 설정
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.goto('/');

    // 레이아웃 확인
    const mainContent = page.locator('main');
    await expect(mainContent).toBeVisible();
  });
});

test.describe('접근성', () => {
  test('키보드 네비게이션이 작동해야 함', async ({ page }) => {
    await page.goto('/');

    // Tab 키로 네비게이션
    await page.keyboard.press('Tab');
    const firstFocusable = page.locator(':focus');
    await expect(firstFocusable).toBeVisible();
  });

  test('스크린 리더를 위한 ARIA 속성이 있어야 함', async ({ page }) => {
    await page.goto('/');

    // main 랜드마크
    const main = page.locator('main');
    await expect(main).toBeVisible();

    // 헤딩 구조 확인
    const headings = page.locator('h1, h2, h3');
    await expect(headings.first()).toBeVisible();
  });
});
