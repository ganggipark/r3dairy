/**
 * 완전한 사주 데이터 타입 정의
 *
 * 모든 AI 응답 및 분석에 필요한 데이터를 포함
 * Customer.saju_data의 새로운 표준 구조
 *
 * @author Claude Code
 * @version 1.0.0
 */

import type { BodyStrengthAnalysis } from '../analysis/bodyStrength';

// ============================================================
// 기본 타입
// ============================================================

export type CheonGan = '갑' | '을' | '병' | '정' | '무' | '기' | '경' | '신' | '임' | '계';
export type JiJi = '자' | '축' | '인' | '묘' | '진' | '사' | '오' | '미' | '신' | '유' | '술' | '해';
export type OhHaeng = '목' | '화' | '토' | '금' | '수';
export type Gender = 'male' | 'female';

// ============================================================
// 사주 기둥 (Pillar)
// ============================================================

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
// 오행 분석
// ============================================================

export interface OhHaengBalance {
  목: number;
  화: number;
  토: number;
  금: number;
  수: number;
}

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
  balance: SipSungBalance;     // 그룹별 합계
  detail: SipSungDetail;       // 개별 십성
  dominant: keyof SipSungBalance;  // 가장 강한 십성 그룹
  weak: keyof SipSungBalance;      // 가장 약한 십성 그룹
}

// ============================================================
// 격국 분석
// ============================================================

export interface GyeokGukAnalysis {
  dayMaster: CheonGan;              // 일간
  dayMasterOhHaeng: OhHaeng;        // 일간 오행
  strength: '신강' | '신약' | '중화';  // 일간 강약
  monthBranch: JiJi;                // 월지 (월령)
  season: '봄' | '여름' | '가을' | '겨울';
  gyeokGukType: string;             // 격국 유형 (정관격, 편관격, 식신격 등)
  description: string;              // 격국 설명

  // 통관용신 분석
  tonggwanYongshin?: {
    hasConflict: boolean;
    conflictPair: [OhHaeng, OhHaeng] | null;
    tonggwanElement: OhHaeng | null;
    strength: 'strong' | 'weak' | 'absent';
    interpretation: string;
  };

  // 종격 분석
  jongGyeok?: {
    isJongGyeok: boolean;
    jongGyeokType: '종아격' | '종재격' | '종관격' | '종살격' | null;
    dominantElement: string | null;
    interpretation: string;
  };

  // 화기격 분석
  hwaGiGyeok?: {
    isHwaGiGyeok: boolean;
    hwaGiGyeokType: '화토격' | '화금격' | '화수격' | '화목격' | '화화격' | null;
    combinationPair: [CheonGan, CheonGan] | null;
    transformedElement: OhHaeng | null;
    isComplete: boolean;
    interpretation: string;
  };

  // Optional: Detailed body strength analysis
  strengthDetail?: string;
  strengthScore?: number;
  strengthGrade?: '극신강' | '신강' | '중화' | '신약' | '극신약';
}

// ============================================================
// 용신/기신 분석
// ============================================================

export interface YongSinAnalysis {
  yongSin: OhHaeng[];           // 용신 (필요한 오행)
  giSin: OhHaeng[];             // 기신 (피해야 할 오행)
  huiSin: OhHaeng[];            // 희신 (용신을 돕는 오행)
  yongSinReason: string;        // 용신 선정 이유
  giSinReason: string;          // 기신 선정 이유
  yongSinScore: Record<OhHaeng, number>;  // 오행별 길흉 점수
}

// ============================================================
// 대운 (10년 운)
// ============================================================

export interface DaewoonItem {
  cycle: number;          // 대운 순서 (0=초년운, 1=1대운, ...)
  startAge: number;       // 시작 나이
  endAge: number;         // 종료 나이
  gan: CheonGan;          // 천간
  ji: JiJi;               // 지지
  ganJi: string;          // 합친 문자
  ohHaeng: OhHaeng;       // 천간 오행
  jiOhHaeng: OhHaeng;     // 지지 오행
  score: number;          // 대운 점수 (0-100)
  description: string;    // 대운 설명
  isYongSin: boolean;     // 용신 대운 여부
  isGiSin: boolean;       // 기신 대운 여부
}

export interface DaewoonAnalysis {
  startAge: number;               // 대운 시작 나이
  startAgeDecimal?: number;       // 소수점 시작 나이 (예: 6.3세)
  daysToJeolip?: number;          // 절입일까지 일수
  direction: '순행' | '역행';     // 순역행
  list: DaewoonItem[];            // 대운 목록 (10개)
  current: DaewoonItem | null;    // 현재 대운
  currentAge: number;             // 현재 나이
  bestPeriod: DaewoonItem | null; // 최고 대운
  worstPeriod: DaewoonItem | null;// 최악 대운
}

// ============================================================
// 세운 (연운)
// ============================================================

export interface SewoonItem {
  year: number;           // 연도
  age: number;            // 나이
  gan: CheonGan;          // 천간
  ji: JiJi;               // 지지
  ganJi: string;          // 합친 문자
  ohHaeng: OhHaeng;       // 천간 오행
  animal: string;         // 띠 (쥐, 소, 호랑이...)
  score: number;          // 세운 점수 (0-100)
  description: string;    // 세운 설명
  isYongSin: boolean;     // 용신 세운 여부
  daewoonInteraction: number;  // 대운과의 상호작용 점수
}

// ============================================================
// 공망 세부 분석
// ============================================================

export interface DetailedGongmangAnalysis {
  yearGongmang: [JiJi, JiJi];
  monthGongmang: [JiJi, JiJi];
  dayGongmang: [JiJi, JiJi];
  timeGongmang: [JiJi, JiJi];

  affectedPositions: {
    yearJi: { isYearGong: boolean; isMonthGong: boolean; isDayGong: boolean; isTimeGong: boolean };
    monthJi: { isYearGong: boolean; isMonthGong: boolean; isDayGong: boolean; isTimeGong: boolean };
    dayJi: { isYearGong: boolean; isMonthGong: boolean; isDayGong: boolean; isTimeGong: boolean };
    timeJi: { isYearGong: boolean; isMonthGong: boolean; isDayGong: boolean; isTimeGong: boolean };
  };

  interpretation: {
    yearGong: string;
    monthGong: string;
    dayGong: string;
    timeGong: string;
  };

  summary: string;
}

// ============================================================
// 신살 분석
// ============================================================

export interface SinsalAnalysis {
  gilSin: string[];       // 길신 목록
  hyungSin: string[];     // 흉신 목록

  // 주요 신살 상세
  hasCheonEulGuiIn: boolean;    // 천을귀인
  hasMunChangGuiIn: boolean;    // 문창귀인
  hasYeokMaSal: boolean;        // 역마살
  hasDoHwaSal: boolean;         // 도화살
  hasGongMang: boolean;         // 공망
  hasYangInSal: boolean;        // 양인살
  hasGeopSal: boolean;          // 겁살
  hasGoeGangSal: boolean;       // 괴강살

  detailedGongmang?: DetailedGongmangAnalysis;  // 공망 세분화

  summary: string;              // 신살 요약
}

// ============================================================
// 관계 분석 (합/충/형/파/해)
// ============================================================

export interface PillarRelations {
  // 천간 관계
  cheonganHap: string[];        // 천간합 (예: ["갑기합"])
  cheonganChung: string[];      // 천간충

  // 지지 관계
  jijiYukHap: string[];         // 지지육합
  jijiSamHap: string[];         // 지지삼합
  jijiChung: string[];          // 지지충
  jijiHyung: string[];          // 지지형
  jijiBan: string[];            // 지지반합
  jijiPa: string[];             // 지지파
  jijiHae: string[];            // 지지해

  summary: string;              // 관계 요약
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
  careerAptitude: string[];     // 적합 직업
  relationshipStyle: string;    // 대인관계 스타일
}

// ============================================================
// 완전한 사주 데이터 (통합)
// ============================================================

export interface CompleteSajuData {
  // === 메타 정보 ===
  version: string;                // 데이터 버전
  calculatedAt: string;           // 계산 시간
  isComplete: boolean;            // 완전한 데이터 여부

  // === 기본 정보 ===
  birthInfo: {
    year: number;
    month: number;
    day: number;
    hour: number;
    minute: number;
    gender: Gender;
    isLunar: boolean;
    birthDateString: string;      // "1990-05-15"
    birthTimeString: string;      // "14:30"
  };

  // === 사주 기둥 ===
  fourPillars: FourPillars;
  fullSajuString: string;         // "경오 신사 갑자 신미"

  // === 오행 분석 ===
  ohHaeng: OhHaengAnalysis;

  // === 십성 분석 ===
  sipSung: SipSungAnalysis;

  // === 격국 분석 ===
  gyeokGuk: GyeokGukAnalysis;

  // === 용신/기신 ===
  yongSin: YongSinAnalysis;

  // === 대운 ===
  daewoon: DaewoonAnalysis;

  // === 세운 (올해/내년) ===
  currentYearSewoon: SewoonItem;
  nextYearSewoon: SewoonItem;

  // === 신살 ===
  sinsal: SinsalAnalysis;

  // === 관계 ===
  relations: PillarRelations;

  // === 성격/적성 ===
  personality: PersonalityAnalysis;

  // === 신강/신약 상세 분석 ===
  bodyStrengthDetail?: BodyStrengthAnalysis;

  // === 레거시 호환 필드 (기존 코드 지원) ===
  // 이 필드들은 기존 코드와의 호환성을 위해 유지
  year: { gan: CheonGan; ji: JiJi };
  month: { gan: CheonGan; ji: JiJi };
  day: { gan: CheonGan; ji: JiJi };
  time: { gan: CheonGan; ji: JiJi };
  ohHaengBalance: OhHaengBalance;
  sipSungBalance: SipSungBalance;
  fullSaju: string;
  tenGods: SipSungDetail;
  fiveElements: {
    wood: number;
    fire: number;
    earth: number;
    metal: number;
    water: number;
  };
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
