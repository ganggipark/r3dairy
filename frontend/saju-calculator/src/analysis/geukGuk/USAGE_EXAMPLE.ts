/**
 * 종격(從格) 판단 로직 사용 예시
 * 
 * 이 파일은 checkJongGyeok 함수의 사용법을 보여주는 예시입니다.
 */

import type { GeukGukInput } from './index';
import { checkJongGyeok, determineGeukGuk } from './index';

// ============================================
// 예시 1: 종아격(從兒格) - 식상이 압도적
// ============================================
const jongAExample: GeukGukInput = {
  dayGan: '갑',      // 갑목 일간
  monthJi: '자',     // 자월
  fourPillarGan: ['병', '무', '갑', '정'],  // 년간, 월간, 일간, 시간
  fourPillarJi: ['오', '자', '사', '오'],   // 년지, 월지, 일지, 시지
};

const jongAResult = checkJongGyeok(jongAExample);
console.log('=== 종아격 예시 ===');
console.log('종격 여부:', jongAResult.isJongGyeok);
console.log('종격 타입:', jongAResult.jongGyeokType);
console.log('일간 강약:', jongAResult.dayMasterStrength);
console.log('압도적 오행:', jongAResult.dominantElement);
console.log('해석:', jongAResult.interpretation);

// ============================================
// 예시 2: 종재격(從財格) - 재성이 압도적
// ============================================
const jongJaeExample: GeukGukInput = {
  dayGan: '갑',      // 갑목 일간
  monthJi: '축',     // 축월
  fourPillarGan: ['무', '기', '갑', '기'],  // 년간, 월간, 일간, 시간
  fourPillarJi: ['술', '축', '술', '미'],   // 년지, 월지, 일지, 시지
};

const jongJaeResult = checkJongGyeok(jongJaeExample);
console.log('\n=== 종재격 예시 ===');
console.log('종격 여부:', jongJaeResult.isJongGyeok);
console.log('종격 타입:', jongJaeResult.jongGyeokType);
console.log('일간 강약:', jongJaeResult.dayMasterStrength);
console.log('압도적 오행:', jongJaeResult.dominantElement);
console.log('해석:', jongJaeResult.interpretation);

// ============================================
// 예시 3: 종관격(從官格) - 정관이 압도적
// ============================================
const jongGwanExample: GeukGukInput = {
  dayGan: '갑',      // 갑목 일간
  monthJi: '유',     // 유월
  fourPillarGan: ['신', '신', '갑', '신'],  // 년간, 월간, 일간, 시간
  fourPillarJi: ['유', '유', '사', '유'],   // 년지, 월지, 일지, 시지
};

const jongGwanResult = checkJongGyeok(jongGwanExample);
console.log('\n=== 종관격 예시 ===');
console.log('종격 여부:', jongGwanResult.isJongGyeok);
console.log('종격 타입:', jongGwanResult.jongGyeokType);
console.log('일간 강약:', jongGwanResult.dayMasterStrength);
console.log('압도적 오행:', jongGwanResult.dominantElement);
console.log('해석:', jongGwanResult.interpretation);

// ============================================
// 예시 4: 종살격(從殺格) - 편관이 압도적
// ============================================
const jongSalExample: GeukGukInput = {
  dayGan: '갑',      // 갑목 일간
  monthJi: '신',     // 신월
  fourPillarGan: ['경', '경', '갑', '경'],  // 년간, 월간, 일간, 시간
  fourPillarJi: ['신', '신', '오', '신'],   // 년지, 월지, 일지, 시지
};

const jongSalResult = checkJongGyeok(jongSalExample);
console.log('\n=== 종살격 예시 ===');
console.log('종격 여부:', jongSalResult.isJongGyeok);
console.log('종격 타입:', jongSalResult.jongGyeokType);
console.log('일간 강약:', jongSalResult.dayMasterStrength);
console.log('압도적 오행:', jongSalResult.dominantElement);
console.log('해석:', jongSalResult.interpretation);

// ============================================
// 예시 5: 종격 불성립 - 일간이 강함
// ============================================
const notJongExample: GeukGukInput = {
  dayGan: '갑',      // 갑목 일간
  monthJi: '인',     // 인월 (건록지)
  fourPillarGan: ['갑', '병', '갑', '을'],  // 년간, 월간, 일간, 시간
  fourPillarJi: ['인', '인', '묘', '인'],   // 년지, 월지, 일지, 시지
};

const notJongResult = checkJongGyeok(notJongExample);
console.log('\n=== 종격 불성립 예시 ===');
console.log('종격 여부:', notJongResult.isJongGyeok);
console.log('종격 타입:', notJongResult.jongGyeokType);
console.log('일간 강약:', notJongResult.dayMasterStrength);
console.log('압도적 오행:', notJongResult.dominantElement);
console.log('해석:', notJongResult.interpretation);

// ============================================
// 예시 6: 격국 전체 판단 (종격 자동 포함)
// ============================================
console.log('\n=== 격국 전체 판단 ===');

// 종아격 사주
const geukgukJongA = determineGeukGuk(jongAExample);
console.log('종아격 사주 → 격국:', geukgukJongA.geukguk);
console.log('설명:', geukgukJongA.description);

// 종재격 사주
const geukgukJongJae = determineGeukGuk(jongJaeExample);
console.log('\n종재격 사주 → 격국:', geukgukJongJae.geukguk);
console.log('설명:', geukgukJongJae.description);

// 종관격 사주
const geukgukJongGwan = determineGeukGuk(jongGwanExample);
console.log('\n종관격 사주 → 격국:', geukgukJongGwan.geukguk);
console.log('설명:', geukgukJongGwan.description);

// 종살격 사주
const geukgukJongSal = determineGeukGuk(jongSalExample);
console.log('\n종살격 사주 → 격국:', geukgukJongSal.geukguk);
console.log('설명:', geukgukJongSal.description);

// 건록격 사주 (종격 아님)
const geukgukGeonrok = determineGeukGuk(notJongExample);
console.log('\n건록격 사주 → 격국:', geukgukGeonrok.geukguk);
console.log('설명:', geukgukGeonrok.description);

/*
예상 출력:

=== 종아격 예시 ===
종격 여부: true
종격 타입: 종아격
일간 강약: extreme_weak
압도적 오행: 식상
해석: 일간이 무근무조하고 식상이 3개로 압도적이어서 종아격(從兒格)이 성립합니다.

=== 종재격 예시 ===
종격 여부: true
종격 타입: 종재격
일간 강약: extreme_weak
압도적 오행: 재성
해석: 일간이 무근무조하고 재성이 4개로 압도적이어서 종재격(從財格)이 성립합니다.

=== 종관격 예시 ===
종격 여부: true
종격 타입: 종관격
일간 강약: extreme_weak
압도적 오행: 정관
해석: 일간이 무근무조하고 정관이 4개로 압도적이어서 종관격(從官格)이 성립합니다.

=== 종살격 예시 ===
종격 여부: true
종격 타입: 종살격
일간 강약: extreme_weak
압도적 오행: 편관
해석: 일간이 무근무조하고 편관이 4개로 압도적이어서 종살격(從殺格)이 성립합니다.

=== 종격 불성립 예시 ===
종격 여부: false
종격 타입: null
일간 강약: strong
압도적 오행: null
해석: 일간이 무근무조가 아니므로 종격이 성립하지 않습니다.

=== 격국 전체 판단 ===
종아격 사주 → 격국: 종아격
설명: 일간이 무근무조하고 식상이 3개로 압도적이어서 종아격(從兒格)이 성립합니다.

종재격 사주 → 격국: 종재격
설명: 일간이 무근무조하고 재성이 4개로 압도적이어서 종재격(從財格)이 성립합니다.

종관격 사주 → 격국: 종관격
설명: 일간이 무근무조하고 정관이 4개로 압도적이어서 종관격(從官格)이 성립합니다.

종살격 사주 → 격국: 종살격
설명: 일간이 무근무조하고 편관이 4개로 압도적이어서 종살격(從殺格)이 성립합니다.

건록격 사주 → 격국: 건록격
설명: 갑일간이 인월(록지)에 태어나 건록격입니다.
*/
