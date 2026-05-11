/**
 * 정확한 절기(節氣) 계산 시스템
 *
 * 데이터 출처:
 * - 2024-2026년: 한국천문연구원 (https://astro.kasi.re.kr) 공식 데이터
 * - 2027-2030년: uncle.tools (한국천문연구원 공식 데이터 발표 대기 중)
 * 모든 시각은 KST (한국표준시) 기준
 *
 * @author SajuApp
 * @version 2.0.0
 */
export interface SolarTermData {
    year: number;
    term: string;
    date: string;
    time: string;
    month: number;
    day: number;
    solarMonth: number;
}
export interface DaysToTermResult {
    days: number;
    hours: number;
    minutes: number;
    totalMinutes: number;
}
export declare const SOLAR_TERM_NAMES: readonly ["소한", "대한", "입춘", "우수", "경칩", "춘분", "청명", "곡우", "입하", "소만", "망종", "하지", "소서", "대서", "입추", "처서", "백로", "추분", "한로", "상강", "입동", "소설", "대설", "동지"];
export declare const MONTH_START_TERMS: Record<number, string>;
export declare const TERM_TO_SOLAR_MONTH: Record<string, number>;
export declare const SOLAR_TERMS_DATA: Record<number, SolarTermData[]>;
export declare function getSolarTermsForYear(year: number): SolarTermData[];
export declare function getSolarTermByDate(year: number, month: number, day: number): SolarTermData | null;
export declare function getExactSolarMonth(year: number, month: number, day: number, hour: number, minute: number): number;
export declare function getDaysToNextSolarTerm(year: number, month: number, day: number, hour: number, minute: number): DaysToTermResult;
export declare function getDaysToPrevSolarTerm(year: number, month: number, day: number, hour: number, minute: number): DaysToTermResult;
export declare function calculateDaewoonStartFromSolarTerms(birthYear: number, birthMonth: number, birthDay: number, birthHour: number, birthMinute: number, isForward: boolean): {
    startAge: number;
    startMonth: number;
    totalDays: number;
};
//# sourceMappingURL=solarTermsCalculator.d.ts.map