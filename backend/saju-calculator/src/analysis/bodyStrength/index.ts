/**
 * 신강/신약(身强/身弱) 계산 모듈
 *
 * 명리학 정통 계산법 기반:
 * - 득령(得令): 월지에서 힘을 얻는가
 * - 득지(得地): 지지에서 통근하는가
 * - 득세(得勢): 천간에서 비견/겁재/인성의 도움을 받는가
 *
 * 판단 기준:
 * - 3가지 중 2가지 이상 만족 → 신강(身强)
 * - 3가지 중 1가지 이하 만족 → 신약(身弱)
 *
 * 참고: 연해자평, 적천수, 자평진전
 */

import type { CheonGan, JiJi } from '../../types/saju';
import { JIJANGGAN_SIMPLE } from '../../core/index';

// ==========================================
// 기본 타입 정의
// ==========================================

/** 득령 결과 */
export interface DeukRyeongResult {
  isDeukRyeong: boolean;
  strength: '왕' | '상' | '휴' | '수' | '사';
  score: number;
  description: string;
}

/** 득지 결과 */
export interface DeukJiResult {
  isDeukJi: boolean;
  rootCount: number;
  strength: number;
  roots: Array<{ ji: JiJi; type: 'bigyeob' | 'inseong' | 'partial' }>;
  description: string;
}

/** 득세 결과 */
export interface DeukSeResult {
  isDeukSe: boolean;
  bigyeobCount: number;
  inseongCount: number;
  totalSupport: number;
  description: string;
}

/** 신강/신약 종합 결과 */
export interface BodyStrengthResult {
  isStrong: boolean;
  grade: '극신강' | '신강' | '중화' | '신약' | '극신약';
  score: number;
  deukRyeong: boolean;
  deukJi: boolean;
  deukSe: boolean;
  description: string;
}

/** 상세 분석 결과 */
export interface BodyStrengthAnalysis {
  deukRyeong: DeukRyeongResult;
  deukJi: DeukJiResult;
  deukSe: DeukSeResult;
  bodyStrength: BodyStrengthResult;
  analysis: string;
  yongsinHint: string;
}

/** 계산 입력 */
export interface BodyStrengthInput {
  dayGan: CheonGan;
  monthJi: JiJi;
  fourPillarGan: CheonGan[];
  fourPillarJi: JiJi[];
}

// ==========================================
// 기본 상수 정의
// ==========================================

/** 천간의 오행 */
const GAN_TO_ELEMENT: Record<CheonGan, string> = {
  '갑': '목', '을': '목',
  '병': '화', '정': '화',
  '무': '토', '기': '토',
  '경': '금', '신': '금',
  '임': '수', '계': '수',
};

/** 천간의 음양 */
const GAN_YIN_YANG: Record<CheonGan, 'yang' | 'yin'> = {
  '갑': 'yang', '을': 'yin',
  '병': 'yang', '정': 'yin',
  '무': 'yang', '기': 'yin',
  '경': 'yang', '신': 'yin',
  '임': 'yang', '계': 'yin',
};

/** 지지의 오행 */
const _JI_TO_ELEMENT: Record<JiJi, string> = {
  '자': '수', '축': '토', '인': '목', '묘': '목',
  '진': '토', '사': '화', '오': '화', '미': '토',
  '신': '금', '유': '금', '술': '토', '해': '수',
};

/** 지지 인덱스 */
const _JI_INDEX: Record<JiJi, number> = {
  '자': 0, '축': 1, '인': 2, '묘': 3,
  '진': 4, '사': 5, '오': 6, '미': 7,
  '신': 8, '유': 9, '술': 10, '해': 11,
};

/** 오행 상생 관계 (A가 B를 생함) */
const ELEMENT_GENERATES: Record<string, string> = {
  '목': '화',
  '화': '토',
  '토': '금',
  '금': '수',
  '수': '목',
};

/** 오행 상극 관계 (A가 B를 극함) */
const _ELEMENT_CONTROLS: Record<string, string> = {
  '목': '토',
  '화': '금',
  '토': '수',
  '금': '목',
  '수': '화',
};

/** 월령 에너지 테이블 (오행별 월지에서의 힘) */
export const MONTHLY_ENERGY_TABLE: Record<string, Record<JiJi, number>> = {
  '목': {
    '인': 100, '묘': 100, // 왕(旺) - 봄
    '해': 80, '자': 70, // 상(相) - 겨울 (수생목)
    '진': 50, '미': 40, '술': 40, '축': 40, // 휴(休) - 토월
    '사': 30, '오': 20, // 수(囚) - 여름 (목생화로 설기)
    '신': 10, '유': 10, // 사(死) - 가을 (금극목)
  },
  '화': {
    '사': 100, '오': 100, // 왕(旺) - 여름
    '인': 80, '묘': 70, // 상(相) - 봄 (목생화)
    '진': 50, '미': 50, '술': 40, '축': 40, // 휴(休) - 토월
    '신': 30, '유': 20, // 수(囚) - 가을 (화생토, 설기)
    '해': 10, '자': 10, // 사(死) - 겨울 (수극화)
  },
  '토': {
    '진': 90, '술': 90, '축': 80, '미': 80, // 왕(旺) - 사계절 토월
    '사': 70, '오': 70, // 상(相) - 여름 (화생토)
    '신': 50, '유': 40, // 휴(休) - 가을 (토생금, 설기)
    '해': 30, '자': 30, // 수(囚) - 겨울
    '인': 20, '묘': 10, // 사(死) - 봄 (목극토)
  },
  '금': {
    '신': 100, '유': 100, // 왕(旺) - 가을
    '진': 70, '술': 80, '축': 70, '미': 60, // 상(相) - 토월 (토생금)
    '해': 50, '자': 40, // 휴(休) - 겨울 (금생수, 설기)
    '인': 30, '묘': 20, // 수(囚) - 봄
    '사': 10, '오': 10, // 사(死) - 여름 (화극금)
  },
  '수': {
    '해': 100, '자': 100, // 왕(旺) - 겨울
    '신': 80, '유': 70, // 상(相) - 가을 (금생수)
    '인': 50, '묘': 40, // 휴(休) - 봄 (수생목, 설기)
    '사': 30, '오': 20, // 수(囚) - 여름
    '진': 20, '술': 10, '축': 30, '미': 10, // 사(死) - 토월 (토극수)
  },
};

// ==========================================
// 득령(得令) 계산
// ==========================================

/**
 * 득령 여부 계산 - 월지에서 힘을 얻는가
 * @param dayGan 일간
 * @param monthJi 월지
 * @returns 득령 결과
 */
export function checkDeukRyeong(dayGan: CheonGan, monthJi: JiJi): DeukRyeongResult {
  const dayElement = GAN_TO_ELEMENT[dayGan];
  const energy = MONTHLY_ENERGY_TABLE[dayElement][monthJi];

  let strength: '왕' | '상' | '휴' | '수' | '사';
  let isDeukRyeong: boolean;
  let description: string;

  if (energy >= 80) {
    strength = '왕';
    isDeukRyeong = true;
    description = `${dayGan}(${dayElement})이(가) ${monthJi}월에 왕성한 힘을 얻습니다.`;
  } else if (energy >= 60) {
    strength = '상';
    isDeukRyeong = true;
    description = `${dayGan}(${dayElement})이(가) ${monthJi}월에 상생으로 힘을 얻습니다.`;
  } else if (energy >= 40) {
    strength = '휴';
    isDeukRyeong = false;
    description = `${dayGan}(${dayElement})이(가) ${monthJi}월에 휴식 상태입니다.`;
  } else if (energy >= 20) {
    strength = '수';
    isDeukRyeong = false;
    description = `${dayGan}(${dayElement})이(가) ${monthJi}월에 수세(囚勢)입니다.`;
  } else {
    strength = '사';
    isDeukRyeong = false;
    description = `${dayGan}(${dayElement})이(가) ${monthJi}월에 쇠약한 상태입니다.`;
  }

  return {
    isDeukRyeong,
    strength,
    score: energy,
    description,
  };
}

// ==========================================
// 득지(得地) 계산
// ==========================================

/**
 * 득지 여부 계산 - 지지에서 통근하는가
 * @param dayGan 일간
 * @param fourPillarJi 4주의 지지 [년지, 월지, 일지, 시지]
 * @returns 득지 결과
 */
export function checkDeukJi(dayGan: CheonGan, fourPillarJi: JiJi[]): DeukJiResult {
  const dayElement = GAN_TO_ELEMENT[dayGan];
  const _dayYinYang = GAN_YIN_YANG[dayGan];
  const roots: Array<{ ji: JiJi; type: 'bigyeob' | 'inseong' | 'partial' }> = [];
  let strength = 0;

  // 인성 오행 찾기 (나를 생하는 오행)
  let inseongElement = '';
  for (const [gen, target] of Object.entries(ELEMENT_GENERATES)) {
    if (target === dayElement) {
      inseongElement = gen;
      break;
    }
  }

  for (const ji of fourPillarJi) {
    const jijanggan = JIJANGGAN_SIMPLE[ji];
    const length = jijanggan.length;

    for (let i = 0; i < length; i++) {
      const hiddenGan = jijanggan[i];
      const hiddenElement = GAN_TO_ELEMENT[hiddenGan];
      const _hiddenYinYang = GAN_YIN_YANG[hiddenGan];

      // 비견/겁재 확인 (같은 오행)
      if (hiddenElement === dayElement) {
        // JIJANGGAN_SIMPLE: 본기(本氣)는 마지막 인덱스 (가장 강함)
        const weight = i === length - 1 ? 30 : (i === length - 2 ? 20 : 10);
        strength += weight;

        if (!roots.find(r => r.ji === ji && r.type === 'bigyeob')) {
          roots.push({ ji, type: 'bigyeob' });
        }
      }

      // 인성 확인 (나를 생하는 오행)
      if (hiddenElement === inseongElement) {
        // JIJANGGAN_SIMPLE: 본기(本氣)는 마지막 인덱스 (가장 강함)
        const weight = i === length - 1 ? 20 : (i === length - 2 ? 15 : 8);
        strength += weight;

        if (!roots.find(r => r.ji === ji && r.type === 'inseong')) {
          roots.push({ ji, type: 'inseong' });
        }
      }
    }
  }

  const rootCount = roots.length;
  const isDeukJi = rootCount >= 1 && strength >= 20;

  let description: string;
  if (rootCount === 0) {
    description = `${dayGan}이(가) 지지에서 통근하지 못합니다.`;
  } else if (rootCount === 1) {
    description = `${dayGan}이(가) ${roots[0].ji}에서 통근합니다.`;
  } else {
    description = `${dayGan}이(가) ${roots.map(r => r.ji).join(', ')}에서 통근합니다.`;
  }

  return {
    isDeukJi,
    rootCount,
    strength,
    roots,
    description,
  };
}

// ==========================================
// 득세(得勢) 계산
// ==========================================

/**
 * 득세 여부 계산 - 천간에서 도움받는가
 * @param dayGan 일간
 * @param fourPillarGan 4주의 천간 [년간, 월간, 일간, 시간]
 * @returns 득세 결과
 */
export function checkDeukSe(dayGan: CheonGan, fourPillarGan: CheonGan[]): DeukSeResult {
  const dayElement = GAN_TO_ELEMENT[dayGan];
  let bigyeobCount = 0;
  let inseongCount = 0;

  // 인성 오행 찾기 (나를 생하는 오행)
  let inseongElement = '';
  for (const [gen, target] of Object.entries(ELEMENT_GENERATES)) {
    if (target === dayElement) {
      inseongElement = gen;
      break;
    }
  }

  for (let i = 0; i < fourPillarGan.length; i++) {
    const gan = fourPillarGan[i];

    // 일간 자신은 제외 (보통 인덱스 2)
    if (i === 2) continue;

    const ganElement = GAN_TO_ELEMENT[gan];

    // 비견/겁재 (같은 오행)
    if (ganElement === dayElement) {
      bigyeobCount++;
    }

    // 인성 (나를 생하는 오행)
    if (ganElement === inseongElement) {
      inseongCount++;
    }
  }

  const totalSupport = bigyeobCount + inseongCount;
  const isDeukSe = totalSupport >= 2;

  let description: string;
  if (totalSupport === 0) {
    description = `${dayGan}이(가) 천간에서 도움받지 못합니다.`;
  } else {
    const parts: string[] = [];
    if (bigyeobCount > 0) parts.push(`비겁 ${bigyeobCount}개`);
    if (inseongCount > 0) parts.push(`인성 ${inseongCount}개`);
    description = `${dayGan}이(가) 천간에서 ${parts.join(', ')}의 도움을 받습니다.`;
  }

  return {
    isDeukSe,
    bigyeobCount,
    inseongCount,
    totalSupport,
    description,
  };
}

// ==========================================
// 신강/신약 종합 판단
// ==========================================

/**
 * 신강/신약 종합 계산
 * @param input 계산 입력
 * @returns 신강/신약 종합 결과
 */
export function calculateBodyStrength(input: BodyStrengthInput): BodyStrengthResult {
  const { dayGan, monthJi, fourPillarGan, fourPillarJi } = input;

  // 1. 득령 확인
  const deukRyeongResult = checkDeukRyeong(dayGan, monthJi);
  const deukRyeong = deukRyeongResult.isDeukRyeong;

  // 2. 득지 확인
  const deukJiResult = checkDeukJi(dayGan, fourPillarJi);
  const deukJi = deukJiResult.isDeukJi;

  // 3. 득세 확인
  const deukSeResult = checkDeukSe(dayGan, fourPillarGan);
  const deukSe = deukSeResult.isDeukSe;

  // 4. 종합 점수 계산
  let score = 0;

  // 득령 점수 (최대 40점)
  score += deukRyeongResult.score * 0.4;

  // 득지 점수 (최대 35점)
  score += Math.min(deukJiResult.strength, 100) * 0.35;

  // 득세 점수 (최대 25점)
  score += Math.min(deukSeResult.totalSupport * 10, 30) * 0.83;

  // 점수 범위 조정 (0-100)
  score = Math.max(0, Math.min(100, score));

  // 5. 등급 결정
  let grade: '극신강' | '신강' | '중화' | '신약' | '극신약';
  let isStrong: boolean;

  const satisfiedCount = [deukRyeong, deukJi, deukSe].filter(Boolean).length;

  if (score >= 75 && satisfiedCount >= 3) {
    grade = '극신강';
    isStrong = true;
  } else if (score >= 55 || satisfiedCount >= 2) {
    grade = '신강';
    isStrong = true;
  } else if (score >= 40 && score < 55) {
    grade = '중화';
    isStrong = false; // 중화도 신약 쪽으로 분류
  } else if (score >= 25) {
    grade = '신약';
    isStrong = false;
  } else {
    grade = '극신약';
    isStrong = false;
  }

  // 6. 설명 생성
  let description: string;
  if (isStrong) {
    description = `일간 ${dayGan}이(가) ${grade}입니다. `;
    if (deukRyeong) description += '월령에서 힘을 얻고, ';
    if (deukJi) description += '지지에서 통근하며, ';
    if (deukSe) description += '천간의 도움을 받습니다.';
  } else {
    description = `일간 ${dayGan}이(가) ${grade}입니다. `;
    description += '일간의 힘이 부족하여 도움이 필요합니다.';
  }

  return {
    isStrong,
    grade,
    score: Math.round(score),
    deukRyeong,
    deukJi,
    deukSe,
    description,
  };
}

// ==========================================
// 상세 분석
// ==========================================

/**
 * 신강/신약 상세 분석
 * @param input 계산 입력
 * @returns 상세 분석 결과
 */
export function analyzeBodyStrengthDetails(input: BodyStrengthInput): BodyStrengthAnalysis {
  const { dayGan, monthJi, fourPillarGan, fourPillarJi } = input;
  const dayElement = GAN_TO_ELEMENT[dayGan];

  // 각 항목 계산
  const deukRyeong = checkDeukRyeong(dayGan, monthJi);
  const deukJi = checkDeukJi(dayGan, fourPillarJi);
  const deukSe = checkDeukSe(dayGan, fourPillarGan);
  const bodyStrength = calculateBodyStrength(input);

  // 종합 분석 텍스트
  let analysis = '### 신강/신약 분석\n\n';
  analysis += `**일간**: ${dayGan}(${dayElement})\n\n`;
  analysis += `**득령(得令)**: ${deukRyeong.isDeukRyeong ? '✓' : '✗'} - ${deukRyeong.description}\n`;
  analysis += `**득지(得地)**: ${deukJi.isDeukJi ? '✓' : '✗'} - ${deukJi.description}\n`;
  analysis += `**득세(得勢)**: ${deukSe.isDeukSe ? '✓' : '✗'} - ${deukSe.description}\n\n`;
  analysis += `**종합 판단**: ${bodyStrength.grade} (점수: ${bodyStrength.score}점)\n`;
  analysis += bodyStrength.description;

  // 용신 힌트
  let yongsinHint: string;
  if (bodyStrength.isStrong) {
    // 신강이면 설기(식상/재성) 또는 극(관성)이 용신
    yongsinHint = '신강한 사주이므로 식상(食傷), 재성(財星), 관성(官星)으로 설기하거나 제어하는 것이 좋습니다.';
    if (bodyStrength.grade === '극신강') {
      yongsinHint += ' 특히 관성(官星)으로 제어하거나 식상으로 설기하는 것이 효과적입니다.';
    }
  } else {
    // 신약이면 생조(인성/비겁)가 용신
    yongsinHint = '신약한 사주이므로 인성(印星), 비겁(比劫)으로 힘을 보충하는 것이 좋습니다.';
    if (bodyStrength.grade === '극신약') {
      yongsinHint += ' 특히 인성으로 생조받는 것이 우선입니다.';
    }
  }

  return {
    deukRyeong,
    deukJi,
    deukSe,
    bodyStrength,
    analysis,
    yongsinHint,
  };
}
