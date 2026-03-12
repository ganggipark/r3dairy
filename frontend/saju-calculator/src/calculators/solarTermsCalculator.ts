/**
 * 정확한 절기(節氣) 계산 시스템
 *
 * 데이터 출처:
 * - 2024-2026년: 한국천문연구원 (https://astro.kasi.re.kr) 공식 데이터
 * - 2027-2030년: uncle.tools (한국천문연구원 공식 데이터 발표 대기 중)
 * - 기타 연도(1900-2100): 천문학적 알고리즘 (Meeus, Astronomical Algorithms) 기반 계산
 * 모든 시각은 KST (한국표준시) 기준
 *
 * @author Claude Code
 * @version 2.0.0
 * @updated 2026-01-12 - 2027-2030년 절기 데이터 추가
 */

// ============================================================
// 타입 정의
// ============================================================

export interface SolarTermData {
  year: number;
  term: string;           // 절기명
  date: string;           // YYYY-MM-DD
  time: string;           // HH:MM (24시간제, KST)
  month: number;          // 양력 월
  day: number;            // 양력 일
  solarMonth: number;     // 절기월 (1=인월 ~ 12=축월)
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

/**
 * 24절기 순서 및 절기월 매핑
 * 절기월: 인월(1) ~ 축월(12)
 *
 * 절(節): 월의 시작을 알림
 * 중(中): 월의 중간
 */
export const SOLAR_TERM_NAMES = [
  '소한', '대한',   // 축월(12) - 1월
  '입춘', '우수',   // 인월(1) - 2월 시작
  '경칩', '춘분',   // 묘월(2) - 3월
  '청명', '곡우',   // 진월(3) - 4월
  '입하', '소만',   // 사월(4) - 5월
  '망종', '하지',   // 오월(5) - 6월
  '소서', '대서',   // 미월(6) - 7월
  '입추', '처서',   // 신월(7) - 8월
  '백로', '추분',   // 유월(8) - 9월
  '한로', '상강',   // 술월(9) - 10월
  '입동', '소설',   // 해월(10) - 11월
  '대설', '동지',   // 자월(11) - 12월
] as const;

/**
 * 월을 시작하는 절기 (節)
 * 이 절기가 해당 월의 시작점
 */
export const MONTH_START_TERMS: Record<number, string> = {
  1: '입춘',   // 인월 시작
  2: '경칩',   // 묘월 시작
  3: '청명',   // 진월 시작
  4: '입하',   // 사월 시작
  5: '망종',   // 오월 시작
  6: '소서',   // 미월 시작
  7: '입추',   // 신월 시작
  8: '백로',   // 유월 시작
  9: '한로',   // 술월 시작
  10: '입동',  // 해월 시작
  11: '대설',  // 자월 시작
  12: '소한',  // 축월 시작
};

/**
 * 절기 → 절기월 매핑
 */
export const TERM_TO_SOLAR_MONTH: Record<string, number> = {
  '소한': 12, '대한': 12,   // 축월
  '입춘': 1,  '우수': 1,    // 인월
  '경칩': 2,  '춘분': 2,    // 묘월
  '청명': 3,  '곡우': 3,    // 진월
  '입하': 4,  '소만': 4,    // 사월
  '망종': 5,  '하지': 5,    // 오월
  '소서': 6,  '대서': 6,    // 미월
  '입추': 7,  '처서': 7,    // 신월
  '백로': 8,  '추분': 8,    // 유월
  '한로': 9,  '상강': 9,    // 술월
  '입동': 10, '소설': 10,   // 해월
  '대설': 11, '동지': 11,   // 자월
};

// ============================================================
// 절기 데이터 테이블 (한국천문연구원 기준)
// ============================================================

/**
 * 2024년 24절기 데이터 (KST)
 * 출처: 한국천문연구원
 */
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

/**
 * 2025년 24절기 데이터 (KST)
 * 출처: 한국천문연구원
 */
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

/**
 * 2026년 24절기 데이터 (KST)
 * 출처: 한국천문연구원
 */
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

/**
 * 2027년 24절기 데이터 (KST)
 * 출처: uncle.tools (한국천문연구원 공식 데이터 대기 중)
 */
const SOLAR_TERMS_2027: SolarTermData[] = [
  { year: 2027, term: '소한', date: '2027-01-05', time: '23:09', month: 1, day: 5, solarMonth: 12 },
  { year: 2027, term: '대한', date: '2027-01-20', time: '16:29', month: 1, day: 20, solarMonth: 12 },
  { year: 2027, term: '입춘', date: '2027-02-04', time: '10:46', month: 2, day: 4, solarMonth: 1 },
  { year: 2027, term: '우수', date: '2027-02-19', time: '06:33', month: 2, day: 19, solarMonth: 1 },
  { year: 2027, term: '경칩', date: '2027-03-06', time: '04:39', month: 3, day: 6, solarMonth: 2 },
  { year: 2027, term: '춘분', date: '2027-03-21', time: '05:24', month: 3, day: 21, solarMonth: 2 },
  { year: 2027, term: '청명', date: '2027-04-05', time: '09:17', month: 4, day: 5, solarMonth: 3 },
  { year: 2027, term: '곡우', date: '2027-04-20', time: '16:17', month: 4, day: 20, solarMonth: 3 },
  { year: 2027, term: '입하', date: '2027-05-06', time: '02:25', month: 5, day: 6, solarMonth: 4 },
  { year: 2027, term: '소만', date: '2027-05-21', time: '15:18', month: 5, day: 21, solarMonth: 4 },
  { year: 2027, term: '망종', date: '2027-06-06', time: '06:25', month: 6, day: 6, solarMonth: 5 },
  { year: 2027, term: '하지', date: '2027-06-21', time: '23:10', month: 6, day: 21, solarMonth: 5 },
  { year: 2027, term: '소서', date: '2027-07-07', time: '16:37', month: 7, day: 7, solarMonth: 6 },
  { year: 2027, term: '대서', date: '2027-07-23', time: '10:04', month: 7, day: 23, solarMonth: 6 },
  { year: 2027, term: '입추', date: '2027-08-08', time: '02:26', month: 8, day: 8, solarMonth: 7 },
  { year: 2027, term: '처서', date: '2027-08-23', time: '17:14', month: 8, day: 23, solarMonth: 7 },
  { year: 2027, term: '백로', date: '2027-09-08', time: '05:28', month: 9, day: 8, solarMonth: 8 },
  { year: 2027, term: '추분', date: '2027-09-23', time: '15:01', month: 9, day: 23, solarMonth: 8 },
  { year: 2027, term: '한로', date: '2027-10-08', time: '21:17', month: 10, day: 8, solarMonth: 9 },
  { year: 2027, term: '상강', date: '2027-10-24', time: '00:32', month: 10, day: 24, solarMonth: 9 },
  { year: 2027, term: '입동', date: '2027-11-08', time: '00:38', month: 11, day: 8, solarMonth: 10 },
  { year: 2027, term: '소설', date: '2027-11-22', time: '22:16', month: 11, day: 22, solarMonth: 10 },
  { year: 2027, term: '대설', date: '2027-12-07', time: '17:37', month: 12, day: 7, solarMonth: 11 },
  { year: 2027, term: '동지', date: '2027-12-22', time: '11:42', month: 12, day: 22, solarMonth: 11 },
];

/**
 * 2028년 24절기 데이터 (KST)
 * 출처: uncle.tools (한국천문연구원 공식 데이터 대기 중)
 */
const SOLAR_TERMS_2028: SolarTermData[] = [
  { year: 2028, term: '소한', date: '2028-01-06', time: '04:54', month: 1, day: 6, solarMonth: 12 },
  { year: 2028, term: '대한', date: '2028-01-20', time: '22:21', month: 1, day: 20, solarMonth: 12 },
  { year: 2028, term: '입춘', date: '2028-02-04', time: '16:31', month: 2, day: 4, solarMonth: 1 },
  { year: 2028, term: '우수', date: '2028-02-19', time: '12:26', month: 2, day: 19, solarMonth: 1 },
  { year: 2028, term: '경칩', date: '2028-03-05', time: '10:24', month: 3, day: 5, solarMonth: 2 },
  { year: 2028, term: '춘분', date: '2028-03-20', time: '11:17', month: 3, day: 20, solarMonth: 2 },
  { year: 2028, term: '청명', date: '2028-04-04', time: '15:03', month: 4, day: 4, solarMonth: 3 },
  { year: 2028, term: '곡우', date: '2028-04-19', time: '22:09', month: 4, day: 19, solarMonth: 3 },
  { year: 2028, term: '입하', date: '2028-05-05', time: '08:12', month: 5, day: 5, solarMonth: 4 },
  { year: 2028, term: '소만', date: '2028-05-20', time: '21:09', month: 5, day: 20, solarMonth: 4 },
  { year: 2028, term: '망종', date: '2028-06-05', time: '12:16', month: 6, day: 5, solarMonth: 5 },
  { year: 2028, term: '하지', date: '2028-06-21', time: '05:02', month: 6, day: 21, solarMonth: 5 },
  { year: 2028, term: '소서', date: '2028-07-06', time: '22:30', month: 7, day: 6, solarMonth: 6 },
  { year: 2028, term: '대서', date: '2028-07-22', time: '15:53', month: 7, day: 22, solarMonth: 6 },
  { year: 2028, term: '입추', date: '2028-08-07', time: '08:21', month: 8, day: 7, solarMonth: 7 },
  { year: 2028, term: '처서', date: '2028-08-22', time: '23:00', month: 8, day: 22, solarMonth: 7 },
  { year: 2028, term: '백로', date: '2028-09-07', time: '11:22', month: 9, day: 7, solarMonth: 8 },
  { year: 2028, term: '추분', date: '2028-09-22', time: '20:45', month: 9, day: 22, solarMonth: 8 },
  { year: 2028, term: '한로', date: '2028-10-08', time: '03:08', month: 10, day: 8, solarMonth: 9 },
  { year: 2028, term: '상강', date: '2028-10-23', time: '06:13', month: 10, day: 23, solarMonth: 9 },
  { year: 2028, term: '입동', date: '2028-11-07', time: '06:27', month: 11, day: 7, solarMonth: 10 },
  { year: 2028, term: '소설', date: '2028-11-22', time: '03:54', month: 11, day: 22, solarMonth: 10 },
  { year: 2028, term: '대설', date: '2028-12-06', time: '23:24', month: 12, day: 6, solarMonth: 11 },
  { year: 2028, term: '동지', date: '2028-12-21', time: '17:19', month: 12, day: 21, solarMonth: 11 },
];

/**
 * 2029년 24절기 데이터 (KST)
 * 출처: uncle.tools (한국천문연구원 공식 데이터 대기 중)
 */
const SOLAR_TERMS_2029: SolarTermData[] = [
  { year: 2029, term: '소한', date: '2029-01-05', time: '10:41', month: 1, day: 5, solarMonth: 12 },
  { year: 2029, term: '대한', date: '2029-01-20', time: '04:00', month: 1, day: 20, solarMonth: 12 },
  { year: 2029, term: '입춘', date: '2029-02-03', time: '22:20', month: 2, day: 3, solarMonth: 1 },
  { year: 2029, term: '우수', date: '2029-02-18', time: '18:07', month: 2, day: 18, solarMonth: 1 },
  { year: 2029, term: '경칩', date: '2029-03-05', time: '16:17', month: 3, day: 5, solarMonth: 2 },
  { year: 2029, term: '춘분', date: '2029-03-20', time: '17:01', month: 3, day: 20, solarMonth: 2 },
  { year: 2029, term: '청명', date: '2029-04-04', time: '20:58', month: 4, day: 4, solarMonth: 3 },
  { year: 2029, term: '곡우', date: '2029-04-20', time: '03:55', month: 4, day: 20, solarMonth: 3 },
  { year: 2029, term: '입하', date: '2029-05-05', time: '14:07', month: 5, day: 5, solarMonth: 4 },
  { year: 2029, term: '소만', date: '2029-05-21', time: '02:55', month: 5, day: 21, solarMonth: 4 },
  { year: 2029, term: '망종', date: '2029-06-05', time: '18:09', month: 6, day: 5, solarMonth: 5 },
  { year: 2029, term: '하지', date: '2029-06-21', time: '10:48', month: 6, day: 21, solarMonth: 5 },
  { year: 2029, term: '소서', date: '2029-07-07', time: '04:22', month: 7, day: 7, solarMonth: 6 },
  { year: 2029, term: '대서', date: '2029-07-22', time: '21:42', month: 7, day: 22, solarMonth: 6 },
  { year: 2029, term: '입추', date: '2029-08-07', time: '14:11', month: 8, day: 7, solarMonth: 7 },
  { year: 2029, term: '처서', date: '2029-08-23', time: '04:51', month: 8, day: 23, solarMonth: 7 },
  { year: 2029, term: '백로', date: '2029-09-07', time: '17:11', month: 9, day: 7, solarMonth: 8 },
  { year: 2029, term: '추분', date: '2029-09-23', time: '02:38', month: 9, day: 23, solarMonth: 8 },
  { year: 2029, term: '한로', date: '2029-10-08', time: '08:58', month: 10, day: 8, solarMonth: 9 },
  { year: 2029, term: '상강', date: '2029-10-23', time: '12:08', month: 10, day: 23, solarMonth: 9 },
  { year: 2029, term: '입동', date: '2029-11-07', time: '12:16', month: 11, day: 7, solarMonth: 10 },
  { year: 2029, term: '소설', date: '2029-11-22', time: '09:49', month: 11, day: 22, solarMonth: 10 },
  { year: 2029, term: '대설', date: '2029-12-07', time: '05:13', month: 12, day: 7, solarMonth: 11 },
  { year: 2029, term: '동지', date: '2029-12-21', time: '23:14', month: 12, day: 21, solarMonth: 11 },
];

/**
 * 2030년 24절기 데이터 (KST)
 * 출처: uncle.tools (한국천문연구원 공식 데이터 대기 중)
 */
const SOLAR_TERMS_2030: SolarTermData[] = [
  { year: 2030, term: '소한', date: '2030-01-05', time: '16:30', month: 1, day: 5, solarMonth: 12 },
  { year: 2030, term: '대한', date: '2030-01-20', time: '09:54', month: 1, day: 20, solarMonth: 12 },
  { year: 2030, term: '입춘', date: '2030-02-04', time: '04:08', month: 2, day: 4, solarMonth: 1 },
  { year: 2030, term: '우수', date: '2030-02-18', time: '23:59', month: 2, day: 18, solarMonth: 1 },
  { year: 2030, term: '경칩', date: '2030-03-05', time: '22:03', month: 3, day: 5, solarMonth: 2 },
  { year: 2030, term: '춘분', date: '2030-03-20', time: '22:52', month: 3, day: 20, solarMonth: 2 },
  { year: 2030, term: '청명', date: '2030-04-05', time: '02:41', month: 4, day: 5, solarMonth: 3 },
  { year: 2030, term: '곡우', date: '2030-04-20', time: '09:43', month: 4, day: 20, solarMonth: 3 },
  { year: 2030, term: '입하', date: '2030-05-05', time: '19:46', month: 5, day: 5, solarMonth: 4 },
  { year: 2030, term: '소만', date: '2030-05-21', time: '08:41', month: 5, day: 21, solarMonth: 4 },
  { year: 2030, term: '망종', date: '2030-06-05', time: '23:44', month: 6, day: 5, solarMonth: 5 },
  { year: 2030, term: '하지', date: '2030-06-21', time: '16:31', month: 6, day: 21, solarMonth: 5 },
  { year: 2030, term: '소서', date: '2030-07-07', time: '09:55', month: 7, day: 7, solarMonth: 6 },
  { year: 2030, term: '대서', date: '2030-07-23', time: '03:24', month: 7, day: 23, solarMonth: 6 },
  { year: 2030, term: '입추', date: '2030-08-07', time: '19:47', month: 8, day: 7, solarMonth: 7 },
  { year: 2030, term: '처서', date: '2030-08-23', time: '10:36', month: 8, day: 23, solarMonth: 7 },
  { year: 2030, term: '백로', date: '2030-09-07', time: '22:52', month: 9, day: 7, solarMonth: 8 },
  { year: 2030, term: '추분', date: '2030-09-23', time: '08:26', month: 9, day: 23, solarMonth: 8 },
  { year: 2030, term: '한로', date: '2030-10-08', time: '14:45', month: 10, day: 8, solarMonth: 9 },
  { year: 2030, term: '상강', date: '2030-10-23', time: '18:00', month: 10, day: 23, solarMonth: 9 },
  { year: 2030, term: '입동', date: '2030-11-07', time: '18:08', month: 11, day: 7, solarMonth: 10 },
  { year: 2030, term: '소설', date: '2030-11-22', time: '15:44', month: 11, day: 22, solarMonth: 10 },
  { year: 2030, term: '대설', date: '2030-12-07', time: '11:07', month: 12, day: 7, solarMonth: 11 },
  { year: 2030, term: '동지', date: '2030-12-22', time: '05:09', month: 12, day: 22, solarMonth: 11 },
];

/**
 * 전체 절기 데이터 (연도별)
 */
export const SOLAR_TERMS_DATA: Record<number, SolarTermData[]> = {
  2024: SOLAR_TERMS_2024,
  2025: SOLAR_TERMS_2025,
  2026: SOLAR_TERMS_2026,
  2027: SOLAR_TERMS_2027,
  2028: SOLAR_TERMS_2028,
  2029: SOLAR_TERMS_2029,
  2030: SOLAR_TERMS_2030,
};

// ============================================================
// 천문학적 절기 계산 알고리즘 (1900-2100년 지원)
// ============================================================

/**
 * 24절기 황경(ecliptic longitude) 매핑
 * 소한(285°)부터 동지(270°)까지 달력 순서
 */
const SOLAR_TERM_LONGITUDES: Array<{ name: string; longitude: number }> = [
  { name: '소한', longitude: 285 },
  { name: '대한', longitude: 300 },
  { name: '입춘', longitude: 315 },
  { name: '우수', longitude: 330 },
  { name: '경칩', longitude: 345 },
  { name: '춘분', longitude: 0 },
  { name: '청명', longitude: 15 },
  { name: '곡우', longitude: 30 },
  { name: '입하', longitude: 45 },
  { name: '소만', longitude: 60 },
  { name: '망종', longitude: 75 },
  { name: '하지', longitude: 90 },
  { name: '소서', longitude: 105 },
  { name: '대서', longitude: 120 },
  { name: '입추', longitude: 135 },
  { name: '처서', longitude: 150 },
  { name: '백로', longitude: 165 },
  { name: '추분', longitude: 180 },
  { name: '한로', longitude: 195 },
  { name: '상강', longitude: 210 },
  { name: '입동', longitude: 225 },
  { name: '소설', longitude: 240 },
  { name: '대설', longitude: 255 },
  { name: '동지', longitude: 270 },
];

const DEG_TO_RAD = Math.PI / 180;

/**
 * Gregorian date → Julian Day Number (Meeus Ch.7)
 */
function gregorianToJD(year: number, month: number, day: number, hour: number = 0, minute: number = 0): number {
  let y = year;
  let m = month;
  if (m <= 2) { y -= 1; m += 12; }
  const A = Math.floor(y / 100);
  const B = 2 - A + Math.floor(A / 4);
  return Math.floor(365.25 * (y + 4716)) + Math.floor(30.6001 * (m + 1)) + day + (hour + minute / 60) / 24 + B - 1524.5;
}

/**
 * Julian Day → Gregorian date (UTC)
 */
function jdToGregorian(jd: number): { year: number; month: number; day: number; hour: number; minute: number } {
  const jd0 = jd + 0.5;
  const Z = Math.floor(jd0);
  const F = jd0 - Z;
  let A: number;
  if (Z < 2299161) { A = Z; }
  else { const alpha = Math.floor((Z - 1867216.25) / 36524.25); A = Z + 1 + alpha - Math.floor(alpha / 4); }
  const B = A + 1524;
  const C = Math.floor((B - 122.1) / 365.25);
  const D = Math.floor(365.25 * C);
  const E = Math.floor((B - D) / 30.6001);
  const dayFrac = B - D - Math.floor(30.6001 * E) + F;
  const day = Math.floor(dayFrac);
  const timeFrac = (dayFrac - day) * 24;
  const hour = Math.floor(timeFrac);
  const minuteVal = Math.round((timeFrac - hour) * 60);
  const month = E < 14 ? E - 1 : E - 13;
  const year = month > 2 ? C - 4716 : C - 4715;
  if (minuteVal === 60) return jdToGregorian(jd + 1 / 1440);
  return { year, month, day, hour, minute: minuteVal };
}

function _julianCentury(jd: number): number { return (jd - 2451545.0) / 36525.0; }
function _normalize360(deg: number): number { let r = deg % 360; if (r < 0) r += 360; return r; }
function _sunMeanLongitude(T: number): number { return _normalize360(280.46646 + 36000.76983 * T + 0.0003032 * T * T); }
function _sunMeanAnomaly(T: number): number { return _normalize360(357.52911 + 35999.05029 * T - 0.0001537 * T * T); }

function _sunEquationOfCenter(T: number): number {
  const M = _sunMeanAnomaly(T) * DEG_TO_RAD;
  return (1.9146 - 0.004817 * T - 0.000014 * T * T) * Math.sin(M)
    + (0.019993 - 0.000101 * T) * Math.sin(2 * M)
    + 0.00029 * Math.sin(3 * M);
}

function _moonMeanLongitude(T: number): number { return _normalize360(218.3165 + 481267.8813 * T); }

function _nutationInLongitude(T: number): number {
  const omega = (125.04 - 1934.136 * T) * DEG_TO_RAD;
  const L0 = _sunMeanLongitude(T) * DEG_TO_RAD;
  const Lm = _moonMeanLongitude(T) * DEG_TO_RAD;
  return (-17.20 / 3600) * Math.sin(omega) - (1.32 / 3600) * Math.sin(2 * L0)
    - (0.23 / 3600) * Math.sin(2 * Lm) + (0.21 / 3600) * Math.sin(2 * omega);
}

/**
 * 태양 시황경 계산 (Meeus Ch.25)
 */
function sunApparentLongitude(jd: number): number {
  const T = _julianCentury(jd);
  const L0 = _sunMeanLongitude(T);
  const C = _sunEquationOfCenter(T);
  const sunLong = L0 + C;
  const omega = (125.04 - 1934.136 * T) * DEG_TO_RAD;
  const apparent = sunLong - 0.00569 - 0.00478 * Math.sin(omega);
  const deltaPsi = _nutationInLongitude(T);
  return _normalize360(apparent + deltaPsi);
}

/**
 * 절기별 근사 월 (Newton-Raphson 초기값용)
 */
const SOLAR_TERM_APPROX_MONTH: Record<number, number> = {
  285: 1, 300: 1, 315: 2, 330: 2, 345: 3, 0: 3,
  15: 4, 30: 4, 45: 5, 60: 5, 75: 6, 90: 6,
  105: 7, 120: 7, 135: 8, 150: 8, 165: 9, 180: 9,
  195: 10, 210: 10, 225: 11, 240: 11, 255: 12, 270: 12,
};

/**
 * Newton-Raphson으로 태양 황경이 targetLongitude인 JD 산출
 */
function findSolarTermJD(year: number, targetLongitude: number): number {
  const approxMonth = SOLAR_TERM_APPROX_MONTH[targetLongitude] || 3;
  let jd = gregorianToJD(year, approxMonth, 15, 12, 0);
  for (let i = 0; i < 50; i++) {
    const lng = sunApparentLongitude(jd);
    let diff = targetLongitude - lng;
    if (diff > 180) diff -= 360;
    if (diff < -180) diff += 360;
    if (Math.abs(diff) < 0.0000001) break;
    jd += diff * (365.25 / 360);
  }
  return jd;
}

/**
 * Delta T (TT - UT) 근사치 (초) - Meeus / Espenak & Meeus
 */
function deltaT(year: number): number {
  const y = year + 0.5;
  if (year < 1900) { const t = (y - 1820) / 100; return -20 + 32 * t * t; }
  else if (year < 1920) { const t = y - 1900; return -2.79 + 1.494119 * t - 0.0598939 * t * t + 0.0061966 * t * t * t - 0.000197 * t * t * t * t; }
  else if (year < 1941) { const t = y - 1920; return 21.20 + 0.84493 * t - 0.076100 * t * t + 0.0020936 * t * t * t; }
  else if (year < 1961) { const t = y - 1950; return 29.07 + 0.407 * t - t * t / 233 + t * t * t / 2547; }
  else if (year < 1986) { const t = y - 1975; return 45.45 + 1.067 * t - t * t / 260 - t * t * t / 718; }
  else if (year < 2005) { const t = y - 2000; return 63.86 + 0.3345 * t - 0.060374 * t * t + 0.0017275 * t * t * t + 0.000651814 * t * t * t * t + 0.00002373599 * t * t * t * t * t; }
  else if (year < 2050) { const t = y - 2000; return 62.92 + 0.32217 * t + 0.005589 * t * t; }
  else if (year < 2150) { const u = (y - 1820) / 100; return -20 + 32 * u * u - 0.5628 * (2150 - y); }
  else { const u = (y - 1820) / 100; return -20 + 32 * u * u; }
}

/** 천문학적 알고리즘 캐시 */
const _computedSolarTermsCache: Record<number, SolarTermData[]> = {};

/**
 * 천문학적 알고리즘으로 특정 연도의 24절기를 SolarTermData[] 형식으로 계산
 */
function computeSolarTermsForYear(year: number): SolarTermData[] {
  const result: SolarTermData[] = [];
  for (const { name, longitude } of SOLAR_TERM_LONGITUDES) {
    const jdTT = findSolarTermJD(year, longitude);
    const dT = deltaT(year);
    const jdUT = jdTT - dT / 86400;
    const jdKST = jdUT + 9 / 24;
    const greg = jdToGregorian(jdKST);
    const mm = String(greg.month).padStart(2, '0');
    const dd = String(greg.day).padStart(2, '0');
    const hh = String(greg.hour).padStart(2, '0');
    const mi = String(greg.minute).padStart(2, '0');
    result.push({
      year: greg.year,
      term: name,
      date: `${greg.year}-${mm}-${dd}`,
      time: `${hh}:${mi}`,
      month: greg.month,
      day: greg.day,
      solarMonth: TERM_TO_SOLAR_MONTH[name],
    });
  }
  return result;
}

/**
 * 특정 연도의 절기 데이터 보장 (하드코딩 우선, 없으면 천문 계산)
 * 1900-2100 지원
 */
function ensureSolarTermsData(year: number): SolarTermData[] | null {
  if (year < 1900 || year > 2100) return null;
  if (SOLAR_TERMS_DATA[year]) return SOLAR_TERMS_DATA[year];
  if (_computedSolarTermsCache[year]) return _computedSolarTermsCache[year];
  const computed = computeSolarTermsForYear(year);
  _computedSolarTermsCache[year] = computed;
  // Also populate SOLAR_TERMS_DATA so downstream code finds it
  SOLAR_TERMS_DATA[year] = computed;
  return computed;
}

// ============================================================
// 근사 절기 계산 (데이터가 없는 연도용 폴백)
// ============================================================

/**
 * 근사 절기월 계산 (절기 데이터가 없는 연도용)
 *
 * 평균 절기 일자 기준으로 계산합니다.
 * 실제 절기는 매년 ±1-2일 차이가 있을 수 있지만,
 * 역사적 날짜에 대해 근사치를 제공합니다.
 *
 * @param month 양력 월 (1-12)
 * @param day 양력 일 (1-31)
 * @returns 절기월 (1=인월 ~ 12=축월)
 */
function getApproximateSolarMonth(month: number, day: number): number {
  // 각 월을 시작하는 절기의 평균 일자 (평균값 기준)
  // 형식: [양력월, 양력일, 절기월]
  const TERM_BOUNDARIES: [number, number, number][] = [
    [1, 6, 12],   // 소한 (축월 시작) - 평균 1/6
    [2, 4, 1],    // 입춘 (인월 시작) - 평균 2/4
    [3, 6, 2],    // 경칩 (묘월 시작) - 평균 3/6
    [4, 5, 3],    // 청명 (진월 시작) - 평균 4/5
    [5, 6, 4],    // 입하 (사월 시작) - 평균 5/6
    [6, 6, 5],    // 망종 (오월 시작) - 평균 6/6
    [7, 7, 6],    // 소서 (미월 시작) - 평균 7/7
    [8, 8, 7],    // 입추 (신월 시작) - 평균 8/8
    [9, 8, 8],    // 백로 (유월 시작) - 평균 9/8
    [10, 8, 9],   // 한로 (술월 시작) - 평균 10/8
    [11, 7, 10],  // 입동 (해월 시작) - 평균 11/7
    [12, 7, 11],  // 대설 (자월 시작) - 평균 12/7
  ];

  // 현재 날짜가 어떤 절기 구간에 있는지 확인
  // 역순으로 순회하여 가장 최근에 지난 절기를 찾음
  for (let i = TERM_BOUNDARIES.length - 1; i >= 0; i--) {
    const [termMonth, termDay, solarMonth] = TERM_BOUNDARIES[i];

    // 현재 월이 절기 월보다 크거나, 같은 월에서 일자가 같거나 크면
    if (month > termMonth || (month === termMonth && day >= termDay)) {
      return solarMonth;
    }
  }

  // 1월 1일~5일은 전년도 대설(12월 7일) 이후이므로 자월(11)
  // 실제로는 소한(1/6) 전이므로 자월이 맞음
  return 11; // 자월
}

// ============================================================
// 유틸리티 함수
// ============================================================

/**
 * 날짜+시간을 분 단위 타임스탬프로 변환
 */
function dateTimeToMinutes(year: number, month: number, day: number, hour: number, minute: number): number {
  const date = new Date(year, month - 1, day, hour, minute);
  return Math.floor(date.getTime() / (1000 * 60));
}

/**
 * 절기 데이터를 분 단위 타임스탬프로 변환
 */
function termToMinutes(term: SolarTermData): number {
  const [hour, minute] = term.time.split(':').map(Number);
  return dateTimeToMinutes(term.year, term.month, term.day, hour, minute);
}

// ============================================================
// 공개 API 함수
// ============================================================

/**
 * 특정 연도의 모든 절기 데이터 가져오기
 */
export function getSolarTermsForYear(year: number): SolarTermData[] {
  ensureSolarTermsData(year);
  return SOLAR_TERMS_DATA[year] || [];
}

/**
 * 특정 날짜의 절기 정보 가져오기
 * @returns 해당 날짜가 절기일인 경우 절기 데이터, 아니면 null
 */
export function getSolarTermByDate(year: number, month: number, day: number): SolarTermData | null {
  ensureSolarTermsData(year);
  const terms = SOLAR_TERMS_DATA[year];
  if (!terms) return null;

  return terms.find(t => t.month === month && t.day === day) || null;
}

/**
 * 정확한 절기월 계산 (시분까지 고려)
 *
 * @param year 연도
 * @param month 월 (1-12)
 * @param day 일 (1-31)
 * @param hour 시 (0-23)
 * @param minute 분 (0-59)
 * @returns 절기월 (1=인월 ~ 12=축월)
 */
export function getExactSolarMonth(
  year: number,
  month: number,
  day: number,
  hour: number,
  minute: number,
): number {
  // 해당 연도와 전년도/다음연도 절기 데이터 보장 (없으면 천문 계산)
  ensureSolarTermsData(year);
  ensureSolarTermsData(year - 1);
  ensureSolarTermsData(year + 1);

  const currentYearTerms = SOLAR_TERMS_DATA[year] || [];
  const prevYearTerms = SOLAR_TERMS_DATA[year - 1] || [];
  const nextYearTerms = SOLAR_TERMS_DATA[year + 1] || [];

  // 1900-2100 범위 밖이면 근사 계산 사용
  if (currentYearTerms.length === 0 && prevYearTerms.length === 0 && nextYearTerms.length === 0) {
    console.warn(`[절기] ${year}년 계산 실패 (범위 밖), 근사 계산 사용`);
    return getApproximateSolarMonth(month, day);
  }

  const targetMinutes = dateTimeToMinutes(year, month, day, hour, minute);

  // 월 시작 절기만 필터링 (節)
  const monthStartTermNames = Object.values(MONTH_START_TERMS);
  const allTerms = [
    ...prevYearTerms.filter(t => monthStartTermNames.includes(t.term)),
    ...currentYearTerms.filter(t => monthStartTermNames.includes(t.term)),
    ...nextYearTerms.filter(t => monthStartTermNames.includes(t.term)),
  ].sort((a, b) => termToMinutes(a) - termToMinutes(b));

  // 현재 시점이 속한 절기월 찾기
  for (let i = allTerms.length - 1; i >= 0; i--) {
    const termMinutes = termToMinutes(allTerms[i]);
    if (targetMinutes >= termMinutes) {
      return TERM_TO_SOLAR_MONTH[allTerms[i].term];
    }
  }

  // 기본값: 근사 계산으로 폴백
  return getApproximateSolarMonth(month, day);
}

/**
 * 다음 절기까지 남은 시간 계산
 *
 * @returns 일/시/분 형태의 남은 시간
 */
export function getDaysToNextSolarTerm(
  year: number,
  month: number,
  day: number,
  hour: number,
  minute: number,
): DaysToTermResult {
  const targetMinutes = dateTimeToMinutes(year, month, day, hour, minute);

  // 월 시작 절기만 필터링
  ensureSolarTermsData(year);
  ensureSolarTermsData(year + 1);
  const monthStartTermNames = Object.values(MONTH_START_TERMS);
  const currentYearTerms = SOLAR_TERMS_DATA[year] || [];
  const nextYearTerms = SOLAR_TERMS_DATA[year + 1] || [];

  const allTerms = [
    ...currentYearTerms.filter(t => monthStartTermNames.includes(t.term)),
    ...nextYearTerms.filter(t => monthStartTermNames.includes(t.term)),
  ].sort((a, b) => termToMinutes(a) - termToMinutes(b));

  // 다음 절기 찾기
  for (const term of allTerms) {
    const termMinutes = termToMinutes(term);
    if (termMinutes > targetMinutes) {
      const diffMinutes = termMinutes - targetMinutes;
      return minutesToDaysHoursMinutes(diffMinutes);
    }
  }

  // 기본값
  return { days: 0, hours: 0, minutes: 0, totalMinutes: 0 };
}

/**
 * 이전 절기까지의 시간 계산
 *
 * @returns 일/시/분 형태의 경과 시간
 */
export function getDaysToPrevSolarTerm(
  year: number,
  month: number,
  day: number,
  hour: number,
  minute: number,
): DaysToTermResult {
  const targetMinutes = dateTimeToMinutes(year, month, day, hour, minute);

  // 월 시작 절기만 필터링
  ensureSolarTermsData(year - 1);
  ensureSolarTermsData(year);
  const monthStartTermNames = Object.values(MONTH_START_TERMS);
  const prevYearTerms = SOLAR_TERMS_DATA[year - 1] || [];
  const currentYearTerms = SOLAR_TERMS_DATA[year] || [];

  const allTerms = [
    ...prevYearTerms.filter(t => monthStartTermNames.includes(t.term)),
    ...currentYearTerms.filter(t => monthStartTermNames.includes(t.term)),
  ].sort((a, b) => termToMinutes(a) - termToMinutes(b));

  // 이전 절기 찾기 (가장 가까운 과거 절기)
  for (let i = allTerms.length - 1; i >= 0; i--) {
    const termMinutes = termToMinutes(allTerms[i]);
    if (termMinutes <= targetMinutes) {
      const diffMinutes = targetMinutes - termMinutes;
      return minutesToDaysHoursMinutes(diffMinutes);
    }
  }

  // 기본값
  return { days: 0, hours: 0, minutes: 0, totalMinutes: 0 };
}

/**
 * 분을 일/시/분으로 변환
 */
function minutesToDaysHoursMinutes(totalMinutes: number): DaysToTermResult {
  const days = Math.floor(totalMinutes / (24 * 60));
  const remainingMinutes = totalMinutes % (24 * 60);
  const hours = Math.floor(remainingMinutes / 60);
  const minutes = remainingMinutes % 60;

  return { days, hours, minutes, totalMinutes };
}

/**
 * 대운 시작 나이 계산을 위한 절기 일수 계산
 *
 * @param birthYear 출생 연도
 * @param birthMonth 출생 월
 * @param birthDay 출생 일
 * @param birthHour 출생 시
 * @param birthMinute 출생 분
 * @param isForward 순행 여부 (양남음녀=순행, 음남양녀=역행)
 * @returns 대운 시작 나이 및 월
 */
export function calculateDaewoonStartFromSolarTerms(
  birthYear: number,
  birthMonth: number,
  birthDay: number,
  birthHour: number,
  birthMinute: number,
  isForward: boolean,
): { startAge: number; startMonth: number; totalDays: number } {
  let daysInfo: DaysToTermResult;

  if (isForward) {
    // 순행: 다음 절기까지 일수
    daysInfo = getDaysToNextSolarTerm(birthYear, birthMonth, birthDay, birthHour, birthMinute);
  } else {
    // 역행: 이전 절기까지 일수
    daysInfo = getDaysToPrevSolarTerm(birthYear, birthMonth, birthDay, birthHour, birthMinute);
  }

  // 대운 공식: 3일 = 1년 (또는 1일 = 4개월)
  const totalDays = daysInfo.days + (daysInfo.hours / 24) + (daysInfo.minutes / (24 * 60));
  const totalYears = totalDays / 3;

  const startAge = Math.floor(totalYears);
  const remainingYears = totalYears - startAge;
  const startMonth = Math.round(remainingYears * 12);

  return {
    startAge: Math.max(1, startAge), // 최소 1세
    startMonth,
    totalDays: Math.round(totalDays),
  };
}
