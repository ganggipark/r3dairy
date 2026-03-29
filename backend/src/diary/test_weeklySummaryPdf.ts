/**
 * Test for weekly summary pages
 * 
 * Tests 1-month period to ensure weekly summaries are created
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
 * Helper to calculate expected week count
 */
function calculateExpectedWeekCount(entries: any[]): number {
  const weekSet = new Set<string>();
  
  entries.forEach(entry => {
    const date = new Date(entry.date);
    const dayOfWeek = date.getDay();
    const daysToMonday = dayOfWeek === 0 ? -6 : 1 - dayOfWeek;
    const weekStart = new Date(date);
    weekStart.setDate(weekStart.getDate() + daysToMonday);
    const weekKey = weekStart.toISOString().split('T')[0];
    weekSet.add(weekKey);
  });
  
  return weekSet.size;
}

/**
 * Test 1-month period with weekly summaries
 */
async function test1MonthWithWeeklySummaries(): Promise<void> {
  console.log('\n========== Test: 1-Month PDF with Weekly Summaries ==========');
  
  try {
    // 1. Generate 1-month period data
    console.log('Step 1: Generating 1-month period data...');
    const periodInput: PeriodDiaryInput = {
      startDate: '2026-03-01',
      durationType: '1m',
      birth: TEST_BIRTH
    };
    
    const periodData = await buildPeriodDiary(periodInput);
    console.log(`Generated ${periodData.entries.length} daily entries`);
    console.log(`Period: ${periodData.startDate} to ${periodData.endDate}`);
    
    // 2. Calculate expected weeks
    const expectedWeeks = calculateExpectedWeekCount(periodData.entries);
    console.log(`Expected weeks in period: ${expectedWeeks}`);
    
    // 3. Render PDF with weekly summaries
    console.log('\nStep 2: Rendering PDF with weekly summaries...');
    const result = await renderPeriodDiaryPdf({
      period: periodData,
      outputPath: path.join('./test_output', `test_1month_weekly_${Date.now()}.pdf`)
    });
    
    // 4. Verify results
    console.log('\n=== Test Results ===');
    console.log(`Success: ${result.success}`);
    console.log(`Output Path: ${result.outputPath}`);
    console.log(`Total Page Count: ${result.pageCount}`);
    
    // Calculate expected page count
    const monthCount = 1; // 1 month period
    const monthlySummaryPages = 0; // No monthly summary for 1m period
    const weeklySummaryPages = expectedWeeks;
    const expectedPageCount = 1 + monthCount + monthlySummaryPages + weeklySummaryPages + periodData.entries.length;
    
    console.log('\n=== Page Breakdown ===');
    console.log(`Cover Page: 1`);
    console.log(`Month Dividers: ${monthCount}`);
    console.log(`Monthly Summaries: ${monthlySummaryPages}`);
    console.log(`Weekly Summaries: ${weeklySummaryPages}`);
    console.log(`Daily Pages: ${periodData.entries.length}`);
    console.log(`Expected Total: ${expectedPageCount}`);
    
    if (result.pageCount === expectedPageCount) {
      console.log(`✓ Page count correct: ${result.pageCount} pages`);
    } else {
      console.log(`✗ Page count mismatch: expected ${expectedPageCount}, got ${result.pageCount}`);
    }
    
    // Verify files exist
    if (result.outputPath && fs.existsSync(result.outputPath)) {
      const stats = fs.statSync(result.outputPath);
      console.log(`✓ PDF file created: ${(stats.size / 1024).toFixed(2)} KB`);
    }
    
    // Check HTML for weekly summaries
    const htmlPath = result.outputPath?.replace('.pdf', '.html');
    if (htmlPath && fs.existsSync(htmlPath)) {
      const htmlContent = fs.readFileSync(htmlPath, 'utf-8');
      const weeklySummaryCount = (htmlContent.match(/class="weekly-summary"/g) || []).length;
      
      console.log('\n=== HTML Structure Verification ===');
      console.log(`Weekly Summaries found in HTML: ${weeklySummaryCount}`);
      
      if (weeklySummaryCount === weeklySummaryPages) {
        console.log('✓ Correct number of weekly summaries');
      } else {
        console.log(`✗ Expected ${weeklySummaryPages} weekly summaries, found ${weeklySummaryCount}`);
      }
    }
    
  } catch (error) {
    console.error('Test failed:', error);
  }
}

/**
 * Test month boundary crossing
 */
async function testMonthBoundaryWeeks(): Promise<void> {
  console.log('\n========== Test: Month Boundary Week Handling ==========');
  
  try {
    // Start on a Wednesday to ensure week crosses month boundary
    const periodInput: PeriodDiaryInput = {
      startDate: '2026-02-25',  // Wednesday
      durationType: '1m',
      birth: TEST_BIRTH
    };
    
    // Generate only 10 days for testing
    const periodData = await buildPeriodDiary(periodInput);
    const shortPeriod = {
      ...periodData,
      entries: periodData.entries.slice(0, 10),
      endDate: '2026-03-06',
      totalDays: 10
    };
    
    console.log(`Testing with ${shortPeriod.entries.length} days crossing month boundary`);
    console.log(`Period: ${shortPeriod.entries[0].date} to ${shortPeriod.entries[shortPeriod.entries.length - 1].date}`);
    
    const result = await renderPeriodDiaryPdf({
      period: shortPeriod,
      outputPath: path.join('./test_output', `test_boundary_weekly_${Date.now()}.pdf`)
    });
    
    // Expect 2 weeks (Feb 23-Mar 1, Mar 2-Mar 8)
    const expectedWeeks = 2;
    const expectedPageCount = 1 + 2 + 0 + expectedWeeks + 10; // cover + 2 month dividers + 0 monthly + 2 weekly + 10 daily
    
    console.log(`Result: ${result.pageCount} pages (expected: ${expectedPageCount})`);
    console.log(result.pageCount === expectedPageCount ? '✓ Correct page count' : '✗ Page count mismatch');
    
  } catch (error) {
    console.error('Test failed:', error);
  }
}

// Main test runner
async function runTests(): Promise<void> {
  console.log('========================================');
  console.log('Weekly Summary PDF Test Suite');
  console.log('========================================');
  
  try {
    // Create output directory
    const outputDir = './test_output';
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }
    
    // Run tests
    await test1MonthWithWeeklySummaries();
    await testMonthBoundaryWeeks();
    
    console.log('\n========================================');
    console.log('All tests completed');
    console.log('Check ./test_output directory for PDFs');
    console.log('========================================');
  } catch (error) {
    console.error('Test suite failed:', error);
    process.exit(1);
  }
}

// Run tests if executed directly
if (require.main === module) {
  runTests().catch(console.error);
}

export { runTests, test1MonthWithWeeklySummaries, testMonthBoundaryWeeks };