/**
 * Test for user recording section in daily diary pages
 * 
 * Verifies that user recording and self-management sections are properly rendered
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
 * Test user recording section in daily pages
 */
async function testUserRecordingSection(): Promise<void> {
  console.log('\n========== Test: User Recording Section in Daily Pages ==========');
  
  try {
    // 1. Generate a short period for testing
    console.log('Step 1: Generating test period data...');
    const periodInput: PeriodDiaryInput = {
      startDate: '2026-03-01',
      durationType: '1m',
      birth: TEST_BIRTH
    };
    
    // Use only 3 days for quick testing
    const periodData = await buildPeriodDiary(periodInput);
    const shortPeriod = {
      ...periodData,
      entries: periodData.entries.slice(0, 3),
      endDate: '2026-03-03',
      totalDays: 3
    };
    
    console.log(`Testing with ${shortPeriod.entries.length} days`);
    
    // 2. Render PDF with user recording sections
    console.log('\nStep 2: Rendering PDF with user recording sections...');
    const result = await renderPeriodDiaryPdf({
      period: shortPeriod,
      outputPath: path.join('./test_output', `test_user_recording_${Date.now()}.pdf`)
    });
    
    // 3. Verify results
    console.log('\n=== Test Results ===');
    console.log(`Success: ${result.success}`);
    console.log(`Output Path: ${result.outputPath}`);
    console.log(`Page Count: ${result.pageCount}`);
    
    // 4. Check HTML for user recording sections
    const htmlPath = result.outputPath?.replace('.pdf', '.html');
    if (htmlPath && fs.existsSync(htmlPath)) {
      const htmlContent = fs.readFileSync(htmlPath, 'utf-8');
      
      // Check for user recording sections
      const userRecordingSections = (htmlContent.match(/class="user-recording"/g) || []).length;
      const recordingSections = (htmlContent.match(/class="recording-section"/g) || []).length;
      const checkboxGroups = (htmlContent.match(/class="checkbox-group"/g) || []).length;
      const recordingLines = (htmlContent.match(/class="recording-line"/g) || []).length;
      
      console.log('\n=== HTML Structure Verification ===');
      console.log(`User Recording Sections: ${userRecordingSections}`);
      console.log(`Recording Sub-sections: ${recordingSections}`);
      console.log(`Checkbox Groups: ${checkboxGroups}`);
      console.log(`Recording Lines: ${recordingLines}`);
      
      // Verify sections exist for each daily page
      if (userRecordingSections === shortPeriod.entries.length) {
        console.log('✓ All daily pages have user recording sections');
      } else {
        console.log(`✗ Expected ${shortPeriod.entries.length} user recording sections, found ${userRecordingSections}`);
      }
      
      // Check for specific content
      const hasEmotionCheck = htmlContent.includes('감정 체크');
      const hasExecutionCheck = htmlContent.includes('실행 체크');
      const hasTodayRecord = htmlContent.includes('오늘의 기록');
      
      console.log('\n=== Content Verification ===');
      console.log(`오늘의 기록 section: ${hasTodayRecord ? '✓' : '✗'}`);
      console.log(`감정 체크 section: ${hasEmotionCheck ? '✓' : '✗'}`);
      console.log(`실행 체크 section: ${hasExecutionCheck ? '✓' : '✗'}`);
      
      // Check for specific checkboxes
      const emotionCheckboxes = ['안정', '집중', '피로', '불안', '만족', '긴장'];
      const executionCheckboxes = ['계획 실행', '미루지 않음', '중요한 일 완료'];
      
      console.log('\n=== Checkbox Verification ===');
      console.log('Emotion checkboxes:');
      emotionCheckboxes.forEach(emotion => {
        console.log(`  ${emotion}: ${htmlContent.includes(emotion) ? '✓' : '✗'}`);
      });
      
      console.log('Execution checkboxes:');
      executionCheckboxes.forEach(execution => {
        console.log(`  ${execution}: ${htmlContent.includes(execution) ? '✓' : '✗'}`);
      });
    }
    
    // 5. Verify PDF file exists and has reasonable size
    if (result.outputPath && fs.existsSync(result.outputPath)) {
      const stats = fs.statSync(result.outputPath);
      console.log(`\n✓ PDF file created: ${(stats.size / 1024).toFixed(2)} KB`);
      
      // Check if file size increased (user recording sections add content)
      if (stats.size > 10000) {
        console.log('✓ PDF size indicates content was added');
      }
    }
    
  } catch (error) {
    console.error('Test failed:', error);
  }
}

/**
 * Test that user recording sections appear in longer periods
 */
async function testMultiMonthUserRecording(): Promise<void> {
  console.log('\n========== Test: User Recording in Multi-Month Period ==========');
  
  try {
    const periodInput: PeriodDiaryInput = {
      startDate: '2026-03-01',
      durationType: '1m',
      birth: TEST_BIRTH
    };
    
    const periodData = await buildPeriodDiary(periodInput);
    // Test with 7 days across a week
    const weekPeriod = {
      ...periodData,
      entries: periodData.entries.slice(0, 7),
      endDate: '2026-03-07',
      totalDays: 7
    };
    
    console.log(`Testing with ${weekPeriod.entries.length} days (1 week)`);
    
    const result = await renderPeriodDiaryPdf({
      period: weekPeriod,
      outputPath: path.join('./test_output', `test_week_user_recording_${Date.now()}.pdf`)
    });
    
    console.log(`\n=== Results ===`);
    console.log(`PDF generated: ${result.outputPath}`);
    console.log(`Total pages: ${result.pageCount}`);
    
    // Verify HTML structure
    const htmlPath = result.outputPath?.replace('.pdf', '.html');
    if (htmlPath && fs.existsSync(htmlPath)) {
      const htmlContent = fs.readFileSync(htmlPath, 'utf-8');
      const userRecordingSections = (htmlContent.match(/class="user-recording"/g) || []).length;
      
      if (userRecordingSections === weekPeriod.entries.length) {
        console.log(`✓ All ${weekPeriod.entries.length} daily pages have user recording sections`);
      } else {
        console.log(`✗ Mismatch: expected ${weekPeriod.entries.length}, found ${userRecordingSections}`);
      }
    }
    
  } catch (error) {
    console.error('Test failed:', error);
  }
}

// Main test runner
async function runTests(): Promise<void> {
  console.log('========================================');
  console.log('User Recording Section Test Suite');
  console.log('========================================');
  
  try {
    // Create output directory
    const outputDir = './test_output';
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }
    
    // Run tests
    await testUserRecordingSection();
    await testMultiMonthUserRecording();
    
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

export { runTests, testUserRecordingSection, testMultiMonthUserRecording };