/**
 * 사주 계산 패키지 - 타입 정의
 *
 * @author SajuApp
 * @version 1.0.0
 */

// ============================================================
// 기본 타입
// ============================================================

/** 천간(天干) - 10개 */
export type CheonGan = '갑' | '을' | '병' | '정' | '무' | '기' | '경' | '신' | '임' | '계';

/** 지지(地支) - 12개 */
export type JiJi = '자' | '축' | '인' | '묘' | '진' | '사' | '오' | '미' | '신' | '유' | '술' | '해';

/** 오행 */
export type OhHaeng = '목' | '화' | '토' | '금' | '수';

/** 성별 */
export type Gender = 'male' | 'female';

// ============================================================
// 사주 기둥 (Pillar)
// ============================================================

/** 사주의 기둥 (연월일시) - 기본 */
export interface SajuPillarBasic {
  gan: CheonGan;
  ji: JiJi;
}

/** 기둥 결과 (계산 후) */
export interface PillarResult {
  heavenly: string;  // 천간
  earthly: string;   // 지지
  combined: string;  // 천간+지지 (예: 갑자)
}

/** 사주 기둥 (확장) */
export interface SajuPillar {
  gan: CheonGan;       // 천간
  ji: JiJi;            // 지지
  ganJi: string;       // 합친 문자 (예: "갑자")
  ganOhHaeng: OhHaeng; // 천간 오행
  jiOhHaeng: OhHaeng;  // 지지 오행
}

export interface FourPillars {
  year: SajuPillar;    // 년주
  month: SajuPillar;   // 월주
  day: SajuPillar;     // 일주
  time: SajuPillar;    // 시주
}

// ============================================================
// 입력 타입
// ============================================================

/** 생년월일시 정보 */
export interface BirthInfo {
  year: number;
  month: number;
  day: number;
  hour: number;
  minute?: number;
  isLunar?: boolean;       // 음력 여부 (기본: false)
  isLeapMonth?: boolean;   // 윤달 여부 (음력일 때만)
  gender?: Gender;
}

// ============================================================
// 출력 타입
// ============================================================

/** 사주 팔자 (四柱八字) 결과 */
export interface FourPillarsResult {
  year: PillarResult;   // 년주
  month: PillarResult;  // 월주
  day: PillarResult;    // 일주
  hour: PillarResult;   // 시주
}

/** 오행 균형 */
export interface FiveElements {
  wood: number;   // 목
  fire: number;   // 화
  earth: number;  // 토
  metal: number;  // 금
  water: number;  // 수
}

/** 오행 균형 (한글) */
export interface OhHaengBalance {
  목: number;
  화: number;
  토: number;
  금: number;
  수: number;
}

/** 십성 (十星) */
export interface TenGods {
  bijeon: number;      // 비견
  geopjae: number;     // 겁재
  siksin: number;      // 식신
  sanggwan: number;    // 상관
  jeongjae: number;    // 정재
  pyeonjae: number;    // 편재
  jeonggwan: number;   // 정관
  pyeongwan: number;   // 편관
  jeongin: number;     // 정인
  pyeonin: number;     // 편인
}

// ============================================================
// 음력 변환 타입
// ============================================================

/** 음력 날짜 */
export interface LunarDate {
  year: number;
  month: number;
  day: number;
  isLeapMonth: boolean;
  zodiac?: string;       // 띠
  chineseYear?: string;  // 간지
}

// ============================================================
// 오행 분석
// ============================================================

export interface OhHaengAnalysis {
  balance: OhHaengBalance;     // 오행 점수
  dominant: OhHaeng;           // 가장 강한 오행
  weak: OhHaeng;               // 가장 약한 오행
  dominantScore: number;       // 강한 오행 점수
  weakScore: number;           // 약한 오행 점수
  isBalanced: boolean;         // 균형 여부
}

// ============================================================
// 십성 분석
// ============================================================

export interface SipSungBalance {
  비겁: number;   // 비견 + 겁재
  식상: number;   // 식신 + 상관
  재성: number;   // 정재 + 편재
  관성: number;   // 정관 + 편관
  인성: number;   // 정인 + 편인
}

export interface SipSungDetail {
  비견: number;
  겁재: number;
  식신: number;
  상관: number;
  정재: number;
  편재: number;
  정관: number;
  편관: number;
  정인: number;
  편인: number;
}

export interface SipSungAnalysis {
  balance: SipSungBalance;
  detail: SipSungDetail;
  dominant: keyof SipSungBalance;
  weak: keyof SipSungBalance;
}

// ============================================================
// 격국 분석
// ============================================================

export interface GyeokGukAnalysis {
  dayMaster: CheonGan;
  dayMasterOhHaeng: OhHaeng;
  strength: '신강' | '신약' | '중화';
  monthBranch: JiJi;
  season: '봄' | '여름' | '가을' | '겨울';
  gyeokGukType: string;
  description: string;
}

// ============================================================
// 용신/기신 분석
// ============================================================

export interface YongSinAnalysis {
  yongSin: OhHaeng[];
  giSin: OhHaeng[];
  huiSin: OhHaeng[];
  yongSinReason: string;
  giSinReason: string;
  yongSinScore: Record<OhHaeng, number>;
}

// ============================================================
// 대운
// ============================================================

export interface DaewoonItem {
  cycle: number;
  startAge: number;
  endAge: number;
  gan: CheonGan;
  ji: JiJi;
  ganJi: string;
  ohHaeng: OhHaeng;
  jiOhHaeng: OhHaeng;
  score: number;
  description: string;
  isYongSin: boolean;
  isGiSin: boolean;
}

export interface DaewoonAnalysis {
  startAge: number;
  direction: '순행' | '역행';
  list: DaewoonItem[];
  current: DaewoonItem | null;
  currentAge: number;
  bestPeriod: DaewoonItem | null;
  worstPeriod: DaewoonItem | null;
}

// ============================================================
// 세운
// ============================================================

export interface SewoonItem {
  year: number;
  age: number;
  gan: CheonGan;
  ji: JiJi;
  ganJi: string;
  ohHaeng: OhHaeng;
  animal: string;
  score: number;
  description: string;
  isYongSin: boolean;
  daewoonInteraction: number;
}

// ============================================================
// 신살 분석
// ============================================================

export interface SinsalAnalysis {
  gilSin: string[];
  hyungSin: string[];
  hasCheonEulGuiIn: boolean;
  hasMunChangGuiIn: boolean;
  hasYeokMaSal: boolean;
  hasDoHwaSal: boolean;
  hasGongMang: boolean;
  hasYangInSal: boolean;
  hasGeopSal: boolean;
  summary: string;
}

// ============================================================
// 관계 분석
// ============================================================

export interface PillarRelations {
  cheonganHap: string[];
  cheonganChung: string[];
  jijiYukHap: string[];
  jijiSamHap: string[];
  jijiChung: string[];
  jijiHyung: string[];
  jijiBan: string[];
  jijiPa: string[];
  jijiHae: string[];
  summary: string;
}

// ============================================================
// 성격/적성 분석
// ============================================================

export interface PersonalityAnalysis {
  dayMasterTraits: {
    keyword: string;
    strengths: string[];
    weaknesses: string[];
    advice: string;
  };
  dominantSipsung: {
    type: keyof SipSungBalance;
    traits: string[];
  };
  careerAptitude: string[];
  relationshipStyle: string;
}

// ============================================================
// 완전한 사주 데이터
// ============================================================

export interface CompleteSajuData {
  version: string;
  calculatedAt: string;
  isComplete: boolean;

  birthInfo: {
    year: number;
    month: number;
    day: number;
    hour: number;
    minute: number;
    gender: Gender;
    isLunar: boolean;
    birthDateString: string;
    birthTimeString: string;
  };

  fourPillars: FourPillars;
  fullSajuString: string;

  ohHaeng: OhHaengAnalysis;
  sipSung: SipSungAnalysis;
  gyeokGuk: GyeokGukAnalysis;
  yongSin: YongSinAnalysis;
  daewoon: DaewoonAnalysis;
  currentYearSewoon: SewoonItem;
  nextYearSewoon: SewoonItem;
  sinsal: SinsalAnalysis;
  relations: PillarRelations;
  personality: PersonalityAnalysis;

  // 레거시 호환
  year: { gan: CheonGan; ji: JiJi };
  month: { gan: CheonGan; ji: JiJi };
  day: { gan: CheonGan; ji: JiJi };
  time: { gan: CheonGan; ji: JiJi };
  ohHaengBalance: OhHaengBalance;
  sipSungBalance: SipSungBalance;
  fullSaju: string;
  tenGods: SipSungDetail;
  fiveElements: FiveElements;
}

// ============================================================
// 타입 가드
// ============================================================

export function isCompleteSajuData(data: any): data is CompleteSajuData {
  return data &&
    data.isComplete === true &&
    data.version !== undefined &&
    data.fourPillars !== undefined &&
    data.daewoon !== undefined;
}

export function hasMinimalSajuData(data: any): boolean {
  return data &&
    data.year?.gan !== undefined &&
    data.month?.gan !== undefined &&
    data.day?.gan !== undefined &&
    data.time?.gan !== undefined;
}
