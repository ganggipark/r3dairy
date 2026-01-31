/**
 * 대운(大運) 상세 분석 모듈
 *
 * 대운의 길흉 판단, 용신/기신 관계, 흐름 분석을 제공합니다.
 *
 * 대운 분석 원칙:
 * 1. 대운 천간: 상반기 5년 영향
 * 2. 대운 지지: 하반기 5년 영향
 * 3. 용신 대운: 최상의 시기
 * 4. 기신 대운: 주의가 필요한 시기
 */

import type { CheonGan, JiJi, OhHaeng } from '../sinsal/types';
import { SANG_SAENG, SANG_GEUK } from '../../core/index';

// ==================== 타입 정의 ====================

export type DaewoonQuality = 'excellent' | 'good' | 'neutral' | 'bad' | 'terrible';

export interface DaewoonQualityInput {
  dayGan: CheonGan;
  daewoonGan: CheonGan;
  daewoonJi: JiJi;
}

export interface DaewoonYongSinInput extends DaewoonQualityInput {
  yongSin: OhHaeng[];
  giSin: OhHaeng[];
}

export interface DaewoonFlowInput {
  daewoonGan: CheonGan;
  daewoonJi: JiJi;
  dayGan: CheonGan;
  startAge: number;
  endAge: number;
}

export interface DaewoonSummaryInput {
  currentDaewoon: {
    gan: CheonGan;
    ji: JiJi;
    ganJi: string;
    startAge: number;
    endAge: number;
  };
  nextDaewoon?: {
    gan: CheonGan;
    ji: JiJi;
    ganJi: string;
    startAge: number;
    endAge: number;
  };
  dayGan: CheonGan;
  yongSin: OhHaeng[];
  giSin: OhHaeng[];
  currentAge: number;
}

export interface ElementAnalysis {
  element: OhHaeng;
  relation: 'sangSaeng' | 'sangGeuk' | 'biHwa' | 'seolGi';
  description: string;
  effect: 'positive' | 'negative' | 'neutral';
}

export interface DaewoonAnalysisResult {
  quality: DaewoonQuality;
  score: number;
  ganAnalysis: ElementAnalysis;
  jiAnalysis: ElementAnalysis;
  interpretation: string;
}

export interface DaewoonYongSinResult extends DaewoonAnalysisResult {
  isYongSinDaewoon: boolean;
  isGiSinDaewoon: boolean;
  yongSinMatch: OhHaeng[];
  giSinMatch: OhHaeng[];
}

export interface HalfPeriodAnalysis {
  period: string;
  dominantElement: OhHaeng;
  relationToDay: string;
  quality: DaewoonQuality;
  advice: string;
}

export interface DaewoonFlowResult {
  firstHalf: HalfPeriodAnalysis;
  secondHalf: HalfPeriodAnalysis;
  combination: {
    analysis: string;
    synergy: 'good' | 'bad' | 'neutral';
  };
  overallAdvice: string;
}

// ==================== 상수 정의 ====================

const GAN_OH_HAENG: Record<CheonGan, OhHaeng> = {
  '갑': '목', '을': '목',
  '병': '화', '정': '화',
  '무': '토', '기': '토',
  '경': '금', '신': '금',
  '임': '수', '계': '수',
};

const JI_OH_HAENG: Record<JiJi, OhHaeng> = {
  '인': '목', '묘': '목',
  '사': '화', '오': '화',
  '진': '토', '술': '토', '축': '토', '미': '토',
  '신': '금', '유': '금',
  '해': '수', '자': '수',
};

// 오행 한글 설명
const OH_HAENG_NAME: Record<OhHaeng, string> = {
  '목': '목(木)',
  '화': '화(火)',
  '토': '토(土)',
  '금': '금(金)',
  '수': '수(水)',
};

// ==================== 핵심 함수 ====================

/**
 * 두 오행 간의 관계 분석
 * @param daewoonElement 대운 오행
 * @param dayElement 일간 오행
 */
function analyzeElementRelation(
  daewoonElement: OhHaeng,
  dayElement: OhHaeng,
): { relation: 'sangSaeng' | 'sangGeuk' | 'biHwa' | 'seolGi'; effect: 'positive' | 'negative' | 'neutral' } {
  // 같은 오행 (비화) - 힘이 되지만 경쟁도 있음
  if (daewoonElement === dayElement) {
    return { relation: 'biHwa', effect: 'neutral' };
  }

  // 대운이 일간을 생함 (상생 - 길)
  // 예: 대운 수(水) → 일간 목(木) = 수생목 = 좋음
  if (SANG_SAENG[daewoonElement] === dayElement) {
    return { relation: 'sangSaeng', effect: 'positive' };
  }

  // 일간이 대운을 생함 (설기 - 에너지 소모)
  // 예: 일간 목(木) → 대운 화(火) = 목생화 = 설기
  if (SANG_SAENG[dayElement] === daewoonElement) {
    return { relation: 'seolGi', effect: 'neutral' };
  }

  // 대운이 일간을 극함 (상극 - 흉)
  // 예: 대운 금(金) → 일간 목(木) = 금극목 = 나쁨
  if (SANG_GEUK[daewoonElement] === dayElement) {
    return { relation: 'sangGeuk', effect: 'negative' };
  }

  // 일간이 대운을 극함 (재성 - 에너지 소모지만 재물운)
  // 예: 일간 목(木) → 대운 토(土) = 목극토 = 중립
  if (SANG_GEUK[dayElement] === daewoonElement) {
    return { relation: 'sangGeuk', effect: 'neutral' };
  }

  return { relation: 'biHwa', effect: 'neutral' };
}

/**
 * 대운 천간/지지 분석
 */
function analyzeElement(
  elementType: 'gan' | 'ji',
  element: CheonGan | JiJi,
  dayGan: CheonGan,
): ElementAnalysis {
  const sourceOhHaeng = elementType === 'gan'
    ? GAN_OH_HAENG[element as CheonGan]
    : JI_OH_HAENG[element as JiJi];
  const dayOhHaeng = GAN_OH_HAENG[dayGan];

  const { relation, effect } = analyzeElementRelation(sourceOhHaeng, dayOhHaeng);

  let description = '';
  switch (relation) {
    case 'sangSaeng':
      description = `${OH_HAENG_NAME[sourceOhHaeng]}이 ${OH_HAENG_NAME[dayOhHaeng]}을 생하여 도움이 됩니다.`;
      break;
    case 'sangGeuk':
      description = effect === 'negative'
        ? `${OH_HAENG_NAME[sourceOhHaeng]}이 ${OH_HAENG_NAME[dayOhHaeng]}을 극하여 주의가 필요합니다.`
        : `${OH_HAENG_NAME[dayOhHaeng]}이 ${OH_HAENG_NAME[sourceOhHaeng]}을 극하여 에너지 소모가 있습니다.`;
      break;
    case 'biHwa':
      description = `${OH_HAENG_NAME[sourceOhHaeng]}과 ${OH_HAENG_NAME[dayOhHaeng]}이 같은 기운으로 힘이 됩니다.`;
      break;
    case 'seolGi':
      description = `${OH_HAENG_NAME[dayOhHaeng]}이 ${OH_HAENG_NAME[sourceOhHaeng]}을 생하여 에너지가 분산됩니다.`;
      break;
  }

  return {
    element: sourceOhHaeng,
    relation,
    description,
    effect,
  };
}

/**
 * 대운 종합 점수 계산
 * 점수 기준:
 * - 85+ : excellent (최상)
 * - 70+ : good (길)
 * - 45+ : neutral (보통)
 * - 25+ : bad (흉)
 * - 25미만 : terrible (최흉)
 */
function calculateDaewoonScore(
  ganAnalysis: ElementAnalysis,
  jiAnalysis: ElementAnalysis,
): number {
  const baseScore = 50;
  let score = baseScore;

  // 천간 영향 (60%) - 상반기 주도
  switch (ganAnalysis.relation) {
    case 'sangSaeng':
      score += 25; // 대운이 일간을 생함 → 길
      break;
    case 'sangGeuk':
      score += ganAnalysis.effect === 'negative' ? -20 : -5; // 대운이 극하면 흉, 내가 극하면 약간 소모
      break;
    case 'biHwa':
      score += 10; // 같은 오행 → 힘이 됨
      break;
    case 'seolGi':
      score += 0; // 내가 생해줌 → 에너지 소모
      break;
  }

  // 지지 영향 (40%) - 하반기 주도
  switch (jiAnalysis.relation) {
    case 'sangSaeng':
      score += 15; // 대운이 일간을 생함 → 길
      break;
    case 'sangGeuk':
      score += jiAnalysis.effect === 'negative' ? -12 : -3; // 대운이 극하면 흉
      break;
    case 'biHwa':
      score += 5; // 같은 오행 → 힘이 됨
      break;
    case 'seolGi':
      score += 0; // 내가 생해줌 → 에너지 소모
      break;
  }

  return Math.max(0, Math.min(100, score));
}

/**
 * 점수로 대운 품질 결정
 */
function determineQuality(score: number): DaewoonQuality {
  if (score >= 85) return 'excellent';
  if (score >= 70) return 'good';
  if (score >= 45) return 'neutral';
  if (score >= 25) return 'bad';
  return 'terrible';
}

// ==================== 공개 API ====================

/**
 * 대운 길흉 분석
 */
export function analyzeDaewoonQuality(input: DaewoonQualityInput): DaewoonAnalysisResult {
  const { dayGan, daewoonGan, daewoonJi } = input;

  const ganAnalysis = analyzeElement('gan', daewoonGan, dayGan);
  const jiAnalysis = analyzeElement('ji', daewoonJi, dayGan);

  const score = calculateDaewoonScore(ganAnalysis, jiAnalysis);
  const quality = determineQuality(score);

  // 해석 생성
  let interpretation = '';
  switch (quality) {
    case 'excellent':
      interpretation = '최상의 대운입니다. 하는 일마다 순조롭고 큰 발전이 기대됩니다.';
      break;
    case 'good':
      interpretation = '좋은 대운입니다. 노력한 만큼 결실을 거두는 시기입니다.';
      break;
    case 'neutral':
      interpretation = '평범한 대운입니다. 큰 변화 없이 안정적인 시기입니다.';
      break;
    case 'bad':
      interpretation = '주의가 필요한 대운입니다. 신중하게 행동하고 큰 결정은 미루세요.';
      break;
    case 'terrible':
      interpretation = '어려운 대운입니다. 건강과 재정 관리에 특히 주의하세요.';
      break;
  }

  return {
    quality,
    score,
    ganAnalysis,
    jiAnalysis,
    interpretation,
  };
}

/**
 * 용신/기신 관계를 고려한 대운 분석
 */
export function analyzeDaewoonWithYongSin(input: DaewoonYongSinInput): DaewoonYongSinResult {
  const { dayGan, daewoonGan, daewoonJi, yongSin, giSin } = input;

  // 기본 분석
  const baseResult = analyzeDaewoonQuality({ dayGan, daewoonGan, daewoonJi });

  const ganOhHaeng = GAN_OH_HAENG[daewoonGan];
  const jiOhHaeng = JI_OH_HAENG[daewoonJi];

  // 용신 매칭
  const yongSinMatch: OhHaeng[] = [];
  if (yongSin.includes(ganOhHaeng)) yongSinMatch.push(ganOhHaeng);
  if (yongSin.includes(jiOhHaeng) && !yongSinMatch.includes(jiOhHaeng)) yongSinMatch.push(jiOhHaeng);

  // 기신 매칭
  const giSinMatch: OhHaeng[] = [];
  if (giSin.includes(ganOhHaeng)) giSinMatch.push(ganOhHaeng);
  if (giSin.includes(jiOhHaeng) && !giSinMatch.includes(jiOhHaeng)) giSinMatch.push(jiOhHaeng);

  const isYongSinDaewoon = yongSinMatch.length > 0;
  const isGiSinDaewoon = giSinMatch.length > 0 && !isYongSinDaewoon;

  // 점수 조정
  let adjustedScore = baseResult.score;
  if (isYongSinDaewoon) {
    adjustedScore = Math.min(100, adjustedScore + 35);
  } else if (isGiSinDaewoon) {
    adjustedScore = Math.max(0, adjustedScore - 30);
  }

  const quality = isYongSinDaewoon
    ? 'excellent'
    : isGiSinDaewoon
    ? 'bad'
    : baseResult.quality;

  // 해석 업데이트
  let interpretation = baseResult.interpretation;
  if (isYongSinDaewoon) {
    interpretation = `용신(${yongSinMatch.join(', ')}) 대운으로 최상의 시기입니다. 적극적으로 기회를 잡으세요!`;
  } else if (isGiSinDaewoon) {
    interpretation = `기신(${giSinMatch.join(', ')}) 대운으로 주의가 필요한 시기입니다. 무리한 확장은 피하세요.`;
  }

  return {
    ...baseResult,
    quality,
    score: adjustedScore,
    interpretation,
    isYongSinDaewoon,
    isGiSinDaewoon,
    yongSinMatch,
    giSinMatch,
  };
}

/**
 * 대운 흐름 분석 (상반기/하반기)
 */
export function getDaewoonFlowAnalysis(input: DaewoonFlowInput): DaewoonFlowResult {
  const { daewoonGan, daewoonJi, dayGan, startAge, endAge } = input;

  const ganOhHaeng = GAN_OH_HAENG[daewoonGan];
  const jiOhHaeng = JI_OH_HAENG[daewoonJi];
  const dayOhHaeng = GAN_OH_HAENG[dayGan];

  const midAge = Math.floor((startAge + endAge) / 2);

  // 상반기 분석 (천간 위주)
  const firstHalfRelation = analyzeElementRelation(ganOhHaeng, dayOhHaeng);
  const firstHalf: HalfPeriodAnalysis = {
    period: `${startAge}-${midAge}세`,
    dominantElement: ganOhHaeng,
    relationToDay: `${OH_HAENG_NAME[ganOhHaeng]} → ${OH_HAENG_NAME[dayOhHaeng]}`,
    quality: determineQuality(calculateDaewoonScore(
      analyzeElement('gan', daewoonGan, dayGan),
      { element: ganOhHaeng, relation: 'biHwa', description: '', effect: 'neutral' },
    )),
    advice: firstHalfRelation.effect === 'positive'
      ? '적극적인 활동과 새로운 시작에 좋은 시기입니다.'
      : firstHalfRelation.effect === 'negative'
      ? '조심스럽게 행동하고 큰 변화는 피하세요.'
      : '안정적으로 현재 상태를 유지하세요.',
  };

  // 하반기 분석 (지지 위주)
  const secondHalfRelation = analyzeElementRelation(jiOhHaeng, dayOhHaeng);
  const secondHalf: HalfPeriodAnalysis = {
    period: `${midAge + 1}-${endAge}세`,
    dominantElement: jiOhHaeng,
    relationToDay: `${OH_HAENG_NAME[jiOhHaeng]} → ${OH_HAENG_NAME[dayOhHaeng]}`,
    quality: determineQuality(calculateDaewoonScore(
      { element: jiOhHaeng, relation: 'biHwa', description: '', effect: 'neutral' },
      analyzeElement('ji', daewoonJi, dayGan),
    )),
    advice: secondHalfRelation.effect === 'positive'
      ? '결실을 거두고 성과를 정리하는 시기입니다.'
      : secondHalfRelation.effect === 'negative'
      ? '건강과 인간관계에 주의하세요.'
      : '꾸준히 노력하면 좋은 결과가 있습니다.',
  };

  // 천간지지 조합 분석
  let combinationSynergy: 'good' | 'bad' | 'neutral' = 'neutral';
  let combinationAnalysis = `${OH_HAENG_NAME[ganOhHaeng]}과 ${OH_HAENG_NAME[jiOhHaeng]}의 조합입니다. `;

  if (ganOhHaeng === jiOhHaeng) {
    combinationSynergy = 'good';
    combinationAnalysis += '천간과 지지가 같은 오행으로 일관된 에너지가 흐릅니다.';
  } else if (SANG_SAENG[ganOhHaeng] === jiOhHaeng || SANG_SAENG[jiOhHaeng] === ganOhHaeng) {
    combinationSynergy = 'good';
    combinationAnalysis += '천간과 지지가 상생하여 좋은 흐름입니다.';
  } else if (SANG_GEUK[ganOhHaeng] === jiOhHaeng || SANG_GEUK[jiOhHaeng] === ganOhHaeng) {
    combinationSynergy = 'bad';
    combinationAnalysis += '천간과 지지가 상충하여 변동이 많을 수 있습니다.';
  } else {
    combinationAnalysis += '천간과 지지가 중립적인 관계입니다.';
  }

  const overallAdvice = combinationSynergy === 'good'
    ? '이 대운은 전반적으로 순탄하게 흘러갑니다.'
    : combinationSynergy === 'bad'
    ? '상반기와 하반기의 흐름이 다르니 유연하게 대처하세요.'
    : '평범하게 흘러가는 대운이니 꾸준함이 중요합니다.';

  return {
    firstHalf,
    secondHalf,
    combination: {
      analysis: combinationAnalysis,
      synergy: combinationSynergy,
    },
    overallAdvice,
  };
}

/**
 * AI용 대운 요약 텍스트 생성
 */
export function getDaewoonSummaryForAI(input: DaewoonSummaryInput): string {
  const { currentDaewoon, nextDaewoon, dayGan, yongSin, giSin, currentAge } = input;

  const currentAnalysis = analyzeDaewoonWithYongSin({
    dayGan,
    daewoonGan: currentDaewoon.gan,
    daewoonJi: currentDaewoon.ji,
    yongSin,
    giSin,
  });

  const lines: string[] = [];
  lines.push('【대운 분석】');
  lines.push('');

  // 현재 대운
  const remainingYears = currentDaewoon.endAge - currentAge + 1;
  lines.push(`▶ 현재 대운: ${currentDaewoon.ganJi} (${currentDaewoon.startAge}-${currentDaewoon.endAge}세)`);
  lines.push(`  현재 나이: ${currentAge}세 (남은 기간: ${remainingYears}년)`);
  lines.push(`  대운 점수: ${currentAnalysis.score}점`);

  if (currentAnalysis.isYongSinDaewoon) {
    lines.push(`  ★ 용신 대운: ${currentAnalysis.yongSinMatch.join(', ')} 오행이 용신과 일치합니다.`);
  } else if (currentAnalysis.isGiSinDaewoon) {
    lines.push(`  ⚠ 기신 대운: ${currentAnalysis.giSinMatch.join(', ')} 오행이 기신과 일치합니다.`);
  }
  lines.push(`  해석: ${currentAnalysis.interpretation}`);

  // 흐름 분석
  const flow = getDaewoonFlowAnalysis({
    daewoonGan: currentDaewoon.gan,
    daewoonJi: currentDaewoon.ji,
    dayGan,
    startAge: currentDaewoon.startAge,
    endAge: currentDaewoon.endAge,
  });

  lines.push('');
  lines.push('▶ 대운 흐름:');
  lines.push(`  상반기(${flow.firstHalf.period}): ${flow.firstHalf.dominantElement} 기운 - ${flow.firstHalf.advice}`);
  lines.push(`  하반기(${flow.secondHalf.period}): ${flow.secondHalf.dominantElement} 기운 - ${flow.secondHalf.advice}`);

  // 다음 대운
  if (nextDaewoon) {
    const nextAnalysis = analyzeDaewoonWithYongSin({
      dayGan,
      daewoonGan: nextDaewoon.gan,
      daewoonJi: nextDaewoon.ji,
      yongSin,
      giSin,
    });

    lines.push('');
    lines.push(`▶ 다음 대운: ${nextDaewoon.ganJi} (${nextDaewoon.startAge}-${nextDaewoon.endAge}세)`);
    lines.push(`  대운 점수: ${nextAnalysis.score}점`);

    if (nextAnalysis.isYongSinDaewoon) {
      lines.push('  ★ 용신 대운으로 좋은 시기가 옵니다.');
    } else if (nextAnalysis.isGiSinDaewoon) {
      lines.push('  ⚠ 기신 대운으로 준비가 필요합니다.');
    }
  }

  return lines.join('\n');
}

// ==================== 대운 시작 나이 계산 ====================

export type {
  DaeunStartAgeInput,
  DaeunStartAgeResult,
} from './daeunStartAge';

export {
  calculateDaeunStartAge,
  getSimpleDaeunStartAge,
} from './daeunStartAge';
