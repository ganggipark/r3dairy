/**
 * 귀문관살(鬼門關煞) 계산 모듈
 *
 * 귀문관살 계산 원리:
 * - 육합(六合) 관계의 지지가 인접하게 배치될 때 발생
 * - 월지-일지 또는 일지-시지가 육합 관계일 때
 *
 * 육합 조합:
 * - 子丑, 寅亥, 卯戌, 辰酉, 巳申, 午未
 *
 * 귀문관살의 의미:
 * - 귀신의 문을 지키는 살
 * - 영적 감수성이 높음
 * - 악몽, 환각, 불안감
 * - 어린 시절 건강 주의
 */

import type { JiJi } from '../../types/saju';
import type { SinsalResult } from './types';

// 육합 테이블
const YUK_HAP_TABLE: Record<JiJi, JiJi> = {
  '자': '축', '축': '자',
  '인': '해', '해': '인',
  '묘': '술', '술': '묘',
  '진': '유', '유': '진',
  '사': '신', '신': '사',
  '오': '미', '미': '오',
};

/**
 * 두 지지가 육합 관계인지 확인
 */
export function isYukHap(ji1: JiJi, ji2: JiJi): boolean {
  return YUK_HAP_TABLE[ji1] === ji2;
}

/**
 * 귀문관살 확인
 * 월지-일지 또는 일지-시지가 육합 관계일 때 발생
 *
 * @param monthJi 월지
 * @param dayJi 일지
 * @param hourJi 시지
 */
export function hasGuiMunGwanSal(
  monthJi: JiJi,
  dayJi: JiJi,
  hourJi: JiJi,
): { present: boolean; location: 'monthDay' | 'dayHour' | null } {
  // 월지-일지 육합 확인
  if (isYukHap(monthJi, dayJi)) {
    return { present: true, location: 'monthDay' };
  }

  // 일지-시지 육합 확인
  if (isYukHap(dayJi, hourJi)) {
    return { present: true, location: 'dayHour' };
  }

  return { present: false, location: null };
}

/**
 * 귀문관살 분석 결과 생성
 */
export function analyzeGuiMunGwanSal(
  monthJi: JiJi,
  dayJi: JiJi,
  hourJi: JiJi,
): SinsalResult | null {
  const result = hasGuiMunGwanSal(monthJi, dayJi, hourJi);

  if (!result.present) {
    return null;
  }

  const locationText = result.location === 'monthDay'
    ? `월지(${monthJi})-일지(${dayJi})`
    : `일지(${dayJi})-시지(${hourJi})`;

  return {
    name: '귀문관살(鬼門關煞)',
    type: 'guiMunGwanSal',
    present: true,
    description: `${locationText}이 육합으로 귀문관살 형성`,
    effect: 'bad',
    detailedMeaning: `귀문관살은 귀신의 문을 지키는 살로, ${locationText}이 육합 관계를 이루어 형성되었습니다. 영적 감수성이 높아 직관력이 뛰어나지만, 악몽이나 불안감을 느끼기 쉽습니다. 어린 시절 건강에 특히 주의가 필요하며, 밤에 혼자 다니거나 어두운 곳을 피하는 것이 좋습니다. 종교나 명상을 통해 마음의 안정을 찾으면 긍정적으로 전환할 수 있습니다.`,
  };
}

/**
 * 귀문관살 상세 설명
 */
export function getGuiMunGwanSalDescription(): string {
  return `
귀문관살(鬼門關煞)은 육합 지지가 인접하여 배치될 때 형성됩니다.

【육합 조합】
- 子丑(자축) - 土로 합화
- 寅亥(인해) - 木으로 합화
- 卯戌(묘술) - 火로 합화
- 辰酉(진유) - 金으로 합화
- 巳申(사신) - 水로 합화
- 午未(오미) - 火로 합화

【귀문관살의 특징】
- 영적 감수성과 직관력이 높음
- 예지몽이나 신비 체험 가능
- 불안, 공포, 악몽 경향
- 어린이의 경우 경기(驚氣) 주의
- 밤에 혼자 있는 것을 두려워함

【해소 방법】
- 종교 활동이나 명상
- 밝고 양기 있는 환경 유지
- 규칙적인 생활 패턴
- 영적 능력을 긍정적으로 활용 (상담, 예술)
`.trim();
}

/**
 * 특정 날짜가 귀문관살과 연관되는지 확인
 * (택일에서 사용)
 */
export function isDayRelatedToGuiMunGwan(
  dayJi: JiJi,
  personMonthJi: JiJi,
  personDayJi: JiJi,
): boolean {
  // 해당 일의 일지가 본인 월지나 일지와 육합을 이루면 주의
  return isYukHap(dayJi, personMonthJi) || isYukHap(dayJi, personDayJi);
}

export { YUK_HAP_TABLE };
