"use strict";
/**
 * 사주 계산 패키지 - 메인 Export
 *
 * 한국 전통 사주명리학 계산 라이브러리
 *
 * @author SajuApp
 * @version 1.0.0
 */
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __exportStar = (this && this.__exportStar) || function(m, exports) {
    for (var p in m) if (p !== "default" && !Object.prototype.hasOwnProperty.call(exports, p)) __createBinding(exports, m, p);
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.SOLAR_TERMS_DATA = exports.TERM_TO_SOLAR_MONTH = exports.MONTH_START_TERMS = exports.SOLAR_TERM_NAMES = exports.calculateDaewoonStartFromSolarTerms = exports.getDaysToPrevSolarTerm = exports.getDaysToNextSolarTerm = exports.getSolarTermByDate = exports.getSolarTermsForYear = exports.getExactSolarMonth = exports.KST_STANDARD_LONGITUDE = exports.MAJOR_CITIES = exports.getTrueSolarTimeDescription = exports.getCityInfo = exports.getAvailableCities = exports.getTrueSolarTimeCorrectionByCity = exports.applyTrueSolarTimeByCity = exports.applyTrueSolarTime = exports.calculateTrueSolarTimeCorrection = exports.SOLAR_TERMS = exports.getLunarMonthName = exports.getSpecialLunarDay = exports.getSolarTerm = exports.formatLunarDate = exports.lunarToSolar = exports.solarToLunar = exports.calculateCompleteSajuData = exports.SIXTY_CYCLE = exports.EARTHLY_BRANCHES = exports.HEAVENLY_STEMS = exports.getZodiac = exports.getDayMaster = exports.calculateFiveElements = exports.formatFourPillars = exports.calculateDayPillar = exports.calculateFourPillars = void 0;
// ============================================================
// 타입 Export
// ============================================================
__exportStar(require("./types"), exports);
// ============================================================
// 기본 사주 계산기 (간단 버전)
// ============================================================
var sajuCalculator_1 = require("./sajuCalculator");
Object.defineProperty(exports, "calculateFourPillars", { enumerable: true, get: function () { return sajuCalculator_1.calculateFourPillars; } });
Object.defineProperty(exports, "calculateDayPillar", { enumerable: true, get: function () { return sajuCalculator_1.calculateDayPillar; } });
Object.defineProperty(exports, "formatFourPillars", { enumerable: true, get: function () { return sajuCalculator_1.formatFourPillars; } });
Object.defineProperty(exports, "calculateFiveElements", { enumerable: true, get: function () { return sajuCalculator_1.calculateFiveElements; } });
Object.defineProperty(exports, "getDayMaster", { enumerable: true, get: function () { return sajuCalculator_1.getDayMaster; } });
Object.defineProperty(exports, "getZodiac", { enumerable: true, get: function () { return sajuCalculator_1.getZodiac; } });
Object.defineProperty(exports, "HEAVENLY_STEMS", { enumerable: true, get: function () { return sajuCalculator_1.HEAVENLY_STEMS; } });
Object.defineProperty(exports, "EARTHLY_BRANCHES", { enumerable: true, get: function () { return sajuCalculator_1.EARTHLY_BRANCHES; } });
Object.defineProperty(exports, "SIXTY_CYCLE", { enumerable: true, get: function () { return sajuCalculator_1.SIXTY_CYCLE; } });
// ============================================================
// 완전한 사주 계산기 (전체 분석)
// ============================================================
var completeSajuCalculator_1 = require("./calculators/completeSajuCalculator");
Object.defineProperty(exports, "calculateCompleteSajuData", { enumerable: true, get: function () { return completeSajuCalculator_1.calculateCompleteSajuData; } });
// ============================================================
// 음양력 변환
// ============================================================
var lunarCalendar_1 = require("./lunarCalendar");
Object.defineProperty(exports, "solarToLunar", { enumerable: true, get: function () { return lunarCalendar_1.solarToLunar; } });
Object.defineProperty(exports, "lunarToSolar", { enumerable: true, get: function () { return lunarCalendar_1.lunarToSolar; } });
Object.defineProperty(exports, "formatLunarDate", { enumerable: true, get: function () { return lunarCalendar_1.formatLunarDate; } });
Object.defineProperty(exports, "getSolarTerm", { enumerable: true, get: function () { return lunarCalendar_1.getSolarTerm; } });
Object.defineProperty(exports, "getSpecialLunarDay", { enumerable: true, get: function () { return lunarCalendar_1.getSpecialLunarDay; } });
Object.defineProperty(exports, "getLunarMonthName", { enumerable: true, get: function () { return lunarCalendar_1.getLunarMonthName; } });
Object.defineProperty(exports, "SOLAR_TERMS", { enumerable: true, get: function () { return lunarCalendar_1.SOLAR_TERMS; } });
// ============================================================
// 진태양시 계산
// ============================================================
var trueSolarTimeCalculator_1 = require("./trueSolarTimeCalculator");
Object.defineProperty(exports, "calculateTrueSolarTimeCorrection", { enumerable: true, get: function () { return trueSolarTimeCalculator_1.calculateTrueSolarTimeCorrection; } });
Object.defineProperty(exports, "applyTrueSolarTime", { enumerable: true, get: function () { return trueSolarTimeCalculator_1.applyTrueSolarTime; } });
Object.defineProperty(exports, "applyTrueSolarTimeByCity", { enumerable: true, get: function () { return trueSolarTimeCalculator_1.applyTrueSolarTimeByCity; } });
Object.defineProperty(exports, "getTrueSolarTimeCorrectionByCity", { enumerable: true, get: function () { return trueSolarTimeCalculator_1.getTrueSolarTimeCorrectionByCity; } });
Object.defineProperty(exports, "getAvailableCities", { enumerable: true, get: function () { return trueSolarTimeCalculator_1.getAvailableCities; } });
Object.defineProperty(exports, "getCityInfo", { enumerable: true, get: function () { return trueSolarTimeCalculator_1.getCityInfo; } });
Object.defineProperty(exports, "getTrueSolarTimeDescription", { enumerable: true, get: function () { return trueSolarTimeCalculator_1.getTrueSolarTimeDescription; } });
Object.defineProperty(exports, "MAJOR_CITIES", { enumerable: true, get: function () { return trueSolarTimeCalculator_1.MAJOR_CITIES; } });
Object.defineProperty(exports, "KST_STANDARD_LONGITUDE", { enumerable: true, get: function () { return trueSolarTimeCalculator_1.KST_STANDARD_LONGITUDE; } });
// ============================================================
// 절기 계산
// ============================================================
var solarTermsCalculator_1 = require("./solarTermsCalculator");
Object.defineProperty(exports, "getExactSolarMonth", { enumerable: true, get: function () { return solarTermsCalculator_1.getExactSolarMonth; } });
Object.defineProperty(exports, "getSolarTermsForYear", { enumerable: true, get: function () { return solarTermsCalculator_1.getSolarTermsForYear; } });
Object.defineProperty(exports, "getSolarTermByDate", { enumerable: true, get: function () { return solarTermsCalculator_1.getSolarTermByDate; } });
Object.defineProperty(exports, "getDaysToNextSolarTerm", { enumerable: true, get: function () { return solarTermsCalculator_1.getDaysToNextSolarTerm; } });
Object.defineProperty(exports, "getDaysToPrevSolarTerm", { enumerable: true, get: function () { return solarTermsCalculator_1.getDaysToPrevSolarTerm; } });
Object.defineProperty(exports, "calculateDaewoonStartFromSolarTerms", { enumerable: true, get: function () { return solarTermsCalculator_1.calculateDaewoonStartFromSolarTerms; } });
Object.defineProperty(exports, "SOLAR_TERM_NAMES", { enumerable: true, get: function () { return solarTermsCalculator_1.SOLAR_TERM_NAMES; } });
Object.defineProperty(exports, "MONTH_START_TERMS", { enumerable: true, get: function () { return solarTermsCalculator_1.MONTH_START_TERMS; } });
Object.defineProperty(exports, "TERM_TO_SOLAR_MONTH", { enumerable: true, get: function () { return solarTermsCalculator_1.TERM_TO_SOLAR_MONTH; } });
Object.defineProperty(exports, "SOLAR_TERMS_DATA", { enumerable: true, get: function () { return solarTermsCalculator_1.SOLAR_TERMS_DATA; } });
//# sourceMappingURL=index.js.map