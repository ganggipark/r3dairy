"use strict";
/**
 * saju-engine - 사주팔자 계산 엔진
 *
 * 전통 명리학 기반의 정밀한 사주팔자 계산을 제공합니다.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.SANG_GEUK = exports.SANG_SAENG = exports.JIJANGGAN_SIMPLE = exports.JIJI = exports.CHEONGAN = exports.generateComprehensiveSinsalSummary = exports.analyzeGuiMunGwanSal = exports.analyzeYangInSal = exports.analyzeTwelveSinsal = exports.analyzeDateSinsal = exports.analyzeAllSinsal = exports.getMonthlyMainGan = exports.checkTouchul = exports.checkJongGyeok = exports.checkHwaGiGyeok = exports.analyzeGeukGukDetails = exports.determineGeukGuk = exports.identifyMediatingYongsin = exports.determineGiSin = exports.determineYongSin = exports.getYongSinByJohu = exports.getYongSinByEokBu = exports.analyzeYongSinGiSin = exports.KST_STANDARD_LONGITUDE = exports.MAJOR_CITIES = exports.getTrueSolarTimeDescription = exports.getCityInfo = exports.getAvailableCities = exports.getTrueSolarTimeCorrectionByCity = exports.applyTrueSolarTimeByCity = exports.applyTrueSolarTime = exports.getLunarMonthName = exports.getSpecialLunarDay = exports.getSolarTerm = exports.formatLunarDate = exports.lunarToSolar = exports.solarToLunar = exports.MONTH_START_TERMS = exports.isBefore24Jeolip = exports.getSolarTermDate = exports.getSolarTermsForYear = exports.getSimpleDaeunStartAge = exports.calculateDaeunStartAge = exports.analyzeBodyStrengthDetails = exports.checkDeukSe = exports.checkDeukJi = exports.checkDeukRyeong = exports.calculateBodyStrength = exports.isCompleteSajuData = exports.calculateCompleteSajuData = void 0;
exports.SIPSUNG_INFO = void 0;
// ============ Main Calculator ============
var completeSajuCalculator_1 = require("./calculators/completeSajuCalculator");
Object.defineProperty(exports, "calculateCompleteSajuData", { enumerable: true, get: function () { return completeSajuCalculator_1.calculateCompleteSajuData; } });
var completeSajuData_1 = require("./types/completeSajuData");
Object.defineProperty(exports, "isCompleteSajuData", { enumerable: true, get: function () { return completeSajuData_1.isCompleteSajuData; } });
// ============ Sub-calculators ============
var bodyStrength_1 = require("./analysis/bodyStrength");
Object.defineProperty(exports, "calculateBodyStrength", { enumerable: true, get: function () { return bodyStrength_1.calculateBodyStrength; } });
Object.defineProperty(exports, "checkDeukRyeong", { enumerable: true, get: function () { return bodyStrength_1.checkDeukRyeong; } });
Object.defineProperty(exports, "checkDeukJi", { enumerable: true, get: function () { return bodyStrength_1.checkDeukJi; } });
Object.defineProperty(exports, "checkDeukSe", { enumerable: true, get: function () { return bodyStrength_1.checkDeukSe; } });
Object.defineProperty(exports, "analyzeBodyStrengthDetails", { enumerable: true, get: function () { return bodyStrength_1.analyzeBodyStrengthDetails; } });
var daeunStartAge_1 = require("./analysis/daewoonAnalysis/daeunStartAge");
Object.defineProperty(exports, "calculateDaeunStartAge", { enumerable: true, get: function () { return daeunStartAge_1.calculateDaeunStartAge; } });
Object.defineProperty(exports, "getSimpleDaeunStartAge", { enumerable: true, get: function () { return daeunStartAge_1.getSimpleDaeunStartAge; } });
var solarTermsCalculator_1 = require("./calculators/solarTermsCalculator");
Object.defineProperty(exports, "getSolarTermsForYear", { enumerable: true, get: function () { return solarTermsCalculator_1.getSolarTermsForYear; } });
Object.defineProperty(exports, "getSolarTermDate", { enumerable: true, get: function () { return solarTermsCalculator_1.getSolarTermDate; } });
Object.defineProperty(exports, "isBefore24Jeolip", { enumerable: true, get: function () { return solarTermsCalculator_1.isBefore24Jeolip; } });
Object.defineProperty(exports, "MONTH_START_TERMS", { enumerable: true, get: function () { return solarTermsCalculator_1.MONTH_START_TERMS; } });
var lunarCalendar_1 = require("./calculators/lunarCalendar");
Object.defineProperty(exports, "solarToLunar", { enumerable: true, get: function () { return lunarCalendar_1.solarToLunar; } });
Object.defineProperty(exports, "lunarToSolar", { enumerable: true, get: function () { return lunarCalendar_1.lunarToSolar; } });
Object.defineProperty(exports, "formatLunarDate", { enumerable: true, get: function () { return lunarCalendar_1.formatLunarDate; } });
Object.defineProperty(exports, "getSolarTerm", { enumerable: true, get: function () { return lunarCalendar_1.getSolarTerm; } });
Object.defineProperty(exports, "getSpecialLunarDay", { enumerable: true, get: function () { return lunarCalendar_1.getSpecialLunarDay; } });
Object.defineProperty(exports, "getLunarMonthName", { enumerable: true, get: function () { return lunarCalendar_1.getLunarMonthName; } });
var trueSolarTimeCalculator_1 = require("./calculators/trueSolarTimeCalculator");
Object.defineProperty(exports, "applyTrueSolarTime", { enumerable: true, get: function () { return trueSolarTimeCalculator_1.applyTrueSolarTime; } });
Object.defineProperty(exports, "applyTrueSolarTimeByCity", { enumerable: true, get: function () { return trueSolarTimeCalculator_1.applyTrueSolarTimeByCity; } });
Object.defineProperty(exports, "getTrueSolarTimeCorrectionByCity", { enumerable: true, get: function () { return trueSolarTimeCalculator_1.getTrueSolarTimeCorrectionByCity; } });
Object.defineProperty(exports, "getAvailableCities", { enumerable: true, get: function () { return trueSolarTimeCalculator_1.getAvailableCities; } });
Object.defineProperty(exports, "getCityInfo", { enumerable: true, get: function () { return trueSolarTimeCalculator_1.getCityInfo; } });
Object.defineProperty(exports, "getTrueSolarTimeDescription", { enumerable: true, get: function () { return trueSolarTimeCalculator_1.getTrueSolarTimeDescription; } });
Object.defineProperty(exports, "MAJOR_CITIES", { enumerable: true, get: function () { return trueSolarTimeCalculator_1.MAJOR_CITIES; } });
Object.defineProperty(exports, "KST_STANDARD_LONGITUDE", { enumerable: true, get: function () { return trueSolarTimeCalculator_1.KST_STANDARD_LONGITUDE; } });
// ============ Analysis Modules ============
var yongSinGiSin_1 = require("./analysis/yongSinGiSin");
Object.defineProperty(exports, "analyzeYongSinGiSin", { enumerable: true, get: function () { return yongSinGiSin_1.analyzeYongSinGiSin; } });
Object.defineProperty(exports, "getYongSinByEokBu", { enumerable: true, get: function () { return yongSinGiSin_1.getYongSinByEokBu; } });
Object.defineProperty(exports, "getYongSinByJohu", { enumerable: true, get: function () { return yongSinGiSin_1.getYongSinByJohu; } });
Object.defineProperty(exports, "determineYongSin", { enumerable: true, get: function () { return yongSinGiSin_1.determineYongSin; } });
Object.defineProperty(exports, "determineGiSin", { enumerable: true, get: function () { return yongSinGiSin_1.determineGiSin; } });
Object.defineProperty(exports, "identifyMediatingYongsin", { enumerable: true, get: function () { return yongSinGiSin_1.identifyMediatingYongsin; } });
var geukGuk_1 = require("./analysis/geukGuk");
Object.defineProperty(exports, "determineGeukGuk", { enumerable: true, get: function () { return geukGuk_1.determineGeukGuk; } });
Object.defineProperty(exports, "analyzeGeukGukDetails", { enumerable: true, get: function () { return geukGuk_1.analyzeGeukGukDetails; } });
Object.defineProperty(exports, "checkHwaGiGyeok", { enumerable: true, get: function () { return geukGuk_1.checkHwaGiGyeok; } });
Object.defineProperty(exports, "checkJongGyeok", { enumerable: true, get: function () { return geukGuk_1.checkJongGyeok; } });
Object.defineProperty(exports, "checkTouchul", { enumerable: true, get: function () { return geukGuk_1.checkTouchul; } });
Object.defineProperty(exports, "getMonthlyMainGan", { enumerable: true, get: function () { return geukGuk_1.getMonthlyMainGan; } });
var sinsal_1 = require("./analysis/sinsal");
Object.defineProperty(exports, "analyzeAllSinsal", { enumerable: true, get: function () { return sinsal_1.analyzeAllSinsal; } });
Object.defineProperty(exports, "analyzeDateSinsal", { enumerable: true, get: function () { return sinsal_1.analyzeDateSinsal; } });
Object.defineProperty(exports, "analyzeTwelveSinsal", { enumerable: true, get: function () { return sinsal_1.analyzeTwelveSinsal; } });
Object.defineProperty(exports, "analyzeYangInSal", { enumerable: true, get: function () { return sinsal_1.analyzeYangInSal; } });
Object.defineProperty(exports, "analyzeGuiMunGwanSal", { enumerable: true, get: function () { return sinsal_1.analyzeGuiMunGwanSal; } });
Object.defineProperty(exports, "generateComprehensiveSinsalSummary", { enumerable: true, get: function () { return sinsal_1.generateComprehensiveSinsalSummary; } });
// ============ Core Constants ============
var core_1 = require("./core");
Object.defineProperty(exports, "CHEONGAN", { enumerable: true, get: function () { return core_1.CHEONGAN; } });
Object.defineProperty(exports, "JIJI", { enumerable: true, get: function () { return core_1.JIJI; } });
Object.defineProperty(exports, "JIJANGGAN_SIMPLE", { enumerable: true, get: function () { return core_1.JIJANGGAN_SIMPLE; } });
Object.defineProperty(exports, "SANG_SAENG", { enumerable: true, get: function () { return core_1.SANG_SAENG; } });
Object.defineProperty(exports, "SANG_GEUK", { enumerable: true, get: function () { return core_1.SANG_GEUK; } });
Object.defineProperty(exports, "SIPSUNG_INFO", { enumerable: true, get: function () { return core_1.SIPSUNG_INFO; } });
//# sourceMappingURL=index.js.map