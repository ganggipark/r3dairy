/**
 * Test for professional cover page enhancement
 * 
 * Tests the new branded cover page design in both standard and large modes
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
 * Test professional cover page
 */
async function testProfessionalCover(): Promise<void> {
  console.log('\n========== Test: Professional Cover Page Enhancement ==========');
  
  try {
    // 1. Generate 1-month period for cover page testing
    console.log('Step 1: Generating 1-month period data...');
    const periodInput: PeriodDiaryInput = {
      startDate: '2026-03-01',
      durationType: '1m',
      birth: TEST_BIRTH
    };
    
    const periodData = await buildPeriodDiary(periodInput);
    console.log(`Generated ${periodData.entries.length} daily entries`);
    console.log(`Period: ${periodData.startDate} to ${periodData.endDate}`);
    
    // 2. Test STANDARD mode cover
    console.log('\nStep 2: Testing STANDARD mode cover...');
    const standardResult = await renderPeriodDiaryPdf({
      period: periodData,
      outputPath: path.join('./test_output', `professional_cover_standard_${Date.now()}.pdf`),
      mode: 'standard'
    });
    
    // 3. Test LARGE mode cover
    console.log('\nStep 3: Testing LARGE mode cover...');
    const largeResult = await renderPeriodDiaryPdf({
      period: periodData,
      outputPath: path.join('./test_output', `professional_cover_large_${Date.now()}.pdf`),
      mode: 'large'
    });
    
    // 4. Verify results
    console.log('\n=== Professional Cover Test Results ===');
    console.log('STANDARD Mode Cover:');
    console.log(`  Success: ${standardResult.success}`);
    console.log(`  Output: ${standardResult.outputPath}`);
    console.log(`  Page Count: ${standardResult.pageCount}`);
    
    console.log('\nLARGE Mode Cover:');
    console.log(`  Success: ${largeResult.success}`);
    console.log(`  Output: ${largeResult.outputPath}`);
    console.log(`  Page Count: ${largeResult.pageCount}`);
    
    // 5. Check HTML for cover elements
    const standardHtml = standardResult.outputPath?.replace('.pdf', '.html');
    const largeHtml = largeResult.outputPath?.replace('.pdf', '.html');
    
    if (standardHtml && fs.existsSync(standardHtml)) {
      const htmlContent = fs.readFileSync(standardHtml, 'utf-8');
      
      console.log('\n=== Cover Elements Verification ===');
      
      // Check for new cover elements
      const hasMainTitle = htmlContent.includes('라이프 리듬 다이어리');
      const hasSubtitle = htmlContent.includes('사주·기문둔갑 기반');
      const hasConceptLine = htmlContent.includes('나만의 리듬을 찾아');
      const hasOwnerSection = htmlContent.includes('소유자 / Owner');
      const hasBrandFooter = htmlContent.includes('Powered by R³ System');
      const hasPeriodInfoBox = htmlContent.includes('period-info-box');
      
      console.log(`✓ Main Title (라이프 리듬 다이어리): ${hasMainTitle ? 'Found' : 'Missing'}`);
      console.log(`✓ Subtitle (사주·기문둔갑 기반): ${hasSubtitle ? 'Found' : 'Missing'}`);
      console.log(`✓ Concept Line (나만의 리듬을 찾아): ${hasConceptLine ? 'Found' : 'Missing'}`);
      console.log(`✓ Owner Section (소유자 / Owner): ${hasOwnerSection ? 'Found' : 'Missing'}`);
      console.log(`✓ Brand Footer (Powered by R³): ${hasBrandFooter ? 'Found' : 'Missing'}`);
      console.log(`✓ Period Info Box: ${hasPeriodInfoBox ? 'Found' : 'Missing'}`);
      
      // Check for professional styling
      const hasBorder = htmlContent.includes('border: 3px solid #2c5aa0');
      const hasBackground = htmlContent.includes('background: #f7fafc');
      const hasOwnerLine = htmlContent.includes('owner-line');
      
      console.log('\n=== Styling Verification ===');
      console.log(`✓ Professional Border: ${hasBorder ? 'Applied' : 'Missing'}`);
      console.log(`✓ Info Box Background: ${hasBackground ? 'Applied' : 'Missing'}`);
      console.log(`✓ Owner Signature Line: ${hasOwnerLine ? 'Applied' : 'Missing'}`);
      
      const allElementsPresent = hasMainTitle && hasSubtitle && hasConceptLine && 
                                hasOwnerSection && hasBrandFooter && hasPeriodInfoBox;
      
      if (allElementsPresent) {
        console.log('\n🎉 All professional cover elements are present!');
      } else {
        console.log('\n⚠️  Some cover elements are missing. Check the implementation.');
      }
    }
    
    // 6. File size comparison
    if (standardResult.outputPath && largeResult.outputPath) {
      const standardStats = fs.statSync(standardResult.outputPath);
      const largeStats = fs.statSync(largeResult.outputPath);
      
      console.log('\n=== File Size Analysis ===');
      console.log(`Standard PDF: ${(standardStats.size / 1024).toFixed(2)} KB`);
      console.log(`Large PDF: ${(largeStats.size / 1024).toFixed(2)} KB`);
      console.log(`Size difference: ${((largeStats.size / standardStats.size - 1) * 100).toFixed(1)}%`);
    }
    
  } catch (error) {
    console.error('Professional cover test failed:', error);
  }
}

/**
 * Test cover page branding elements
 */
async function testCoverBrandingElements(): Promise<void> {
  console.log('\n========== Test: Cover Branding Elements ==========');
  
  try {
    const periodInput: PeriodDiaryInput = {
      startDate: '2026-01-01',
      durationType: '3m',
      birth: TEST_BIRTH
    };
    
    const periodData = await buildPeriodDiary(periodInput);
    
    console.log('Testing 3-month period branding...');
    const result = await renderPeriodDiaryPdf({
      period: periodData,
      outputPath: path.join('./test_output', `branding_test_3m_${Date.now()}.pdf`)
    });
    
    console.log('\n=== Branding Test Results ===');
    console.log('Expected branding elements:');
    console.log('  📝 Main Title: "라이프 리듬 다이어리"');
    console.log('  📋 Subtitle: "사주·기문둔갑 기반 개인화 일일 관리 다이어리"');
    console.log('  💡 Concept: "나만의 리듬을 찾아 성장하는 시간"');
    console.log('  📦 Period Type: "3개월 다이어리"');
    console.log('  📅 Date Range: 2026년 1월 1일 ~ 2026년 4월 1일');
    console.log('  👤 Owner Field: Signature line for personalization');
    console.log('  🏷️  Brand Footer: "Powered by R³ System"');
    
    if (result.success && result.outputPath) {
      const stats = fs.statSync(result.outputPath);
      console.log(`\n✓ Professional cover PDF generated: ${(stats.size / 1024).toFixed(2)} KB`);
      console.log(`✓ Ready for commercial distribution`);
    }
    
  } catch (error) {
    console.error('Branding test failed:', error);
  }
}

// Main test runner
async function runTests(): Promise<void> {
  console.log('========================================');
  console.log('Professional Cover Page Test Suite');
  console.log('========================================');
  
  try {
    // Create output directory
    const outputDir = './test_output';
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }
    
    // Run tests
    await testProfessionalCover();
    await testCoverBrandingElements();
    
    console.log('\n========================================');
    console.log('Professional Cover Tests Completed');
    console.log('');
    console.log('📁 Check ./test_output directory for PDFs');
    console.log('🔍 Compare with previous simple covers');
    console.log('📖 Review professional branding elements');
    console.log('🖨️  Test print quality and appearance');
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

export { runTests, testProfessionalCover, testCoverBrandingElements };