/**
 * 사주 계산 모듈 (만세력)
 *
 * 정확한 사주(四柱) 계산:
 * - 년주: 입춘 기준 60갑자 순환
 * - 월주: 절기 기준 월간 계산
 * - 일주: 1900년 1월 1일 갑술 기준
 * - 시주: 야자시(夜子時) 규칙 + 진태양시 보정
 *
 * @author SajuApp
 * @version 1.0.0
 */
import type { BirthInfo, FourPillarsResult, PillarResult, FiveElements } from './types';
/** 천간(天干) - 10개 */
export declare const HEAVENLY_STEMS: readonly ["갑", "을", "병", "정", "무", "기", "경", "신", "임", "계"];
/** 지지(地支) - 12개 */
export declare const EARTHLY_BRANCHES: readonly ["자", "축", "인", "묘", "진", "사", "오", "미", "신", "유", "술", "해"];
/** 60갑자 순환표 */
export declare const SIXTY_CYCLE: readonly ["갑자", "을축", "병인", "정묘", "무진", "기사", "경오", "신미", "임신", "계유", "갑술", "을해", "병자", "정축", "무인", "기묘", "경진", "신사", "임오", "계미", "갑신", "을유", "병술", "정해", "무자", "기축", "경인", "신묘", "임진", "계사", "갑오", "을미", "병신", "정유", "무술", "기해", "경자", "신축", "임인", "계묘", "갑진", "을사", "병오", "정미", "무신", "기유", "경술", "신해", "임자", "계축", "갑인", "을묘", "병진", "정사", "무오", "기미", "경신", "신유", "임술", "계해"];
/**
 * 일주 계산
 * 기준일: 1900년 1월 1일 = 갑술(甲戌, index 10)
 */
export declare function calculateDayPillar(year: number, month: number, day: number): PillarResult;
/**
 * 사주팔자 계산 (메인 함수)
 */
export declare function calculateFourPillars(birthInfo: BirthInfo, useTrueSolarTime?: boolean, birthPlace?: string): FourPillarsResult;
/**
 * 사주 결과를 문자열로 포맷팅
 */
export declare function formatFourPillars(pillars: FourPillarsResult): string;
/**
 * 오행 균형 계산
 */
export declare function calculateFiveElements(pillars: FourPillarsResult): FiveElements;
/**
 * 일간(日干) 추출
 */
export declare function getDayMaster(pillars: FourPillarsResult): string;
/**
 * 띠(12지신) 반환
 */
export declare function getZodiac(year: number): string;
//# sourceMappingURL=sajuCalculator.d.ts.map