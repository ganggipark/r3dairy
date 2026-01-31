/**
 * 완전한 사주 데이터 계산기
 *
 * 모든 사주 분석 데이터를 한 번에 계산하여 CompleteSajuData 구조로 반환
 *
 * @author SajuApp
 * @version 2.0.0
 */
import type { CompleteSajuData, Gender } from './types';
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
//# sourceMappingURL=completeSajuCalculator.d.ts.map