import { buildPeriodDiary } from './periodDiaryGenerator';
import { renderPeriodDiaryPdf } from './periodDiaryPdfRenderer';

async function quickTest() {
  console.log('Starting quick reflection test...');
  
  const period = await buildPeriodDiary({
    startDate: '2026-03-01',
    durationType: '1m',
    birth: {
      year: 1971, month: 11, day: 17, hour: 4, minute: 0,
      isLunar: false as const, birthPlace: '서울'
    }
  });
  
  // Test with exactly 14 days
  const twoWeeks = {
    ...period,
    entries: period.entries.slice(0, 14),
    endDate: '2026-03-14',
    totalDays: 14
  };
  
  console.log('Rendering PDF for 14 days...');
  const result = await renderPeriodDiaryPdf({
    period: twoWeeks,
    outputPath: './test_output/quick_reflection_test.pdf'
  });
  
  console.log('=== Results ===');
  console.log('Pages:', result.pageCount);
  console.log('Output:', result.outputPath);
  console.log('Success:', result.success);
  
  // Check if HTML exists
  const fs = require('fs');
  const htmlPath = result.outputPath?.replace('.pdf', '.html');
  if (htmlPath && fs.existsSync(htmlPath)) {
    const html = fs.readFileSync(htmlPath, 'utf-8');
    const reflections = (html.match(/class="weekly-reflection"/g) || []).length;
    const summaries = (html.match(/class="weekly-summary"/g) || []).length;
    
    console.log('\n=== HTML Analysis ===');
    console.log('Weekly summaries:', summaries);
    console.log('Weekly reflections:', reflections);
    
    // Expected: 1 cover + 1 index + 1 month divider + 2 summaries + 2 reflections + 14 daily = 21
    const expected = 1 + 1 + 1 + 2 + 2 + 14;
    console.log('\nExpected pages:', expected);
    console.log('Actual pages:', result.pageCount);
    console.log('Match:', result.pageCount === expected ? '✓' : '✗');
  }
}

quickTest().catch(console.error);