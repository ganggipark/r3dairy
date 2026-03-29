/**
 * Test for weekly reflection pages in period diary PDF
 * 
 * Verifies that weekly reflection pages appear after weekly summaries
 */

import { buildPeriodDiary, PeriodDiaryInput } from './periodDiaryGenerator';
import { renderPeriodDiaryPdf } from './periodDiaryPdfRenderer';
import * as fs from 'fs';
import * as path from 'path';

// Test Configuration
const TEST_BIRTH = {
  year: 1971,
  month: 11,
  day: 17,
  hour: 4,
  minute: 0,
  isLunar: false as const,
  birthPlace: '서울'
};

/**
 * Test weekly reflection page rendering
 */
async function testWeeklyReflection(): Promise<void> {
  console.log('\n========== Test: Weekly Reflection Pages ==========');
  
  try {
    // 1. Generate a 2-week period to test weekly reflection
    console.log('Step 1: Generating 2-week test period...');
    const periodInput: PeriodDiaryInput = {
      startDate: '2026-03-01',
      durationType: '1m',
      birth: TEST_BIRTH
    };
    
    const periodData = await buildPeriodDiary(periodInput);
    // Use 14 days for 2 full weeks
    const twoWeekPeriod = {
      ...periodData,
      entries: periodData.entries.slice(0, 14),
      endDate: '2026-03-14',
      totalDays: 14
    };
    
    console.log(`Testing with ${twoWeekPeriod.entries.length} days (2 weeks)`);
    
    // 2. Render PDF with weekly reflections
    console.log('\nStep 2: Rendering PDF with weekly reflection pages...');
    const result = await renderPeriodDiaryPdf({
      period: twoWeekPeriod,
      outputPath: path.join('./test_output', `test_weekly_reflection_${Date.now()}.pdf`)
    });
    
    // 3. Verify results
    console.log('\n=== Test Results ===');
    console.log(`Success: ${result.success}`);
    console.log(`Output Path: ${result.outputPath}`);
    console.log(`Page Count: ${result.pageCount}`);
    
    // Calculate expected page count with reflections
    const coverPages = 1;
    const indexPages = 1; // ~25 entries per page, 14 entries = 1 page
    const monthDividers = 1; // March only
    const weeklySummaries = 2; // 2 weeks
    const weeklyReflections = 2; // NEW: 2 reflection pages
    const dailyPages = 14;
    const expectedPageCount = coverPages + indexPages + monthDividers + weeklySummaries + weeklyReflections + dailyPages;
    
    console.log('\n=== Page Breakdown ===');
    console.log(`Cover Page: ${coverPages}`);
    console.log(`Index Pages: ${indexPages}`);
    console.log(`Month Dividers: ${monthDividers}`);
    console.log(`Weekly Summaries: ${weeklySummaries}`);
    console.log(`Weekly Reflections: ${weeklyReflections} (NEW)`);
    console.log(`Daily Pages: ${dailyPages}`);
    console.log(`Expected Total: ${expectedPageCount}`);
    console.log(`Actual Total: ${result.pageCount}`);
    
    if (result.pageCount === expectedPageCount) {
      console.log(`✓ Page count correct including weekly reflections`);
    } else {
      console.log(`✗ Page count mismatch: expected ${expectedPageCount}, got ${result.pageCount}`);
    }
    
    // 4. Check HTML for weekly reflection sections
    const htmlPath = result.outputPath?.replace('.pdf', '.html');
    if (htmlPath && fs.existsSync(htmlPath)) {
      const htmlContent = fs.readFileSync(htmlPath, 'utf-8');
      
      // Check for weekly reflection pages
      const reflectionPages = (htmlContent.match(/class="weekly-reflection"/g) || []).length;
      const reflectionSections = (htmlContent.match(/class="reflection-section"/g) || []).length;
      const reflectionLines = (htmlContent.match(/class="reflection-line"/g) || []).length;
      const memoBoxes = (htmlContent.match(/class="memo-box"/g) || []).length;
      
      console.log('\n=== HTML Structure Verification ===');
      console.log(`Weekly Reflection Pages: ${reflectionPages}`);
      console.log(`Reflection Sections: ${reflectionSections}`);
      console.log(`Reflection Lines: ${reflectionLines}`);
      console.log(`Memo Boxes: ${memoBoxes}`);
      
      // Verify we have 2 weekly reflections (one per week)
      if (reflectionPages === 2) {
        console.log('✓ Correct number of weekly reflection pages');
      } else {
        console.log(`✗ Expected 2 weekly reflection pages, found ${reflectionPages}`);
      }
      
      // Check for specific content
      const hasSectionA = htmlContent.includes('A. 이번 주 돌아보기');
      const hasSectionB = htmlContent.includes('B. 감정 회고');
      const hasSectionC = htmlContent.includes('C. 실행 점검');
      const hasSectionD = htmlContent.includes('D. 자유 메모');
      
      console.log('\n=== Content Verification ===');
      console.log(`Section A (이번 주 돌아보기): ${hasSectionA ? '✓' : '✗'}`);
      console.log(`Section B (감정 회고): ${hasSectionB ? '✓' : '✗'}`);
      console.log(`Section C (실행 점검): ${hasSectionC ? '✓' : '✗'}`);
      console.log(`Section D (자유 메모): ${hasSectionD ? '✓' : '✗'}`);
    }
    
    // 5. Verify PDF file exists
    if (result.outputPath && fs.existsSync(result.outputPath)) {
      const stats = fs.statSync(result.outputPath);
      console.log(`\n✓ PDF file created: ${(stats.size / 1024).toFixed(2)} KB`);
    }
    
  } catch (error) {
    console.error('Test failed:', error);
  }
}

// Run test if executed directly
if (require.main === module) {
  testWeeklyReflection().catch(console.error);
}

export { testWeeklyReflection };