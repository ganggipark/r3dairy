/**
 * Test for index pages in period diary PDF
 * 
 * Tests index page generation with accurate page numbers
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
 * Test 1-month period with index pages
 */
async function test1MonthWithIndex(): Promise<void> {
  console.log('\n========== Test: 1-Month PDF with Index Pages ==========');
  
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
    
    // 2. Render PDF with index pages
    console.log('\nStep 2: Rendering PDF with index pages...');
    const result = await renderPeriodDiaryPdf({
      period: periodData,
      outputPath: path.join('./test_output', `test_1month_index_${Date.now()}.pdf`)
    });
    
    // 3. Verify results
    console.log('\n=== Test Results ===');
    console.log(`Success: ${result.success}`);
    console.log(`Output Path: ${result.outputPath}`);
    console.log(`Total Page Count: ${result.pageCount}`);
    
    // Calculate expected page count
    const monthCount = 1; // 1 month period
    const indexPageCount = Math.ceil(periodData.entries.length / 25); // ~25 entries per index page
    const monthlySummaryPages = 0; // No monthly summary for 1m period
    const weekGroups = Math.ceil(periodData.entries.length / 7);
    const weeklySummaryPages = weekGroups;
    const expectedPageCount = 1 + indexPageCount + monthCount + monthlySummaryPages + weeklySummaryPages + periodData.entries.length;
    
    console.log('\n=== Page Breakdown ===');
    console.log(`Cover Page: 1`);
    console.log(`Index Pages: ${indexPageCount}`);
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
    
    // Check HTML for index pages
    const htmlPath = result.outputPath?.replace('.pdf', '.html');
    if (htmlPath && fs.existsSync(htmlPath)) {
      const htmlContent = fs.readFileSync(htmlPath, 'utf-8');
      const indexPageCount = (htmlContent.match(/class="index-page"/g) || []).length;
      const indexTableCount = (htmlContent.match(/class="index-table"/g) || []).length;
      
      console.log('\n=== HTML Structure Verification ===');
      console.log(`Index Pages found in HTML: ${indexPageCount}`);
      console.log(`Index Tables found in HTML: ${indexTableCount}`);
      
      // Check for page numbers in index
      const pageNumMatches = htmlContent.match(/p\.\d+/g) || [];
      console.log(`Page number references in index: ${pageNumMatches.length}`);
      
      if (pageNumMatches.length === periodData.entries.length) {
        console.log('✓ All entries have page numbers in index');
      } else {
        console.log(`✗ Expected ${periodData.entries.length} page numbers, found ${pageNumMatches.length}`);
      }
    }
    
  } catch (error) {
    console.error('Test failed:', error);
  }
}

/**
 * Test 3-month period with multiple index pages
 */
async function test3MonthWithMultipleIndexPages(): Promise<void> {
  console.log('\n========== Test: 3-Month PDF with Multiple Index Pages ==========');
  
  try {
    const periodInput: PeriodDiaryInput = {
      startDate: '2026-02-01',
      durationType: '3m',
      birth: TEST_BIRTH
    };
    
    const periodData = await buildPeriodDiary(periodInput);
    console.log(`Testing with ${periodData.entries.length} days across 3 months`);
    
    const result = await renderPeriodDiaryPdf({
      period: periodData,
      outputPath: path.join('./test_output', `test_3month_index_${Date.now()}.pdf`)
    });
    
    // For 3 months, we expect multiple index pages
    const indexPageCount = Math.ceil(periodData.entries.length / 25);
    const monthCount = 3;
    const monthlySummaryPages = 3; // Monthly summaries for 3m period
    
    console.log(`\n=== Results ===`);
    console.log(`Total entries: ${periodData.entries.length}`);
    console.log(`Index pages needed: ${indexPageCount}`);
    console.log(`PDF generated: ${result.outputPath}`);
    console.log(`Total pages: ${result.pageCount}`);
    
    // Verify HTML structure
    const htmlPath = result.outputPath?.replace('.pdf', '.html');
    if (htmlPath && fs.existsSync(htmlPath)) {
      const htmlContent = fs.readFileSync(htmlPath, 'utf-8');
      
      // Check for month headers in index
      const monthHeaders = htmlContent.match(/index-month-header/g) || [];
      console.log(`Month headers in index: ${monthHeaders.length}`);
      
      // Verify correct pagination
      if (periodData.entries.length > 25) {
        const continuationHeaders = htmlContent.match(/날짜별 인덱스 \(계속\)/g) || [];
        console.log(`Index continuation pages: ${continuationHeaders.length}`);
      }
    }
    
  } catch (error) {
    console.error('Test failed:', error);
  }
}

/**
 * Test index page accuracy
 */
async function testIndexPageAccuracy(): Promise<void> {
  console.log('\n========== Test: Index Page Number Accuracy ==========');
  
  try {
    // Use a small period for detailed verification
    const periodInput: PeriodDiaryInput = {
      startDate: '2026-03-01',
      durationType: '1m',
      birth: TEST_BIRTH
    };
    
    // Generate with only 7 days for easier manual verification
    const periodData = await buildPeriodDiary(periodInput);
    const shortPeriod = {
      ...periodData,
      entries: periodData.entries.slice(0, 7),
      endDate: '2026-03-07',
      totalDays: 7
    };
    
    console.log(`Testing index accuracy with ${shortPeriod.entries.length} days`);
    
    const result = await renderPeriodDiaryPdf({
      period: shortPeriod,
      outputPath: path.join('./test_output', `test_index_accuracy_${Date.now()}.pdf`)
    });
    
    // Manual page calculation
    let expectedPageNum = 1; // Cover
    expectedPageNum += 1; // Index page
    expectedPageNum += 1; // Month divider
    // No monthly summary for 7 days
    // Daily pages start here
    
    console.log('\n=== Page Number Verification ===');
    console.log('Expected page numbers for daily entries:');
    for (let i = 0; i < shortPeriod.entries.length; i++) {
      console.log(`  ${shortPeriod.entries[i].date}: Page ${expectedPageNum + i}`);
    }
    
    // Weekly summary after all daily pages
    const totalExpectedPages = expectedPageNum + shortPeriod.entries.length + 1; // +1 for weekly summary
    
    console.log(`\nTotal expected pages: ${totalExpectedPages}`);
    console.log(`Actual page count: ${result.pageCount}`);
    console.log(result.pageCount === totalExpectedPages ? '✓ Page count accurate' : '✗ Page count mismatch');
    
  } catch (error) {
    console.error('Test failed:', error);
  }
}

// Main test runner
async function runTests(): Promise<void> {
  console.log('========================================');
  console.log('Index Pages PDF Test Suite');
  console.log('========================================');
  
  try {
    // Create output directory
    const outputDir = './test_output';
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }
    
    // Run tests
    await test1MonthWithIndex();
    await test3MonthWithMultipleIndexPages();
    await testIndexPageAccuracy();
    
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

export { runTests, test1MonthWithIndex, test3MonthWithMultipleIndexPages, testIndexPageAccuracy };