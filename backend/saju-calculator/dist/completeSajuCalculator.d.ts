/**
 * 완전한 사주 데이터 계산기
 *
 * 모든 사주 분석 데이터를 한 번에 계산하여 CompleteSajuData 구조로 반환
 *
 * @author SajuApp
 * @version 2.0.0
 */
import type { CompleteSajuData, Gender, FourPillars, OhHaengAnalysis, SipSungAnalysis, GyeokGukAnalysis, YongSinAnalysis } from './types';
export interface SajuCalculationInput {
    year: number;
    month: number;
    day: number;
    hour: number;
    minute?: number;
    gender: Gender;
    isLunar?: boolean;
    isLeapMonth?: boolean;
    useTrueSolarTime?: boolean;
    birthPlace?: string;
}
export declare function calculateCompleteSajuData(input: SajuCalculationInput): CompleteSajuData;
declare function calculateFourPillars(year: number, month: number, day: number, hour: number, minute: number, isLunar: boolean, isLeapMonth: boolean, useTrueSolarTime: boolean, birthPlace: string): FourPillars;
declare function analyzeOhHaeng(fourPillars: FourPillars): OhHaengAnalysis;
declare function analyzeSipSung(fourPillars: FourPillars): SipSungAnalysis;
declare function analyzeGyeokGuk(fourPillars: FourPillars, ohHaeng: OhHaengAnalysis): GyeokGukAnalysis;
declare function analyzeYongSin(gyeokGuk: GyeokGukAnalysis): YongSinAnalysis;
export { calculateFourPillars, analyzeOhHaeng, analyzeSipSung, analyzeGyeokGuk, analyzeYongSin };
//# sourceMappingURL=completeSajuCalculator.d.ts.map