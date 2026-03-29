/**
 * 주문형 인쇄 제작 파이프라인 테스트
 * 
 * 샘플 주문으로 PDF 생성을 테스트하고 운영자 워크플로우 검증
 */

import * as fs from 'fs';
import * as path from 'path';
import { buildOrderDiary, OrderInput, OrderBuildResult } from './orderDiaryBuilder';

// ============================================================
// Test Data
// ============================================================

const SAMPLE_ORDERS: OrderInput[] = [
  {
    customerName: '김다이어리',
    ownerLabel: '김다이어리님의 전용 다이어리',
    productTitle: '나만의 특별한 리듬 다이어리',
    calendarType: 'solar',
    gender: 'female',
    birth: {
      year: 1990,
      month: 5,
      day: 15,
      hour: 14,
      minute: 30
    },
    startDate: '2026-04-01',
    durationType: '1m',
    renderMode: 'standard'
  },
  {
    customerName: '이연구',
    calendarType: 'solar', 
    gender: 'male',
    birth: {
      year: 1985,
      month: 12,
      day: 3,
      hour: 9,
      minute: 0
    },
    startDate: '2026-04-01',
    durationType: '3m',
    renderMode: 'large'
  },
  {
    customerName: 'Park Diary',
    ownerLabel: '박다이어리',
    calendarType: 'lunar',
    gender: 'female',
    birth: {
      year: 1971,
      month: 11, 
      day: 17,
      hour: 4,
      minute: 0
    },
    startDate: '2026-03-01',
    durationType: '1m',
    renderMode: 'standard'
  }
];

// ============================================================
// Test Functions
// ============================================================

/**
 * 개별 주문 테스트
 */
async function testSingleOrder(order: OrderInput, orderIndex: number): Promise<boolean> {
  console.log(`\n========== 주문 ${orderIndex + 1}: ${order.customerName} ==========`);
  console.log(`기간: ${order.durationType} (${order.startDate}부터)`);
  console.log(`모드: ${order.renderMode || 'standard'}`);
  console.log(`성별: ${order.gender}, 달력: ${order.calendarType}`);
  
  try {
    const startTime = Date.now();
    const result: OrderBuildResult = await buildOrderDiary(order);
    const endTime = Date.now();
    const processingTime = endTime - startTime;
    
    // 결과 검증
    console.log('\n=== 주문 결과 검증 ===');
    console.log(`✓ 성공 여부: ${result.success ? '성공' : '실패'}`);
    
    if (!result.success) {
      console.error(`❌ 실패 원인: ${result.error}`);
      return false;
    }
    
    // 주문 요약 검증
    console.log(`✓ 고객명: ${result.orderSummary.customerName}`);
    console.log(`✓ 기간: ${result.orderSummary.startDate} ~ ${result.orderSummary.endDate}`);
    console.log(`✓ 총 일수: ${result.orderSummary.totalDays}일`);
    console.log(`✓ 총 페이지: ${result.orderSummary.totalPages}페이지`);
    
    // 파일 검증
    console.log('\n=== 파일 검증 ===');
    if (result.files.pdfPath) {
      const pdfExists = fs.existsSync(result.files.pdfPath);
      console.log(`✓ PDF 파일: ${pdfExists ? '생성됨' : '없음'} (${result.files.pdfPath})`);
      
      if (pdfExists) {
        const stats = fs.statSync(result.files.pdfPath);
        console.log(`  크기: ${(stats.size / 1024).toFixed(2)} KB`);
      }
      
      if (!pdfExists) {
        console.error('❌ PDF 파일이 생성되지 않았습니다');
        return false;
      }
    } else {
      console.error('❌ PDF 파일 경로가 없습니다');
      return false;
    }
    
    // 파일명 규칙 검증
    const fileName = path.basename(result.files.pdfPath || '');
    const expectedPattern = /^\d{8}_[^_]+_\w+_(standard|large)\.pdf$/;
    const fileNameValid = expectedPattern.test(fileName);
    console.log(`✓ 파일명 규칙: ${fileNameValid ? '준수' : '위반'} (${fileName})`);
    
    if (!fileNameValid) {
      console.error('❌ 파일명 규칙을 준수하지 않습니다');
      return false;
    }
    
    // 메타데이터 검증
    console.log('\n=== 메타데이터 검증 ===');
    console.log(`✓ 생성 시각: ${result.metadata.generatedAt}`);
    console.log(`✓ 렌더링 모드: ${result.metadata.renderMode}`);
    console.log(`✓ 달력 타입: ${result.metadata.calendarType}`);
    
    // 처리 시간
    console.log(`✓ 처리 시간: ${processingTime}ms (${(processingTime / 1000).toFixed(1)}초)`);
    
    console.log('\n🎉 주문 테스트 성공!');
    return true;
    
  } catch (error) {
    console.error(`❌ 테스트 중 오류: ${error instanceof Error ? error.message : String(error)}`);
    return false;
  }
}

/**
 * 유효성 검증 테스트
 */
async function testValidation(): Promise<boolean> {
  console.log('\n========== 유효성 검증 테스트 ==========');
  
  const invalidOrders = [
    {
      // 고객명 없음
      customerName: '',
      calendarType: 'solar' as const,
      gender: 'male' as const,
      birth: { year: 1990, month: 1, day: 1 },
      startDate: '2026-04-01',
      durationType: '1m' as const
    },
    {
      // 잘못된 날짜 형식
      customerName: '테스트',
      calendarType: 'solar' as const,
      gender: 'female' as const,
      birth: { year: 1990, month: 1, day: 1 },
      startDate: '2026/04/01', // 잘못된 형식
      durationType: '1m' as const
    },
    {
      // 잘못된 출생년도
      customerName: '테스트',
      calendarType: 'solar' as const,
      gender: 'male' as const,
      birth: { year: 1800, month: 1, day: 1 }, // 너무 옛날
      startDate: '2026-04-01',
      durationType: '1m' as const
    }
  ];
  
  let validationTestsPassed = 0;
  
  for (let i = 0; i < invalidOrders.length; i++) {
    const order = invalidOrders[i] as OrderInput;
    console.log(`\n--- 유효성 테스트 ${i + 1} ---`);
    
    try {
      const result = await buildOrderDiary(order);
      
      if (!result.success) {
        console.log(`✓ 예상대로 실패: ${result.error}`);
        validationTestsPassed++;
      } else {
        console.error('❌ 유효하지 않은 입력이 성공했습니다');
      }
    } catch (error) {
      console.error(`❌ 유효성 테스트 중 예외: ${error instanceof Error ? error.message : String(error)}`);
    }
  }
  
  const allValidationPassed = validationTestsPassed === invalidOrders.length;
  console.log(`\n유효성 검증 결과: ${validationTestsPassed}/${invalidOrders.length} 통과`);
  
  return allValidationPassed;
}

/**
 * 출력 디렉토리 정보 확인
 */
function checkOutputDirectory(): void {
  console.log('\n========== 출력 디렉토리 정보 ==========');
  
  const outputDir = './order_output';
  const absolutePath = path.resolve(outputDir);
  
  console.log(`출력 경로: ${absolutePath}`);
  
  if (fs.existsSync(outputDir)) {
    const files = fs.readdirSync(outputDir);
    const pdfFiles = files.filter(f => f.endsWith('.pdf'));
    
    console.log(`총 파일 수: ${files.length}`);
    console.log(`PDF 파일 수: ${pdfFiles.length}`);
    
    if (pdfFiles.length > 0) {
      console.log('\nPDF 파일 목록:');
      pdfFiles.forEach(file => {
        const fullPath = path.join(outputDir, file);
        const stats = fs.statSync(fullPath);
        const size = (stats.size / 1024).toFixed(2);
        console.log(`  ${file} (${size} KB)`);
      });
    }
  } else {
    console.log('출력 디렉토리가 아직 생성되지 않았습니다');
  }
}

// ============================================================
// Main Test Runner
// ============================================================

/**
 * 전체 테스트 실행
 */
async function runAllTests(): Promise<void> {
  console.log('========================================');
  console.log('주문형 인쇄 제작 파이프라인 테스트 시작');
  console.log('========================================');
  
  const startTime = Date.now();
  let successCount = 0;
  
  try {
    // 1. 출력 디렉토리 확인
    checkOutputDirectory();
    
    // 2. 유효성 검증 테스트
    const validationPassed = await testValidation();
    if (validationPassed) {
      console.log('✅ 유효성 검증 테스트 통과');
    } else {
      console.error('❌ 유효성 검증 테스트 실패');
    }
    
    // 3. 샘플 주문 테스트
    for (let i = 0; i < SAMPLE_ORDERS.length; i++) {
      const success = await testSingleOrder(SAMPLE_ORDERS[i], i);
      if (success) {
        successCount++;
      }
    }
    
    // 4. 최종 출력 디렉토리 상태
    checkOutputDirectory();
    
    // 5. 테스트 결과 요약
    const endTime = Date.now();
    const totalTime = endTime - startTime;
    
    console.log('\n========================================');
    console.log('테스트 결과 요약');
    console.log('========================================');
    console.log(`✓ 성공한 주문: ${successCount}/${SAMPLE_ORDERS.length}`);
    console.log(`✓ 유효성 검증: ${validationPassed ? '통과' : '실패'}`);
    console.log(`✓ 총 소요 시간: ${(totalTime / 1000).toFixed(1)}초`);
    
    if (successCount === SAMPLE_ORDERS.length && validationPassed) {
      console.log('\n🎉 모든 테스트가 성공했습니다!');
      console.log('\n운영자 가이드:');
      console.log('1. ./order_output 디렉토리에서 생성된 PDF 확인');
      console.log('2. 파일명 형식: YYYYMMDD_고객명_기간_모드.pdf');
      console.log('3. buildOrderDiary() 함수로 주문 처리 가능');
    } else {
      console.error('\n❌ 일부 테스트가 실패했습니다');
      process.exit(1);
    }
    
  } catch (error) {
    console.error('\n❌ 테스트 실행 중 치명적 오류:', error instanceof Error ? error.message : String(error));
    process.exit(1);
  }
}

// ============================================================
// Execute Tests
// ============================================================

// 직접 실행 시 테스트 시작
if (require.main === module) {
  runAllTests().catch(console.error);
}

// 개별 함수 내보내기
export {
  runAllTests,
  testSingleOrder,
  testValidation,
  checkOutputDirectory,
  SAMPLE_ORDERS
};