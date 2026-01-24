/**
 * 정확한 절기(節氣) 계산 시스템
 *
 * 데이터 출처:
 * - 2024-2026년: 한국천문연구원 (https://astro.kasi.re.kr) 공식 데이터
 * - 2027-2030년: uncle.tools (한국천문연구원 공식 데이터 발표 대기 중)
 * 모든 시각은 KST (한국표준시) 기준
 *
 * @author SajuApp
 * @version 2.0.0
 */

// ============================================================
// 타입 정의
// ============================================================

export interface SolarTermData {
  year: number;
  term: string;
  date: string;
  time: string;
  month: number;
  day: number;
  solarMonth: number;
}

export interface DaysToTermResult {
  days: number;
  hours: number;
  minutes: number;
  totalMinutes: number;
}

// ============================================================
// 24절기 정의
// ============================================================

export const SOLAR_TERM_NAMES = [
  '소한', '대한',
  '입춘', '우수',
  '경칩', '춘분',
  '청명', '곡우',
  '입하', '소만',
  '망종', '하지',
  '소서', '대서',
  '입추', '처서',
  '백로', '추분',
  '한로', '상강',
  '입동', '소설',
  '대설', '동지',
] as const;

export const MONTH_START_TERMS: Record<number, string> = {
  1: '입춘',
  2: '경칩',
  3: '청명',
  4: '입하',
  5: '망종',
  6: '소서',
  7: '입추',
  8: '백로',
  9: '한로',
  10: '입동',
  11: '대설',
  12: '소한',
};

export const TERM_TO_SOLAR_MONTH: Record<string, number> = {
  '소한': 12, '대한': 12,
  '입춘': 1,  '우수': 1,
  '경칩': 2,  '춘분': 2,
  '청명': 3,  '곡우': 3,
  '입하': 4,  '소만': 4,
  '망종': 5,  '하지': 5,
  '소서': 6,  '대서': 6,
  '입추': 7,  '처서': 7,
  '백로': 8,  '추분': 8,
  '한로': 9,  '상강': 9,
  '입동': 10, '소설': 10,
  '대설': 11, '동지': 11,
};

// ============================================================
// 절기 데이터 (2024-2030)
// ============================================================

const SOLAR_TERMS_2024: SolarTermData[] = [
  { year: 2024, term: '소한', date: '2024-01-06', time: '05:49', month: 1, day: 6, solarMonth: 12 },
  { year: 2024, term: '대한', date: '2024-01-20', time: '23:07', month: 1, day: 20, solarMonth: 12 },
  { year: 2024, term: '입춘', date: '2024-02-04', time: '17:27', month: 2, day: 4, solarMonth: 1 },
  { year: 2024, term: '우수', date: '2024-02-19', time: '13:13', month: 2, day: 19, solarMonth: 1 },
  { year: 2024, term: '경칩', date: '2024-03-05', time: '10:23', month: 3, day: 5, solarMonth: 2 },
  { year: 2024, term: '춘분', date: '2024-03-20', time: '12:06', month: 3, day: 20, solarMonth: 2 },
  { year: 2024, term: '청명', date: '2024-04-04', time: '15:02', month: 4, day: 4, solarMonth: 3 },
  { year: 2024, term: '곡우', date: '2024-04-19', time: '21:59', month: 4, day: 19, solarMonth: 3 },
  { year: 2024, term: '입하', date: '2024-05-05', time: '08:10', month: 5, day: 5, solarMonth: 4 },
  { year: 2024, term: '소만', date: '2024-05-20', time: '20:59', month: 5, day: 20, solarMonth: 4 },
  { year: 2024, term: '망종', date: '2024-06-05', time: '12:10', month: 6, day: 5, solarMonth: 5 },
  { year: 2024, term: '하지', date: '2024-06-21', time: '05:51', month: 6, day: 21, solarMonth: 5 },
  { year: 2024, term: '소서', date: '2024-07-06', time: '22:20', month: 7, day: 6, solarMonth: 6 },
  { year: 2024, term: '대서', date: '2024-07-22', time: '15:44', month: 7, day: 22, solarMonth: 6 },
  { year: 2024, term: '입추', date: '2024-08-07', time: '08:09', month: 8, day: 7, solarMonth: 7 },
  { year: 2024, term: '처서', date: '2024-08-22', time: '22:55', month: 8, day: 22, solarMonth: 7 },
  { year: 2024, term: '백로', date: '2024-09-07', time: '11:11', month: 9, day: 7, solarMonth: 8 },
  { year: 2024, term: '추분', date: '2024-09-22', time: '20:44', month: 9, day: 22, solarMonth: 8 },
  { year: 2024, term: '한로', date: '2024-10-08', time: '03:00', month: 10, day: 8, solarMonth: 9 },
  { year: 2024, term: '상강', date: '2024-10-23', time: '06:15', month: 10, day: 23, solarMonth: 9 },
  { year: 2024, term: '입동', date: '2024-11-07', time: '06:20', month: 11, day: 7, solarMonth: 10 },
  { year: 2024, term: '소설', date: '2024-11-22', time: '03:56', month: 11, day: 22, solarMonth: 10 },
  { year: 2024, term: '대설', date: '2024-12-07', time: '00:17', month: 12, day: 7, solarMonth: 11 },
  { year: 2024, term: '동지', date: '2024-12-21', time: '18:21', month: 12, day: 21, solarMonth: 11 },
];

const SOLAR_TERMS_2025: SolarTermData[] = [
  { year: 2025, term: '소한', date: '2025-01-05', time: '11:32', month: 1, day: 5, solarMonth: 12 },
  { year: 2025, term: '대한', date: '2025-01-20', time: '04:59', month: 1, day: 20, solarMonth: 12 },
  { year: 2025, term: '입춘', date: '2025-02-03', time: '23:10', month: 2, day: 3, solarMonth: 1 },
  { year: 2025, term: '우수', date: '2025-02-18', time: '19:07', month: 2, day: 18, solarMonth: 1 },
  { year: 2025, term: '경칩', date: '2025-03-05', time: '16:07', month: 3, day: 5, solarMonth: 2 },
  { year: 2025, term: '춘분', date: '2025-03-20', time: '18:01', month: 3, day: 20, solarMonth: 2 },
  { year: 2025, term: '청명', date: '2025-04-04', time: '20:48', month: 4, day: 4, solarMonth: 3 },
  { year: 2025, term: '곡우', date: '2025-04-20', time: '03:55', month: 4, day: 20, solarMonth: 3 },
  { year: 2025, term: '입하', date: '2025-05-05', time: '13:57', month: 5, day: 5, solarMonth: 4 },
  { year: 2025, term: '소만', date: '2025-05-21', time: '02:54', month: 5, day: 21, solarMonth: 4 },
  { year: 2025, term: '망종', date: '2025-06-05', time: '17:56', month: 6, day: 5, solarMonth: 5 },
  { year: 2025, term: '하지', date: '2025-06-21', time: '11:42', month: 6, day: 21, solarMonth: 5 },
  { year: 2025, term: '소서', date: '2025-07-07', time: '04:05', month: 7, day: 7, solarMonth: 6 },
  { year: 2025, term: '대서', date: '2025-07-22', time: '21:29', month: 7, day: 22, solarMonth: 6 },
  { year: 2025, term: '입추', date: '2025-08-07', time: '13:51', month: 8, day: 7, solarMonth: 7 },
  { year: 2025, term: '처서', date: '2025-08-23', time: '04:33', month: 8, day: 23, solarMonth: 7 },
  { year: 2025, term: '백로', date: '2025-09-07', time: '16:52', month: 9, day: 7, solarMonth: 8 },
  { year: 2025, term: '추분', date: '2025-09-23', time: '02:19', month: 9, day: 23, solarMonth: 8 },
  { year: 2025, term: '한로', date: '2025-10-08', time: '08:41', month: 10, day: 8, solarMonth: 9 },
  { year: 2025, term: '상강', date: '2025-10-23', time: '11:51', month: 10, day: 23, solarMonth: 9 },
  { year: 2025, term: '입동', date: '2025-11-07', time: '11:54', month: 11, day: 7, solarMonth: 10 },
  { year: 2025, term: '소설', date: '2025-11-22', time: '09:35', month: 11, day: 22, solarMonth: 10 },
  { year: 2025, term: '대설', date: '2025-12-07', time: '05:52', month: 12, day: 7, solarMonth: 11 },
  { year: 2025, term: '동지', date: '2025-12-22', time: '00:03', month: 12, day: 22, solarMonth: 11 },
];

const SOLAR_TERMS_2026: SolarTermData[] = [
  { year: 2026, term: '소한', date: '2026-01-05', time: '17:23', month: 1, day: 5, solarMonth: 12 },
  { year: 2026, term: '대한', date: '2026-01-20', time: '10:45', month: 1, day: 20, solarMonth: 12 },
  { year: 2026, term: '입춘', date: '2026-02-04', time: '05:02', month: 2, day: 4, solarMonth: 1 },
  { year: 2026, term: '우수', date: '2026-02-19', time: '00:52', month: 2, day: 19, solarMonth: 1 },
  { year: 2026, term: '경칩', date: '2026-03-05', time: '21:59', month: 3, day: 5, solarMonth: 2 },
  { year: 2026, term: '춘분', date: '2026-03-20', time: '23:46', month: 3, day: 20, solarMonth: 2 },
  { year: 2026, term: '청명', date: '2026-04-05', time: '02:40', month: 4, day: 5, solarMonth: 3 },
  { year: 2026, term: '곡우', date: '2026-04-20', time: '09:39', month: 4, day: 20, solarMonth: 3 },
  { year: 2026, term: '입하', date: '2026-05-05', time: '19:48', month: 5, day: 5, solarMonth: 4 },
  { year: 2026, term: '소만', date: '2026-05-21', time: '08:37', month: 5, day: 21, solarMonth: 4 },
  { year: 2026, term: '망종', date: '2026-06-05', time: '23:48', month: 6, day: 5, solarMonth: 5 },
  { year: 2026, term: '하지', date: '2026-06-21', time: '17:24', month: 6, day: 21, solarMonth: 5 },
  { year: 2026, term: '소서', date: '2026-07-07', time: '09:57', month: 7, day: 7, solarMonth: 6 },
  { year: 2026, term: '대서', date: '2026-07-23', time: '03:13', month: 7, day: 23, solarMonth: 6 },
  { year: 2026, term: '입추', date: '2026-08-07', time: '19:42', month: 8, day: 7, solarMonth: 7 },
  { year: 2026, term: '처서', date: '2026-08-23', time: '10:19', month: 8, day: 23, solarMonth: 7 },
  { year: 2026, term: '백로', date: '2026-09-07', time: '22:41', month: 9, day: 7, solarMonth: 8 },
  { year: 2026, term: '추분', date: '2026-09-23', time: '08:05', month: 9, day: 23, solarMonth: 8 },
  { year: 2026, term: '한로', date: '2026-10-08', time: '14:29', month: 10, day: 8, solarMonth: 9 },
  { year: 2026, term: '상강', date: '2026-10-23', time: '17:38', month: 10, day: 23, solarMonth: 9 },
  { year: 2026, term: '입동', date: '2026-11-07', time: '17:52', month: 11, day: 7, solarMonth: 10 },
  { year: 2026, term: '소설', date: '2026-11-22', time: '15:23', month: 11, day: 22, solarMonth: 10 },
  { year: 2026, term: '대설', date: '2026-12-07', time: '11:52', month: 12, day: 7, solarMonth: 11 },
  { year: 2026, term: '동지', date: '2026-12-22', time: '05:50', month: 12, day: 22, solarMonth: 11 },
];

export const SOLAR_TERMS_DATA: Record<number, SolarTermData[]> = {
  2024: SOLAR_TERMS_2024,
  2025: SOLAR_TERMS_2025,
  2026: SOLAR_TERMS_2026,
};

// ============================================================
// 근사 계산 (폴백)
// ============================================================

function getApproximateSolarMonth(month: number, day: number): number {
  const TERM_BOUNDARIES: [number, number, number][] = [
    [1, 6, 12], [2, 4, 1], [3, 6, 2], [4, 5, 3],
    [5, 6, 4], [6, 6, 5], [7, 7, 6], [8, 8, 7],
    [9, 8, 8], [10, 8, 9], [11, 7, 10], [12, 7, 11],
  ];

  for (let i = TERM_BOUNDARIES.length - 1; i >= 0; i--) {
    const [termMonth, termDay, solarMonth] = TERM_BOUNDARIES[i];
    if (month > termMonth || (month === termMonth && day >= termDay)) {
      return solarMonth;
    }
  }

  return 11;
}

// ============================================================
// 유틸리티
// ============================================================

function dateTimeToMinutes(year: number, month: number, day: number, hour: number, minute: number): number {
  const date = new Date(year, month - 1, day, hour, minute);
  return Math.floor(date.getTime() / (1000 * 60));
}

function termToMinutes(term: SolarTermData): number {
  const [hour, minute] = term.time.split(':').map(Number);
  return dateTimeToMinutes(term.year, term.month, term.day, hour, minute);
}

// ============================================================
// 공개 API
// ============================================================

export function getSolarTermsForYear(year: number): SolarTermData[] {
  return SOLAR_TERMS_DATA[year] || [];
}

export function getSolarTermByDate(year: number, month: number, day: number): SolarTermData | null {
  const terms = SOLAR_TERMS_DATA[year];
  if (!terms) return null;
  return terms.find(t => t.month === month && t.day === day) || null;
}

export function getExactSolarMonth(
  year: number,
  month: number,
  day: number,
  hour: number,
  minute: number,
): number {
  const currentYearTerms = SOLAR_TERMS_DATA[year] || [];
  const prevYearTerms = SOLAR_TERMS_DATA[year - 1] || [];
  const nextYearTerms = SOLAR_TERMS_DATA[year + 1] || [];

  if (currentYearTerms.length === 0 && prevYearTerms.length === 0 && nextYearTerms.length === 0) {
    return getApproximateSolarMonth(month, day);
  }

  const targetMinutes = dateTimeToMinutes(year, month, day, hour, minute);

  const monthStartTermNames = Object.values(MONTH_START_TERMS);
  const allTerms = [
    ...prevYearTerms.filter(t => monthStartTermNames.includes(t.term)),
    ...currentYearTerms.filter(t => monthStartTermNames.includes(t.term)),
    ...nextYearTerms.filter(t => monthStartTermNames.includes(t.term)),
  ].sort((a, b) => termToMinutes(a) - termToMinutes(b));

  for (let i = allTerms.length - 1; i >= 0; i--) {
    const termMinutes = termToMinutes(allTerms[i]);
    if (targetMinutes >= termMinutes) {
      return TERM_TO_SOLAR_MONTH[allTerms[i].term];
    }
  }

  return getApproximateSolarMonth(month, day);
}

function minutesToDaysHoursMinutes(totalMinutes: number): DaysToTermResult {
  const days = Math.floor(totalMinutes / (24 * 60));
  const remainingMinutes = totalMinutes % (24 * 60);
  const hours = Math.floor(remainingMinutes / 60);
  const minutes = remainingMinutes % 60;
  return { days, hours, minutes, totalMinutes };
}

export function getDaysToNextSolarTerm(
  year: number, month: number, day: number, hour: number, minute: number,
): DaysToTermResult {
  const targetMinutes = dateTimeToMinutes(year, month, day, hour, minute);

  const monthStartTermNames = Object.values(MONTH_START_TERMS);
  const currentYearTerms = SOLAR_TERMS_DATA[year] || [];
  const nextYearTerms = SOLAR_TERMS_DATA[year + 1] || [];

  const allTerms = [
    ...currentYearTerms.filter(t => monthStartTermNames.includes(t.term)),
    ...nextYearTerms.filter(t => monthStartTermNames.includes(t.term)),
  ].sort((a, b) => termToMinutes(a) - termToMinutes(b));

  for (const term of allTerms) {
    const termMinutes = termToMinutes(term);
    if (termMinutes > targetMinutes) {
      const diffMinutes = termMinutes - targetMinutes;
      return minutesToDaysHoursMinutes(diffMinutes);
    }
  }

  return { days: 0, hours: 0, minutes: 0, totalMinutes: 0 };
}

export function getDaysToPrevSolarTerm(
  year: number, month: number, day: number, hour: number, minute: number,
): DaysToTermResult {
  const targetMinutes = dateTimeToMinutes(year, month, day, hour, minute);

  const monthStartTermNames = Object.values(MONTH_START_TERMS);
  const prevYearTerms = SOLAR_TERMS_DATA[year - 1] || [];
  const currentYearTerms = SOLAR_TERMS_DATA[year] || [];

  const allTerms = [
    ...prevYearTerms.filter(t => monthStartTermNames.includes(t.term)),
    ...currentYearTerms.filter(t => monthStartTermNames.includes(t.term)),
  ].sort((a, b) => termToMinutes(a) - termToMinutes(b));

  for (let i = allTerms.length - 1; i >= 0; i--) {
    const termMinutes = termToMinutes(allTerms[i]);
    if (termMinutes <= targetMinutes) {
      const diffMinutes = targetMinutes - termMinutes;
      return minutesToDaysHoursMinutes(diffMinutes);
    }
  }

  return { days: 0, hours: 0, minutes: 0, totalMinutes: 0 };
}

export function calculateDaewoonStartFromSolarTerms(
  birthYear: number, birthMonth: number, birthDay: number,
  birthHour: number, birthMinute: number, isForward: boolean,
): { startAge: number; startMonth: number; totalDays: number } {
  let daysInfo: DaysToTermResult;

  if (isForward) {
    daysInfo = getDaysToNextSolarTerm(birthYear, birthMonth, birthDay, birthHour, birthMinute);
  } else {
    daysInfo = getDaysToPrevSolarTerm(birthYear, birthMonth, birthDay, birthHour, birthMinute);
  }

  const totalDays = daysInfo.days + (daysInfo.hours / 24) + (daysInfo.minutes / (24 * 60));
  const totalYears = totalDays / 3;

  const startAge = Math.floor(totalYears);
  const remainingYears = totalYears - startAge;
  const startMonth = Math.round(remainingYears * 12);

  return {
    startAge: Math.max(1, startAge),
    startMonth,
    totalDays: Math.round(totalDays),
  };
}
