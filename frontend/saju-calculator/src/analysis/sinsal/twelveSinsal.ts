/**
 * 12신살 계산 모듈
 * 전통 명리학 기반 정확한 삼합 계산
 *
 * 12신살 순서 (고정):
 * 겁살 → 재살 → 천살 → 지살 → 년살(도화) → 월살 →
 * 망신살 → 장성살 → 반안살 → 역마살 → 육해살 → 화개살
 *
 * 계산 원리:
 * - 삼합의 마지막 글자(고지: 辰戌丑未) 다음부터 12지지 순서로 배치
 */

import type { JiJi } from '../../types/saju';
import type {
  SamhapGroup,
  TwelveSinsalTable,
  SinsalResult,
  TwelveSinsalType,
} from './types';

// 12지지 순서
const JIJI_ORDER: JiJi[] = [
  '자', '축', '인', '묘', '진', '사',
  '오', '미', '신', '유', '술', '해',
];

// 지지 → 인덱스 매핑
const JIJI_INDEX: Record<JiJi, number> = {
  '자': 0, '축': 1, '인': 2, '묘': 3, '진': 4, '사': 5,
  '오': 6, '미': 7, '신': 8, '유': 9, '술': 10, '해': 11,
};

// 삼합 그룹 매핑 (지지 → 삼합 그룹)
export const SAMHAP_GROUP_MAP: Record<JiJi, SamhapGroup> = {
  '인': '인오술', '오': '인오술', '술': '인오술',  // 화국
  '사': '사유축', '유': '사유축', '축': '사유축',  // 금국
  '신': '신자진', '자': '신자진', '진': '신자진',  // 수국
  '해': '해묘미', '묘': '해묘미', '미': '해묘미',  // 목국
};

// 삼합별 마지막 글자 (고지 - 庫地)
const SAMHAP_LAST: Record<SamhapGroup, JiJi> = {
  '인오술': '술',  // 화국의 고지
  '사유축': '축',  // 금국의 고지
  '신자진': '진',  // 수국의 고지
  '해묘미': '미',  // 목국의 고지
};

// 삼합별 첫 글자 (생지 - 生地)
const SAMHAP_FIRST: Record<SamhapGroup, JiJi> = {
  '인오술': '인',  // 화국의 생지
  '사유축': '사',  // 금국의 생지
  '신자진': '신',  // 수국의 생지
  '해묘미': '해',  // 목국의 생지
};

// 삼합별 왕지 (旺地) - 이전 계절의 왕지가 도화살
const SAMHAP_PEAK: Record<SamhapGroup, JiJi> = {
  '인오술': '오',  // 화국의 왕지
  '사유축': '유',  // 금국의 왕지
  '신자진': '자',  // 수국의 왕지
  '해묘미': '묘',  // 목국의 왕지
};

/**
 * 지지 충(沖) 계산
 * 자↔오, 축↔미, 인↔신, 묘↔유, 진↔술, 사↔해
 */
function getChungJiji(ji: JiJi): JiJi {
  const index = JIJI_INDEX[ji];
  const chungIndex = (index + 6) % 12;
  return JIJI_ORDER[chungIndex];
}

/**
 * n번째 다음 지지 계산
 */
function getNextJiji(ji: JiJi, offset: number): JiJi {
  const index = JIJI_INDEX[ji];
  const nextIndex = (index + offset) % 12;
  return JIJI_ORDER[nextIndex];
}

/**
 * 12신살 테이블 생성
 * 삼합 그룹에 따른 12신살 배치
 */
export function getTwelveSinsalTable(samhapGroup: SamhapGroup): TwelveSinsalTable {
  const lastJiji = SAMHAP_LAST[samhapGroup]; // 고지 (화개살)
  const firstJiji = SAMHAP_FIRST[samhapGroup]; // 생지
  const peakJiji = SAMHAP_PEAK[samhapGroup]; // 왕지

  // 12신살은 고지 다음부터 시작 (겁살부터)
  // 겁살 = 고지 + 1
  const geobSalJi = getNextJiji(lastJiji, 1);

  return {
    // 겁살: 고지 + 1
    geobSal: geobSalJi,
    // 재살: 고지 + 2
    jaeSal: getNextJiji(lastJiji, 2),
    // 천살: 고지 + 3
    cheonSal: getNextJiji(lastJiji, 3),
    // 지살: 고지 + 4
    jiSal: getNextJiji(lastJiji, 4),
    // 년살(도화살): 고지 + 5 = 이전 계절 왕지
    // 실제로는 삼합의 이전 계절 왕지
    nyeonSal: getDoHwaSal(samhapGroup),
    // 월살: 고지 + 6
    wolSal: getNextJiji(lastJiji, 6),
    // 망신살: 고지 + 7
    mangSinSal: getNextJiji(lastJiji, 7),
    // 장성살: 고지 + 8 = 왕지
    jangSeongSal: peakJiji,
    // 반안살: 고지 + 9
    banAnSal: getNextJiji(lastJiji, 9),
    // 역마살: 생지를 충하는 지지
    yeokMaSal: getChungJiji(firstJiji),
    // 육해살: 고지 + 11
    yukHaeSal: getNextJiji(lastJiji, 11),
    // 화개살: 고지 자체
    hwaGaeSal: lastJiji,
  };
}

/**
 * 도화살(년살) 계산
 * 삼합의 이전 계절 왕지가 도화살
 */
function getDoHwaSal(samhapGroup: SamhapGroup): JiJi {
  // 전통 공식: 삼합의 이전 계절 왕지
  const doHwaMap: Record<SamhapGroup, JiJi> = {
    '인오술': '묘',  // 화국 → 목국의 왕지(묘)
    '사유축': '오',  // 금국 → 화국의 왕지(오)
    '신자진': '유',  // 수국 → 금국의 왕지(유)
    '해묘미': '자',  // 목국 → 수국의 왕지(자)
  };
  return doHwaMap[samhapGroup];
}

// 12신살 상세 정보
const SINSAL_INFO: Record<TwelveSinsalType, {
  name: string;
  effect: 'good' | 'bad' | 'neutral';
  description: string;
  detailedMeaning: string;
}> = {
  geobSal: {
    name: '겁살(劫煞)',
    effect: 'bad',
    description: '재물 손실, 도난, 사기 주의',
    detailedMeaning: '겁살은 강도나 도적을 의미하며, 재물의 손실이나 도난, 사기를 당할 수 있는 살입니다. 금전 거래나 투자에 특히 주의가 필요합니다.',
  },
  jaeSal: {
    name: '재살(災煞)',
    effect: 'bad',
    description: '재난, 질병, 사고 주의',
    detailedMeaning: '재살은 뜻밖의 재난이나 질병, 사고를 의미합니다. 건강 관리에 유의하고 위험한 활동은 자제해야 합니다.',
  },
  cheonSal: {
    name: '천살(天煞)',
    effect: 'bad',
    description: '하늘의 재앙, 불의의 사고',
    detailedMeaning: '천살은 하늘에서 내리는 재앙을 의미합니다. 자연재해나 불의의 사고에 주의하며, 무리한 도전은 피하는 것이 좋습니다.',
  },
  jiSal: {
    name: '지살(地煞)',
    effect: 'bad',
    description: '땅의 재앙, 부동산/이사 주의',
    detailedMeaning: '지살은 땅에서 오는 재앙을 의미합니다. 부동산 관련 문제나 이사, 건축 등에서 문제가 생길 수 있습니다.',
  },
  nyeonSal: {
    name: '도화살(桃花煞)/년살',
    effect: 'neutral',
    description: '이성운, 매력, 인기. 과하면 색정 문제',
    detailedMeaning: '도화살은 복숭아꽃처럼 이성을 끄는 매력을 의미합니다. 긍정적으로는 인기와 매력을 주지만, 과하면 이성 문제나 스캔들에 휘말릴 수 있습니다.',
  },
  wolSal: {
    name: '월살(月煞)',
    effect: 'bad',
    description: '육친 문제, 가정불화',
    detailedMeaning: '월살은 매달의 살로, 가족이나 가까운 사람과의 갈등을 의미합니다. 가정 내 불화나 친인척 문제에 주의가 필요합니다.',
  },
  mangSinSal: {
    name: '망신살(亡身煞)',
    effect: 'bad',
    description: '명예 실추, 체면 손상',
    detailedMeaning: '망신살은 몸을 망치는 살로, 명예나 체면이 손상될 수 있습니다. 공개적인 자리에서의 실수나 비밀 노출에 주의해야 합니다.',
  },
  jangSeongSal: {
    name: '장성살(將星煞)',
    effect: 'good',
    description: '리더십, 권위, 출세운',
    detailedMeaning: '장성살은 장군의 별로, 리더십과 권위를 의미합니다. 조직에서 인정받고 승진하거나 지도자적 위치에 오를 수 있습니다.',
  },
  banAnSal: {
    name: '반안살(攀鞍煞)',
    effect: 'good',
    description: '안정, 기회 포착, 행운',
    detailedMeaning: '반안살은 말 안장에 오르는 것처럼 기회를 잡는 행운을 의미합니다. 좋은 기회가 찾아오고 안정을 얻을 수 있습니다.',
  },
  yeokMaSal: {
    name: '역마살(驛馬煞)',
    effect: 'neutral',
    description: '이동, 변화, 해외/출장운',
    detailedMeaning: '역마살은 역마를 뜻하며 이동과 변화를 의미합니다. 이사, 여행, 해외 출장 등 움직임이 많고, 직장이나 거주지 변동이 생길 수 있습니다.',
  },
  yukHaeSal: {
    name: '육해살(六害煞)',
    effect: 'bad',
    description: '대인관계 갈등, 배신',
    detailedMeaning: '육해살은 여섯 가지 해로움으로, 가까운 사람과의 갈등이나 배신을 의미합니다. 인간관계에서 오해나 다툼이 생길 수 있습니다.',
  },
  hwaGaeSal: {
    name: '화개살(華蓋煞)',
    effect: 'neutral',
    description: '예술성, 종교성, 고독',
    detailedMeaning: '화개살은 빛나는 덮개로, 예술적 재능이나 종교적 성향을 의미합니다. 혼자만의 시간을 즐기며 깊은 사색을 좋아하지만, 고독할 수 있습니다.',
  },
};

/**
 * 특정 지지의 12신살 분석
 * @param baseJiji 기준 지지 (년지 또는 일지)
 * @param targetJiji 대상 지지들 (사주의 모든 지지)
 */
export function analyzeTwelveSinsal(
  baseJiji: JiJi,
  targetJijis: JiJi[],
): SinsalResult[] {
  const samhapGroup = SAMHAP_GROUP_MAP[baseJiji];
  const table = getTwelveSinsalTable(samhapGroup);
  const results: SinsalResult[] = [];

  // 12신살 각각에 대해 검사
  const sinsalTypes: TwelveSinsalType[] = [
    'geobSal', 'jaeSal', 'cheonSal', 'jiSal',
    'nyeonSal', 'wolSal', 'mangSinSal', 'jangSeongSal',
    'banAnSal', 'yeokMaSal', 'yukHaeSal', 'hwaGaeSal',
  ];

  for (const type of sinsalTypes) {
    const triggerJiji = table[type];
    const present = targetJijis.includes(triggerJiji);
    const info = SINSAL_INFO[type];

    results.push({
      name: info.name,
      type,
      present,
      triggerJiji,
      description: info.description,
      effect: info.effect,
      detailedMeaning: info.detailedMeaning,
    });
  }

  return results;
}

/**
 * 도화살 단독 계산
 * @param baseJiji 기준 지지 (년지 또는 일지)
 */
export function calculateDoHwaSal(baseJiji: JiJi): JiJi {
  const samhapGroup = SAMHAP_GROUP_MAP[baseJiji];
  return getDoHwaSal(samhapGroup);
}

/**
 * 역마살 단독 계산
 * @param baseJiji 기준 지지 (년지 또는 일지)
 */
export function calculateYeokMaSal(baseJiji: JiJi): JiJi {
  const samhapGroup = SAMHAP_GROUP_MAP[baseJiji];
  const firstJiji = SAMHAP_FIRST[samhapGroup];
  return getChungJiji(firstJiji);
}

/**
 * 화개살 단독 계산
 * @param baseJiji 기준 지지 (년지 또는 일지)
 */
export function calculateHwaGaeSal(baseJiji: JiJi): JiJi {
  const samhapGroup = SAMHAP_GROUP_MAP[baseJiji];
  return SAMHAP_LAST[samhapGroup];
}

export { SINSAL_INFO };
