/**
 * 화기격(化氣格) 사용 예시
 *
 * 이 파일은 화기격 판단 기능의 사용법을 보여줍니다.
 */

import { checkHwaGiGyeok, determineGeukGuk } from './index';
import type { GeukGukInput } from './index';
import type { CheonGan, JiJi } from '../../types/saju';

// ==========================================
// 예시 1: 갑기합토 화토격 (완전 성립)
// ==========================================

/**
 * 갑일간이 기월간과 합하여 토(土)로 화하고,
 * 진월(토왕절)에 태어나 진정한 화토격이 완전 성립하는 경우
 */
export function example1_HwaToGyeok_Complete() {
  const input: GeukGukInput = {
    dayGan: '갑' as CheonGan,
    monthJi: '진' as JiJi,
    fourPillarGan: ['병' as CheonGan, '기' as CheonGan, '갑' as CheonGan, '신' as CheonGan],
    fourPillarJi: ['인' as JiJi, '진' as JiJi, '오' as JiJi, '신' as JiJi],
  };

  const hwaGiResult = checkHwaGiGyeok(input);
  console.log('=== 화토격 완전 성립 예시 ===');
  console.log('화기격 여부:', hwaGiResult.isHwaGiGyeok);
  console.log('화기격 타입:', hwaGiResult.hwaGiGyeokType);
  console.log('합 조합:', hwaGiResult.combinationPair);
  console.log('변화된 오행:', hwaGiResult.transformedElement);
  console.log('완전 성립:', hwaGiResult.isComplete);
  console.log('해석:', hwaGiResult.interpretation);

  const geukguk = determineGeukGuk(input);
  console.log('최종 격국:', geukguk.geukguk);
  console.log('설명:', geukguk.description);
}

// ==========================================
// 예시 2: 을경합금 화금격 (완전 성립)
// ==========================================

/**
 * 을일간이 경월간과 합하여 금(金)으로 화하고,
 * 유월(금왕절)에 태어나 진정한 화금격이 완전 성립하는 경우
 */
export function example2_HwaGeumGyeok_Complete() {
  const input: GeukGukInput = {
    dayGan: '을' as CheonGan,
    monthJi: '유' as JiJi,
    fourPillarGan: ['무' as CheonGan, '경' as CheonGan, '을' as CheonGan, '임' as CheonGan],
    fourPillarJi: ['묘' as JiJi, '유' as JiJi, '해' as JiJi, '축' as JiJi],
  };

  const hwaGiResult = checkHwaGiGyeok(input);
  console.log('=== 화금격 완전 성립 예시 ===');
  console.log('화기격 타입:', hwaGiResult.hwaGiGyeokType);
  console.log('변화된 오행:', hwaGiResult.transformedElement);
  console.log('완전 성립:', hwaGiResult.isComplete);
  console.log('해석:', hwaGiResult.interpretation);
}

// ==========================================
// 예시 3: 갑기합토 (불완전 - 계절 불일치)
// ==========================================

/**
 * 갑일간이 기월간과 합하여 토(土)로 화하지만,
 * 자월(수왕절)에 태어나 계절이 맞지 않아 불완전한 경우
 */
export function example3_HwaToGyeok_Incomplete_Season() {
  const input: GeukGukInput = {
    dayGan: '갑' as CheonGan,
    monthJi: '자' as JiJi,
    fourPillarGan: ['병' as CheonGan, '기' as CheonGan, '갑' as CheonGan, '신' as CheonGan],
    fourPillarJi: ['인' as JiJi, '자' as JiJi, '오' as JiJi, '신' as JiJi],
  };

  const hwaGiResult = checkHwaGiGyeok(input);
  console.log('=== 화토격 불완전 (계절 불일치) 예시 ===');
  console.log('화기격 타입:', hwaGiResult.hwaGiGyeokType);
  console.log('완전 성립:', hwaGiResult.isComplete);  // false
  console.log('해석:', hwaGiResult.interpretation);    // "불완전" 포함
}

// ==========================================
// 예시 4: 갑기합토 (불완전 - 파격 요소)
// ==========================================

/**
 * 갑일간이 기월간과 합하여 토(土)로 화하고 진월(토왕절)이지만,
 * 년간 갑(목)이 토를 극하여 파격되는 경우
 */
export function example4_HwaToGyeok_Incomplete_Breaker() {
  const input: GeukGukInput = {
    dayGan: '갑' as CheonGan,
    monthJi: '진' as JiJi,
    fourPillarGan: ['갑' as CheonGan, '기' as CheonGan, '갑' as CheonGan, '병' as CheonGan],
    fourPillarJi: ['인' as JiJi, '진' as JiJi, '오' as JiJi, '신' as JiJi],
  };

  const hwaGiResult = checkHwaGiGyeok(input);
  console.log('=== 화토격 불완전 (파격 요소) 예시 ===');
  console.log('화기격 타입:', hwaGiResult.hwaGiGyeokType);
  console.log('완전 성립:', hwaGiResult.isComplete);  // false
  console.log('해석:', hwaGiResult.interpretation);    // "극하는 오행" 포함
}

// ==========================================
// 예시 5: 화기격 미성립
// ==========================================

/**
 * 일간과 월간/시간 사이에 천간합이 없어
 * 화기격이 성립하지 않는 경우
 */
export function example5_NoHwaGiGyeok() {
  const input: GeukGukInput = {
    dayGan: '갑' as CheonGan,
    monthJi: '인' as JiJi,
    fourPillarGan: ['병' as CheonGan, '을' as CheonGan, '갑' as CheonGan, '정' as CheonGan],
    fourPillarJi: ['인' as JiJi, '인' as JiJi, '오' as JiJi, '신' as JiJi],
  };

  const hwaGiResult = checkHwaGiGyeok(input);
  console.log('=== 화기격 미성립 예시 ===');
  console.log('화기격 여부:', hwaGiResult.isHwaGiGyeok);  // false
  console.log('해석:', hwaGiResult.interpretation);        // "천간합이 없어"

  // 화기격이 없으면 정격 판단으로 진행
  const geukguk = determineGeukGuk(input);
  console.log('정격 판단 결과:', geukguk.geukguk);  // 건록격 (갑일간 인월)
}

// ==========================================
// 예시 6: 시간 합을 통한 화기격
// ==========================================

/**
 * 월간과는 합이 없지만 시간과 합하여 화기격이 되는 경우
 * (월간 합보다 우선순위는 낮지만 성립 가능)
 */
export function example6_HourCombination() {
  const input: GeukGukInput = {
    dayGan: '병' as CheonGan,
    monthJi: '자' as JiJi,
    fourPillarGan: ['경' as CheonGan, '임' as CheonGan, '병' as CheonGan, '신' as CheonGan],
    fourPillarJi: ['진' as JiJi, '자' as JiJi, '인' as JiJi, '해' as JiJi],
  };

  const hwaGiResult = checkHwaGiGyeok(input);
  console.log('=== 시간 합 화수격 예시 ===');
  console.log('화기격 타입:', hwaGiResult.hwaGiGyeokType);  // 화수격
  console.log('합 조합:', hwaGiResult.combinationPair);      // [병, 신]
  console.log('완전 성립:', hwaGiResult.isComplete);         // true (자월은 수왕절)
  console.log('해석:', hwaGiResult.interpretation);          // "시간" 포함
}

// ==========================================
// 전체 실행 함수
// ==========================================

export function runAllExamples() {
  console.log('\n🔮 화기격(化氣格) 판단 예시 모음\n');

  example1_HwaToGyeok_Complete();
  console.log('\n' + '='.repeat(50) + '\n');

  example2_HwaGeumGyeok_Complete();
  console.log('\n' + '='.repeat(50) + '\n');

  example3_HwaToGyeok_Incomplete_Season();
  console.log('\n' + '='.repeat(50) + '\n');

  example4_HwaToGyeok_Incomplete_Breaker();
  console.log('\n' + '='.repeat(50) + '\n');

  example5_NoHwaGiGyeok();
  console.log('\n' + '='.repeat(50) + '\n');

  example6_HourCombination();
}

// 직접 실행 시 예시 출력
if (import.meta.url === `file://${process.argv[1]}`) {
  runAllExamples();
}
