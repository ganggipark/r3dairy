/**
 * 용신/기신(用神/忌神) 계산 모듈
 *
 * 용신(用神): 사주에서 필요로 하는 오행, 일간을 돕거나 균형을 맞추는 역할
 * 기신(忌神): 사주에서 해로운 오행, 일간에 불리하게 작용
 *
 * 억부법(抑扶法) 원리:
 * - 신강(身强)이면 설기(泄氣)/극제(剋制)가 필요 → 식상, 재성, 관성이 용신
 * - 신약(身弱)이면 생조(生助)가 필요 → 인성, 비겁이 용신
 *
 * 조후법(調候法) 원리:
 * - 계절에 따른 한난조습(寒暖燥濕) 조절
 * - 겨울생은 따뜻한 오행(화, 목), 여름생은 시원한 오행(수, 금) 필요
 */

import type { CheonGan, JiJi, OhHaeng } from '../sinsal/types';
import type { FourPillars } from '../core/types';

// 신강/신약 등급 타입
export type BodyStrengthGrade = '극신강' | '신강' | '중화' | '신약' | '극신약';

// 십성 카테고리 타입
export type SipSungCategory = '비겁' | '식상' | '재성' | '관성' | '인성';

// 조후 필요성 타입
export type JohuNecessity = '높음' | '중간' | '낮음';

// 오행 관계 타입
export interface OhHaengRelation {
  생: OhHaeng; // 내가 생하는 오행
  극: OhHaeng; // 내가 극하는 오행
  피생: OhHaeng; // 나를 생하는 오행
  피극: OhHaeng; // 나를 극하는 오행
  비: OhHaeng; // 나와 같은 오행
}

// 용신 입력 타입
export interface YongSinInput {
  dayGan: CheonGan;
  monthJi: JiJi;
  bodyStrength: BodyStrengthGrade;
  fourPillars: FourPillars;
  geukGuk?: string; // 종격일 경우
}

// 억부법 결과 타입
export interface EokBuResult {
  yongSinCategory: SipSungCategory[];
  yongSinOhHaeng: OhHaeng[];
  giSinCategory: SipSungCategory[];
  giSinOhHaeng: OhHaeng[];
  isBalanced: boolean;
}

// 조후법 결과 타입
export interface JohuResult {
  johuYongSin: OhHaeng[];
  johuNecessity: JohuNecessity;
  reason: string;
}

// 기신 결과 타입
export interface GiSinResult {
  giSinCategory: SipSungCategory[];
  giSinOhHaeng: OhHaeng[];
  mostHarmful: SipSungCategory;
  mostHarmfulOhHaeng: OhHaeng;
}

// 용신 결과 타입
export interface YongSinResult {
  primaryYongSin: OhHaeng[];
  johuYongSin: OhHaeng[];
  yongSinHarmony: '일치' | '불일치' | '부분일치';
  mediatingYongSin?: OhHaeng[]; // 통관용신
}

// 통관용신 결과 타입
export interface MediatingYongSinResult {
  hasMediatingNeed: boolean;
  mediatingElement?: OhHaeng;
  conflictingElements?: [OhHaeng, OhHaeng];
  reason?: string;
}

// 실용 정보 타입
export interface PracticalInfo {
  colors: string[];
  directions: string[];
  numbers: number[];
  avoid: {
    colors: string[];
    directions: string[];
    numbers: number[];
  };
}

// 종합 분석 결과 타입
export interface YongSinAnalysis {
  dayGan: CheonGan;
  dayGanOhHaeng: OhHaeng;
  bodyStrength: BodyStrengthGrade;
  isBalanced: boolean;
  yongSin: {
    primary: OhHaeng[];
    category: SipSungCategory[];
  };
  giSin: {
    primary: OhHaeng[];
    category: SipSungCategory[];
  };
  johu: {
    yongSin: OhHaeng[];
    necessity: JohuNecessity;
    reason: string;
  };
  mediating?: {
    // 통관용신
    yongSin: OhHaeng[];
    conflictingElements?: [OhHaeng, OhHaeng];
    reason: string;
  };
  specialYongSin?: OhHaeng; // 종격일 경우
  recommendation: string;
  practical: PracticalInfo;
}

// 오행 관계표
export const OHAENG_RELATIONSHIP: Record<OhHaeng, OhHaengRelation> = {
  목: { 생: '화', 극: '토', 피생: '수', 피극: '금', 비: '목' },
  화: { 생: '토', 극: '금', 피생: '목', 피극: '수', 비: '화' },
  토: { 생: '금', 극: '수', 피생: '화', 피극: '목', 비: '토' },
  금: { 생: '수', 극: '목', 피생: '토', 피극: '화', 비: '금' },
  수: { 생: '목', 극: '화', 피생: '금', 피극: '토', 비: '수' },
};

// 십성과 오행 관계 (카테고리화)
export const SIPSUNG_TO_OHAENG: Record<string, string> = {
  비견: '비',
  겁재: '비',
  식신: '식상',
  상관: '식상',
  편재: '재성',
  정재: '재성',
  편관: '관성',
  정관: '관성',
  편인: '인성',
  정인: '인성',
};

// 천간 → 오행 매핑
const CHEONGAN_OHAENG: Record<CheonGan, OhHaeng> = {
  갑: '목',
  을: '목',
  병: '화',
  정: '화',
  무: '토',
  기: '토',
  경: '금',
  신: '금',
  임: '수',
  계: '수',
};

// 지지 → 계절 매핑
const JIJI_SEASON: Record<JiJi, string> = {
  인: '봄',
  묘: '봄',
  진: '봄',
  사: '여름',
  오: '여름',
  미: '여름',
  신: '가을',
  유: '가을',
  술: '가을',
  해: '겨울',
  자: '겨울',
  축: '겨울',
};

// 오행 → 색상 매핑
const OHAENG_COLOR: Record<OhHaeng, string[]> = {
  목: ['초록', '청색', '녹색'],
  화: ['빨강', '주황', '분홍'],
  토: ['노랑', '갈색', '베이지'],
  금: ['흰색', '은색', '금색'],
  수: ['검정', '파랑', '남색'],
};

// 오행 → 방위 매핑
const OHAENG_DIRECTION: Record<OhHaeng, string[]> = {
  목: ['동쪽'],
  화: ['남쪽'],
  토: ['중앙'],
  금: ['서쪽'],
  수: ['북쪽'],
};

// 오행 → 숫자 매핑
const OHAENG_NUMBER: Record<OhHaeng, number[]> = {
  목: [3, 8],
  화: [2, 7],
  토: [5, 10],
  금: [4, 9],
  수: [1, 6],
};

// 통관용신 매핑 (오행 충돌 시 중재 오행)
// 목-토 conflict → 화 (wood→fire→earth)
// 화-금 conflict → 토 (fire→earth→metal)
// 토-수 conflict → 금 (earth→metal→water)
// 금-목 conflict → 수 (metal→water→wood)
// 수-화 conflict → 목 (water→wood→fire)
const MEDIATING_ELEMENT_MAP: Record<string, OhHaeng> = {
  '목-토': '화',
  '토-목': '화',
  '화-금': '토',
  '금-화': '토',
  '토-수': '금',
  '수-토': '금',
  '금-목': '수',
  '목-금': '수',
  '수-화': '목',
  '화-수': '목',
};

/**
 * 일간의 오행 반환
 */
function getDayGanOhHaeng(dayGan: CheonGan): OhHaeng {
  return CHEONGAN_OHAENG[dayGan];
}

/**
 * 지지의 오행 반환 (장간 무시, 본기만 고려)
 */
function getJiJiOhHaeng(jiJi: JiJi): OhHaeng {
  const jiJiOhHaeng: Record<JiJi, OhHaeng> = {
    인: '목',
    묘: '목',
    진: '토',
    사: '화',
    오: '화',
    미: '토',
    신: '금',
    유: '금',
    술: '토',
    해: '수',
    자: '수',
    축: '토',
  };
  return jiJiOhHaeng[jiJi];
}

/**
 * 사주에서 오행 분포를 계산 (천간과 지지 포함)
 */
function countOhHaengInFourPillars(fourPillars: FourPillars): Record<OhHaeng, number> {
  const count: Record<OhHaeng, number> = {
    목: 0,
    화: 0,
    토: 0,
    금: 0,
    수: 0,
  };

  // 천간 카운트
  [fourPillars.year.gan, fourPillars.month.gan, fourPillars.day.gan, fourPillars.time.gan].forEach(
    (gan) => {
      const oh = CHEONGAN_OHAENG[gan];
      count[oh]++;
    },
  );

  // 지지 카운트
  [fourPillars.year.ji, fourPillars.month.ji, fourPillars.day.ji, fourPillars.time.ji].forEach(
    (ji) => {
      const oh = getJiJiOhHaeng(ji);
      count[oh]++;
    },
  );

  return count;
}

/**
 * 일간 기준 특정 십성 카테고리의 오행 반환
 */
function getCategoryOhHaeng(dayGan: CheonGan, category: SipSungCategory): OhHaeng {
  const dayOhHaeng = getDayGanOhHaeng(dayGan);
  const relation = OHAENG_RELATIONSHIP[dayOhHaeng];

  switch (category) {
    case '비겁':
      return relation.비;
    case '식상':
      return relation.생;
    case '재성':
      return relation.극;
    case '관성':
      return relation.피극;
    case '인성':
      return relation.피생;
    default:
      return dayOhHaeng;
  }
}

/**
 * 억부법에 의한 용신 결정
 *
 * 신강이면: 설기(식상), 극제(재성, 관성) 필요
 * 신약이면: 생조(인성, 비겁) 필요
 */
export function getYongSinByEokBu(
  dayGan: CheonGan,
  bodyStrength: BodyStrengthGrade,
): EokBuResult {
  const yongSinCategory: SipSungCategory[] = [];
  const yongSinOhHaeng: OhHaeng[] = [];
  const giSinCategory: SipSungCategory[] = [];
  const giSinOhHaeng: OhHaeng[] = [];

  if (bodyStrength === '중화') {
    return {
      yongSinCategory,
      yongSinOhHaeng,
      giSinCategory,
      giSinOhHaeng,
      isBalanced: true,
    };
  }

  const isStrong = bodyStrength === '신강' || bodyStrength === '극신강';
  const isVeryStrong = bodyStrength === '극신강';
  const isVeryWeak = bodyStrength === '극신약';

  if (isStrong) {
    // 신강: 설기/극제 필요 → 식상, 재성, 관성이 용신
    if (isVeryStrong) {
      // 극신강: 관성 > 재성 > 식상 순
      yongSinCategory.push('관성', '재성', '식상');
      giSinCategory.push('인성', '비겁');
    } else {
      // 신강: 재성 > 식상 순 (관성은 일간을 극하므로 주의)
      yongSinCategory.push('재성', '식상');
      giSinCategory.push('비겁', '인성');
    }
  } else {
    // 신약: 생조 필요 → 인성, 비겁이 용신
    if (isVeryWeak) {
      // 극신약: 인성 > 비겁 순
      yongSinCategory.push('인성', '비겁');
      giSinCategory.push('관성', '재성', '식상');
    } else {
      // 신약: 인성, 비겁 둘 다 필요
      yongSinCategory.push('인성', '비겁');
      giSinCategory.push('관성', '재성');
    }
  }

  // 카테고리를 오행으로 변환
  yongSinCategory.forEach((cat) => {
    const oh = getCategoryOhHaeng(dayGan, cat);
    if (!yongSinOhHaeng.includes(oh)) {
      yongSinOhHaeng.push(oh);
    }
  });

  giSinCategory.forEach((cat) => {
    const oh = getCategoryOhHaeng(dayGan, cat);
    if (!giSinOhHaeng.includes(oh)) {
      giSinOhHaeng.push(oh);
    }
  });

  return {
    yongSinCategory,
    yongSinOhHaeng,
    giSinCategory,
    giSinOhHaeng,
    isBalanced: false,
  };
}

/**
 * 통관용신(通關用神) 결정
 *
 * 두 오행이 충돌할 때 중재하는 오행을 찾습니다.
 * - 목-토 충돌 → 화 중재 (목→화→토)
 * - 화-금 충돌 → 토 중재 (화→토→금)
 * - 토-수 충돌 → 금 중재 (토→금→수)
 * - 금-목 충돌 → 수 중재 (금→수→목)
 * - 수-화 충돌 → 목 중재 (수→목→화)
 */
export function identifyMediatingYongsin(input: YongSinInput): MediatingYongSinResult {
  const { fourPillars } = input;

  // 사주 내 오행 분포 계산
  const ohHaengCount = countOhHaengInFourPillars(fourPillars);

  // 강한 오행들 찾기 (2개 이상 등장)
  const strongElements: OhHaeng[] = [];
  (Object.keys(ohHaengCount) as OhHaeng[]).forEach((oh) => {
    if (ohHaengCount[oh] >= 2) {
      strongElements.push(oh);
    }
  });

  // 충돌 감지: 두 강한 오행이 상극 관계인지 확인
  for (let i = 0; i < strongElements.length; i++) {
    for (let j = i + 1; j < strongElements.length; j++) {
      const elem1 = strongElements[i];
      const elem2 = strongElements[j];

      // 상극 관계인지 확인 (elem1이 elem2를 극하거나, elem2가 elem1을 극함)
      const relation1 = OHAENG_RELATIONSHIP[elem1];
      const relation2 = OHAENG_RELATIONSHIP[elem2];

      const isClashing = relation1.극 === elem2 || relation2.극 === elem1;

      if (isClashing) {
        // 통관용신 찾기
        const key = `${elem1}-${elem2}`;
        const mediatingElement = MEDIATING_ELEMENT_MAP[key];

        if (mediatingElement) {
          return {
            hasMediatingNeed: true,
            mediatingElement,
            conflictingElements: [elem1, elem2],
            reason: `${elem1}와 ${elem2}의 충돌을 ${mediatingElement}가 중재`,
          };
        }
      }
    }
  }

  return {
    hasMediatingNeed: false,
  };
}

/**
 * 조후법에 의한 용신 결정
 *
 * 계절에 따른 한난조습 조절:
 * - 겨울생(해, 자, 축월): 화(火) 필요 (따뜻함)
 * - 여름생(사, 오, 미월): 수(水) 필요 (시원함)
 */
export function getYongSinByJohu(dayGan: CheonGan, monthJi: JiJi): JohuResult {
  const season = JIJI_SEASON[monthJi];
  const johuYongSin: OhHaeng[] = [];
  let johuNecessity: JohuNecessity = '낮음';
  let reason = '';

  switch (season) {
    case '겨울':
      johuYongSin.push('화');
      johuNecessity = '높음';
      reason = '한기가 강한 겨울생으로 따뜻한 화기(火氣)가 필요';
      break;
    case '여름':
      johuYongSin.push('수');
      johuNecessity = '높음';
      reason = '열기가 강한 여름생으로 시원한 수기(水氣)가 필요';
      break;
    case '가을': {
      johuNecessity = '중간';
      reason = '가을생으로 조후 필요성 중간';
      // 가을은 금의 계절, 화로 단련하거나 수로 설기
      const dayOh = getDayGanOhHaeng(dayGan);
      if (dayOh === '금') {
        johuYongSin.push('화'); // 금은 화로 단련
      } else {
        johuYongSin.push('수'); // 일반적으로 수
      }
      break;
    }
    case '봄':
    default:
      johuNecessity = '낮음';
      reason = '온화한 봄생으로 조후 필요성 낮음';
      break;
  }

  return {
    johuYongSin,
    johuNecessity,
    reason,
  };
}

/**
 * 종합 용신 결정
 *
 * 억부법, 조후법, 통관법을 종합하여 용신 결정
 */
export function determineYongSin(input: YongSinInput): YongSinResult {
  const { dayGan, monthJi, bodyStrength } = input;

  const eokBuResult = getYongSinByEokBu(dayGan, bodyStrength);
  const johuResult = getYongSinByJohu(dayGan, monthJi);
  const mediatingResult = identifyMediatingYongsin(input);

  const primaryYongSin = eokBuResult.yongSinOhHaeng;
  const johuYongSin = johuResult.johuYongSin;
  const mediatingYongSin = mediatingResult.hasMediatingNeed && mediatingResult.mediatingElement
    ? [mediatingResult.mediatingElement]
    : undefined;

  // 일치 여부 확인
  let yongSinHarmony: '일치' | '불일치' | '부분일치' = '불일치';

  if (primaryYongSin.length > 0 && johuYongSin.length > 0) {
    const hasMatch = primaryYongSin.some((oh) => johuYongSin.includes(oh));
    const allMatch = primaryYongSin.every((oh) => johuYongSin.includes(oh));

    if (allMatch && primaryYongSin.length === johuYongSin.length) {
      yongSinHarmony = '일치';
    } else if (hasMatch) {
      yongSinHarmony = '부분일치';
    }
  } else if (bodyStrength === '중화') {
    yongSinHarmony = '일치'; // 중화는 특별한 용신 불필요
  }

  return {
    primaryYongSin,
    johuYongSin,
    yongSinHarmony,
    mediatingYongSin,
  };
}

/**
 * 기신 결정
 */
export function determineGiSin(
  dayGan: CheonGan,
  bodyStrength: BodyStrengthGrade,
): GiSinResult {
  const giSinCategory: SipSungCategory[] = [];
  const giSinOhHaeng: OhHaeng[] = [];
  let mostHarmful: SipSungCategory;

  const isStrong = bodyStrength === '신강' || bodyStrength === '극신강';
  const isVeryStrong = bodyStrength === '극신강';
  const isVeryWeak = bodyStrength === '극신약';

  if (isStrong) {
    // 신강이면 인성, 비겁이 기신
    giSinCategory.push('인성', '비겁');
    mostHarmful = isVeryStrong ? '인성' : '비겁';
  } else {
    // 신약이면 관성, 재성, 식상이 기신
    giSinCategory.push('관성', '재성', '식상');
    mostHarmful = isVeryWeak ? '관성' : '재성';
  }

  giSinCategory.forEach((cat) => {
    const oh = getCategoryOhHaeng(dayGan, cat);
    if (!giSinOhHaeng.includes(oh)) {
      giSinOhHaeng.push(oh);
    }
  });

  const mostHarmfulOhHaeng = getCategoryOhHaeng(dayGan, mostHarmful);

  return {
    giSinCategory,
    giSinOhHaeng,
    mostHarmful,
    mostHarmfulOhHaeng,
  };
}

/**
 * 종격에 따른 특수 용신 결정
 */
function getSpecialYongSin(dayGan: CheonGan, geukGuk: string): OhHaeng | undefined {
  const dayOhHaeng = getDayGanOhHaeng(dayGan);
  const relation = OHAENG_RELATIONSHIP[dayOhHaeng];

  switch (geukGuk) {
    case '종아격': // 식상을 따름
      return relation.생;
    case '종재격': // 재성을 따름
      return relation.극;
    case '종관격': // 관성을 따름
      return relation.피극;
    case '종강격': // 비겁을 따름
      return relation.비;
    default:
      return undefined;
  }
}

/**
 * 실용 정보 생성
 */
function getPracticalInfo(
  yongSinOhHaeng: OhHaeng[],
  giSinOhHaeng: OhHaeng[],
): PracticalInfo {
  const colors: string[] = [];
  const directions: string[] = [];
  const numbers: number[] = [];

  yongSinOhHaeng.forEach((oh) => {
    colors.push(...OHAENG_COLOR[oh]);
    directions.push(...OHAENG_DIRECTION[oh]);
    numbers.push(...OHAENG_NUMBER[oh]);
  });

  const avoidColors: string[] = [];
  const avoidDirections: string[] = [];
  const avoidNumbers: number[] = [];

  giSinOhHaeng.forEach((oh) => {
    avoidColors.push(...OHAENG_COLOR[oh]);
    avoidDirections.push(...OHAENG_DIRECTION[oh]);
    avoidNumbers.push(...OHAENG_NUMBER[oh]);
  });

  return {
    colors: [...new Set(colors)],
    directions: [...new Set(directions)],
    numbers: [...new Set(numbers)],
    avoid: {
      colors: [...new Set(avoidColors)],
      directions: [...new Set(avoidDirections)],
      numbers: [...new Set(avoidNumbers)],
    },
  };
}

/**
 * 추천 문구 생성
 */
function getRecommendation(
  bodyStrength: BodyStrengthGrade,
  yongSinOhHaeng: OhHaeng[],
  johuNecessity: JohuNecessity,
): string {
  const yongStr = yongSinOhHaeng.join(', ');

  let base = '';
  switch (bodyStrength) {
    case '극신강':
      base = `극도로 강한 기운을 가지고 있어 ${yongStr} 오행으로 기운을 분산시키는 것이 좋습니다.`;
      break;
    case '신강':
      base = `강한 기운을 가지고 있어 ${yongStr} 오행으로 균형을 맞추는 것이 좋습니다.`;
      break;
    case '중화':
      base = '이미 균형 잡힌 사주로 현재 상태를 유지하는 것이 좋습니다.';
      break;
    case '신약':
      base = `약한 기운을 가지고 있어 ${yongStr} 오행으로 보강하는 것이 좋습니다.`;
      break;
    case '극신약':
      base = `극도로 약한 기운을 가지고 있어 ${yongStr} 오행으로 적극적으로 보강하는 것이 좋습니다.`;
      break;
  }

  if (johuNecessity === '높음') {
    base += ' 특히 계절적 조후가 필요합니다.';
  }

  return base;
}

/**
 * 추천 문구 생성 (통관용신 포함)
 */
function getRecommendationWithMediating(
  bodyStrength: BodyStrengthGrade,
  yongSinOhHaeng: OhHaeng[],
  johuNecessity: JohuNecessity,
  mediating?: {
    yongSin: OhHaeng[];
    conflictingElements?: [OhHaeng, OhHaeng];
    reason: string;
  },
): string {
  let base = getRecommendation(bodyStrength, yongSinOhHaeng, johuNecessity);

  // 통관용신이 있으면 추가 설명
  if (mediating && mediating.conflictingElements) {
    const [elem1, elem2] = mediating.conflictingElements;
    const mediatingElem = mediating.yongSin.join(', ');
    base += ` 또한 사주 내 ${elem1}와 ${elem2}의 충돌이 있어 ${mediatingElem}를 통관용신으로 활용하면 기운의 흐름을 원활하게 할 수 있습니다.`;
  }

  return base;
}

/**
 * 종합 분석
 */
export function analyzeYongSinGiSin(input: YongSinInput): YongSinAnalysis {
  const { dayGan, monthJi, bodyStrength, geukGuk } = input;

  const dayGanOhHaeng = getDayGanOhHaeng(dayGan);
  const eokBuResult = getYongSinByEokBu(dayGan, bodyStrength);
  const johuResult = getYongSinByJohu(dayGan, monthJi);
  const giSinResult = determineGiSin(dayGan, bodyStrength);
  const mediatingResult = identifyMediatingYongsin(input);

  // 종격인 경우 특수 용신
  const specialYongSin = geukGuk ? getSpecialYongSin(dayGan, geukGuk) : undefined;

  // 통관용신 정보 구성
  const mediating = mediatingResult.hasMediatingNeed && mediatingResult.mediatingElement
    ? {
        yongSin: [mediatingResult.mediatingElement],
        conflictingElements: mediatingResult.conflictingElements,
        reason: mediatingResult.reason || '',
      }
    : undefined;

  // 실용 정보 (통관용신 포함)
  const yongSinForPractical = [
    ...eokBuResult.yongSinOhHaeng,
    ...(mediating ? mediating.yongSin : []),
  ];
  const practical = getPracticalInfo(yongSinForPractical, giSinResult.giSinOhHaeng);

  // 추천 문구 (통관용신 고려)
  const recommendation = getRecommendationWithMediating(
    bodyStrength,
    eokBuResult.yongSinOhHaeng.length > 0
      ? eokBuResult.yongSinOhHaeng
      : specialYongSin
        ? [specialYongSin]
        : [],
    johuResult.johuNecessity,
    mediating,
  );

  return {
    dayGan,
    dayGanOhHaeng,
    bodyStrength,
    isBalanced: bodyStrength === '중화',
    yongSin: {
      primary: eokBuResult.yongSinOhHaeng,
      category: eokBuResult.yongSinCategory,
    },
    giSin: {
      primary: giSinResult.giSinOhHaeng,
      category: giSinResult.giSinCategory,
    },
    johu: {
      yongSin: johuResult.johuYongSin,
      necessity: johuResult.johuNecessity,
      reason: johuResult.reason,
    },
    mediating,
    specialYongSin,
    recommendation,
    practical,
  };
}
