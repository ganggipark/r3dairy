/**
 * Core Saju Module
 *
 * Canonical source for types, constants, and caching utilities.
 * @version 1.0.0 (v1.2.13)
 */

// Types
export type {
  CheonGan,
  JiJi,
  OhHaeng,
  SajuPillar,
  FourPillars,
  FourPillarsLegacy,
  OhHaengBalance,
  SipSinType,
  SipSinCategory,
  JijangganEntry,
} from './types';

// Constants
export {
  CHEONGAN_TO_OHHAENG,
  CHEONGAN_YINYANG,
  JIJI_TO_OHHAENG,
  JIJI_YINYANG,
  JIJANGGAN,
  JIJANGGAN_SIMPLE,
  getMainJijanggan,
  SANG_SAENG,
  SANG_GEUK,
  SIXTY_GAPJA,
  SIXTY_GAPJA_SET,
  SIXTY_GAPJA_INDEX,
  isValidGapja,
  getGapjaIndex,
  isValidGanJiPair,
  getNextGapja,
  getPreviousGapja,
  cycleGapjaIndex,
} from './constants';

// Cache utilities
export {
  getCachedAstrologicalMonth,
  clearSolarTermCache,
  getSolarTermCacheSize,
  getCachedSipSin,
  preWarmTenGodsCache,
  clearTenGodsCache,
  getTenGodsCacheSize,
  memoize,
} from './cache';
