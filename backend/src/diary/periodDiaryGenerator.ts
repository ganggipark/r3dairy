/**
 * 기간별 다이어리 생성기
 * 
 * 특정 기간(1개월/3개월/6개월/1년)의 다이어리 데이터를 일괄 생성
 * 각 날짜마다 실제 사주/기문 엔진을 호출하여 새로운 데이터 생성
 */

import { DailyDiaryPayload, BuilderInput } from './types';
import { buildDailyDiaryPayload } from './dailyDiaryBuilder';

// ============================================================
// Type Definitions
// ============================================================

export type DurationType = '1m' | '3m' | '6m' | '1y';

export interface PeriodDiaryInput {
  /** 시작 날짜 (YYYY-MM-DD) */
  startDate: string;
  /** 기간 타입 */
  durationType: DurationType;
  /** 생년월일 정보 (선택사항) */
  birth?: {
    year: number;
    month: number;
    day: number;
    hour?: number;
    minute?: number;
    isLunar?: boolean;
    birthPlace?: string;
  };
}

export interface PeriodDiaryResult {
  /** 시작 날짜 */
  startDate: string;
  /** 종료 날짜 */
  endDate: string;
  /** 기간 타입 */
  durationType: DurationType;
  /** 총 일수 */
  totalDays: number;
  /** 일별 다이어리 페이로드 배열 */
  entries: DailyDiaryPayload[];
}

// ============================================================
// Helper Functions
// ============================================================

/**
 * 특정 년월의 마지막 일자 구하기
 */
function getLastDayOfMonth(year: number, month: number): number {
  // month는 0-based (0=1월, 11=12월)
  // 다음 달의 0일을 구하면 이번 달의 마지막 날
  return new Date(year, month + 1, 0).getDate();
}

/**
 * 다이어리 제품용 월 단위 날짜 추가
 * 타겟 월에 동일 일이 없으면 그 달의 마지막 날로 clamp
 */
function addMonthsProper(date: Date, months: number): Date {
  const originalDay = date.getDate();
  
  // 년과 월 계산
  let targetMonth = date.getMonth() + months;
  let targetYear = date.getFullYear();
  
  // 월이 12를 넘어가면 년도 조정
  while (targetMonth > 11) {
    targetMonth -= 12;
    targetYear += 1;
  }
  while (targetMonth < 0) {
    targetMonth += 12;
    targetYear -= 1;
  }
  
  // 타겟 월의 마지막 일 구하기
  const lastDayOfTargetMonth = getLastDayOfMonth(targetYear, targetMonth);
  
  // 원래 일자가 타겟 월의 마지막 일보다 크면 마지막 일로 설정
  const targetDay = Math.min(originalDay, lastDayOfTargetMonth);
  
  // 새 Date 객체를 년, 월, 일로 정확히 생성
  const targetDate = new Date(targetYear, targetMonth, targetDay);
  
  return targetDate;
}

/**
 * 기간 타입에 따른 종료일 계산
 * 다이어리 제품용 캘린더 월 기준 계산
 */
function calculateEndDate(startDate: string, durationType: DurationType): { endDate: string; totalDays: number } {
  const start = new Date(startDate);
  
  // 유효성 검증
  if (isNaN(start.getTime())) {
    throw new Error(`Invalid start date: ${startDate}`);
  }
  
  let end: Date;
  
  switch (durationType) {
    case '1m':
      // 1개월 후 (다이어리 규칙: 월말 clamp)
      end = addMonthsProper(start, 1);
      break;
    case '3m':
      // 3개월 후
      end = addMonthsProper(start, 3);
      break;
    case '6m':
      // 6개월 후
      end = addMonthsProper(start, 6);
      break;
    case '1y':
      // 1년 후 (다이어리 규칙: 월말 clamp 적용)
      end = addMonthsProper(start, 12);
      break;
    default:
      throw new Error(`Invalid duration type: ${durationType}`);
  }
  
  // 총 일수 계산 (시작일과 종료일 모두 포함)
  const totalDays = Math.ceil((end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24)) + 1;
  
  return {
    endDate: formatDate(end),
    totalDays
  };
}

/**
 * Date 객체를 YYYY-MM-DD 형식으로 변환
 */
function formatDate(date: Date): string {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

/**
 * 날짜 문자열에 일수를 더함
 */
function addDays(dateStr: string, days: number): string {
  const date = new Date(dateStr);
  date.setDate(date.getDate() + days);
  return formatDate(date);
}

/**
 * 두 날짜 사이의 모든 날짜 생성
 */
function generateDateRange(startDate: string, endDate: string): string[] {
  const dates: string[] = [];
  const current = new Date(startDate);
  const end = new Date(endDate);
  
  while (current <= end) {
    dates.push(formatDate(new Date(current)));
    current.setDate(current.getDate() + 1);
  }
  
  return dates;
}

// ============================================================
// Main Function
// ============================================================

/**
 * 기간별 다이어리 생성
 * 
 * @param input 기간 다이어리 생성 입력
 * @returns 기간별 다이어리 결과
 */
export async function buildPeriodDiary(input: PeriodDiaryInput): Promise<PeriodDiaryResult> {
  const { startDate, durationType, birth } = input;
  
  console.log(`[PeriodDiaryGenerator] Starting generation for ${durationType} from ${startDate}`);
  
  // 1. 종료일 및 총 일수 계산
  const { endDate, totalDays } = calculateEndDate(startDate, durationType);
  console.log(`[PeriodDiaryGenerator] Period: ${startDate} to ${endDate} (${totalDays} days)`);
  
  // 2. 날짜 범위 생성
  const dateRange = generateDateRange(startDate, endDate);
  
  // 3. 각 날짜에 대해 다이어리 생성
  const entries: DailyDiaryPayload[] = [];
  
  for (let i = 0; i < dateRange.length; i++) {
    const currentDate = dateRange[i];
    console.log(`[PeriodDiaryGenerator] Generating diary for ${currentDate} (${i + 1}/${totalDays})`);
    
    try {
      // 각 날짜마다 새로운 사주/기문 계산
      const dailyPayload = await buildDailyDiaryPayload({
        date: currentDate,
        birth,
        options: {
          includeSaju: true,
          includeQimen: true,
          includeNlp: true
        }
      });
      
      entries.push(dailyPayload);
      
      // Rate limiting을 위한 짧은 대기 (선택사항)
      if (i < dateRange.length - 1) {
        await new Promise(resolve => setTimeout(resolve, 10));
      }
    } catch (error) {
      console.error(`[PeriodDiaryGenerator] Error generating diary for ${currentDate}:`, error);
      throw new Error(`Failed to generate diary for ${currentDate}: ${error}`);
    }
  }
  
  console.log(`[PeriodDiaryGenerator] Successfully generated ${entries.length} diary entries`);
  
  // 4. 결과 반환
  return {
    startDate,
    endDate,
    durationType,
    totalDays,
    entries
  };
}

// ============================================================
// Export Additional Utilities
// ============================================================

/**
 * 기간별 예상 종료일 계산 (미리보기용)
 */
export function getExpectedEndDate(startDate: string, durationType: DurationType): string {
  const { endDate } = calculateEndDate(startDate, durationType);
  return endDate;
}

/**
 * 기간별 예상 일수 계산 (미리보기용)
 */
export function getExpectedDays(startDate: string, durationType: DurationType): number {
  const { totalDays } = calculateEndDate(startDate, durationType);
  return totalDays;
}

/**
 * 월말 처리 규칙 설명
 * 
 * 1. 1월 31일 + 1개월 = 2월 28/29일 (월말)
 * 2. 3월 31일 + 1개월 = 4월 30일 (월말)
 * 3. 8월 31일 + 6개월 = 2월 28/29일 (월말)
 * 4. 2월 29일(윤년) + 1년 = 2월 28일(평년) 또는 2월 29일(윤년)
 * 
 * JavaScript Date 객체는 자동으로 월말을 처리함
 */