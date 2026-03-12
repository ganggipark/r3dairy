/**
 * 신살(神煞) 통합 분석 모듈
 *
 * 이 모듈은 사주의 모든 신살을 종합적으로 분석합니다.
 * AI 챗에서 신살 관련 질문 시 이 모듈의 결과를 프롬프트에 전달합니다.
 */

import type { CheonGan, JiJi, SimpleSajuData } from '../../types/saju';
import type { SinsalAnalysis, SinsalResult } from './types';
import { getGapjaIndex } from '../../core/constants';

// 12신살 모듈
import {
  analyzeTwelveSinsal,
  calculateDoHwaSal,
  calculateYeokMaSal,
  calculateHwaGaeSal,
  SAMHAP_GROUP_MAP,
  SINSAL_INFO,
} from './twelveSinsal';

// 양인살 모듈
import {
  analyzeYangInSal,
  calculateYangInSal,
  analyzeYangInSalStrength,
} from './yangInSal';

// 귀문관살 모듈
import {
  analyzeGuiMunGwanSal,
  hasGuiMunGwanSal,
  isYukHap,
} from './guiMunGwanSal';

// 기타 신살 모듈
import {
  analyzeCheonEulGwiIn,
  analyzeMunChangGwiIn,
  analyzeHongYeomSal,
  analyzeBaekHoSal,
  analyzeHyeonChimSal,
  analyzeWonJinSal,
  calculateWonJinSal,
  analyzeSamJae,
  getSamJaeYears,
  isSamJaeYear,
} from './otherSinsal';

// 신살 해석 모듈
import {
  SINSAL_INTERPRETATIONS,
  getSinsalInterpretation,
  getSinsalByCategory,
  generateComprehensiveSinsalSummary,
} from './sinsalInterpretations';

import type { SinsalInterpretation } from './sinsalInterpretations';

// 타입 재export
export * from './types';
export type { SinsalInterpretation };

// 개별 함수 재export
export {
  // 12신살
  analyzeTwelveSinsal,
  calculateDoHwaSal,
  calculateYeokMaSal,
  calculateHwaGaeSal,
  SAMHAP_GROUP_MAP,
  SINSAL_INFO,
  // 양인살
  analyzeYangInSal,
  calculateYangInSal,
  analyzeYangInSalStrength,
  // 귀문관살
  analyzeGuiMunGwanSal,
  hasGuiMunGwanSal,
  isYukHap,
  // 기타 신살
  analyzeCheonEulGwiIn,
  analyzeMunChangGwiIn,
  analyzeHongYeomSal,
  analyzeBaekHoSal,
  analyzeHyeonChimSal,
  analyzeWonJinSal,
  calculateWonJinSal,
  analyzeSamJae,
  getSamJaeYears,
  isSamJaeYear,
  // 신살 해석
  SINSAL_INTERPRETATIONS,
  getSinsalInterpretation,
  getSinsalByCategory,
  generateComprehensiveSinsalSummary,
};

/**
 * 사주 전체 신살 분석
 * @param sajuData 사주 데이터
 * @param currentYearJi 현재 연도 지지 (세운 분석용)
 */
export function analyzeAllSinsal(
  sajuData: SimpleSajuData,
  _currentYearJi?: JiJi,
): SinsalAnalysis {
  // 사주에서 지지 추출
  const yearJi = sajuData.year.ji as JiJi;
  const monthJi = sajuData.month.ji as JiJi;
  const dayJi = sajuData.day.ji as JiJi;
  const hourJi = sajuData.time.ji as JiJi;
  const dayGan = sajuData.day.gan as CheonGan;

  const allJijis: JiJi[] = [yearJi, monthJi, dayJi, hourJi];
  const _allGans: CheonGan[] = [
    sajuData.year.gan as CheonGan,
    sajuData.month.gan as CheonGan,
    dayGan,
    sajuData.time.gan as CheonGan,
  ];

  // 12신살 분석 (년지 기준)
  const twelveSinsalByYear = analyzeTwelveSinsal(yearJi, allJijis);

  // 12신살 분석 (일지 기준)
  const twelveSinsalByDay = analyzeTwelveSinsal(dayJi, allJijis);

  // 양인살 분석
  const yangInSal = analyzeYangInSal(dayGan, allJijis);

  // 귀문관살 분석
  const guiMunGwanSal = analyzeGuiMunGwanSal(monthJi, dayJi, hourJi);

  // 천을귀인 분석
  const cheonEulGwiIn = analyzeCheonEulGwiIn(dayGan, allJijis);

  // 원진살 분석
  const wonJinSal = analyzeWonJinSal(dayJi, yearJi, monthJi, hourJi);

  // 공망 분석 (일주 60갑자 旬 기반)
  const gongMang = analyzeGongMang(dayGan, dayJi, allJijis);

  // 결과 분류
  const goodSinsal: string[] = [];
  const badSinsal: string[] = [];
  const neutralSinsal: string[] = [];

  // 12신살 (년지 기준) 분류
  twelveSinsalByYear.filter(s => s.present).forEach(s => {
    if (s.effect === 'good') goodSinsal.push(s.name);
    else if (s.effect === 'bad') badSinsal.push(s.name);
    else neutralSinsal.push(s.name);
  });

  // 기타 신살 분류
  if (yangInSal?.present) {
    badSinsal.push(yangInSal.name);
  }
  if (guiMunGwanSal?.present) {
    badSinsal.push(guiMunGwanSal.name);
  }
  if (wonJinSal?.present) {
    badSinsal.push(wonJinSal.name);
  }
  if (cheonEulGwiIn.present) {
    goodSinsal.push(cheonEulGwiIn.name);
  }
  if (gongMang?.present) {
    neutralSinsal.push(gongMang.name);
  }

  // AI용 요약 텍스트 생성
  const summaryText = generateSinsalSummary(
    twelveSinsalByYear,
    twelveSinsalByDay,
    yangInSal,
    guiMunGwanSal,
    wonJinSal,
    cheonEulGwiIn,
    gongMang,
    goodSinsal,
    badSinsal,
  );

  return {
    yearJiji: yearJi,
    dayJiji: dayJi,
    dayGan,
    twelveSinsalByYear,
    twelveSinsalByDay,
    yangInSal,
    guiMunGwanSal,
    wonJinSal,
    gongMang,
    cheonEulGwiIn,
    goodSinsal,
    badSinsal,
    neutralSinsal,
    summaryText,
  };
}

/**
 * 공망(空亡) 지지 계산 - 旬(순) 기반 정확한 알고리즘
 *
 * 60갑자는 6개의 旬(10일 주기)으로 나뉘며, 각 旬에서
 * 천간 10개와 짝을 이루지 못하는 지지 2개가 공망이 됩니다.
 *
 * 甲子旬 (index  0-9):  공망 = 술(戌), 해(亥)
 * 甲戌旬 (index 10-19): 공망 = 신(申), 유(酉)
 * 甲申旬 (index 20-29): 공망 = 오(午), 미(未)
 * 甲午旬 (index 30-39): 공망 = 진(辰), 사(巳)
 * 甲辰旬 (index 40-49): 공망 = 인(寅), 묘(卯)
 * 甲寅旬 (index 50-59): 공망 = 자(子), 축(丑)
 *
 * @param dayPillarIndex 일주의 60갑자 인덱스 (0-59)
 * @returns 공망에 해당하는 2개의 지지
 */
function getGongMangBranches(dayPillarIndex: number): JiJi[] {
  // 각 旬의 공망 지지 (旬 인덱스 0~5 순서)
  const GONG_MANG_BY_SUN: readonly (readonly [JiJi, JiJi])[] = [
    ['술', '해'], // 甲子旬 (index 0-9)
    ['신', '유'], // 甲戌旬 (index 10-19)
    ['오', '미'], // 甲申旬 (index 20-29)
    ['진', '사'], // 甲午旬 (index 30-39)
    ['인', '묘'], // 甲辰旬 (index 40-49)
    ['자', '축'], // 甲寅旬 (index 50-59)
  ];

  const sunIndex = Math.floor(dayPillarIndex / 10);
  return [...GONG_MANG_BY_SUN[sunIndex]];
}

/**
 * 공망 분석 - 일주(日柱)의 旬(순) 기반 정확한 계산
 *
 * 기존의 일간(dayGan) 단독 조회 방식은 부정확합니다.
 * 동일한 천간이라도 어떤 旬에 속하느냐에 따라 공망이 달라지므로,
 * 반드시 일주(천간+지지)의 60갑자 인덱스를 기준으로 계산해야 합니다.
 */
function analyzeGongMang(
  dayGan: CheonGan,
  dayJi: JiJi,
  allJijis: JiJi[],
): SinsalResult | null {
  // 일주의 60갑자 인덱스 계산 (간+지 조합으로 조회)
  const dayPillarGapja = `${dayGan}${dayJi}`;
  const dayPillarIndex = getGapjaIndex(dayPillarGapja);

  if (dayPillarIndex === -1) {
    // 유효하지 않은 간지 조합 (음양 불일치 등)
    return null;
  }

  const gongMangJijis = getGongMangBranches(dayPillarIndex);
  const foundGongMang = allJijis.filter(ji => gongMangJijis.includes(ji));
  const present = foundGongMang.length > 0;

  return {
    name: '공망(空亡)',
    type: 'gongMang',
    present,
    triggerJiji: foundGongMang[0],
    description: present
      ? `공망 지지(${foundGongMang.join(', ')})가 사주에 있음`
      : `공망 지지(${gongMangJijis.join(', ')})가 사주에 없음`,
    effect: 'neutral',
    detailedMeaning: present
      ? '공망은 비어있음을 의미합니다. 해당 지지의 작용이 약해지며, 물질적 성취보다 정신적 성장에 유리합니다. 종교, 철학, 예술 분야와 인연이 있습니다.'
      : '공망이 사주에 없어 일반적인 운세 흐름을 따릅니다.',
  };
}

/**
 * AI용 신살 요약 텍스트 생성
 */
function generateSinsalSummary(
  twelveSinsalByYear: SinsalResult[],
  twelveSinsalByDay: SinsalResult[],
  yangInSal: SinsalResult | null,
  guiMunGwanSal: SinsalResult | null,
  wonJinSal: SinsalResult | null,
  cheonEulGwiIn: SinsalResult,
  gongMang: SinsalResult | null,
  goodSinsal: string[],
  badSinsal: string[],
): string {
  const lines: string[] = [];

  lines.push('【신살 분석 결과】');
  lines.push('');

  // 길한 신살
  if (goodSinsal.length > 0) {
    lines.push(`▶ 길한 신살: ${goodSinsal.join(', ')}`);
    goodSinsal.forEach(name => {
      const sinsal = twelveSinsalByYear.find(s => s.name === name && s.present);
      if (sinsal) {
        lines.push(`  - ${sinsal.description}`);
      }
    });
    if (cheonEulGwiIn.present) {
      lines.push(`  - 천을귀인: ${cheonEulGwiIn.description}`);
    }
    lines.push('');
  }

  // 흉한 신살
  if (badSinsal.length > 0) {
    lines.push(`▶ 주의 신살: ${badSinsal.join(', ')}`);
    badSinsal.forEach(name => {
      const sinsal = twelveSinsalByYear.find(s => s.name === name && s.present);
      if (sinsal) {
        lines.push(`  - ${sinsal.description}`);
      }
    });
    if (yangInSal?.present) {
      lines.push(`  - 양인살: ${yangInSal.description}`);
    }
    if (guiMunGwanSal?.present) {
      lines.push(`  - 귀문관살: ${guiMunGwanSal.description}`);
    }
    if (wonJinSal?.present) {
      lines.push(`  - 원진살: ${wonJinSal.description}`);
    }
    lines.push('');
  }

  // 도화살 특별 언급
  const doHwa = twelveSinsalByYear.find(s => s.type === 'nyeonSal' && s.present);
  if (doHwa) {
    lines.push(`▶ 도화살(桃花煞): ${doHwa.detailedMeaning}`);
    lines.push('');
  }

  // 역마살 특별 언급
  const yeokMa = twelveSinsalByYear.find(s => s.type === 'yeokMaSal' && s.present);
  if (yeokMa) {
    lines.push(`▶ 역마살(驛馬煞): ${yeokMa.detailedMeaning}`);
    lines.push('');
  }

  // 화개살 특별 언급
  const hwaGae = twelveSinsalByYear.find(s => s.type === 'hwaGaeSal' && s.present);
  if (hwaGae) {
    lines.push(`▶ 화개살(華蓋煞): ${hwaGae.detailedMeaning}`);
    lines.push('');
  }

  if (goodSinsal.length === 0 && badSinsal.length === 0) {
    lines.push('특별히 강하게 작용하는 신살이 없습니다.');
  }

  return lines.join('\n');
}

/**
 * 특정 날짜의 신살 분석 (택일용)
 * @param date 분석할 날짜
 * @param dayPillar 해당 날짜의 일주
 * @param userSajuData 사용자 사주 데이터
 */
export function analyzeDateSinsal(
  date: Date,
  dayPillar: { gan: CheonGan; ji: JiJi },
  userSajuData: SimpleSajuData,
): {
  activeSinsal: SinsalResult[];
  isGoodDay: boolean;
  isBadDay: boolean;
  score: number;
  summary: string;
} {
  const userYearJi = userSajuData.year.ji as JiJi;
  const _userDayJi = userSajuData.day.ji as JiJi;
  const userDayGan = userSajuData.day.gan as CheonGan;

  const activeSinsal: SinsalResult[] = [];
  let goodCount = 0;
  let badCount = 0;

  // 1. 도화살 확인
  const doHwaJi = calculateDoHwaSal(userYearJi);
  if (dayPillar.ji === doHwaJi) {
    activeSinsal.push({
      name: '도화살일(桃花日)',
      type: 'nyeonSal',
      present: true,
      triggerJiji: doHwaJi,
      description: '이성운이 강한 날, 미팅/소개팅에 좋음',
      effect: 'neutral',
      detailedMeaning: '오늘은 도화살이 작용하는 날입니다. 이성에게 매력적으로 보이며, 새로운 만남에 유리합니다.',
    });
  }

  // 2. 역마살 확인
  const yeokMaJi = calculateYeokMaSal(userYearJi);
  if (dayPillar.ji === yeokMaJi) {
    activeSinsal.push({
      name: '역마살일(驛馬日)',
      type: 'yeokMaSal',
      present: true,
      triggerJiji: yeokMaJi,
      description: '이동, 여행, 변화에 좋은 날',
      effect: 'neutral',
      detailedMeaning: '오늘은 역마살이 작용하는 날입니다. 출장, 여행, 이사 등 움직임과 관련된 일에 좋습니다.',
    });
  }

  // 3. 양인살 확인
  const yangInJi = calculateYangInSal(userDayGan);
  if (yangInJi && dayPillar.ji === yangInJi) {
    activeSinsal.push({
      name: '양인살일(羊刃日)',
      type: 'yangInSal',
      present: true,
      triggerJiji: yangInJi,
      description: '충동적 결정, 다툼, 부상 주의',
      effect: 'bad',
      detailedMeaning: '오늘은 양인살이 작용합니다. 날카로운 기운이 강하니 충동적인 결정이나 다툼을 피하세요.',
    });
    badCount++;
  }

  // 4. 천을귀인 확인
  const cheonEulGwiInResult = analyzeCheonEulGwiIn(userDayGan, [dayPillar.ji]);
  if (cheonEulGwiInResult.present) {
    activeSinsal.push({
      ...cheonEulGwiInResult,
      name: '천을귀인일(天乙貴人日)',
      description: '귀인의 도움을 받기 좋은 날',
      detailedMeaning: '오늘은 천을귀인이 작용하는 날입니다. 중요한 만남, 면접, 협상에 좋습니다.',
    });
    goodCount++;
  }

  // 점수 계산 (기본 60점, 길신 +10, 흉신 -15)
  let score = 60;
  score += goodCount * 10;
  score -= badCount * 15;
  score = Math.max(20, Math.min(100, score));

  const isGoodDay = goodCount > badCount && score >= 70;
  const isBadDay = badCount > goodCount && score < 50;

  // 요약 생성
  let summary = '';
  if (activeSinsal.length === 0) {
    summary = '특별한 신살이 작용하지 않는 평범한 날입니다.';
  } else if (isGoodDay) {
    summary = `길한 신살(${activeSinsal.filter(s => s.effect === 'good').map(s => s.name).join(', ')})이 작용하여 좋은 날입니다.`;
  } else if (isBadDay) {
    summary = `주의 신살(${activeSinsal.filter(s => s.effect === 'bad').map(s => s.name).join(', ')})이 작용하여 조심해야 할 날입니다.`;
  } else {
    summary = `신살(${activeSinsal.map(s => s.name).join(', ')})이 작용하는 날입니다.`;
  }

  return {
    activeSinsal,
    isGoodDay,
    isBadDay,
    score,
    summary,
  };
}
