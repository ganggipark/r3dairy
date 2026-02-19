/**
 * 사주 계산 패키지 - 메인 Export
 *
 * 한국 전통 사주명리학 계산 라이브러리
 *
 * @author SajuApp
 * @version 1.0.0
 */

// ============================================================
// 타입 Export
// ============================================================
export * from './types';

// ============================================================
// 기본 사주 계산기 (간단 버전)
// ============================================================
export {
  calculateFourPillars,
  calculateDayPillar,
  formatFourPillars,
  calculateFiveElements,
  getDayMaster,
  getZodiac,
  HEAVENLY_STEMS,
  EARTHLY_BRANCHES,
  SIXTY_CYCLE,
} from './sajuCalculator';

// ============================================================
// 완전한 사주 계산기 (전체 분석)
// ============================================================
export {
  calculateCompleteSajuData,
  type SajuCalculationInput,
} from './calculators/completeSajuCalculator';

// ============================================================
// 음양력 변환
// ============================================================
export {
  solarToLunar,
  lunarToSolar,
  formatLunarDate,
  getSolarTerm,
  getSpecialLunarDay,
  getLunarMonthName,
  SOLAR_TERMS,
} from './lunarCalendar';

// ============================================================
// 진태양시 계산
// ============================================================
export {
  calculateTrueSolarTimeCorrection,
  applyTrueSolarTime,
  applyTrueSolarTimeByCity,
  getTrueSolarTimeCorrectionByCity,
  getAvailableCities,
  getCityInfo,
  getTrueSolarTimeDescription,
  MAJOR_CITIES,
  KST_STANDARD_LONGITUDE,
  type TrueSolarTimeResult,
  type Location,
} from './trueSolarTimeCalculator';

// ============================================================
// 절기 계산
// ============================================================
export {
  getExactSolarMonth,
  getSolarTermsForYear,
  getSolarTermByDate,
  getDaysToNextSolarTerm,
  getDaysToPrevSolarTerm,
  calculateDaewoonStartFromSolarTerms,
  SOLAR_TERM_NAMES,
  MONTH_START_TERMS,
  TERM_TO_SOLAR_MONTH,
  SOLAR_TERMS_DATA,
  type SolarTermData,
  type DaysToTermResult,
} from './solarTermsCalculator';
