/**
 * 음양력 변환 모듈
 *
 * 의존성: korean-lunar-calendar 패키지 필요
 * npm install korean-lunar-calendar
 *
 * @author SajuApp
 * @version 1.0.0
 */
import type { LunarDate } from './types';
/**
 * 양력 날짜를 음력으로 변환
 * @param date 양력 Date 객체
 * @returns 음력 날짜 정보
 */
export declare function solarToLunar(date: Date): LunarDate;
/**
 * 음력 날짜를 양력으로 변환
 * @param year 음력 연도
 * @param month 음력 월
 * @param day 음력 일
 * @param isLeapMonth 윤달 여부
 * @returns 양력 Date 객체
 */
export declare function lunarToSolar(year: number, month: number, day: number, isLeapMonth?: boolean): Date;
/**
 * 음력 날짜를 포맷팅된 문자열로 반환
 */
export declare function formatLunarDate(date: Date, includeYear?: boolean): string;
/**
 * 24절기 데이터 (양력 기준 근사값)
 */
export declare const SOLAR_TERMS: Record<string, {
    month: number;
    day: number;
}>;
/**
 * 24절기인지 확인
 */
export declare function getSolarTerm(date: Date): string | null;
/**
 * 특별한 음력 날짜인지 확인 (명절)
 */
export declare function getSpecialLunarDay(date: Date): string | null;
/**
 * 음력 월의 한글 이름 반환
 */
export declare function getLunarMonthName(month: number): string;
//# sourceMappingURL=lunarCalendar.d.ts.map