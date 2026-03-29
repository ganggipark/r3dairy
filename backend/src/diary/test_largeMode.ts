/**
 * Test for large mode (enhanced readability template) in period diary PDF
 * 
 * Tests both standard and large modes for font size, spacing, and readability
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
 * Test standard vs large mode comparison
 */
async function testLargeModeComparison(): Promise<void> {
  console.log('\n========== Test: Standard vs Large Mode Comparison ==========');
  
  try {
    // 1. Generate test period data (1 week for quick comparison)
    console.log('Step 1: Generating 1-week test period...');
    const periodInput: PeriodDiaryInput = {
      startDate: '2026-03-01',
      durationType: '1m',
      birth: TEST_BIRTH
    };
    
    const periodData = await buildPeriodDiary(periodInput);
    const weekPeriod = {
      ...periodData,
      entries: periodData.entries.slice(0, 7),
      endDate: '2026-03-07',
      totalDays: 7
    };
    
    console.log(`Testing with ${weekPeriod.entries.length} days`);
    
    // 2. Generate STANDARD mode PDF
    console.log('\nStep 2: Generating STANDARD mode PDF...');
    const standardResult = await renderPeriodDiaryPdf({
      period: weekPeriod,
      outputPath: path.join('./test_output', `test_standard_mode_${Date.now()}.pdf`),
      mode: 'standard'
    });
    
    // 3. Generate LARGE mode PDF
    console.log('\nStep 3: Generating LARGE mode PDF...');
    const largeResult = await renderPeriodDiaryPdf({
      period: weekPeriod,
      outputPath: path.join('./test_output', `test_large_mode_${Date.now()}.pdf`),
      mode: 'large'
    });
    
    // 4. Compare results
    console.log('\n=== Mode Comparison Results ===');
    console.log('STANDARD Mode:');
    console.log(`  Success: ${standardResult.success}`);
    console.log(`  Output: ${standardResult.outputPath}`);
    console.log(`  Page Count: ${standardResult.pageCount}`);
    
    console.log('\nLARGE Mode:');
    console.log(`  Success: ${largeResult.success}`);
    console.log(`  Output: ${largeResult.outputPath}`);
    console.log(`  Page Count: ${largeResult.pageCount}`);
    
    // 5. Analyze file sizes
    if (standardResult.outputPath && largeResult.outputPath) {
      const standardStats = fs.statSync(standardResult.outputPath);
      const largeStats = fs.statSync(largeResult.outputPath);
      
      console.log('\n=== File Size Comparison ===');
      console.log(`Standard PDF: ${(standardStats.size / 1024).toFixed(2)} KB`);
      console.log(`Large PDF: ${(largeStats.size / 1024).toFixed(2)} KB`);
      console.log(`Size increase: ${((largeStats.size / standardStats.size - 1) * 100).toFixed(1)}%`);
    }
    
    // 6. Check HTML for style differences
    const standardHtml = standardResult.outputPath?.replace('.pdf', '.html');
    const largeHtml = largeResult.outputPath?.replace('.pdf', '.html');
    
    if (standardHtml && fs.existsSync(standardHtml) && largeHtml && fs.existsSync(largeHtml)) {
      const standardContent = fs.readFileSync(standardHtml, 'utf-8');
      const largeContent = fs.readFileSync(largeHtml, 'utf-8');
      
      // Check font sizes
      const standardBodyFont = standardContent.match(/font-size:\s*(\d+pt)/)?.[1];
      const largeBodyFont = largeContent.match(/font-size:\s*(\d+pt)/)?.[1];
      
      console.log('\n=== Style Verification ===');
      console.log(`Standard body font: ${standardBodyFont || 'not found'}`);
      console.log(`Large body font: ${largeBodyFont || 'not found'}`);
      
      // Check margins
      const standardMargin = standardContent.match(/margin:\s*(\d+mm)/)?.[1];
      const largeMargin = largeContent.match(/margin:\s*(\d+mm)/)?.[1];
      
      console.log(`Standard margin: ${standardMargin || 'not found'}`);
      console.log(`Large margin: ${largeMargin || 'not found'}`);
    }
    
  } catch (error) {
    console.error('Test failed:', error);
  }
}

/**
 * Test large mode readability features
 */
async function testLargeModeFeatures(): Promise<void> {
  console.log('\n========== Test: Large Mode Specific Features ==========');
  
  try {
    const periodInput: PeriodDiaryInput = {
      startDate: '2026-03-01',
      durationType: '1m',
      birth: TEST_BIRTH
    };
    
    const periodData = await buildPeriodDiary(periodInput);
    const shortPeriod = {
      ...periodData,
      entries: periodData.entries.slice(0, 3), // Just 3 days for quick test
      endDate: '2026-03-03',
      totalDays: 3
    };
    
    console.log('Generating LARGE mode PDF with enhanced features...');
    const result = await renderPeriodDiaryPdf({
      period: shortPeriod,
      outputPath: path.join('./test_output', `test_large_features_${Date.now()}.pdf`),
      mode: 'large'
    });
    
    console.log('\n=== Large Mode Features ===');
    console.log('Expected improvements:');
    console.log('  ✓ Body font: 12pt+ (vs 10pt standard)');
    console.log('  ✓ Header font: 18pt+ (vs 14pt standard)');
    console.log('  ✓ Line height: 1.5+ (vs 1.3 standard)');
    console.log('  ✓ Margins: 15mm+ (vs 10mm standard)');
    console.log('  ✓ Checkbox size: 5mm+ (vs 3mm standard)');
    console.log('  ✓ Recording line height: 8mm+ (vs 5mm standard)');
    
    if (result.outputPath && fs.existsSync(result.outputPath)) {
      const stats = fs.statSync(result.outputPath);
      console.log(`\n✓ Large mode PDF created: ${(stats.size / 1024).toFixed(2)} KB`);
    }
    
  } catch (error) {
    console.error('Test failed:', error);
  }
}

// Main test runner
async function runTests(): Promise<void> {
  console.log('========================================');
  console.log('Large Mode Template Test Suite');
  console.log('========================================');
  
  try {
    // Create output directory
    const outputDir = './test_output';
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }
    
    // Run tests
    await testLargeModeComparison();
    await testLargeModeFeatures();
    
    console.log('\n========================================');
    console.log('All tests completed');
    console.log('Check ./test_output directory for PDFs');
    console.log('Compare standard vs large PDFs side-by-side');
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

export { runTests, testLargeModeComparison, testLargeModeFeatures };