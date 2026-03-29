/**
 * Test for month divider and monthly summary pages
 * 
 * Tests 3-month period to ensure multiple month dividers are created
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
 * Test 3-month period with month dividers
 */
async function test3MonthWithDividers(): Promise<void> {
  console.log('\n========== Test: 3-Month PDF with Month Dividers ==========');
  
  try {
    // 1. Generate 3-month period data
    console.log('Step 1: Generating 3-month period data...');
    const periodInput: PeriodDiaryInput = {
      startDate: '2026-02-15',  // Mid-February to ensure crossing 3 months
      durationType: '3m',
      birth: TEST_BIRTH
    };
    
    const periodData = await buildPeriodDiary(periodInput);
    console.log(`Generated ${periodData.entries.length} daily entries`);
    console.log(`Period: ${periodData.startDate} to ${periodData.endDate}`);
    
    // 2. Count unique months
    const monthSet = new Set<string>();
    periodData.entries.forEach(entry => {
      monthSet.add(entry.date.substring(0, 7));
    });
    console.log(`Unique months in period: ${Array.from(monthSet).join(', ')}`);
    console.log(`Total unique months: ${monthSet.size}`);
    
    // 3. Render PDF with month dividers
    console.log('\nStep 2: Rendering PDF with month dividers...');
    const result = await renderPeriodDiaryPdf({
      period: periodData,
      outputPath: path.join('./test_output', `test_3month_dividers_${Date.now()}.pdf`)
    });
    
    // 4. Verify results
    console.log('\n=== Test Results ===');
    console.log(`Success: ${result.success}`);
    console.log(`Output Path: ${result.outputPath}`);
    console.log(`Total Page Count: ${result.pageCount}`);
    
    // Calculate expected page count
    const monthCount = monthSet.size;
    const summaryPages = monthCount; // One summary per month for 3m period
    const expectedPageCount = 1 + monthCount + summaryPages + periodData.entries.length;
    
    console.log('\n=== Page Breakdown ===');
    console.log(`Cover Page: 1`);
    console.log(`Month Dividers: ${monthCount}`);
    console.log(`Monthly Summaries: ${summaryPages}`);
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
    
    // Check HTML for month dividers
    const htmlPath = result.outputPath?.replace('.pdf', '.html');
    if (htmlPath && fs.existsSync(htmlPath)) {
      const htmlContent = fs.readFileSync(htmlPath, 'utf-8');
      const dividerCount = (htmlContent.match(/class="month-divider"/g) || []).length;
      const summaryCount = (htmlContent.match(/class="monthly-summary"/g) || []).length;
      
      console.log('\n=== HTML Structure Verification ===');
      console.log(`Month Dividers found in HTML: ${dividerCount}`);
      console.log(`Monthly Summaries found in HTML: ${summaryCount}`);
      
      if (dividerCount === monthCount) {
        console.log('✓ Correct number of month dividers');
      } else {
        console.log(`✗ Expected ${monthCount} dividers, found ${dividerCount}`);
      }
      
      if (summaryCount === summaryPages) {
        console.log('✓ Correct number of monthly summaries');
      } else {
        console.log(`✗ Expected ${summaryPages} summaries, found ${summaryCount}`);
      }
    }
    
  } catch (error) {
    console.error('Test failed:', error);
  }
}

/**
 * Test 1-week period (should NOT have monthly summary)
 */
async function test1WeekNoSummary(): Promise<void> {
  console.log('\n========== Test: 1-Week PDF (No Monthly Summary) ==========');
  
  try {
    const periodInput: PeriodDiaryInput = {
      startDate: '2026-03-01',
      durationType: '1m',
      birth: TEST_BIRTH
    };
    
    // Generate only 7 days for testing
    const periodData = await buildPeriodDiary(periodInput);
    const shortPeriod = {
      ...periodData,
      entries: periodData.entries.slice(0, 7),
      endDate: '2026-03-07',
      totalDays: 7
    };
    
    console.log(`Testing with ${shortPeriod.entries.length} days`);
    
    const result = await renderPeriodDiaryPdf({
      period: shortPeriod,
      outputPath: path.join('./test_output', `test_1week_nosummary_${Date.now()}.pdf`)
    });
    
    // For 7 days in one month: 1 cover + 1 divider + 0 summary + 7 daily = 9 pages
    const expectedPageCount = 1 + 1 + 0 + 7;
    
    console.log(`Result: ${result.pageCount} pages (expected: ${expectedPageCount})`);
    console.log(result.pageCount === expectedPageCount ? '✓ Correct page count' : '✗ Page count mismatch');
    
  } catch (error) {
    console.error('Test failed:', error);
  }
}

// Main test runner
async function runTests(): Promise<void> {
  console.log('========================================');
  console.log('Month Divider PDF Test Suite');
  console.log('========================================');
  
  try {
    // Create output directory
    const outputDir = './test_output';
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }
    
    // Run tests
    await test3MonthWithDividers();
    await test1WeekNoSummary();
    
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

export { runTests, test3MonthWithDividers, test1WeekNoSummary };