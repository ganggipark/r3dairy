/**
 * 사주 계산 패키지 - 타입 정의
 *
 * @author SajuApp
 * @version 1.0.0
 */
/** 천간(天干) - 10개 */
export type CheonGan = '갑' | '을' | '병' | '정' | '무' | '기' | '경' | '신' | '임' | '계';
/** 지지(地支) - 12개 */
export type JiJi = '자' | '축' | '인' | '묘' | '진' | '사' | '오' | '미' | '신' | '유' | '술' | '해';
/** 오행 */
export type OhHaeng = '목' | '화' | '토' | '금' | '수';
/** 성별 */
export type Gender = 'male' | 'female';
/** 사주의 기둥 (연월일시) - 기본 */
export interface SajuPillarBasic {
    gan: CheonGan;
    ji: JiJi;
}
/** 기둥 결과 (계산 후) */
export interface PillarResult {
    heavenly: string;
    earthly: string;
    combined: string;
}
/** 사주 기둥 (확장) */
export interface SajuPillar {
    gan: CheonGan;
    ji: JiJi;
    ganJi: string;
    ganOhHaeng: OhHaeng;
    jiOhHaeng: OhHaeng;
}
export interface FourPillars {
    year: SajuPillar;
    month: SajuPillar;
    day: SajuPillar;
    time: SajuPillar;
}
/** 생년월일시 정보 */
export interface BirthInfo {
    year: number;
    month: number;
    day: number;
    hour: number;
    minute?: number;
    isLunar?: boolean;
    isLeapMonth?: boolean;
    gender?: Gender;
}
/** 사주 팔자 (四柱八字) 결과 */
export interface FourPillarsResult {
    year: PillarResult;
    month: PillarResult;
    day: PillarResult;
    hour: PillarResult;
}
/** 오행 균형 */
export interface FiveElements {
    wood: number;
    fire: number;
    earth: number;
    metal: number;
    water: number;
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
    bijeon: number;
    geopjae: number;
    siksin: number;
    sanggwan: number;
    jeongjae: number;
    pyeonjae: number;
    jeonggwan: number;
    pyeongwan: number;
    jeongin: number;
    pyeonin: number;
}
/** 음력 날짜 */
export interface LunarDate {
    year: number;
    month: number;
    day: number;
    isLeapMonth: boolean;
    zodiac?: string;
    chineseYear?: string;
}
export interface OhHaengAnalysis {
    balance: OhHaengBalance;
    dominant: OhHaeng;
    weak: OhHaeng;
    dominantScore: number;
    weakScore: number;
    isBalanced: boolean;
}
export interface SipSungBalance {
    비겁: number;
    식상: number;
    재성: number;
    관성: number;
    인성: number;
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
export interface GyeokGukAnalysis {
    dayMaster: CheonGan;
    dayMasterOhHaeng: OhHaeng;
    strength: '신강' | '신약' | '중화';
    monthBranch: JiJi;
    season: '봄' | '여름' | '가을' | '겨울';
    gyeokGukType: string;
    description: string;
}
export interface YongSinAnalysis {
    yongSin: OhHaeng[];
    giSin: OhHaeng[];
    huiSin: OhHaeng[];
    yongSinReason: string;
    giSinReason: string;
    yongSinScore: Record<OhHaeng, number>;
}
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
    year: {
        gan: CheonGan;
        ji: JiJi;
    };
    month: {
        gan: CheonGan;
        ji: JiJi;
    };
    day: {
        gan: CheonGan;
        ji: JiJi;
    };
    time: {
        gan: CheonGan;
        ji: JiJi;
    };
    ohHaengBalance: OhHaengBalance;
    sipSungBalance: SipSungBalance;
    fullSaju: string;
    tenGods: SipSungDetail;
    fiveElements: FiveElements;
}
export declare function isCompleteSajuData(data: any): data is CompleteSajuData;
export declare function hasMinimalSajuData(data: any): boolean;
//# sourceMappingURL=types.d.ts.map