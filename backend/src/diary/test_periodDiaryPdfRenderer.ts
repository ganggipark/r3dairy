/**
 * 기간별 다이어리 PDF 묶음 렌더러 테스트
 * 
 * 1개월 기간으로 PDF 생성 테스트
 */

import { buildPeriodDiary, PeriodDiaryInput } from './periodDiaryGenerator';
import { renderPeriodDiaryPdf, PeriodDiaryPdfRenderer } from './periodDiaryPdfRenderer';
import * as fs from 'fs';
import * as path from 'path';

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
// Test Functions
// ============================================================

/**
 * 1개월 기간 PDF 생성 테스트
 */
async function test1MonthPdfGeneration(): Promise<void> {
  console.log('\n========== Test: 1 Month PDF Generation ==========');
  
  try {
    // 1. 기간 데이터 생성 (간단한 테스트를 위해 7일만)
    console.log('Step 1: Generating period data for 7 days...');
    const periodInput: PeriodDiaryInput = {
      startDate: '2026-03-01',
      durationType: '1m', // 실제로는 1개월이지만 테스트는 7일만
      birth: TEST_BIRTH
    };
    
    // 테스트를 위해 짧은 기간만 생성
    const testPeriod = await buildPeriodDiary({
      ...periodInput,
      startDate: '2026-03-01',
      durationType: '1m'
    });
    
    // 테스트용으로 7일치만 사용
    const shortPeriod = {
      ...testPeriod,
      entries: testPeriod.entries.slice(0, 7),
      endDate: '2026-03-07',
      totalDays: 7
    };
    
    console.log(`Generated ${shortPeriod.entries.length} daily entries`);
    
    // 2. PDF 렌더링
    console.log('Step 2: Rendering PDF...');
    const result = await renderPeriodDiaryPdf({
      period: shortPeriod,
      outputPath: path.join('./test_output', `test_1week_${Date.now()}.pdf`)
    });
    
    // 3. 결과 검증
    console.log('\n=== Test Results ===');
    console.log(`Success: ${result.success}`);
    console.log(`Output Path: ${result.outputPath}`);
    console.log(`Page Count: ${result.pageCount}`);
    
    // 페이지 수 검증 (Cover + Daily pages)
    const expectedPageCount = 1 + shortPeriod.entries.length;
    if (result.pageCount === expectedPageCount) {
      console.log(`✓ Page count correct: ${result.pageCount} pages`);
    } else {
      console.log(`✗ Page count mismatch: expected ${expectedPageCount}, got ${result.pageCount}`);
    }
    
    // 파일 존재 확인 (HTML은 있지만 PDF 변환은 실패할 수 있음)
    if (result.outputPath) {
      const htmlPath = result.outputPath.replace('.pdf', '.html');
      if (fs.existsSync(htmlPath)) {
        const stats = fs.statSync(htmlPath);
        console.log(`✓ HTML file created: ${stats.size} bytes`);
        
        // HTML 내용 미리보기
        const htmlContent = fs.readFileSync(htmlPath, 'utf-8');
        const coverMatch = htmlContent.includes('R³ 다이어리');
        const dailyPagesMatch = htmlContent.includes('Day 1 /');
        
        console.log(`✓ Cover page: ${coverMatch ? 'Found' : 'Not found'}`);
        console.log(`✓ Daily pages: ${dailyPagesMatch ? 'Found' : 'Not found'}`);
      }
      
      if (fs.existsSync(result.outputPath)) {
        const stats = fs.statSync(result.outputPath);
        console.log(`✓ PDF file created: ${stats.size} bytes`);
      } else {
        console.log('⚠ PDF file not created (puppeteer/wkhtmltopdf may not be installed)');
        console.log('  HTML file is available for review');
      }
    }
    
  } catch (error) {
    console.error('Test failed:', error);
  }
}

/**
 * HTML 구조 검증 테스트
 */
async function testHtmlStructure(): Promise<void> {
  console.log('\n========== Test: HTML Structure Validation ==========');
  
  try {
    // 간단한 테스트 데이터 생성
    const periodInput: PeriodDiaryInput = {
      startDate: '2026-03-01',
      durationType: '1m',
      birth: TEST_BIRTH
    };
    
    // 3일치만 생성
    const testPeriod = await buildPeriodDiary({
      ...periodInput,
      startDate: '2026-03-01',
      durationType: '1m'
    });
    
    const shortPeriod = {
      ...testPeriod,
      entries: testPeriod.entries.slice(0, 3),
      endDate: '2026-03-03',
      totalDays: 3
    };
    
    // 렌더러 직접 사용
    const renderer = new PeriodDiaryPdfRenderer('./test_output');
    const result = await renderer.renderPdf({
      period: shortPeriod,
      includeTableOfContents: false
    });
    
    if (result.outputPath) {
      const htmlPath = result.outputPath.replace('.pdf', '.html');
      if (fs.existsSync(htmlPath)) {
        const htmlContent = fs.readFileSync(htmlPath, 'utf-8');
        
        // HTML 구조 검증
        const checks = [
          { name: 'DOCTYPE', pattern: /<!DOCTYPE html>/ },
          { name: 'UTF-8', pattern: /<meta charset="UTF-8">/ },
          { name: 'Cover Page', pattern: /<div class="cover-page">/ },
          { name: 'Daily Pages', pattern: /<div class="daily-page">/ },
          { name: 'Page Breaks', pattern: /page-break-after:\s*always/ },
          { name: 'Left Panel', pattern: /<div class="left-panel">/ },
          { name: 'Right Panel', pattern: /<div class="right-panel">/ },
          { name: 'Keywords', pattern: /<div class="keywords">/ },
          { name: 'Time Slots', pattern: /class="time-slots"/ }
        ];
        
        console.log('HTML Structure Validation:');
        checks.forEach(check => {
          const found = check.pattern.test(htmlContent);
          console.log(`  ${found ? '✓' : '✗'} ${check.name}`);
        });
        
        // Daily page 수 확인
        const dailyPageCount = (htmlContent.match(/<div class="daily-page">/g) || []).length;
        console.log(`\nDaily pages found: ${dailyPageCount}`);
        
        if (dailyPageCount === shortPeriod.entries.length) {
          console.log('✓ Correct number of daily pages');
        } else {
          console.log(`✗ Expected ${shortPeriod.entries.length} daily pages, found ${dailyPageCount}`);
        }
      }
    }
    
  } catch (error) {
    console.error('Structure test failed:', error);
  }
}

/**
 * 대용량 기간 테스트 (실제로는 실행하지 않음)
 */
async function testLargePeriodEstimate(): Promise<void> {
  console.log('\n========== Test: Large Period Estimation ==========');
  
  const periods = [
    { type: '1m', days: 31, label: '1개월' },
    { type: '3m', days: 91, label: '3개월' },
    { type: '6m', days: 183, label: '6개월' },
    { type: '1y', days: 365, label: '1년' }
  ];
  
  console.log('Estimated page counts for different periods:');
  periods.forEach(period => {
    const pageCount = 1 + period.days; // Cover + Daily pages
    const estimatedSizeMB = pageCount * 0.1; // 대략 페이지당 100KB 추정
    
    console.log(`  ${period.label} (${period.days}일):`);
    console.log(`    - Pages: ${pageCount}`);
    console.log(`    - Estimated size: ~${estimatedSizeMB.toFixed(1)}MB`);
    console.log(`    - Generation time: ~${(period.days * 0.1).toFixed(0)}초`);
  });
}

// ============================================================
// Main Test Runner
// ============================================================

async function runAllTests(): Promise<void> {
  console.log('========================================');
  console.log('Period Diary PDF Renderer Test Suite');
  console.log('========================================');
  
  try {
    // 테스트 출력 디렉토리 생성
    const outputDir = './test_output';
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }
    
    // 테스트 실행
    await test1MonthPdfGeneration();
    await testHtmlStructure();
    await testLargePeriodEstimate();
    
    console.log('\n========================================');
    console.log('All tests completed');
    console.log('Check ./test_output directory for results');
    console.log('========================================');
  } catch (error) {
    console.error('Test suite failed:', error);
    process.exit(1);
  }
}

// Run tests if executed directly
if (require.main === module) {
  runAllTests().catch(console.error);
}

// Export for external use
export { runAllTests, test1MonthPdfGeneration, testHtmlStructure, testLargePeriodEstimate };