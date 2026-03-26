/**
 * 사주명리 계산 엔진 (TypeScript 포트)
 *
 * Python backend/src/rhythm/saju.py 로직을 TypeScript로 포팅.
 * saju-calculator 패키지의 calculateCompleteSajuData를 직접 호출하여
 * subprocess 없이 계산합니다.
 *
 * 내부 전문 용어 사용 가능 (사용자 노출 금지).
 * Content Assembly Engine에서 일반 언어로 변환됩니다.
 */

import type { BirthInfo, SajuData, DailyRhythm, MonthlyRhythm, YearlyRhythm } from './types'

// saju-calculator 패키지 import (빌드 시점에 해결)
// Raw output shape from the saju-calculator package
interface SajuRawOutput {
  fourPillars: {
    year: { gan: string; ji: string; ganJi: string }
    month: { gan: string; ji: string; ganJi: string }
    day: { gan: string; ji: string; ganJi: string }
    time: { gan: string; ji: string; ganJi: string }
  }
  ohHaeng: { balance: Record<string, number> }
  sipSung: { detail: Record<string, number> }
  gyeokGuk: { dayMaster: string; dayMasterOhHaeng: string; strength: string; season: string }
  yongSin: { yongSin: string[]; giSin: string[] }
  daewoon: SajuData['대운']
  sinsal: SajuData['신살']
  personality: SajuData['성격']
  currentYearSewoon: SajuData['세운']
  nextYearSewoon: SajuData['세운']
  [key: string]: unknown
}

let calculateCompleteSajuData: ((...args: unknown[]) => SajuRawOutput) | null = null
try {
  // eslint-disable-next-line @typescript-eslint/no-require-imports
  const mod = require('saju-calculator')
  calculateCompleteSajuData = mod.calculateCompleteSajuData
} catch {
  // 패키지 미설치 시 null 유지 - 빌드/배포 시 별도 설정 필요
}

// ============================================================
// 상수 정의
// ============================================================

const HEAVENLY_STEMS = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸'] as const
const EARTHLY_BRANCHES = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥'] as const

/** 천간 -> 오행 인덱스 (木=0, 火=1, 土=2, 金=3, 水=4) */
const STEM_WUXING: Record<string, number> = {
  '甲': 0, '乙': 0,
  '丙': 1, '丁': 1,
  '戊': 2, '己': 2,
  '庚': 3, '辛': 3,
  '壬': 4, '癸': 4,
  // 한글 천간도 지원
  '갑': 0, '을': 0,
  '병': 1, '정': 1,
  '무': 2, '기': 2,
  '경': 3, '신': 3,
  '임': 4, '계': 4,
}

/** 상생: 木生火, 火生土, 土生金, 金生水, 水生木 */
const SHENG_MAP: Record<number, number> = { 0: 1, 1: 2, 2: 3, 3: 4, 4: 0 }

/** 상극: 木克土, 火克金, 土克水, 金克木, 水克火 */
const KE_MAP: Record<number, number> = { 0: 2, 1: 3, 2: 4, 3: 0, 4: 1 }

/**
 * 일주(日柱) 인덱스 계산 — sajuCalculator.ts와 동일한 기준
 * 기준: 1900-01-01 = 甲戌(index 10)
 * dayDiff로부터 60갑자 인덱스를 직접 계산 (JIAZI_DATE 불필요)
 */
function getDayPillarIndex(dateStr: string): number {
  const [year, month, day] = dateStr.split('-').map(Number)
  const baseDate = Date.UTC(1900, 0, 1)
  const targetDate = Date.UTC(year, month - 1, day)
  const dayDiff = Math.floor((targetDate - baseDate) / (1000 * 60 * 60 * 24))
  return ((10 + dayDiff) % 60 + 60) % 60
}

/** 날짜 객체로부터 일주 인덱스 계산 (내부 월간 루프용) */
function getDayPillarIndexFromDate(d: Date): number {
  const baseDate = Date.UTC(1900, 0, 1)
  const targetDate = Date.UTC(d.getFullYear(), d.getMonth(), d.getDate())
  const dayDiff = Math.floor((targetDate - baseDate) / (1000 * 60 * 60 * 24))
  return ((10 + dayDiff) % 60 + 60) % 60
}

/** 12지지별 시간대 */
const BRANCH_TIMES: Record<string, string> = {
  '子': '23-01시', '丑': '01-03시', '寅': '03-05시', '卯': '05-07시',
  '辰': '07-09시', '巳': '09-11시', '午': '11-13시', '未': '13-15시',
  '申': '15-17시', '酉': '17-19시', '戌': '19-21시', '亥': '21-23시',
}

/** 12지지별 계절 오행 */
const BRANCH_SEASON: Record<string, number> = {
  '子': 4, '丑': 2, '寅': 0, '卯': 0,
  '辰': 2, '巳': 1, '午': 1, '未': 2,
  '申': 3, '酉': 3, '戌': 2, '亥': 4,
}

/** 충(冲) 매핑: 子-午, 丑-未, 寅-申 등 */
const CHUNG_MAP: Record<number, number> = {
  0: 6, 1: 7, 2: 8, 3: 9, 4: 10, 5: 11,
  6: 0, 7: 1, 8: 2, 9: 3, 10: 4, 11: 5,
}

/** 오행 -> 방향 */
const ELEMENT_DIRECTIONS: Record<string, string> = {
  '목': '동쪽', '화': '남쪽', '토': '중앙', '금': '서쪽', '수': '북쪽',
}

/** 오행 -> 사용자 친화 매핑 */
const OHAENG_TO_FRIENDLY: Record<string, Record<string, string>> = {
  '木': { '기회': '성장과 창의성', '도전': '충동 조절' },
  '火': { '기회': '열정과 표현', '도전': '과도한 소비' },
  '土': { '기회': '안정과 신뢰', '도전': '우유부단' },
  '金': { '기회': '결단과 집중', '도전': '완벽주의' },
  '水': { '기회': '통찰과 지혜', '도전': '불안과 걱정' },
  '목': { '기회': '성장과 창의성', '도전': '충동 조절' },
  '화': { '기회': '열정과 표현', '도전': '과도한 소비' },
  '토': { '기회': '안정과 신뢰', '도전': '우유부단' },
  '금': { '기회': '결단과 집중', '도전': '완벽주의' },
  '수': { '기회': '통찰과 지혜', '도전': '불안과 걱정' },
}

// ============================================================
// 캐시
// ============================================================

const _sajuCache: Map<string, SajuData> = new Map()
const SAJU_CACHE_MAX = 200

// ============================================================
// 유틸리티 함수
// ============================================================

/** 날짜 차이를 일수로 계산 (UTC 기준) */
function daysBetween(a: Date, b: Date): number {
  const msPerDay = 86400000
  const utcA = Date.UTC(a.getFullYear(), a.getMonth(), a.getDate())
  const utcB = Date.UTC(b.getFullYear(), b.getMonth(), b.getDate())
  return Math.floor((utcB - utcA) / msPerDay)
}

/** 오행 용어를 사용자 친화 표현으로 변환 */
function convertOhaengToUserFriendly(ohaengList: string[], context: '기회' | '도전'): string[] {
  const result: string[] = []
  for (const element of ohaengList) {
    const mapping = OHAENG_TO_FRIENDLY[element]
    if (mapping) {
      result.push(mapping[context])
    } else {
      result.push(element)
    }
  }
  return result.length > 0 ? result : ['균형과 조화']
}

/** YYYY-MM-DD 문자열을 Date 객체로 파싱 */
function parseDate(dateStr: string): Date {
  const [year, month, day] = dateStr.split('-').map(Number)
  return new Date(year, month - 1, day)
}

/** HH:mm 문자열 파싱 */
function parseTime(timeStr: string): { hour: number; minute: number } {
  const [hour, minute] = timeStr.split(':').map(Number)
  return { hour: hour || 0, minute: minute || 0 }
}

// ============================================================
// 메인 함수: calculateSaju
// ============================================================

/**
 * 사주명리 계산
 *
 * calculateCompleteSajuData를 직접 호출하고 결과를 한국어 키 구조로 재구성합니다.
 *
 * @param birthInfo 출생 정보
 * @param targetDate 분석 대상 날짜 (YYYY-MM-DD)
 * @returns 사주명리 계산 결과 (내부 전문 용어)
 */
export function calculateSaju(birthInfo: BirthInfo, targetDate: string): SajuData {
  if (!calculateCompleteSajuData) {
    throw new Error('saju-calculator 패키지가 로드되지 않았습니다. 패키지 설치를 확인하세요.')
  }

  const birthDate = parseDate(birthInfo.birthDate)
  const { hour, minute } = parseTime(birthInfo.birthTime)

  // 캐시 키: 출생 정보 기반 (targetDate 제외 - 원국은 불변)
  const cacheKey = `${birthInfo.birthDate}_${birthInfo.birthTime}_${birthInfo.gender}_${birthInfo.birthPlace}`

  if (_sajuCache.has(cacheKey)) {
    const cachedBase = _sajuCache.get(cacheKey)!
    const sajuData = { ...cachedBase }
    const targetYear = parseInt(targetDate.split('-')[0], 10)

    // 세운 정보만 target_date에 맞게 재매핑
    let targetYearSewoon: SajuData['세운'] = null
    if (sajuData.원본데이터) {
      const raw = sajuData.원본데이터
      const curSewoon = raw.currentYearSewoon as SajuData['세운']
      const nextSewoon = raw.nextYearSewoon as SajuData['세운']
      if (curSewoon?.year === targetYear) {
        targetYearSewoon = curSewoon
      } else if (nextSewoon?.year === targetYear) {
        targetYearSewoon = nextSewoon
      }
    }
    sajuData.세운 = targetYearSewoon
    return sajuData
  }

  // 입력 데이터 준비
  const input = {
    year: birthDate.getFullYear(),
    month: birthDate.getMonth() + 1,
    day: birthDate.getDate(),
    hour,
    minute,
    gender: birthInfo.gender as 'male' | 'female',
    isLunar: false,
    birthPlace: birthInfo.birthPlace || '서울',
  }

  // 직접 계산 (subprocess 없이)
  const sajuRaw = calculateCompleteSajuData(input)

  // 대상 날짜의 세운 정보 결정
  const targetYear = parseInt(targetDate.split('-')[0], 10)
  let targetYearSewoon = null
  if (sajuRaw.currentYearSewoon?.year === targetYear) {
    targetYearSewoon = sajuRaw.currentYearSewoon
  } else if (sajuRaw.nextYearSewoon?.year === targetYear) {
    targetYearSewoon = sajuRaw.nextYearSewoon
  }

  // 결과 구조화 (한국어 키)
  const resultData: SajuData = {
    사주: {
      년주: {
        천간: sajuRaw.fourPillars.year.gan,
        지지: sajuRaw.fourPillars.year.ji,
        간지: sajuRaw.fourPillars.year.ganJi,
      },
      월주: {
        천간: sajuRaw.fourPillars.month.gan,
        지지: sajuRaw.fourPillars.month.ji,
        간지: sajuRaw.fourPillars.month.ganJi,
      },
      일주: {
        천간: sajuRaw.fourPillars.day.gan,
        지지: sajuRaw.fourPillars.day.ji,
        간지: sajuRaw.fourPillars.day.ganJi,
      },
      시주: {
        천간: sajuRaw.fourPillars.time.gan,
        지지: sajuRaw.fourPillars.time.ji,
        간지: sajuRaw.fourPillars.time.ganJi,
      },
    },
    오행: sajuRaw.ohHaeng.balance,
    십성: sajuRaw.sipSung.detail,
    격국: {
      일간: sajuRaw.gyeokGuk.dayMaster,
      일간오행: sajuRaw.gyeokGuk.dayMasterOhHaeng,
      강약: sajuRaw.gyeokGuk.strength,
      계절: sajuRaw.gyeokGuk.season,
    },
    용신: {
      용신: sajuRaw.yongSin.yongSin,
      기신: sajuRaw.yongSin.giSin,
    },
    대운: sajuRaw.daewoon,
    세운: targetYearSewoon,
    신살: sajuRaw.sinsal,
    성격: sajuRaw.personality,
    원본데이터: sajuRaw,
  }

  // 캐시 저장 (LRU 방식)
  if (_sajuCache.size >= SAJU_CACHE_MAX) {
    const oldestKey = _sajuCache.keys().next().value
    if (oldestKey !== undefined) {
      _sajuCache.delete(oldestKey)
    }
  }
  _sajuCache.set(cacheKey, { ...resultData })

  return resultData
}

// ============================================================
// analyzeDailyFortune
// ============================================================

/**
 * 일간 운세 분석 (내부 해석)
 *
 * 사주 데이터를 기반으로 일간 리듬 신호를 생성합니다.
 *
 * @param birthInfo 출생 정보
 * @param targetDate 분석 날짜 (YYYY-MM-DD)
 * @param sajuData 사주명리 계산 결과 (calculateSaju 반환값)
 * @returns 일간 운세 해석 (내부 표현)
 */
export function analyzeDailyFortune(
  birthInfo: BirthInfo,
  targetDate: string,
  sajuData: SajuData,
): DailyRhythm {
  // 세운 데이터
  const sewoon = sajuData.세운

  // 용신/기신
  const yongsinData = sajuData.용신 || {}
  const yongsinList: string[] = yongsinData.용신 || []
  const gisinList: string[] = yongsinData.기신 || []

  // 오행 균형
  const ohhaeng = sajuData.오행 || {}
  const dominantElement = Object.entries(ohhaeng).length > 0
    ? Object.entries(ohhaeng).reduce((a, b) => (a[1] > b[1] ? a : b))[0]
    : '목'

  // 격국 정보
  const gyeokguk = sajuData.격국 || {}
  const strength = gyeokguk.강약 || '중화'
  const season = gyeokguk.계절 || '봄'

  // 일진(日辰) 계산 - 60간지 순환으로 당일 천간/지지 계산 (sajuCalculator.ts 기준)
  const cycleIdx = getDayPillarIndex(targetDate)
  const todayStemIdx = cycleIdx % 10
  const todayBranchIdx = cycleIdx % 12
  const todayStem = HEAVENLY_STEMS[todayStemIdx]
  const todayBranch = EARTHLY_BRANCHES[todayBranchIdx]

  // 사주 일간(日干)과 당일 천간의 오행 관계 분석
  const dayjugan = sajuData.사주?.일주?.천간 || ''
  let dayRelation = 'bi' // 기본값: 비화(比和)
  let dailyAdjustment = 0

  if (dayjugan && STEM_WUXING[dayjugan] !== undefined && STEM_WUXING[todayStem] !== undefined) {
    const wa = STEM_WUXING[dayjugan]
    const wb = STEM_WUXING[todayStem]
    if (wa === wb) {
      dayRelation = 'bi'
      dailyAdjustment = 0
    } else if (SHENG_MAP[wa] === wb) {
      dayRelation = 'sheng_out'   // 내가 생함(食傷) -> 에너지 소모
      dailyAdjustment = -1
    } else if (SHENG_MAP[wb] === wa) {
      dayRelation = 'sheng_in'    // 내가 생받음(印) -> 에너지 충전
      dailyAdjustment = +1
    } else if (KE_MAP[wa] === wb) {
      dayRelation = 'ke_out'      // 내가 극함(財) -> 활동적
      dailyAdjustment = +1
    } else if (KE_MAP[wb] === wa) {
      dayRelation = 'ke_in'       // 내가 극받음(官殺) -> 긴장/주의
      dailyAdjustment = -1
    }
  }

  // 에너지 수준 계산 (원국 기반 + 일진 조정)
  let baseEnergy = 3
  if (sewoon && yongsinList.includes(dominantElement)) {
    baseEnergy = 4
  } else if (sewoon && gisinList.includes(dominantElement)) {
    baseEnergy = 2
  }

  // 일진 관계로 최종 에너지 조정 (1-5 범위)
  const energyLevel = Math.max(1, Math.min(5, baseEnergy + dailyAdjustment))

  // 집중력/사회운/결정력 계산 (십성 기반 + 일진 조정)
  const sipsung = sajuData.십성 || {}
  let concentration = 3 + Math.floor(((sipsung['식신'] || 0) + (sipsung['상관'] || 0)) / 2)
  let social = 3 + Math.floor(((sipsung['정관'] || 0) + (sipsung['편관'] || 0)) / 2)
  let decision = 3 + Math.floor(((sipsung['비견'] || 0) + (sipsung['겁재'] || 0)) / 2)

  // 일진 관계에 따른 세부 조정
  if (dayRelation === 'sheng_in') {        // 인성일: 집중력 +1
    concentration = Math.min(5, concentration + 1)
  } else if (dayRelation === 'sheng_out') { // 식상일: 창의/사교 +1
    social = Math.min(5, social + 1)
  } else if (dayRelation === 'ke_out') {    // 재성일: 결정력 +1
    decision = Math.min(5, decision + 1)
  } else if (dayRelation === 'ke_in') {     // 관살일: 집중력 변동 (긴장)
    concentration = Math.max(1, concentration - 1)
  }

  // 1-5 범위로 제한
  concentration = Math.min(5, Math.max(1, concentration))
  social = Math.min(5, Math.max(1, social))
  decision = Math.min(5, Math.max(1, decision))

  const fortuneAnalysis: DailyRhythm = {
    에너지_수준: energyLevel,
    집중력: concentration,
    사회운: social,
    결정력: decision,
    유리한_시간: getFavorableTimes(sajuData, targetDate),
    주의_시간: getCautionTimes(sajuData, targetDate),
    유리한_방향: getFavorableDirections(sajuData),
    주요_흐름: `${season}의 에너지, ${strength} 상태`,
    기회_요소: convertOhaengToUserFriendly(yongsinList, '기회'),
    도전_요소: convertOhaengToUserFriendly(gisinList, '도전'),
    격국: gyeokguk,
    세운점수: sewoon?.score ?? 50,
    일진: {
      천간: todayStem,
      지지: todayBranch,
      관계: dayRelation,
    },
  }

  return fortuneAnalysis
}

// ============================================================
// 보조 함수: 시간/방향 계산
// ============================================================

/** 유리한 시간대 계산 (천을귀인 기반 + 일진 시간대) */
function getFavorableTimes(sajuData: SajuData, targetDate: string): string[] {
  const sinsal = sajuData.신살

  const cycleIdxFav = getDayPillarIndex(targetDate)
  const todayBranch = EARTHLY_BRANCHES[cycleIdxFav % 12]
  const todayBranchTime = BRANCH_TIMES[todayBranch] || '09-11시'

  if (sinsal?.hasCheonEulGuiIn) {
    return [`오전 9-11시 (사시)`, `오늘 ${todayBranchTime} (${todayBranch}시)`]
  }

  return [`오늘 ${todayBranchTime} (${todayBranch}시)`, '오후 2-4시']
}

/** 주의 시간대 계산 (일진 기반) */
function getCautionTimes(sajuData: SajuData, targetDate: string): string[] {
  const sinsal = sajuData.신살

  const cycleIdxCaut = getDayPillarIndex(targetDate)
  const todayBranchIdx = cycleIdxCaut % 12
  const chungBranchIdx = CHUNG_MAP[todayBranchIdx]
  const chungBranch = EARTHLY_BRANCHES[chungBranchIdx]
  const chungTime = BRANCH_TIMES[chungBranch] || '자정 전후'

  if (sinsal?.hasGongMang) {
    return ['오후 5-7시 (유시)', `오늘 ${chungTime} (${chungBranch}시, 충 시간대)`]
  }

  return [`오늘 ${chungTime} (${chungBranch}시, 충 시간대)`]
}

/** 유리한 방향 계산 (용신 오행 기반) */
function getFavorableDirections(sajuData: SajuData): string[] {
  const yongsinData = sajuData.용신 || {}
  const yongsinList: string[] = yongsinData.용신 || []

  const directions = yongsinList
    .slice(0, 2)
    .map(elem => ELEMENT_DIRECTIONS[elem] || '동쪽')

  return directions.length > 0 ? directions : ['동쪽', '남쪽']
}

// ============================================================
// analyzeMonthlyRhythm
// ============================================================

/**
 * 월간 리듬 분석 (내부 해석)
 *
 * @param birthInfo 출생 정보
 * @param year 분석 대상 년도
 * @param month 분석 대상 월 (1-12)
 * @param sajuData 사주명리 계산 결과
 * @returns 월간 리듬 해석 (내부 표현)
 */
export function analyzeMonthlyRhythm(
  birthInfo: BirthInfo,
  year: number,
  month: number,
  sajuData: SajuData,
): MonthlyRhythm {
  // 월주 정보
  const monthPillar = sajuData.사주?.월주 || {}
  const monthGan = monthPillar.천간 || ''
  const monthJi = monthPillar.지지 || ''

  // 용신/기신
  const yongsinData = sajuData.용신 || {}
  const yongsinList: string[] = yongsinData.용신 || []
  const gisinList: string[] = yongsinData.기신 || []

  // 격국 정보
  const gyeokguk = sajuData.격국 || {}
  const season = gyeokguk.계절 || '봄'

  // 월간 테마 결정
  const elementThemes: Record<string, string> = {
    '목': '성장과 확장', '화': '활동과 표현', '토': '안정과 정리',
    '금': '수확과 결단', '수': '휴식과 계획',
  }

  // 월별 오행 매핑 (절기 기준 간소화)
  const monthElements: Record<number, string> = {
    1: '수', 2: '수', 3: '목', 4: '목', 5: '화', 6: '화',
    7: '토', 8: '금', 9: '금', 10: '토', 11: '수', 12: '수',
  }
  const currentMonthElement = monthElements[month] || '목'
  const mainTheme = elementThemes[currentMonthElement] || '균형과 조화'

  // 우선순위 결정 (용신 기반)
  const priorities: string[] = []
  if (yongsinList.includes('목')) priorities.push('새로운 시작과 학습')
  if (yongsinList.includes('화')) priorities.push('관계 확장과 소통')
  if (yongsinList.includes('토')) priorities.push('기반 다지기와 정리')
  if (yongsinList.includes('금')) priorities.push('결단과 실행')
  if (yongsinList.includes('수')) priorities.push('계획과 준비')

  // 우선순위 최소 3개 보장
  const defaultPriorities = ['일상 루틴 유지', '건강 관리', '관계 점검']
  for (const dp of defaultPriorities) {
    if (priorities.length >= 3) break
    if (!priorities.includes(dp)) {
      priorities.push(dp)
    }
  }

  // 일별 에너지 수준 계산 (일진 기반)
  const daysInMonth = new Date(year, month, 0).getDate()
  const dailyEnergy: Record<number, number> = {}

  // 일간(사주 일주 천간)
  const dayjugan = sajuData.사주?.일주?.천간 || ''

  // 용신 오행 인덱스
  const yongsinWuxing: Record<string, number> = { '목': 0, '화': 1, '토': 2, '금': 3, '수': 4 }

  for (let day = 1; day <= daysInMonth; day++) {
    const targetDay = new Date(year, month - 1, day)
    const cycleIdxDay = getDayPillarIndexFromDate(targetDay)
    const todayStem = HEAVENLY_STEMS[cycleIdxDay % 10]

    let baseEnergyDay = 3
    if (dayjugan && STEM_WUXING[dayjugan] !== undefined && STEM_WUXING[todayStem] !== undefined) {
      const wa = STEM_WUXING[dayjugan]
      const wb = STEM_WUXING[todayStem]
      if (SHENG_MAP[wb] === wa) {          // 오늘이 나를 생함 (인성) -> +1
        baseEnergyDay = 4
      } else if (KE_MAP[wb] === wa) {      // 오늘이 나를 극함 (관살) -> -1
        baseEnergyDay = 2
      } else if (SHENG_MAP[wa] === wb) {   // 내가 오늘을 생함 (식상) -> 보통
        baseEnergyDay = 3
      } else if (KE_MAP[wa] === wb) {      // 내가 오늘을 극함 (재성) -> 약간 활동적
        baseEnergyDay = 4
      }
    }

    // 용신 오행과 당일 오행이 일치하면 추가 보정
    if (todayStem && STEM_WUXING[todayStem] !== undefined) {
      const wb = STEM_WUXING[todayStem]
      for (const yong of yongsinList) {
        if (yongsinWuxing[yong] === wb) {
          baseEnergyDay = Math.min(5, baseEnergyDay + 1)
          break
        }
      }
      for (const gi of gisinList) {
        if (yongsinWuxing[gi] === wb) {
          baseEnergyDay = Math.max(1, baseEnergyDay - 1)
          break
        }
      }
    }

    dailyEnergy[day] = baseEnergyDay
  }

  // 기회/도전 요소
  const ohaengOpportunityMap: Record<string, string> = {
    '목': '성장 확장 에너지 활용', '화': '활동 소통 에너지 활용',
    '토': '안정 정리 에너지 활용', '금': '결단 실행 에너지 활용',
    '수': '계획 휴식 에너지 활용',
  }
  const ohaengChallengeMap: Record<string, string> = {
    '목': '과도한 확장 주의', '화': '과열 충동 주의',
    '토': '과도한 고집 주의', '금': '지나친 단호함 주의',
    '수': '과도한 소극성 주의',
  }

  const opportunities = yongsinList.map(e => ohaengOpportunityMap[e] || `${e} 에너지 활용`)
  const challenges = gisinList.map(e => ohaengChallengeMap[e] || `${e} 에너지 주의`)

  return {
    년월: `${year}년 ${month}월`,
    주제: mainTheme,
    우선순위: priorities.slice(0, 3),
    일별_에너지: dailyEnergy,
    기회_요소: opportunities.length > 0 ? opportunities : ['루틴 최적화'],
    도전_요소: challenges.length > 0 ? challenges : ['과도한 활동 자제'],
    월주_정보: {
      천간: monthGan,
      지지: monthJi,
      간지: `${monthGan}${monthJi}`,
    },
    전체_흐름: `${season}의 ${mainTheme} 시기`,
  }
}

// ============================================================
// analyzeYearlyRhythm
// ============================================================

/**
 * 연간 리듬 분석 (내부 해석)
 *
 * @param birthInfo 출생 정보
 * @param year 분석 대상 년도
 * @param sajuData 사주명리 계산 결과
 * @returns 연간 리듬 해석 (내부 표현)
 */
export function analyzeYearlyRhythm(
  birthInfo: BirthInfo,
  year: number,
  sajuData: SajuData,
): YearlyRhythm {
  // 대운 정보
  const currentDaewoon = sajuData.대운?.current ?? null

  // 세운 정보
  const sewoon = sajuData.세운

  // 용신/기신
  const yongsinData = sajuData.용신 || {}
  const yongsinList: string[] = yongsinData.용신 || []
  const gisinList: string[] = yongsinData.기신 || []

  // 연간 테마 (대운 + 세운 조합)
  let yearlyTheme = '안정과 성장의 해'
  if (currentDaewoon) {
    const daewoonGan = currentDaewoon.gan || ''
    yearlyTheme = `${daewoonGan} 대운 - 변화와 성장의 시기`
  }

  // 월별 간단한 신호 (12개월)
  const monthThemes: Record<number, string> = {
    1: '새해 계획', 2: '기반 다지기', 3: '활동 시작',
    4: '성장 가속', 5: '관계 확장', 6: '성과 점검',
    7: '재정비', 8: '실행력', 9: '수확 준비',
    10: '정리와 마무리', 11: '성찰', 12: '다음 준비',
  }

  // 용신/기신 오행 인덱스 매핑
  const yongsinWuxing: Record<string, number> = { '목': 0, '화': 1, '토': 2, '금': 3, '수': 4 }

  // 월별 주도 오행 (절기 기준 간소화)
  const monthWuxing: Record<number, number> = {
    1: 4, 2: 4, 3: 0, 4: 0, 5: 1, 6: 1,
    7: 2, 8: 3, 9: 3, 10: 2, 11: 4, 12: 4,
  }

  const monthlySignals: Record<number, { 월: number; 테마: string; 에너지: number }> = {}

  for (let m = 1; m <= 12; m++) {
    const monthWx = monthWuxing[m] ?? 2
    let baseScore = 3

    // 용신 오행과 월 오행이 일치하면 +1
    for (const yong of yongsinList) {
      if (yongsinWuxing[yong] === monthWx) {
        baseScore = Math.min(5, baseScore + 1)
        break
      }
    }
    // 기신 오행과 월 오행이 일치하면 -1
    for (const gi of gisinList) {
      if (yongsinWuxing[gi] === monthWx) {
        baseScore = Math.max(1, baseScore - 1)
        break
      }
    }

    monthlySignals[m] = {
      월: m,
      테마: monthThemes[m] || '균형',
      에너지: baseScore,
    }
  }

  return {
    년도: year,
    주제: yearlyTheme,
    대운_정보: currentDaewoon,
    세운_정보: sewoon,
    월별_신호: monthlySignals,
    용신: yongsinList,
    기신: gisinList,
    전체_흐름: `${year}년은 ${yearlyTheme}`,
    핵심_과제: ['대운에 맞춘 성장', '세운 활용', '용신 오행 강화'],
  }
}
