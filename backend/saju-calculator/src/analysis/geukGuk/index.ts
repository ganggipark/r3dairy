/**
 * 격국(格局) 계산 모듈
 *
 * 명리학 정통 계산법 기반:
 * - 월지 지장간의 투출 여부로 격국 결정
 * - 정격(正格) 8격: 정관격, 편관격, 정인격, 편인격, 정재격, 편재격, 식신격, 상관격
 * - 변격(變格): 전록격, 양인격, 건록격, 종격 등
 *
 * 참고: 자평진전, 연해자평, 명리정종
 */

import type { CheonGan, JiJi } from '../../types/saju';

// ==========================================
// 기본 타입 정의
// ==========================================

/** 격국 타입 */
export type GeukGukType =
  | '정관격' | '편관격' | '정인격' | '편인격'
  | '정재격' | '편재격' | '식신격' | '상관격'
  | '건록격' | '양인격' | '종아격' | '종재격' | '종관격' | '종살격' | '잡격'
  | '화토격' | '화금격' | '화수격' | '화목격' | '화화격';

/** 십성 타입 */
export type SipseongType =
  | '비견' | '겁재' | '식신' | '상관'
  | '편재' | '정재' | '편관' | '정관'
  | '편인' | '정인';

/** 투출 결과 */
export interface TouchulResult {
  isTouchul: boolean;
  touchulGan: CheonGan[];
  mainGan: CheonGan | null;
}

/** 격국 판단 결과 */
export interface GeukGukResult {
  geukguk: GeukGukType;
  monthSipseong: SipseongType | null;
  isJeongGyeok: boolean; // 정격 여부
  touchulGan: CheonGan[];
  description: string;
}

/** 격국 상세 분석 결과 */
export interface GeukGukAnalysis {
  geukguk: GeukGukType;
  monthSipseong: SipseongType | null;
  touchulInfo: TouchulResult;
  characteristics: string[];
  isComplete: boolean; // 격국 성립 여부
  score: number;
  analysis: string;
}

/** 격국 계산 입력 */
export interface GeukGukInput {
  dayGan: CheonGan;
  monthJi: JiJi;
  fourPillarGan: CheonGan[];
  fourPillarJi: JiJi[];
}

/** 화기격 판단 결과 */
export interface HwaGiGyeokResult {
  /** 화기격 여부 */
  isHwaGiGyeok: boolean;
  /** 화기격 타입 */
  hwaGiGyeokType: '화토격' | '화금격' | '화수격' | '화목격' | '화화격' | null;
  /** 합 조합 (일간 + 월간/시간) */
  combinationPair: [CheonGan, CheonGan] | null;
  /** 변화된 오행 */
  transformedElement: string | null;
  /** 완전 성립 여부 (월지 계절 일치) */
  isComplete: boolean;
  /** 해석 */
  interpretation: string;
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

/** 지장간 본기 테이블 */
const JIJANGGAN_MAIN: Record<JiJi, CheonGan> = {
  '자': '계',
  '축': '기',
  '인': '갑',
  '묘': '을',
  '진': '무',
  '사': '병',
  '오': '정',
  '미': '기',
  '신': '경',
  '유': '신',
  '술': '무',
  '해': '임',
};

/** 지장간 전체 테이블 (본기, 중기, 여기) */
const JIJANGGAN_ALL: Record<JiJi, CheonGan[]> = {
  '자': ['계'],
  '축': ['기', '계', '신'],
  '인': ['갑', '병', '무'],
  '묘': ['을'],
  '진': ['무', '을', '계'],
  '사': ['병', '무', '경'],
  '오': ['정', '기'],
  '미': ['기', '정', '을'],
  '신': ['경', '임', '무'],
  '유': ['신'],
  '술': ['무', '신', '정'],
  '해': ['임', '갑'],
};

/** 일간의 건록지 */
const GAN_GEUNROK: Record<CheonGan, JiJi> = {
  '갑': '인', '을': '묘',
  '병': '사', '정': '오',
  '무': '사', '기': '오',
  '경': '신', '신': '유',
  '임': '해', '계': '자',
};

/** 일간의 양인지 (록의 다음) */
const GAN_YANGIN: Record<CheonGan, JiJi> = {
  '갑': '묘', '을': '진',
  '병': '오', '정': '미',
  '무': '오', '기': '미',
  '경': '유', '신': '술',
  '임': '자', '계': '축',
};

/**
 * 천간합(天干合) 테이블
 *
 * 명리학에서 특정 천간 쌍이 만나면 합(合)하여 새로운 오행으로 화(化)합니다.
 * 이는 화기격(化氣格) 판단의 핵심입니다.
 *
 * 오합(五合):
 * - 갑+기(甲己) → 토(土) 합화
 * - 을+경(乙庚) → 금(金) 합화
 * - 병+신(丙辛) → 수(水) 합화
 * - 정+임(丁壬) → 목(木) 합화
 * - 무+계(戊癸) → 화(火) 합화
 */
type HwaGiGyeokType = '화토격' | '화금격' | '화수격' | '화목격' | '화화격';

const CHEONGAN_HOP: Record<string, { pair: [CheonGan, CheonGan]; transformTo: string; geukguk: HwaGiGyeokType }> = {
  '갑기': { pair: ['갑', '기'], transformTo: '토', geukguk: '화토격' },
  '기갑': { pair: ['갑', '기'], transformTo: '토', geukguk: '화토격' },
  '을경': { pair: ['을', '경'], transformTo: '금', geukguk: '화금격' },
  '경을': { pair: ['을', '경'], transformTo: '금', geukguk: '화금격' },
  '병신': { pair: ['병', '신'], transformTo: '수', geukguk: '화수격' },
  '신병': { pair: ['병', '신'], transformTo: '수', geukguk: '화수격' },
  '정임': { pair: ['정', '임'], transformTo: '목', geukguk: '화목격' },
  '임정': { pair: ['정', '임'], transformTo: '목', geukguk: '화목격' },
  '무계': { pair: ['무', '계'], transformTo: '화', geukguk: '화화격' },
  '계무': { pair: ['무', '계'], transformTo: '화', geukguk: '화화격' },
};

/**
 * 월지별 왕성한 오행 (계절 특성)
 *
 * 화기격이 완전히 성립하려면 합화된 오행이 월지의 계절과 일치해야 합니다.
 * 예: 갑기합토는 진술축미월(토왕절)에만 진정한 화토격이 됩니다.
 */
const MONTH_ELEMENT_SEASON: Record<JiJi, string> = {
  '인': '목', '묘': '목',  // 봄 - 목왕
  '사': '화', '오': '화',  // 여름 - 화왕
  '신': '금', '유': '금',  // 가을 - 금왕
  '해': '수', '자': '수',  // 겨울 - 수왕
  '진': '토', '술': '토', '축': '토', '미': '토',  // 사계토 - 토왕
};

/** 격국 순서 */
export const GEUKGUK_ORDER: GeukGukType[] = [
  '화토격', '화금격', '화수격', '화목격', '화화격',  // 화기격 (최우선)
  '정관격', '편관격', '정인격', '편인격',
  '정재격', '편재격', '식신격', '상관격',
  '건록격', '양인격', '종아격', '종재격', '종관격', '종살격', '잡격',
];

/** 격국 정보 */
export const GEUKGUK_INFO: Record<GeukGukType, { description: string; characteristics: string[] }> = {
  '화토격': {
    description: '화토격(化土格)은 일간이 천간합을 통해 토(土)로 화(化)하는 특수 격국입니다. 갑기합토(甲己合土)로 토왕절(辰戌丑未월)에 태어나면 진정한 화토격이 됩니다.',
    characteristics: ['중후함', '신뢰성', '포용력', '안정감', '조화'],
  },
  '화금격': {
    description: '화금격(化金格)은 일간이 천간합을 통해 금(金)으로 화(化)하는 특수 격국입니다. 을경합금(乙庚合金)으로 금왕절(申酉월)에 태어나면 진정한 화금격이 됩니다.',
    characteristics: ['강직함', '결단력', '의리', '명예감', '원칙'],
  },
  '화수격': {
    description: '화수격(化水格)은 일간이 천간합을 통해 수(水)로 화(化)하는 특수 격국입니다. 병신합수(丙辛合水)로 수왕절(亥子월)에 태어나면 진정한 화수격이 됩니다.',
    characteristics: ['지혜', '유연성', '통찰력', '변통', '적응력'],
  },
  '화목격': {
    description: '화목격(化木格)은 일간이 천간합을 통해 목(木)으로 화(化)하는 특수 격국입니다. 정임합목(丁壬合木)으로 목왕절(寅卯월)에 태어나면 진정한 화목격이 됩니다.',
    characteristics: ['성장성', '발전', '인자함', '창의력', '확장'],
  },
  '화화격': {
    description: '화화격(化火格)은 일간이 천간합을 통해 화(火)로 화(化)하는 특수 격국입니다. 무계합화(戊癸合火)로 화왕절(巳午월)에 태어나면 진정한 화화격이 됩니다.',
    characteristics: ['열정', '활력', '리더십', '카리스마', '창조력'],
  },
  '정관격': {
    description: '정관격은 월지의 정관이 투출하여 격을 이룬 것으로, 질서와 규범을 중시하는 성격입니다.',
    characteristics: ['책임감', '조직력', '명예욕', '보수적', '원칙주의'],
  },
  '편관격': {
    description: '편관격(칠살격)은 월지의 편관이 투출하여 격을 이룬 것으로, 강인하고 도전적인 성격입니다.',
    characteristics: ['결단력', '추진력', '권위', '승부욕', '직선적'],
  },
  '정인격': {
    description: '정인격은 월지의 정인이 투출하여 격을 이룬 것으로, 학문과 인덕을 중시하는 성격입니다.',
    characteristics: ['학구적', '인자함', '보호본능', '전통중시', '명예'],
  },
  '편인격': {
    description: '편인격(효신격)은 월지의 편인이 투출하여 격을 이룬 것으로, 창의적이고 독창적인 성격입니다.',
    characteristics: ['창의력', '직관력', '독립심', '비범함', '고독'],
  },
  '정재격': {
    description: '정재격은 월지의 정재가 투출하여 격을 이룬 것으로, 안정과 실리를 중시하는 성격입니다.',
    characteristics: ['안정추구', '실리적', '성실함', '절약', '가정적'],
  },
  '편재격': {
    description: '편재격은 월지의 편재가 투출하여 격을 이룬 것으로, 활동적이고 사교적인 성격입니다.',
    characteristics: ['활동력', '사교성', '모험심', '투자', '인맥'],
  },
  '식신격': {
    description: '식신격은 월지의 식신이 투출하여 격을 이룬 것으로, 온화하고 여유로운 성격입니다.',
    characteristics: ['온화함', '여유', '낙천적', '재능', '표현력'],
  },
  '상관격': {
    description: '상관격은 월지의 상관이 투출하여 격을 이룬 것으로, 개성적이고 예술적인 성격입니다.',
    characteristics: ['개성', '예술성', '비판적', '자유분방', '감수성'],
  },
  '건록격': {
    description: '건록격은 월지가 일간의 록지에 해당하는 것으로, 자수성가형 성격입니다.',
    characteristics: ['자립심', '독립성', '실력주의', '자존심', '노력형'],
  },
  '양인격': {
    description: '양인격은 월지가 일간의 양인에 해당하는 것으로, 강인하고 결단력 있는 성격입니다.',
    characteristics: ['강인함', '결단력', '승부욕', '직선적', '무던함'],
  },
  '종아격': {
    description: '종아격은 일간이 약하여 식상을 따르는 격으로, 재능 발휘형 성격입니다.',
    characteristics: ['재능형', '표현력', '창작력', '유연성', '감성'],
  },
  '종재격': {
    description: '종재격은 일간이 약하여 재성을 따르는 격으로, 현실적이고 실리적인 성격입니다.',
    characteristics: ['현실적', '실리주의', '융통성', '재테크', '적응력'],
  },
  '종관격': {
    description: '종관격은 일간이 약하여 정관을 따르는 격으로, 질서와 조직을 따르는 성격입니다.',
    characteristics: ['조직순응', '책임감', '안정지향', '명예', '충성심'],
  },
  '종살격': {
    description: '종살격은 일간이 약하여 관살을 따르는 격으로, 권위와 지위를 추구하는 성격입니다.',
    characteristics: ['권위추구', '야심', '조직적', '명예욕', '충성'],
  },
  '잡격': {
    description: '잡격은 특정 격국으로 분류하기 어려운 복합적인 구조입니다.',
    characteristics: ['다양성', '복합적', '변화무쌍', '다재다능', '유연함'],
  },
};

// ==========================================
// 월지 지장간 본기 추출
// ==========================================

/**
 * 월지의 본기(主氣) 천간 반환
 * @param monthJi 월지
 * @returns 본기 천간
 */
export function getMonthlyMainGan(monthJi: JiJi): CheonGan {
  return JIJANGGAN_MAIN[monthJi];
}

// ==========================================
// 투출(透出) 확인
// ==========================================

/**
 * 월지 지장간의 투출 여부 확인
 * @param monthJi 월지
 * @param fourPillarGan 4주의 천간
 * @returns 투출 결과
 */
export function checkTouchul(monthJi: JiJi, fourPillarGan: CheonGan[]): TouchulResult {
  const jijanggan = JIJANGGAN_ALL[monthJi];
  const touchulGan: CheonGan[] = [];

  for (const gan of jijanggan) {
    if (fourPillarGan.includes(gan)) {
      touchulGan.push(gan);
    }
  }

  return {
    isTouchul: touchulGan.length > 0,
    touchulGan,
    mainGan: touchulGan.length > 0 ? touchulGan[0] : null,
  };
}

// ==========================================
// 십성 계산
// ==========================================

/**
 * 일간과 다른 천간의 십성 관계 계산
 * @param dayGan 일간
 * @param targetGan 대상 천간
 * @returns 십성
 */
function getSipseong(dayGan: CheonGan, targetGan: CheonGan): SipseongType {
  const dayElement = GAN_TO_ELEMENT[dayGan];
  const dayYinYang = GAN_YIN_YANG[dayGan];
  const targetElement = GAN_TO_ELEMENT[targetGan];
  const targetYinYang = GAN_YIN_YANG[targetGan];

  const isSameYinYang = dayYinYang === targetYinYang;

  // 오행 상생상극 관계
  const generates: Record<string, string> = {
    '목': '화', '화': '토', '토': '금', '금': '수', '수': '목',
  };
  const controls: Record<string, string> = {
    '목': '토', '화': '금', '토': '수', '금': '목', '수': '화',
  };

  // 비겁 (같은 오행)
  if (dayElement === targetElement) {
    return isSameYinYang ? '비견' : '겁재';
  }

  // 식상 (내가 생하는 오행)
  if (generates[dayElement] === targetElement) {
    return isSameYinYang ? '식신' : '상관';
  }

  // 재성 (내가 극하는 오행)
  if (controls[dayElement] === targetElement) {
    return isSameYinYang ? '편재' : '정재';
  }

  // 관성 (나를 극하는 오행)
  if (controls[targetElement] === dayElement) {
    return isSameYinYang ? '편관' : '정관';
  }

  // 인성 (나를 생하는 오행)
  if (generates[targetElement] === dayElement) {
    return isSameYinYang ? '편인' : '정인';
  }

  // 기본값 (이론적으로 도달 불가)
  return '비견';
}

/**
 * 십성을 격국으로 변환
 * @param sipseong 십성
 * @returns 격국
 */
function sipseongToGeukguk(sipseong: SipseongType): GeukGukType {
  const mapping: Record<SipseongType, GeukGukType> = {
    '정관': '정관격',
    '편관': '편관격',
    '정인': '정인격',
    '편인': '편인격',
    '정재': '정재격',
    '편재': '편재격',
    '식신': '식신격',
    '상관': '상관격',
    '비견': '잡격',
    '겁재': '잡격',
  };
  return mapping[sipseong];
}

// ==========================================
// 화기격(化氣格) 판단
// ==========================================

/**
 * 화기격(化氣格) 판단
 *
 * 화기격은 일간이 다른 천간과 합(合)하여 새로운 오행으로 화(化)하는 특수 격국입니다.
 *
 * 성립 조건:
 * 1. 일간이 월간 또는 시간과 천간합(天干合) 형성
 *    - 갑+기 → 토, 을+경 → 금, 병+신 → 수, 정+임 → 목, 무+계 → 화
 * 2. 합화된 오행이 월지의 계절과 일치해야 진정한 화기격 (isComplete = true)
 *    - 화토격: 진술축미월(토왕절)
 *    - 화금격: 신유월(금왕절)
 *    - 화수격: 해자월(수왕절)
 *    - 화목격: 인묘월(목왕절)
 *    - 화화격: 사오월(화왕절)
 * 3. 화신(化神)을 극하는 오행이 없어야 완전 성립
 *
 * 참고: 자평진전, 연해자평의 화기격 이론
 *
 * @param input 격국 계산 입력
 * @returns 화기격 판단 결과
 */
export function checkHwaGiGyeok(input: GeukGukInput): HwaGiGyeokResult {
  const { dayGan, monthJi, fourPillarGan } = input;

  // 월간(1번 인덱스)과 시간(3번 인덱스) 확인
  const monthGan = fourPillarGan[1];
  const hourGan = fourPillarGan[3];

  // 1. 일간 + 월간 합 확인
  const monthKey = dayGan + monthGan;
  const monthHop = CHEONGAN_HOP[monthKey];

  // 2. 일간 + 시간 합 확인
  const hourKey = dayGan + hourGan;
  const hourHop = CHEONGAN_HOP[hourKey];

  // 천간합이 없으면 화기격 아님
  if (!monthHop && !hourHop) {
    return {
      isHwaGiGyeok: false,
      hwaGiGyeokType: null,
      combinationPair: null,
      transformedElement: null,
      isComplete: false,
      interpretation: '일간과 월간/시간 사이에 천간합이 없어 화기격이 성립하지 않습니다.',
    };
  }

  // 우선순위: 월간 합 > 시간 합
  const hop = monthHop || hourHop;
  const combinationGan = monthHop ? monthGan : hourGan;
  const combinationPosition = monthHop ? '월간' : '시간';

  if (!hop) {
    return {
      isHwaGiGyeok: false,
      hwaGiGyeokType: null,
      combinationPair: null,
      transformedElement: null,
      isComplete: false,
      interpretation: '천간합이 없습니다.',
    };
  }

  const { pair, transformTo, geukguk } = hop;

  // 3. 월지 계절과 합화 오행 일치 확인
  const monthSeason = MONTH_ELEMENT_SEASON[monthJi];
  const isSeasonMatch = monthSeason === transformTo;

  // 4. 화신을 극하는 오행 확인 (파격 체크)
  // 극하는 관계: 목극토, 토극수, 수극화, 화극금, 금극목
  const controls: Record<string, string> = {
    '목': '토', '토': '수', '수': '화', '화': '금', '금': '목',
  };

  // 사주 전체에서 화신을 극하는 오행이 있는지 확인
  // 단, 합을 이루는 두 천간은 이미 화(化)했으므로 제외
  const hasBreaker = fourPillarGan.some((gan, idx) => {
    if (idx === 2) return false; // 일간 제외 (합의 주체)
    if (gan === combinationGan) return false; // 합의 상대 제외
    const ganElement = GAN_TO_ELEMENT[gan];
    return controls[ganElement] === transformTo;
  });

  // 5. 완전 성립 여부 판단
  const isComplete = isSeasonMatch && !hasBreaker;

  // 6. 해석 생성
  let interpretation = `${dayGan}일간과 ${combinationPosition} ${combinationGan}이(가) ${pair[0]}${pair[1]}합${transformTo}(合${transformTo.toUpperCase()})하여 ${geukguk}이 형성됩니다.`;

  if (isComplete) {
    interpretation += ` 월지 ${monthJi}가 ${transformTo}왕절이고 파격 요소가 없어 진정한 ${geukguk}이 완전 성립합니다.`;
  } else if (!isSeasonMatch) {
    interpretation += ` 다만 월지 ${monthJi}가 ${monthSeason}왕절이므로 불완전한 ${geukguk}입니다.`;
  } else if (hasBreaker) {
    interpretation += ` 다만 화신 ${transformTo}를 극하는 오행이 있어 불완전한 ${geukguk}입니다.`;
  }

  return {
    isHwaGiGyeok: true,
    hwaGiGyeokType: geukguk as '화토격' | '화금격' | '화수격' | '화목격' | '화화격',
    combinationPair: pair,
    transformedElement: transformTo,
    isComplete,
    interpretation,
  };
}

// ==========================================
// 종격(從格) 판단
// ==========================================

/** 일간 강약 타입 */
export type DayMasterStrength = 'extreme_weak' | 'weak' | 'normal' | 'strong';

/** 종격 판단 결과 */
export interface JongGyeokResult {
  /** 종격 여부 */
  isJongGyeok: boolean;
  /** 종격 타입 */
  jongGyeokType: '종아격' | '종재격' | '종관격' | '종살격' | null;
  /** 일간 강약 */
  dayMasterStrength: DayMasterStrength;
  /** 압도적 오행 */
  dominantElement: string | null;
  /** 해석 */
  interpretation: string;
}

/**
 * 종격(從格) 판단
 *
 * 종격 성립 조건:
 * 1. 일간이 무근(無根): 지지에 일간과 같은 오행의 뿌리가 없음
 * 2. 일간이 무조(無助): 천간에 비겁/인성의 도움이 없음
 * 3. 특정 십성이 압도적(3개 이상)
 *
 * 종격 종류:
 * - 종아격(從兒格): 식상이 압도적
 * - 종재격(從財格): 재성이 압도적
 * - 종관격(從官格): 정관이 압도적
 * - 종살격(從殺格): 편관(칠살)이 압도적
 *
 * @param input 격국 계산 입력
 * @returns 종격 판단 결과
 */
export function checkJongGyeok(input: GeukGukInput): JongGyeokResult {
  const { dayGan, fourPillarGan, fourPillarJi } = input;

  const dayElement = GAN_TO_ELEMENT[dayGan];

  // 십성별 개수 카운트
  const sipseongCount: Record<SipseongType, number> = {
    '비견': 0, '겁재': 0, '식신': 0, '상관': 0,
    '편재': 0, '정재': 0, '편관': 0, '정관': 0,
    '편인': 0, '정인': 0,
  };

  // 1. 천간 십성 카운트 (일간 제외)
  for (let i = 0; i < fourPillarGan.length; i++) {
    if (i === 2) continue; // 일간 제외
    const gan = fourPillarGan[i];
    const sipseong = getSipseong(dayGan, gan);
    sipseongCount[sipseong]++;
  }

  // 2. 지지 본기 십성 카운트
  for (const ji of fourPillarJi) {
    const mainGan = JIJANGGAN_MAIN[ji];
    const sipseong = getSipseong(dayGan, mainGan);
    sipseongCount[sipseong]++;
  }

  // 3. 일간 뿌리 확인 (무근 체크)
  // 지지에 일간과 같은 오행이 있는지 확인
  const hasRoot = fourPillarJi.some(ji => {
    const mainGan = JIJANGGAN_MAIN[ji];
    return GAN_TO_ELEMENT[mainGan] === dayElement;
  });

  // 4. 비겁/인성 도움 확인 (무조 체크)
  const supportCount =
    sipseongCount['비견'] +
    sipseongCount['겁재'] +
    sipseongCount['정인'] +
    sipseongCount['편인'];

  const hasSupport = supportCount > 0;

  // 5. 일간 강약 판단
  let dayMasterStrength: DayMasterStrength;
  if (!hasRoot && !hasSupport) {
    dayMasterStrength = 'extreme_weak'; // 무근무조
  } else if (!hasRoot || supportCount <= 1) {
    dayMasterStrength = 'weak';
  } else if (supportCount >= 3) {
    dayMasterStrength = 'strong';
  } else {
    dayMasterStrength = 'normal';
  }

  // 6. 종격 판단 (일간이 극히 약해야 함)
  if (dayMasterStrength !== 'extreme_weak') {
    return {
      isJongGyeok: false,
      jongGyeokType: null,
      dayMasterStrength,
      dominantElement: null,
      interpretation: '일간이 무근무조가 아니므로 종격이 성립하지 않습니다.',
    };
  }

  // 7. 압도적 십성 확인 (3개 이상)
  const sikSangCount = sipseongCount['식신'] + sipseongCount['상관'];
  const jaeSeongCount = sipseongCount['정재'] + sipseongCount['편재'];
  const jeongGwanCount = sipseongCount['정관'];
  const pyeonGwanCount = sipseongCount['편관'];

  // 우선순위: 식상 > 재성 > 정관 > 편관
  if (sikSangCount >= 3) {
    return {
      isJongGyeok: true,
      jongGyeokType: '종아격',
      dayMasterStrength,
      dominantElement: '식상',
      interpretation: `일간이 무근무조하고 식상이 ${sikSangCount}개로 압도적이어서 종아격(從兒格)이 성립합니다.`,
    };
  }

  if (jaeSeongCount >= 3) {
    return {
      isJongGyeok: true,
      jongGyeokType: '종재격',
      dayMasterStrength,
      dominantElement: '재성',
      interpretation: `일간이 무근무조하고 재성이 ${jaeSeongCount}개로 압도적이어서 종재격(從財格)이 성립합니다.`,
    };
  }

  if (jeongGwanCount >= 3) {
    return {
      isJongGyeok: true,
      jongGyeokType: '종관격',
      dayMasterStrength,
      dominantElement: '정관',
      interpretation: `일간이 무근무조하고 정관이 ${jeongGwanCount}개로 압도적이어서 종관격(從官格)이 성립합니다.`,
    };
  }

  if (pyeonGwanCount >= 3) {
    return {
      isJongGyeok: true,
      jongGyeokType: '종살격',
      dayMasterStrength,
      dominantElement: '편관',
      interpretation: `일간이 무근무조하고 편관이 ${pyeonGwanCount}개로 압도적이어서 종살격(從殺格)이 성립합니다.`,
    };
  }

  // 일간이 극히 약하지만 압도적 십성이 없음
  return {
    isJongGyeok: false,
    jongGyeokType: null,
    dayMasterStrength,
    dominantElement: null,
    interpretation: '일간이 무근무조하나 압도적인 십성이 없어 종격이 성립하지 않습니다.',
  };
}

// ==========================================
// 격국 판단
// ==========================================

/**
 * 격국 판단
 * @param input 격국 계산 입력
 * @returns 격국 판단 결과
 */
export function determineGeukGuk(input: GeukGukInput): GeukGukResult {
  const { dayGan, monthJi, fourPillarGan, fourPillarJi: _fourPillarJi } = input;

  // 1. 건록격 확인 (월지가 일간의 록지) - 최우선
  if (monthJi === GAN_GEUNROK[dayGan]) {
    return {
      geukguk: '건록격',
      monthSipseong: '비견',
      isJeongGyeok: false,
      touchulGan: [],
      description: `${dayGan}일간이 ${monthJi}월(록지)에 태어나 건록격입니다.`,
    };
  }

  // 2. 양인격 확인 (월지가 일간의 양인지) - 최우선
  if (monthJi === GAN_YANGIN[dayGan]) {
    return {
      geukguk: '양인격',
      monthSipseong: '겁재',
      isJeongGyeok: false,
      touchulGan: [],
      description: `${dayGan}일간이 ${monthJi}월(양인)에 태어나 양인격입니다.`,
    };
  }

  // 3. 월지 본기 확인 및 십성 계산
  const monthMainGan = getMonthlyMainGan(monthJi);
  const monthSipseong = getSipseong(dayGan, monthMainGan);
  const touchulResult = checkTouchul(monthJi, fourPillarGan);

  // 4. 정격 판단 (월지 본기가 비겁이 아닌 경우)
  // 정격은 월지 본기가 투출되었을 때 우선 성립
  if (monthSipseong !== '비견' && monthSipseong !== '겁재') {
    // 월지 본기가 천간에 투출되면 정격 우선
    if (touchulResult.isTouchul && touchulResult.touchulGan.includes(monthMainGan)) {
      const geukguk = sipseongToGeukguk(monthSipseong);
      return {
        geukguk,
        monthSipseong,
        isJeongGyeok: true,
        touchulGan: touchulResult.touchulGan,
        description: `${dayGan}일간이 ${monthJi}월에 태어나 월지 본기 ${monthMainGan}이(가) 투출하여 ${geukguk}입니다.`,
      };
    }
  }

  // 5. 화기격 확인 (천간합으로 인한 특수 격국)
  // 월지 본기가 투출되지 않았을 때 화기격 체크
  const hwaGiGyeokResult = checkHwaGiGyeok(input);
  if (hwaGiGyeokResult.isHwaGiGyeok && hwaGiGyeokResult.hwaGiGyeokType) {
    return {
      geukguk: hwaGiGyeokResult.hwaGiGyeokType,
      monthSipseong: null,
      isJeongGyeok: false,  // 화기격은 특수 격국
      touchulGan: [],
      description: hwaGiGyeokResult.interpretation,
    };
  }

  // 6. 종격 확인 (일간이 극히 약한 특수 격국)
  const jongGyeokResult = checkJongGyeok(input);
  if (jongGyeokResult.isJongGyeok && jongGyeokResult.jongGyeokType) {
    return {
      geukguk: jongGyeokResult.jongGyeokType,
      monthSipseong: null,
      isJeongGyeok: false,
      touchulGan: [],
      description: jongGyeokResult.interpretation,
    };
  }

  // 7. 비견/겁재 처리 (특수 격국)
  if (monthSipseong === '비견' || monthSipseong === '겁재') {
    return {
      geukguk: '잡격',
      monthSipseong,
      isJeongGyeok: false,
      touchulGan: touchulResult.touchulGan,
      description: '월지의 본기가 비겁으로 특수 격국입니다.',
    };
  }

  // 8. 정격 기본 성립 (투출 없어도 월지 본기로 정격 성립)
  const geukguk = sipseongToGeukguk(monthSipseong);
  return {
    geukguk,
    monthSipseong,
    isJeongGyeok: true,
    touchulGan: touchulResult.touchulGan,
    description: `${dayGan}일간이 ${monthJi}월에 태어나 ${geukguk}입니다.`,
  };
}

// ==========================================
// 격국 상세 분석
// ==========================================

/**
 * 격국 상세 분석
 * @param input 격국 계산 입력
 * @returns 상세 분석 결과
 */
export function analyzeGeukGukDetails(input: GeukGukInput): GeukGukAnalysis {
  const { dayGan, monthJi, fourPillarGan, fourPillarJi: _fourPillarJi } = input;

  const geukgukResult = determineGeukGuk(input);
  const touchulInfo = checkTouchul(monthJi, fourPillarGan);

  // 격국 성립 여부 판단
  // 정격은 투출이 있어야 완전한 성립
  const isComplete = geukgukResult.isJeongGyeok
    ? touchulInfo.isTouchul
    : true; // 변격은 투출 불필요

  // 격국 점수 계산
  let score = 50; // 기본 점수
  if (geukgukResult.isJeongGyeok) {
    score += 20; // 정격 가산
    if (touchulInfo.isTouchul) {
      score += 15; // 투출 가산
      score += touchulInfo.touchulGan.length * 5; // 투출 개수당 가산
    }
  } else {
    score += 10; // 변격 가산
  }
  score = Math.min(100, Math.max(0, score));

  // 특성
  const characteristics = GEUKGUK_INFO[geukgukResult.geukguk].characteristics;

  // 분석 텍스트 생성
  let analysis = '### 격국 분석\n\n';
  analysis += `**일간**: ${dayGan}\n`;
  analysis += `**월지**: ${monthJi}\n`;
  analysis += `**격국**: ${geukgukResult.geukguk}\n\n`;
  analysis += `**설명**: ${GEUKGUK_INFO[geukgukResult.geukguk].description}\n\n`;
  analysis += `**특성**: ${characteristics.join(', ')}\n\n`;
  analysis += `**투출**: ${touchulInfo.isTouchul ? touchulInfo.touchulGan.join(', ') : '없음'}\n`;
  analysis += `**격국 성립**: ${isComplete ? '완전 성립' : '불완전'}\n`;
  analysis += `**점수**: ${score}점\n`;

  return {
    geukguk: geukgukResult.geukguk,
    monthSipseong: geukgukResult.monthSipseong,
    touchulInfo,
    characteristics,
    isComplete,
    score,
    analysis,
  };
}
