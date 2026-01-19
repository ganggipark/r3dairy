import { test, expect } from '@playwright/test';

/**
 * 전체 사용자 여정 E2E 테스트
 * 회원가입 → 프로필 설정 → 콘텐츠 조회 → 기록 작성 → PDF 다운로드
 */

test.describe('완전한 사용자 여정', () => {
  test.skip('신규 사용자 전체 플로우', async ({ page }) => {
    // ========== 1. 홈페이지 방문 ==========
    await page.goto('/');
    await expect(page).toHaveTitle(/R³ Diary/i);

    // ========== 2. 회원가입 ==========
    await page.getByRole('link', { name: /회원가입/i }).click();
    await expect(page).toHaveURL(/signup/);

    // 회원가입 폼 작성
    const timestamp = Date.now();
    await page.getByLabel(/이름/i).fill('E2E 테스트 사용자');
    await page.getByLabel(/이메일/i).fill(`e2e-test-${timestamp}@example.com`);
    await page.getByLabel(/비밀번호/i).fill('testpass123');

    // 회원가입 버튼 클릭
    await page.getByRole('button', { name: /회원가입/i }).click();

    // 회원가입 성공 확인
    // (자동 로그인 또는 로그인 페이지로 리다이렉트)
    await page.waitForURL(/login|profile/, { timeout: 5000 });

    // ========== 3. 로그인 (자동 로그인 안 될 경우) ==========
    const currentUrl = page.url();
    if (currentUrl.includes('login')) {
      await page.getByLabel(/이메일/i).fill(`e2e-test-${timestamp}@example.com`);
      await page.getByLabel(/비밀번호/i).fill('testpass123');
      await page.getByRole('button', { name: /로그인/i }).click();
    }

    // ========== 4. 프로필 설정 ==========
    await page.waitForURL(/profile/, { timeout: 5000 });

    // 출생 정보 입력
    await page.getByLabel(/생년월일/i).fill('1990-01-15');
    await page.getByLabel(/출생 시간/i).fill('14:30');
    await page.getByLabel(/성별/i).selectOption('male');
    await page.getByLabel(/출생지/i).fill('서울');

    // 역할 선택
    await page.getByLabel(/학생/i).check();

    // 프로필 저장
    await page.getByRole('button', { name: /저장|완료/i }).click();

    // ========== 5. 오늘 페이지 이동 ==========
    await page.waitForURL(/today/, { timeout: 5000 });

    // 좌측 콘텐츠 패널 확인
    const leftPanel = page.locator('[data-testid="left-panel"]');
    await expect(leftPanel).toBeVisible({ timeout: 10000 });

    // 콘텐츠 블록 확인
    const summaryBlock = page.getByTestId('summary-block');
    await expect(summaryBlock).toBeVisible();

    // 키워드 확인
    const keywords = page.getByTestId('keywords-block');
    await expect(keywords).toBeVisible();

    // ========== 6. 우측 패널에 기록 작성 ==========
    const rightPanel = page.locator('[data-testid="right-panel"]');
    await expect(rightPanel).toBeVisible();

    // 기록 입력
    await page.getByLabel(/오늘의 일정/i).fill('E2E 테스트 일정');
    await page.getByLabel(/기분/i).selectOption('4');
    await page.getByLabel(/에너지/i).selectOption('3');
    await page.getByLabel(/메모/i).fill('E2E 테스트 메모입니다.');

    // 기록 저장
    await page.getByRole('button', { name: /저장/i }).click();

    // 저장 성공 메시지 확인
    const successMessage = page.getByText(/저장.*완료|성공/i);
    await expect(successMessage).toBeVisible({ timeout: 3000 });

    // ========== 7. PDF 다운로드 ==========
    const downloadPromise = page.waitForEvent('download');

    await page.getByRole('button', { name: /PDF.*다운로드/i }).click();

    const download = await downloadPromise;

    // 파일명 확인
    expect(download.suggestedFilename()).toMatch(/R3_Diary.*\.pdf/);

    // ========== 8. 월간 페이지 확인 ==========
    await page.goto('/month');

    // 월간 콘텐츠 확인 (Phase 3 이후 구현)
    const monthlyContent = page.locator('main');
    await expect(monthlyContent).toBeVisible();

    // ========== 9. 연간 페이지 확인 ==========
    await page.goto('/year');

    // 연간 콘텐츠 확인 (Phase 3 이후 구현)
    const yearlyContent = page.locator('main');
    await expect(yearlyContent).toBeVisible();

    // ========== 10. 로그아웃 ==========
    await page.getByRole('button', { name: /로그아웃/i }).click();

    // 홈페이지로 리다이렉트
    await expect(page).toHaveURL('/', { timeout: 3000 });
  });
});

test.describe('역할별 콘텐츠 변환', () => {
  test.skip('역할 변경 시 콘텐츠 표현이 달라져야 함', async ({ page }) => {
    // 로그인 및 프로필 설정 (학생)
    await page.goto('/profile');

    // 역할을 '학생'으로 설정
    await page.getByLabel(/학생/i).check();
    await page.getByRole('button', { name: /저장/i }).click();

    // 오늘 페이지 이동
    await page.goto('/today');

    // 학생 전용 표현 확인
    const studentContent = page.getByText(/학습|수업|과제/i);
    await expect(studentContent).toBeVisible();

    // 역할을 '직장인'으로 변경
    await page.goto('/profile');
    await page.getByLabel(/직장인/i).check();
    await page.getByRole('button', { name: /저장/i }).click();

    await page.goto('/today');

    // 직장인 전용 표현 확인
    const officeWorkerContent = page.getByText(/업무|회의|프로젝트/i);
    await expect(officeWorkerContent).toBeVisible();
  });
});

test.describe('데이터 영속성', () => {
  test.skip('기록 저장 후 새로고침해도 유지되어야 함', async ({ page }) => {
    await page.goto('/today');

    // 기록 작성
    const testNote = `E2E 영속성 테스트 ${Date.now()}`;
    await page.getByLabel(/메모/i).fill(testNote);
    await page.getByRole('button', { name: /저장/i }).click();

    // 저장 완료 대기
    await page.waitForTimeout(1000);

    // 페이지 새로고침
    await page.reload();

    // 저장된 기록 확인
    const savedNote = page.getByLabel(/메모/i);
    await expect(savedNote).toHaveValue(testNote);
  });
});

test.describe('에러 처리', () => {
  test.skip('네트워크 오류 시 에러 메시지 표시', async ({ page, context }) => {
    // 네트워크 차단
    await context.route('**/api/**', route => route.abort());

    await page.goto('/today');

    // 에러 메시지 확인
    const errorMessage = page.getByText(/오류|에러|실패/i);
    await expect(errorMessage).toBeVisible({ timeout: 5000 });
  });

  test.skip('만료된 세션 처리', async ({ page }) => {
    // 로그인 상태에서 토큰 만료 시뮬레이션
    await page.goto('/today');

    // 로컬 스토리지에서 토큰 제거
    await page.evaluate(() => {
      localStorage.removeItem('supabase.auth.token');
    });

    // API 요청 시도
    await page.reload();

    // 로그인 페이지로 리다이렉트
    await expect(page).toHaveURL(/login/, { timeout: 3000 });
  });
});

test.describe('성능 검증', () => {
  test('페이지 로딩이 3초 이내여야 함', async ({ page }) => {
    const startTime = Date.now();

    await page.goto('/');

    const loadTime = Date.now() - startTime;

    expect(loadTime).toBeLessThan(3000);
  });

  test.skip('콘텐츠 생성이 5초 이내여야 함', async ({ page }) => {
    const startTime = Date.now();

    await page.goto('/today');

    // 콘텐츠 로드 대기
    await page.waitForSelector('[data-testid="summary-block"]', { timeout: 10000 });

    const loadTime = Date.now() - startTime;

    expect(loadTime).toBeLessThan(5000);
  });
});
