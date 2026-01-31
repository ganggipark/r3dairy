/**
 * 양인살(羊刃煞) 계산 모듈
 *
 * 양인살 계산 원리:
 * - 양간(甲丙戊庚壬)의 제왕지(帝旺地)가 양인살
 * - 음간(乙丁己辛癸)은 양인살이 없음
 *
 * 양인살의 의미:
 * - 양인(羊刃)은 '양의 칼날'로, 날카롭고 강한 기운
 * - 성격이 과격하고 고집이 셈
 * - 긍정: 추진력, 결단력, 승부사 기질
 * - 부정: 성급함, 파괴적 성향, 부상/수술 위험
 */

import type { CheonGan, JiJi } from '../../types/saju';
import type { SinsalResult } from './types';

// 양간 목록 (양인살이 있는 일간)
const YANG_GAN: CheonGan[] = ['갑', '병', '무', '경', '임'];

// 음간 목록 (양인살이 없음)
const YIN_GAN: CheonGan[] = ['을', '정', '기', '신', '계'];

// 양인살 테이블: 양간 → 제왕지
const YANG_IN_SAL_TABLE: Partial<Record<CheonGan, JiJi>> = {
  '갑': '묘',  // 갑목의 제왕지 = 묘(卯)
  '병': '오',  // 병화의 제왕지 = 오(午)
  '무': '오',  // 무토의 제왕지 = 오(午) - 화토동법
  '경': '유',  // 경금의 제왕지 = 유(酉)
  '임': '자',  // 임수의 제왕지 = 자(子)
};

/**
 * 양인살 계산
 * @param dayGan 일간 (천간)
 * @returns 양인살 지지 또는 null (음간인 경우)
 */
export function calculateYangInSal(dayGan: CheonGan): JiJi | null {
  return YANG_IN_SAL_TABLE[dayGan] || null;
}

/**
 * 양인살 존재 여부 확인
 * @param dayGan 일간
 * @param targetJijis 사주의 모든 지지
 */
export function hasYangInSal(dayGan: CheonGan, targetJijis: JiJi[]): boolean {
  const yangInJi = calculateYangInSal(dayGan);
  if (!yangInJi) return false;
  return targetJijis.includes(yangInJi);
}

/**
 * 양인살 분석 결과 생성
 * @param dayGan 일간
 * @param targetJijis 사주의 모든 지지
 */
export function analyzeYangInSal(
  dayGan: CheonGan,
  targetJijis: JiJi[],
): SinsalResult | null {
  const yangInJi = calculateYangInSal(dayGan);

  // 음간은 양인살이 없음
  if (!yangInJi) {
    return null;
  }

  const present = targetJijis.includes(yangInJi);

  return {
    name: '양인살(羊刃煞)',
    type: 'yangInSal',
    present,
    triggerJiji: yangInJi,
    description: present
      ? '강한 추진력과 결단력, 과격한 성향 주의'
      : `양인살 지지(${yangInJi})가 사주에 없음`,
    effect: 'bad',
    detailedMeaning: present
      ? '양인살은 양의 칼날처럼 날카로운 기운입니다. 강한 추진력과 결단력을 가지며 승부사 기질이 있습니다. 그러나 성격이 급하고 과격할 수 있어, 충동적인 결정이나 다툼에 주의해야 합니다. 특히 부상이나 수술과 연관될 수 있으며, 칼이나 날카로운 물건을 다룰 때 조심해야 합니다.'
      : '양인살이 사주에 없어 해당 영향은 미미합니다.',
  };
}

/**
 * 양인살 설명 텍스트 생성
 */
export function getYangInSalDescription(dayGan: CheonGan): string {
  const yangInJi = calculateYangInSal(dayGan);

  if (!yangInJi) {
    return `${dayGan}일간은 음간으로 양인살이 적용되지 않습니다.`;
  }

  const descriptions: Record<CheonGan, string> = {
    '갑': '갑목(甲木) 일간의 양인살은 묘(卯)입니다. 목의 기운이 가장 왕성한 시기로, 봄의 강한 생명력을 나타냅니다.',
    '병': '병화(丙火) 일간의 양인살은 오(午)입니다. 화의 기운이 극에 달한 시기로, 여름의 뜨거운 태양을 상징합니다.',
    '무': '무토(戊土) 일간의 양인살은 오(午)입니다. 화토동법(火土同法)에 따라 화의 왕지에서 토도 힘을 받습니다.',
    '경': '경금(庚金) 일간의 양인살은 유(酉)입니다. 금의 기운이 가장 강한 시기로, 가을의 결실을 의미합니다.',
    '임': '임수(壬水) 일간의 양인살은 자(子)입니다. 수의 기운이 극대화된 시기로, 겨울의 깊은 물을 나타냅니다.',
    // 음간은 빈 문자열 반환
    '을': '', '정': '', '기': '', '신': '', '계': '',
  };

  return descriptions[dayGan] || '';
}

/**
 * 양인살 강도 분석
 * 양인이 여러 개 있거나, 대운/세운에서 만나는 경우 더 강함
 */
export function analyzeYangInSalStrength(
  dayGan: CheonGan,
  sajuJijis: JiJi[],
  currentYearJi?: JiJi,
  daeunJi?: JiJi,
): {
  strength: 'none' | 'weak' | 'normal' | 'strong' | 'very_strong';
  count: number;
  locations: string[];
  warning: string;
} {
  const yangInJi = calculateYangInSal(dayGan);

  if (!yangInJi) {
    return {
      strength: 'none',
      count: 0,
      locations: [],
      warning: '양인살 해당 없음 (음간)',
    };
  }

  let count = 0;
  const locations: string[] = [];

  // 사주 내 양인살 카운트
  const sajuPositions = ['년지', '월지', '일지', '시지'];
  sajuJijis.forEach((ji, index) => {
    if (ji === yangInJi) {
      count++;
      locations.push(sajuPositions[index]);
    }
  });

  // 세운에서 양인살
  if (currentYearJi && currentYearJi === yangInJi) {
    count++;
    locations.push('세운');
  }

  // 대운에서 양인살
  if (daeunJi && daeunJi === yangInJi) {
    count++;
    locations.push('대운');
  }

  // 강도 판정
  let strength: 'none' | 'weak' | 'normal' | 'strong' | 'very_strong';
  let warning: string;

  if (count === 0) {
    strength = 'none';
    warning = '양인살이 사주에 없어 해당 영향이 없습니다.';
  } else if (count === 1) {
    strength = 'weak';
    warning = '양인살이 1개 있어 적당한 추진력을 가집니다.';
  } else if (count === 2) {
    strength = 'normal';
    warning = '양인살이 2개로, 성급함이나 충동적 행동에 주의가 필요합니다.';
  } else if (count === 3) {
    strength = 'strong';
    warning = '양인살이 3개로 강하게 작용합니다. 다툼, 사고, 수술에 특히 주의하세요.';
  } else {
    strength = 'very_strong';
    warning = '양인살이 매우 강합니다. 안전사고, 과격한 행동, 법적 분쟁에 각별히 조심해야 합니다.';
  }

  return { strength, count, locations, warning };
}

export { YANG_GAN, YIN_GAN };
