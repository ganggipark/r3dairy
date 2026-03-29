/**
 * 일일 다이어리 빌더 테스트
 */

import { buildDailyDiaryPayload } from './dailyDiaryBuilder';
import { DailyDiaryPayload } from './types';

// ============================================================
// 테스트 케이스
// ============================================================

async function testBasicGeneration() {
  console.log('='.repeat(70));
  console.log('테스트 1: 기본 다이어리 생성');
  console.log('='.repeat(70));
  
  try {
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
    
    console.log('\n✅ 생성 성공');
    console.log('\n📅 Calendar:');
    console.log(`  - 날짜: ${payload.calendar.solarDate}`);
    console.log(`  - 요일: ${payload.calendar.weekday}`);
    console.log(`  - 음력: ${payload.calendar.lunarDate?.displayText || 'N/A'}`);
    
    console.log('\n📄 Left Page:');
    console.log(`  - 사주 요약: ${payload.leftPage.sajuSummary.mainCharacteristics.join(', ')}`);
    console.log(`  - 건강운: ${payload.leftPage.lifeAreas.health.score}점 (${payload.leftPage.lifeAreas.health.status})`);
    console.log(`  - 재물운: ${payload.leftPage.lifeAreas.wealth.score}점 (${payload.leftPage.lifeAreas.wealth.status})`);
    console.log(`  - 주의사항: ${payload.leftPage.cautions.length}개`);
    console.log(`  - 권장사항: ${payload.leftPage.recommendations.length}개`);
    
    console.log('\n📄 Right Page:');
    console.log(`  - 시간 슬롯: ${payload.rightPage.timeSlots.length}개`);
    console.log(`  - 좋은 시간: ${payload.rightPage.goodHours.join(', ') || 'N/A'}`);
    console.log(`  - 나쁜 시간: ${payload.rightPage.badHours.join(', ') || 'N/A'}`);
    console.log(`  - 좋은 방향: ${payload.rightPage.goodDirections.join(', ') || 'N/A'}`);
    console.log(`  - 나쁜 방향: ${payload.rightPage.badDirections.join(', ') || 'N/A'}`);
    
    console.log('\n📝 Bottom Panel:');
    console.log(`  - 집중 감정: ${payload.bottomPanel.mindset.focusEmotion}`);
    console.log(`  - 주의 감정: ${payload.bottomPanel.mindset.cautionEmotion}`);
    console.log(`  - 일기 프롬프트: ${payload.bottomPanel.journalPrompt.length}개`);
    console.log(`  - 확언: ${payload.bottomPanel.affirmation.substring(0, 50)}...`);
    
    return true;
  } catch (error) {
    console.error('❌ 테스트 실패:', error);
    return false;
  }
}

async function testWithoutBirthInfo() {
  console.log('\n' + '='.repeat(70));
  console.log('테스트 2: 생년월일 없이 생성');
  console.log('='.repeat(70));
  
  try {
    const payload = await buildDailyDiaryPayload({
      date: '2026-03-28'
    });
    
    console.log('\n✅ 생성 성공 (기본값 사용)');
    console.log(`  - 날짜: ${payload.date}`);
    console.log(`  - 버전: ${payload.version}`);
    console.log(`  - 생성 방식: ${payload.metadata?.generationMethod}`);
    
    return true;
  } catch (error) {
    console.error('❌ 테스트 실패:', error);
    return false;
  }
}

async function testJsonStructure() {
  console.log('\n' + '='.repeat(70));
  console.log('테스트 3: JSON 구조 검증');
  console.log('='.repeat(70));
  
  try {
    const payload = await buildDailyDiaryPayload({
      date: '2026-03-28',
      birth: {
        year: 1990,
        month: 5,
        day: 15,
        hour: 14
      }
    });
    
    // 필수 필드 확인
    const requiredFields = ['date', 'calendar', 'leftPage', 'rightPage', 'bottomPanel'];
    const missingFields = requiredFields.filter(field => !(field in payload));
    
    if (missingFields.length > 0) {
      throw new Error(`Missing required fields: ${missingFields.join(', ')}`);
    }
    
    // Calendar 섹션 검증
    if (!payload.calendar.solarDate || !payload.calendar.weekday) {
      throw new Error('Calendar section is incomplete');
    }
    
    // LeftPage 섹션 검증
    if (!payload.leftPage.sajuSummary || !payload.leftPage.lifeAreas || !payload.leftPage.cautions || !payload.leftPage.recommendations) {
      throw new Error('LeftPage section is incomplete');
    }
    
    // RightPage 섹션 검증
    if (!payload.rightPage.timeSlots || !payload.rightPage.goodHours || !payload.rightPage.badHours || !payload.rightPage.goodDirections || !payload.rightPage.badDirections) {
      throw new Error('RightPage section is incomplete');
    }
    
    // BottomPanel 섹션 검증
    if (!payload.bottomPanel.mindset || !payload.bottomPanel.journalPrompt || !payload.bottomPanel.affirmation) {
      throw new Error('BottomPanel section is incomplete');
    }
    
    console.log('\n✅ JSON 구조 검증 성공');
    console.log('  - 모든 필수 필드 존재');
    console.log('  - Calendar 섹션 완전');
    console.log('  - LeftPage 섹션 완전');
    console.log('  - RightPage 섹션 완전');
    console.log('  - BottomPanel 섹션 완전');
    console.log(`  - TimeSlots 개수: ${payload.rightPage.timeSlots.length}개`);
    
    // JSON 샘플 출력
    console.log('\n📋 JSON 샘플 (처음 500자):');
    const jsonStr = JSON.stringify(payload, null, 2);
    console.log(jsonStr.substring(0, 500) + '...');
    
    return true;
  } catch (error) {
    console.error('❌ 테스트 실패:', error);
    return false;
  }
}

// ============================================================
// 메인 테스트 실행
// ============================================================

async function runAllTests() {
  console.log('\n');
  console.log('🚀 일일 다이어리 빌더 테스트 시작');
  console.log('=' + '='.repeat(69));
  
  const results = [];
  
  // 각 테스트 실행
  results.push(await testBasicGeneration());
  results.push(await testWithoutBirthInfo());
  results.push(await testJsonStructure());
  
  // 결과 요약
  console.log('\n' + '='.repeat(70));
  console.log('📊 테스트 결과 요약');
  console.log('=' + '='.repeat(69));
  
  const passed = results.filter(r => r).length;
  const failed = results.filter(r => !r).length;
  
  console.log(`  ✅ 성공: ${passed}개`);
  console.log(`  ❌ 실패: ${failed}개`);
  console.log(`  📈 성공률: ${Math.round(passed / results.length * 100)}%`);
  
  if (failed === 0) {
    console.log('\n🎉 모든 테스트 통과!');
  } else {
    console.log('\n⚠️ 일부 테스트 실패');
  }
  
  process.exit(failed === 0 ? 0 : 1);
}

// 스크립트로 직접 실행시
if (require.main === module) {
  runAllTests().catch(error => {
    console.error('테스트 실행 중 오류:', error);
    process.exit(1);
  });
}