/**
 * 기간별 다이어리 생성기 테스트
 * 
 * 1개월/3개월/6개월/1년 기간 생성 테스트
 */

import {
  buildPeriodDiary,
  getExpectedEndDate,
  getExpectedDays,
  PeriodDiaryInput,
  PeriodDiaryResult,
  DurationType
} from './periodDiaryGenerator';

// ============================================================
// Test Configuration
// ============================================================

const TEST_BIRTH = {
  year: 1971,
  month: 11,
  day: 17,
  hour: 4,
  minute: 0,
  isLunar: false as const,
  birthPlace: '서울'
};

// ============================================================
// Helper Functions
// ============================================================

function validatePeriodResult(result: PeriodDiaryResult, expectedDurationType: DurationType): boolean {
  const errors: string[] = [];
  
  // 기본 필드 검증
  if (!result.startDate) errors.push('Missing startDate');
  if (!result.endDate) errors.push('Missing endDate');
  if (result.durationType !== expectedDurationType) {
    errors.push(`Duration type mismatch: expected ${expectedDurationType}, got ${result.durationType}`);
  }
  if (!result.totalDays || result.totalDays <= 0) {
    errors.push(`Invalid totalDays: ${result.totalDays}`);
  }
  if (!result.entries || !Array.isArray(result.entries)) {
    errors.push('Missing or invalid entries array');
  }
  
  // entries 길이 검증
  if (result.entries && result.entries.length !== result.totalDays) {
    errors.push(`Entries count mismatch: expected ${result.totalDays}, got ${result.entries.length}`);
  }
  
  // 각 entry 검증
  if (result.entries) {
    result.entries.forEach((entry, index) => {
      if (!entry.date) {
        errors.push(`Entry ${index}: missing date`);
      }
      if (!entry.calendar) {
        errors.push(`Entry ${index}: missing calendar`);
      }
      if (!entry.leftPage) {
        errors.push(`Entry ${index}: missing leftPage`);
      }
      if (!entry.rightPage) {
        errors.push(`Entry ${index}: missing rightPage`);
      }
    });
    
    // 날짜 순서 검증
    for (let i = 1; i < result.entries.length; i++) {
      const prevDate = new Date(result.entries[i - 1].date);
      const currDate = new Date(result.entries[i].date);
      const dayDiff = (currDate.getTime() - prevDate.getTime()) / (1000 * 60 * 60 * 24);
      
      if (dayDiff !== 1) {
        errors.push(`Date sequence error between ${result.entries[i - 1].date} and ${result.entries[i].date}`);
      }
    }
  }
  
  if (errors.length > 0) {
    console.error('Validation errors:', errors.join('\n'));
    return false;
  }
  
  return true;
}

// ============================================================
// Test Cases
// ============================================================

async function test1Month(): Promise<void> {
  console.log('\n========== Test: 1 Month Generation ==========');
  
  const input: PeriodDiaryInput = {
    startDate: '2026-03-28',
    durationType: '1m',
    birth: TEST_BIRTH
  };
  
  // 예상값 확인
  const expectedEnd = getExpectedEndDate(input.startDate, input.durationType);
  const expectedDays = getExpectedDays(input.startDate, input.durationType);
  
  console.log(`Expected: ${input.startDate} to ${expectedEnd} (${expectedDays} days)`);
  
  // 실제 생성
  const result = await buildPeriodDiary(input);
  
  console.log(`Result: ${result.startDate} to ${result.endDate} (${result.totalDays} days)`);
  console.log(`Generated ${result.entries.length} entries`);
  
  // 검증
  const isValid = validatePeriodResult(result, '1m');
  console.log(`Validation: ${isValid ? 'PASSED' : 'FAILED'}`);
  
  // 첫날과 마지막날 확인
  if (result.entries.length > 0) {
    console.log(`First entry date: ${result.entries[0].date}`);
    console.log(`Last entry date: ${result.entries[result.entries.length - 1].date}`);
  }
}

async function test3Months(): Promise<void> {
  console.log('\n========== Test: 3 Months Generation ==========');
  
  const input: PeriodDiaryInput = {
    startDate: '2026-01-01',
    durationType: '3m',
    birth: TEST_BIRTH
  };
  
  const expectedEnd = getExpectedEndDate(input.startDate, input.durationType);
  const expectedDays = getExpectedDays(input.startDate, input.durationType);
  
  console.log(`Expected: ${input.startDate} to ${expectedEnd} (${expectedDays} days)`);
  
  const result = await buildPeriodDiary(input);
  
  console.log(`Result: ${result.startDate} to ${result.endDate} (${result.totalDays} days)`);
  console.log(`Generated ${result.entries.length} entries`);
  
  const isValid = validatePeriodResult(result, '3m');
  console.log(`Validation: ${isValid ? 'PASSED' : 'FAILED'}`);
}

async function test6Months(): Promise<void> {
  console.log('\n========== Test: 6 Months Generation ==========');
  
  const input: PeriodDiaryInput = {
    startDate: '2026-07-01',
    durationType: '6m',
    birth: TEST_BIRTH
  };
  
  const expectedEnd = getExpectedEndDate(input.startDate, input.durationType);
  const expectedDays = getExpectedDays(input.startDate, input.durationType);
  
  console.log(`Expected: ${input.startDate} to ${expectedEnd} (${expectedDays} days)`);
  
  const result = await buildPeriodDiary(input);
  
  console.log(`Result: ${result.startDate} to ${result.endDate} (${result.totalDays} days)`);
  console.log(`Generated ${result.entries.length} entries`);
  
  const isValid = validatePeriodResult(result, '6m');
  console.log(`Validation: ${isValid ? 'PASSED' : 'FAILED'}`);
}

async function test1Year(): Promise<void> {
  console.log('\n========== Test: 1 Year Generation ==========');
  
  const input: PeriodDiaryInput = {
    startDate: '2025-01-01',
    durationType: '1y',
    birth: TEST_BIRTH
  };
  
  const expectedEnd = getExpectedEndDate(input.startDate, input.durationType);
  const expectedDays = getExpectedDays(input.startDate, input.durationType);
  
  console.log(`Expected: ${input.startDate} to ${expectedEnd} (${expectedDays} days)`);
  
  const result = await buildPeriodDiary(input);
  
  console.log(`Result: ${result.startDate} to ${result.endDate} (${result.totalDays} days)`);
  console.log(`Generated ${result.entries.length} entries`);
  
  const isValid = validatePeriodResult(result, '1y');
  console.log(`Validation: ${isValid ? 'PASSED' : 'FAILED'}`);
}

async function testEdgeCases(): Promise<void> {
  console.log('\n========== Test: Edge Cases ==========');
  
  // 월말 처리 테스트 1: 2026-01-31 + 1m = 2026-02-28
  console.log('\n--- Edge Case 1: 2026-01-31 + 1m ---');
  const monthEnd1: PeriodDiaryInput = {
    startDate: '2026-01-31',
    durationType: '1m',
    birth: TEST_BIRTH
  };
  
  const result1 = await buildPeriodDiary(monthEnd1);
  console.log(`Result: ${result1.startDate} to ${result1.endDate} (${result1.totalDays} days)`);
  console.log(`Expected: 2026-01-31 to 2026-02-28`);
  if (result1.endDate === '2026-02-28') {
    console.log('✓ PASS: Month-end clamp working correctly');
  } else {
    console.log('✗ FAIL: Expected 2026-02-28, got ' + result1.endDate);
  }
  
  // 월말 처리 테스트 2: 2024-01-31 + 1m = 2024-02-29 (윤년)
  console.log('\n--- Edge Case 2: 2024-01-31 + 1m (leap year) ---');
  const monthEnd2: PeriodDiaryInput = {
    startDate: '2024-01-31',
    durationType: '1m',
    birth: TEST_BIRTH
  };
  
  const result2 = await buildPeriodDiary(monthEnd2);
  console.log(`Result: ${result2.startDate} to ${result2.endDate} (${result2.totalDays} days)`);
  console.log(`Expected: 2024-01-31 to 2024-02-29`);
  if (result2.endDate === '2024-02-29') {
    console.log('✓ PASS: Leap year month-end clamp working');
  } else {
    console.log('✗ FAIL: Expected 2024-02-29, got ' + result2.endDate);
  }
  
  // 윤년 처리 테스트 3: 2024-02-29 + 1y = 2025-02-28
  console.log('\n--- Edge Case 3: 2024-02-29 + 1y ---');
  const leapYearInput: PeriodDiaryInput = {
    startDate: '2024-02-29',
    durationType: '1y',
    birth: TEST_BIRTH
  };
  
  const result3 = await buildPeriodDiary(leapYearInput);
  console.log(`Result: ${result3.startDate} to ${result3.endDate} (${result3.totalDays} days)`);
  console.log(`Expected: 2024-02-29 to 2025-02-28`);
  if (result3.endDate === '2025-02-28') {
    console.log('✓ PASS: Leap to non-leap year clamp working');
  } else {
    console.log('✗ FAIL: Expected 2025-02-28, got ' + result3.endDate);
  }
  
  // 월말 처리 테스트 4: 2026-11-30 + 3m = 2027-02-28
  console.log('\n--- Edge Case 4: 2026-11-30 + 3m ---');
  const monthEnd4: PeriodDiaryInput = {
    startDate: '2026-11-30',
    durationType: '3m',
    birth: TEST_BIRTH
  };
  
  const result4 = await buildPeriodDiary(monthEnd4);
  console.log(`Result: ${result4.startDate} to ${result4.endDate} (${result4.totalDays} days)`);
  console.log(`Expected: 2026-11-30 to 2027-02-28`);
  if (result4.endDate === '2027-02-28') {
    console.log('✓ PASS: 3-month period with month-end clamp working');
  } else {
    console.log('✗ FAIL: Expected 2027-02-28, got ' + result4.endDate);
  }
}

// ============================================================
// Main Test Runner
// ============================================================

async function runAllTests(): Promise<void> {
  console.log('========================================');
  console.log('Period Diary Generator Test Suite');
  console.log('========================================');
  
  try {
    // 짧은 기간부터 테스트
    await test1Month();
    
    // 중간 기간 테스트 (시간 절약을 위해 주석 처리 가능)
    // await test3Months();
    // await test6Months();
    
    // 긴 기간 테스트 (시간이 많이 걸림, 필요시 주석 처리)
    // await test1Year();
    
    // 엣지 케이스
    await testEdgeCases();
    
    console.log('\n========================================');
    console.log('All tests completed');
    console.log('========================================');
  } catch (error) {
    console.error('Test failed with error:', error);
    process.exit(1);
  }
}

// Run tests if executed directly
if (require.main === module) {
  runAllTests().catch(console.error);
}

// Export for external use
export { runAllTests, test1Month, test3Months, test6Months, test1Year, testEdgeCases };