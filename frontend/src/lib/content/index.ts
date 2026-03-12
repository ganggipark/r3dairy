/**
 * Content System - 메인 Export
 *
 * 사주 분석 + 콘텐츠 조합 + 역할 번역을 통합 제공합니다.
 *
 * 사용 흐름:
 * 1. calculateSaju(birthInfo, targetDate) - 사주 원국 계산
 * 2. analyzeDailyFortune(birthInfo, targetDate, sajuData) - 일간 리듬 분석
 * 3. assembleDailyContent(targetDate, sajuData, dailyRhythm) - 콘텐츠 조합
 * 4. translateDailyContent(content, role) - 역할별 번역
 */

// ============================================================
// Types
// ============================================================
export type {
  BirthInfo,
  SajuData,
  PillarData,
  DailyRhythm,
  MonthlyRhythm,
  YearlyRhythm,
  DailyContent,
  MonthlyContent,
  YearlyContent,
  FocusCaution,
  ActionGuide,
  TimeDirection,
  StateTrigger,
  HealthSports,
  MealNutrition,
  FashionBeauty,
  ShoppingFinance,
  LivingSpace,
  DailyRoutines,
  DigitalCommunication,
  HobbiesCreativity,
  RelationshipsSocial,
  SeasonalEnvironment,
  UserRole,
} from './types'

// ============================================================
// Saju Engine (리듬 분석)
// ============================================================
export {
  calculateSaju,
  analyzeDailyFortune,
  analyzeMonthlyRhythm,
  analyzeYearlyRhythm,
} from './saju-engine'

// ============================================================
// Content Assembly (콘텐츠 조합)
// ============================================================
export {
  assembleDailyContent,
  assembleMonthlyContent,
  assembleYearlyContent,
} from './assembly'

// ============================================================
// Role Translation (역할 번역)
// ============================================================
export {
  translateDailyContent,
  translateMonthlyContent,
  translateYearlyContent,
  validateSemanticPreservation,
} from './translator'
