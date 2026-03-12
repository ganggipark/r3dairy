/**
 * Core Saju Type Definitions
 *
 * CANONICAL SOURCE - All modules MUST import from here
 * @version 1.0.0 (v1.2.13)
 */

// Base types from the main types module
export type CheonGan = '갑' | '을' | '병' | '정' | '무' | '기' | '경' | '신' | '임' | '계';
export type JiJi = '자' | '축' | '인' | '묘' | '진' | '사' | '오' | '미' | '신' | '유' | '술' | '해';
export type OhHaeng = '목' | '화' | '토' | '금' | '수';

/**
 * Pillar (柱) - A single column in the Four Pillars
 */
export interface SajuPillar {
  gan: CheonGan;
  ji: JiJi;
}

/**
 * Four Pillars (四柱) - Year, Month, Day, Hour
 *
 * IMPORTANT: Uses 'time' for the fourth pillar (not 'hour')
 * This matches Korean convention: 년주, 월주, 일주, 시주
 */
export interface FourPillars {
  year: SajuPillar;
  month: SajuPillar;
  day: SajuPillar;
  time: SajuPillar;
}

/**
 * Legacy alias for modules using 'hour' property
 * @deprecated Use FourPillars instead, migrate away from 'hour'
 */
export interface FourPillarsLegacy {
  year: SajuPillar;
  month: SajuPillar;
  day: SajuPillar;
  hour: SajuPillar;
}

/**
 * Five Elements Balance (五行均衡)
 */
export interface OhHaengBalance {
  목: number;
  화: number;
  토: number;
  금: number;
  수: number;
  [key: string]: number;
}

/**
 * Ten Gods Type (十神)
 */
export type SipSinType =
  | '비견' | '겁재'
  | '식신' | '상관'
  | '정재' | '편재'
  | '정관' | '편관'
  | '정인' | '편인';

/**
 * Ten Gods Category (五分類)
 */
export type SipSinCategory = '비겁' | '식상' | '재성' | '관성' | '인성';

/**
 * Hidden Stem entry with energy weight
 */
export interface JijangganEntry {
  gan: CheonGan;
  weight: number;
}
