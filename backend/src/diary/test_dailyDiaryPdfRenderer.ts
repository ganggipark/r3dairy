/**
 * 일일 다이어리 PDF 렌더러 테스트
 * 
 * DailyDiaryPdfRenderer 클래스를 테스트하고 실제 PDF 생성 검증
 */

import * as path from 'path';
import * as fs from 'fs';
import { buildDailyDiaryPayload } from './dailyDiaryBuilder';
import { renderDailyDiaryPdf, DailyDiaryPdfRenderer } from './dailyDiaryPdfRenderer';
import { DailyDiaryPayload } from './types';

// ============================================================
// 테스트 헬퍼 함수
// ============================================================

/**
 * 샘플 DailyDiaryPayload 생성
 */
function createSamplePayload(): DailyDiaryPayload {
  return {
    date: '2026-03-28',
    generatedAt: new Date().toISOString(),
    version: '1.0.0',
    calendar: {
      solarDate: '2026-03-28',
      weekday: '금',
      lunarDate: {
        year: 2026,
        month: 2,
        day: 15,
        isLeapMonth: false,
        displayText: '음력 2월 15일'
      },
      solarTerm: '춘분',
      specialDay: ''
    },
    leftPage: {
      sajuSummary: {
        mainCharacteristics: ['안정적', '신중함', '계획적', '집중력'],
        elementBalance: {
          wood: 3,
          fire: 2,
          earth: 2,
          metal: 1,
          water: 2
        },
        dayMasterStrength: 'balanced'
      },
      fortuneLayers: null,
      lifeAreas: {
        health: {
          score: 85,
          status: 'good',
          advice: '규칙적인 운동과 충분한 수면을 유지하세요'
        },
        wealth: {
          score: 72,
          status: 'good',
          advice: '재정 계획을 점검하고 불필요한 지출을 줄이세요'
        },
        relationship: {
          score: 88,
          status: 'excellent',
          advice: '주변 사람들과의 소통을 늘리고 감사 인사를 전하세요'
        },
        career: {
          score: 78,
          status: 'good',
          advice: '새로운 기술 습득이나 업무 효율화에 집중하세요'
        }
      },
      cautions: [
        '오후 3시-5시 사이에는 중요한 결정을 피하세요',
        '서쪽 방향으로의 이동이나 배치는 지양하세요',
        '감정적인 대화나 논쟁을 피하고 차분함을 유지하세요'
      ],
      recommendations: [
        '오전 9시-11시에 집중력이 필요한 업무를 진행하세요',
        '북쪽이나 동쪽 방향에서 중요한 회의를 갖세요',
        '정리정돈과 계획 수립에 시간을 투자하세요',
        '가까운 사람들과 진솔한 대화 시간을 가지세요'
      ]
    },
    rightPage: {
      timeSlots: [
        { time: '06:00', label: '06-08시', qimenLabel: '평', note: '' },
        { time: '08:00', label: '08-10시', qimenLabel: '길', note: '' },
        { time: '10:00', label: '10-12시', qimenLabel: '길', note: '' },
        { time: '12:00', label: '12-14시', qimenLabel: '평', note: '' },
        { time: '14:00', label: '14-16시', qimenLabel: '흉', note: '' },
        { time: '16:00', label: '16-18시', qimenLabel: '평', note: '' },
        { time: '18:00', label: '18-20시', qimenLabel: '길', note: '' },
        { time: '20:00', label: '20-22시', qimenLabel: '평', note: '' },
        { time: '22:00', label: '22-24시', qimenLabel: '평', note: '' }
      ],
      goodHours: ['08-10시', '10-12시', '18-20시'],
      badHours: ['14-16시'],
      goodDirections: ['북쪽', '동쪽'],
      badDirections: ['서쪽']
    },
    bottomPanel: {
      mindset: {
        focusEmotion: '차분함',
        cautionEmotion: '조급함',
        emotionTip: '호흡을 깊게 하고 마음의 중심을 잡으세요. 서두르지 말고 하나씩 차근차근 진행하는 것이 좋습니다.'
      },
      journalPrompt: [
        '오늘 가장 집중하고 싶은 일은 무엇인가요?',
        '어떤 감정 상태를 유지하고 싶나요?',
        '오늘 하루 후 어떤 성취감을 느끼고 싶나요?'
      ],
      affirmation: '나는 오늘 하루를 차분하고 계획적으로 보낼 수 있다. 모든 일이 순조롭게 풀려나갈 것이다.'
    },
    metadata: {
      generationMethod: 'realtime',
      cacheExpiry: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString()
    }
  };
}

/**
 * 파일 존재 여부 확인
 */
function fileExists(filePath: string): boolean {
  try {
    return fs.existsSync(filePath);
  } catch {
    return false;
  }
}

/**
 * 파일 크기 확인 (바이트)
 */
function getFileSize(filePath: string): number {
  try {
    const stats = fs.statSync(filePath);
    return stats.size;
  } catch {
    return 0;
  }
}

// ============================================================
// 테스트 케이스
// ============================================================

async function testBasicPdfGeneration() {
  console.log('='.repeat(70));
  console.log('테스트 1: 기본 PDF 생성');
  console.log('='.repeat(70));

  try {
    // 1. 샘플 페이로드 생성
    const payload = createSamplePayload();
    console.log(`✅ 샘플 페이로드 생성 완료 (${payload.date})`);

    // 2. PDF 렌더러 생성
    const renderer = new DailyDiaryPdfRenderer({
      outputDir: './test_output',
      filePrefix: 'test_diary_',
      quality: 'normal'
    });
    console.log('✅ PDF 렌더러 초기화 완료');

    // 3. PDF 생성
    const pdfPath = await renderer.renderToPdf(payload);
    console.log(`✅ PDF 생성 완료: ${pdfPath}`);

    // 4. 파일 검증
    if (fileExists(pdfPath)) {
      const fileSize = getFileSize(pdfPath);
      console.log(`✅ PDF 파일 확인 (크기: ${Math.round(fileSize / 1024)}KB)`);
      
      if (fileSize > 10000) { // 10KB 이상이면 정상
        console.log('✅ PDF 파일 크기 정상 (최소 10KB 이상)');
        return { success: true, path: pdfPath, size: fileSize };
      } else {
        console.log('⚠️ PDF 파일 크기가 작습니다 (10KB 미만)');
        return { success: false, error: 'File size too small' };
      }
    } else {
      console.log('❌ PDF 파일이 생성되지 않았습니다');
      return { success: false, error: 'File not created' };
    }

  } catch (error: any) {
    console.error('❌ 테스트 실패:', error);
    return { success: false, error: error.message };
  }
}

async function testBuilderIntegration() {
  console.log('\n' + '='.repeat(70));
  console.log('테스트 2: 빌더 통합 테스트');
  console.log('='.repeat(70));

  try {
    // 1. 다이어리 빌더로 페이로드 생성
    console.log('📅 빌더로 페이로드 생성 중...');
    const payload = await buildDailyDiaryPayload({
      date: '2026-03-28',
      birth: {
        year: 1971,
        month: 11,
        day: 17,
        hour: 4,
        minute: 0
      }
    });
    console.log('✅ 빌더로 페이로드 생성 완료');

    // 2. 메인 함수로 PDF 생성
    console.log('📄 PDF 렌더링 중...');
    const pdfPath = await renderDailyDiaryPdf(payload, {
      outputDir: './test_output',
      filePrefix: 'builder_diary_',
      quality: 'high'
    });
    console.log(`✅ PDF 생성 완료: ${pdfPath}`);

    // 3. 내용 검증
    console.log('\n📋 생성된 페이로드 내용:');
    console.log(`  - 날짜: ${payload.calendar.solarDate} (${payload.calendar.weekday})`);
    console.log(`  - 음력: ${payload.calendar.lunarDate?.displayText || 'N/A'}`);
    console.log(`  - 건강운: ${payload.leftPage.lifeAreas.health.score}점`);
    console.log(`  - 시간 슬롯: ${payload.rightPage.timeSlots.length}개`);
    console.log(`  - 마음가짐: ${payload.bottomPanel.mindset.focusEmotion}`);

    // 4. 파일 검증
    if (fileExists(pdfPath)) {
      const fileSize = getFileSize(pdfPath);
      console.log(`✅ PDF 파일 생성 성공 (크기: ${Math.round(fileSize / 1024)}KB)`);
      return { success: true, path: pdfPath, size: fileSize };
    } else {
      console.log('❌ PDF 파일 생성 실패');
      return { success: false, error: 'File not found after generation' };
    }

  } catch (error: any) {
    console.error('❌ 테스트 실패:', error);
    return { success: false, error: error.message };
  }
}

async function testErrorHandling() {
  console.log('\n' + '='.repeat(70));
  console.log('테스트 3: 오류 처리 테스트');
  console.log('='.repeat(70));

  try {
    // 1. 잘못된 날짜로 테스트
    console.log('📅 잘못된 날짜로 빌더 테스트...');
    
    try {
      await buildDailyDiaryPayload({
        date: '2026-13-45', // 잘못된 날짜
      });
      console.log('❌ 잘못된 날짜가 통과되었습니다 (오류)');
      return { success: false, error: 'Invalid date was accepted' };
    } catch (error) {
      console.log('✅ 잘못된 날짜 검증 정상 작동');
    }

    // 2. 빈 페이로드로 PDF 생성 시도
    console.log('📄 빈 페이로드로 PDF 생성 테스트...');
    
    const emptyPayload: any = {
      date: '2026-03-28',
      calendar: { solarDate: '2026-03-28', weekday: '금', lunarDate: null },
      leftPage: { sajuSummary: { mainCharacteristics: [], elementBalance: { wood: 0, fire: 0, earth: 0, metal: 0, water: 0 }, dayMasterStrength: 'balanced' }, fortuneLayers: null, lifeAreas: {}, cautions: [], recommendations: [] },
      rightPage: { timeSlots: [], goodHours: [], badHours: [], goodDirections: [], badDirections: [] },
      bottomPanel: { mindset: { focusEmotion: '', cautionEmotion: '', emotionTip: '' }, journalPrompt: [], affirmation: '' }
    };

    try {
      const pdfPath = await renderDailyDiaryPdf(emptyPayload, {
        outputDir: './test_output',
        filePrefix: 'empty_'
      });
      
      if (fileExists(pdfPath)) {
        console.log('✅ 빈 페이로드도 PDF 생성 가능 (기본값 적용)');
      } else {
        console.log('⚠️ 빈 페이로드로 PDF 생성 실패');
      }
      
    } catch (error: any) {
      console.log(`⚠️ 빈 페이로드 처리 중 오류: ${error.message}`);
    }

    console.log('✅ 오류 처리 테스트 완료');
    return { success: true };

  } catch (error: any) {
    console.error('❌ 오류 처리 테스트 실패:', error);
    return { success: false, error: error.message };
  }
}

async function testOutputFormats() {
  console.log('\n' + '='.repeat(70));
  console.log('테스트 4: 출력 형식 테스트');
  console.log('='.repeat(70));

  try {
    const payload = createSamplePayload();
    const results = [];

    // 1. 다양한 품질로 PDF 생성
    const qualities = ['draft', 'normal', 'high'];
    
    for (const quality of qualities) {
      console.log(`📄 ${quality} 품질로 PDF 생성 중...`);
      
      try {
        const pdfPath = await renderDailyDiaryPdf(payload, {
          outputDir: './test_output',
          filePrefix: `${quality}_diary_`,
          quality: quality as any
        });
        
        if (fileExists(pdfPath)) {
          const fileSize = getFileSize(pdfPath);
          console.log(`✅ ${quality} 품질 PDF 생성 성공 (크기: ${Math.round(fileSize / 1024)}KB)`);
          results.push({ quality, success: true, size: fileSize });
        } else {
          console.log(`❌ ${quality} 품질 PDF 생성 실패`);
          results.push({ quality, success: false });
        }
      } catch (error) {
        console.log(`❌ ${quality} 품질 PDF 생성 오류: ${(error as any).message}`);
        results.push({ quality, success: false, error: (error as any).message });
      }
    }

    // 2. 결과 요약
    const successCount = results.filter(r => r.success).length;
    console.log(`\n📊 품질별 테스트 결과: ${successCount}/${results.length} 성공`);
    
    results.forEach(result => {
      if (result.success) {
        console.log(`  ✅ ${result.quality}: ${Math.round(result.size! / 1024)}KB`);
      } else {
        console.log(`  ❌ ${result.quality}: 실패`);
      }
    });

    return { success: successCount > 0, results };

  } catch (error: any) {
    console.error('❌ 출력 형식 테스트 실패:', error);
    return { success: false, error: error.message };
  }
}

// ============================================================
// 메인 테스트 실행
// ============================================================

async function runAllTests() {
  console.log('\n');
  console.log('🚀 일일 다이어리 PDF 렌더러 테스트 시작');
  console.log('=' + '='.repeat(69));
  
  const results = [];
  
  try {
    // 각 테스트 실행
    results.push(await testBasicPdfGeneration());
    results.push(await testBuilderIntegration());
    results.push(await testErrorHandling());
    results.push(await testOutputFormats());
    
  } catch (error: any) {
    console.error('❌ 테스트 실행 중 치명적 오류:', error);
  }

  // 결과 요약
  console.log('\n' + '='.repeat(70));
  console.log('📊 테스트 결과 요약');
  console.log('=' + '='.repeat(69));
  
  const passed = results.filter(r => r && r.success).length;
  const failed = results.filter(r => !r || !r.success).length;
  
  console.log(`  ✅ 성공: ${passed}개`);
  console.log(`  ❌ 실패: ${failed}개`);
  console.log(`  📈 성공률: ${Math.round(passed / results.length * 100)}%`);
  
  if (failed === 0) {
    console.log('\n🎉 모든 테스트 통과!');
    console.log('📁 생성된 파일들은 ./test_output 디렉토리에서 확인하세요');
  } else {
    console.log('\n⚠️ 일부 테스트 실패');
    console.log('💡 WeasyPrint 설치 여부를 확인하고 Python 환경을 점검하세요');
  }
  
  process.exit(failed === 0 ? 0 : 1);
}

// 스크립트로 직접 실행시
if (require.main === module) {
  runAllTests().catch((error: any) => {
    console.error('테스트 실행 중 오류:', error);
    process.exit(1);
  });
}

export {
  testBasicPdfGeneration,
  testBuilderIntegration,
  testErrorHandling,
  testOutputFormats,
  createSamplePayload
};