/**
 * 대운 시작 나이 정밀 계산
 *
 * 전통 명리학 규칙:
 * - 양남음녀(陽男陰女): 생일 → 다음 절입일 (순행)
 * - 음남양녀(陰男陽女): 생일 → 이전 절입일 (역행)
 * - 계산: 3일 = 1년 (반올림)
 *
 * @module daeunStartAge
 */

import type { CheonGan } from '../sinsal/types';
import { getSolarTermsForYear, MONTH_START_TERMS } from '../../calculators/solarTermsCalculator';

// ==================== 타입 정의 ====================

export interface DaeunStartAgeInput {
  /** 생년월일 (양력) */
  birthDate: Date;
  /** 출생 시각 (HH:mm 형식, 예: '14:30') */
  birthTime: string;
  /** 성별 */
  gender: 'male' | 'female';
  /** 년주 천간 (음양 판별용) */
  yearGan: CheonGan;
}

export interface DaeunStartAgeResult {
  /** 대운 시작 나이 (정수, 예: 7) */
  startAge: number;
  /** 대운 시작 나이 (소수점, 예: 7.4) */
  startAgeDecimal: number;
  /** 절입일까지 일수 (양수: 순행, 음수: 역행) */
  daysToJeolip: number;
  /** 절입일까지 시간 */
  hoursToJeolip: number;
  /** 대운 방향 */
  direction: 'forward' | 'backward';
  /** 가장 가까운 절입일 */
  nearestJeolipDate: Date;
  /** 절입일 이름 */
  jeolipName: string;
  /** 해석 */
  interpretation: string;
}

// ==================== 상수 정의 ====================

/** 양간(陽干) 천간 */
const YANG_GAN: CheonGan[] = ['갑', '병', '무', '경', '임'];

/** 12절(節) 이름 목록 - 대운 계산에 사용하는 절만 */
const JEOL_NAMES = Object.values(MONTH_START_TERMS);

// ==================== 헬퍼 함수 ====================

function isYangGan(gan: CheonGan): boolean {
  return YANG_GAN.includes(gan);
}

function applyTimeToDate(date: Date, timeString: string): Date {
  const [hourStr, minuteStr] = timeString.split(':');
  const hour = parseInt(hourStr, 10) || 0;
  const minute = parseInt(minuteStr, 10) || 0;
  const result = new Date(date);
  result.setHours(hour, minute, 0, 0);
  return result;
}

/**
 * 천문 알고리즘 기반 절입일 목록 생성 (년도 범위)
 */
function getAccurateJeolipDates(year: number): { date: Date; name: string }[] {
  const results: { date: Date; name: string }[] = [];

  for (const y of [year - 1, year, year + 1]) {
    const terms = getSolarTermsForYear(y);
    for (const t of terms) {
      if (JEOL_NAMES.includes(t.term)) {
        const [h, m] = (t.time || '00:00').split(':').map(Number);
        const d = new Date(t.year, t.month - 1, t.day, h || 0, m || 0, 0);
        results.push({ date: d, name: t.term });
      }
    }
  }

  results.sort((a, b) => a.date.getTime() - b.date.getTime());
  return results;
}

/**
 * 생일로부터 가장 가까운 절입일 찾기 (천문 알고리즘 기반)
 */
function findNearestJeolip(
  birthDate: Date,
  direction: 'forward' | 'backward',
): { date: Date; name: string } {
  const year = birthDate.getFullYear();
  const allJeolips = getAccurateJeolipDates(year);

  if (direction === 'forward') {
    const future = allJeolips.filter(j => j.date.getTime() > birthDate.getTime());
    return future[0];
  } else {
    const past = allJeolips.filter(j => j.date.getTime() < birthDate.getTime());
    return past[past.length - 1];
  }
}

function getTimeDifference(date1: Date, date2: Date): number {
  return Math.abs(date2.getTime() - date1.getTime());
}

function millisecondsToTime(ms: number): { days: number; hours: number; minutes: number } {
  const totalMinutes = Math.floor(ms / (1000 * 60));
  const totalHours = Math.floor(totalMinutes / 60);
  const days = Math.floor(totalHours / 24);
  const hours = totalHours % 24;
  const minutes = totalMinutes % 60;
  return { days, hours, minutes };
}

// ==================== 공개 API ====================

export function calculateDaeunStartAge(input: DaeunStartAgeInput): DaeunStartAgeResult {
  const { birthDate, birthTime, gender, yearGan } = input;

  // 1. 생년월일 + 시각 조합
  const birthDateTime = applyTimeToDate(birthDate, birthTime);

  // 2. 음양 판별
  const isYang = isYangGan(yearGan);
  const isMale = gender === 'male';

  // 3. 대운 방향 결정
  const direction: 'forward' | 'backward' =
    (isYang && isMale) || (!isYang && !isMale) ? 'forward' : 'backward';

  // 4. 천문 알고리즘 기반 절입일 찾기
  const { date: jeolipDate, name: jeolipName } = findNearestJeolip(birthDateTime, direction);

  // 5. 시간 차이 계산
  const timeDiffMs = getTimeDifference(birthDateTime, jeolipDate);
  const { days, hours, minutes } = millisecondsToTime(timeDiffMs);

  // 6. 대운 시작 나이 계산: 3일 = 1년 (반올림)
  const totalDaysWithHours = days + hours / 24 + minutes / 1440;
  const exactYears = totalDaysWithHours / 3;
  const startAge = Math.round(exactYears);
  const startAgeDecimal = parseFloat(exactYears.toFixed(1));

  // 7. 해석 생성
  const genderText = isMale ? '남자' : '여자';
  const yangText = isYang ? '양간' : '음간';
  const directionText = direction === 'forward' ? '순행' : '역행';

  const interpretation = [
    `${genderText}이고 ${yearGan}년생(${yangText})이므로 ${directionText}으로 계산합니다.`,
    `생일(${birthDateTime.toLocaleDateString('ko-KR')})부터 ${direction === 'forward' ? '다음' : '이전'} 절입일(${jeolipName} ${jeolipDate.toLocaleDateString('ko-KR')})까지 ${days}일 ${hours}시간입니다.`,
    `계산: ${days}일 ${hours}시간 ÷ 3 = ${startAgeDecimal}년 → 반올림 ${startAge}세`,
    `대운 시작 나이: ${startAge}세 (정확: ${startAgeDecimal}세)`,
  ].join('\n');

  return {
    startAge,
    startAgeDecimal,
    daysToJeolip: direction === 'forward' ? days : -days,
    hoursToJeolip: hours,
    direction,
    nearestJeolipDate: jeolipDate,
    jeolipName,
    interpretation,
  };
}

export function getSimpleDaeunStartAge(
  birthDate: Date,
  gender: 'male' | 'female',
  yearGan: CheonGan,
): number {
  const result = calculateDaeunStartAge({
    birthDate,
    birthTime: '12:00',
    gender,
    yearGan,
  });
  return result.startAge;
}
