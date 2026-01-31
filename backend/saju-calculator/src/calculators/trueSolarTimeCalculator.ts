/**
 * 진태양시(真太陽時) 계산 모듈
 *
 * 한국 표준시(KST)는 동경 135도 기준이지만,
 * 실제 한국의 경도는 125~131도 사이로 지역마다 다릅니다.
 * 진태양시는 실제 태양의 위치에 맞춰 시간을 보정하는 것입니다.
 *
 * 계산 공식:
 * - 진태양시 = 표준시 + (지역경도 - 표준경도) × 4분
 * - 한국 표준경도: 135° (동경 135도)
 * - 1도당 4분 시차
 *
 * @author Claude Code
 * @version 1.0.0
 * @updated 2026-01-12
 */

// ============================================================
// 타입 정의
// ============================================================

export interface TrueSolarTimeResult {
  /** 보정된 시간 (0-23) */
  adjustedHour: number;
  /** 보정된 분 (0-59) */
  adjustedMinute: number;
  /** 보정량 (분 단위) */
  correctionMinutes: number;
  /** 사용된 경도 */
  longitude: number;
  /** 지역명 */
  locationName: string;
}

export interface Location {
  /** 지역명 */
  name: string;
  /** 경도 (동경, 도) */
  longitude: number;
  /** 위도 (북위, 도) */
  latitude?: number;
}

// ============================================================
// 상수 정의
// ============================================================

/** 한국 표준시 기준 경도 (동경 135도) */
export const KST_STANDARD_LONGITUDE = 135.0;

/** 주요 도시 경도 데이터 */
export const MAJOR_CITIES: Record<string, Location> = {
  // 대한민국
  서울: { name: '서울', longitude: 126.9780, latitude: 37.5665 },
  부산: { name: '부산', longitude: 129.0756, latitude: 35.1796 },
  인천: { name: '인천', longitude: 126.7052, latitude: 37.4563 },
  대구: { name: '대구', longitude: 128.6014, latitude: 35.8714 },
  대전: { name: '대전', longitude: 127.3845, latitude: 36.3504 },
  광주: { name: '광주', longitude: 126.8526, latitude: 35.1595 },
  울산: { name: '울산', longitude: 129.3114, latitude: 35.5384 },
  수원: { name: '수원', longitude: 127.0286, latitude: 37.2636 },
  창원: { name: '창원', longitude: 128.6811, latitude: 35.2281 },
  성남: { name: '성남', longitude: 127.1378, latitude: 37.4449 },

  // 조선민주주의인민공화국
  평양: { name: '평양', longitude: 125.7625, latitude: 39.0392 },
  함흥: { name: '함흥', longitude: 127.5367, latitude: 39.9180 },
  청진: { name: '청진', longitude: 129.7758, latitude: 41.7975 },

  // 기본값 (서울)
  기본: { name: '서울', longitude: 126.9780, latitude: 37.5665 },
};

// ============================================================
// 핵심 함수
// ============================================================

/**
 * 진태양시 보정량 계산
 *
 * @param longitude 지역 경도 (동경, 도)
 * @returns 보정량 (분 단위, 음수 = 시간을 빼야 함)
 *
 * @example
 * calculateTrueSolarTimeCorrection(126.978); // 서울 → -32.088분
 * calculateTrueSolarTimeCorrection(129.076); // 부산 → -23.696분
 */
export function calculateTrueSolarTimeCorrection(longitude: number): number {
  // (지역경도 - 표준경도) × 4분
  // 서울(126.978): (126.978 - 135) × 4 = -32.088분
  const correction = (longitude - KST_STANDARD_LONGITUDE) * 4;
  return correction;
}

/**
 * 진태양시 적용 (시간 보정)
 *
 * @param hour 원본 시간 (0-23)
 * @param minute 원본 분 (0-59)
 * @param longitude 지역 경도 (동경, 도)
 * @param locationName 지역명 (선택, 기본값: '사용자 지정')
 * @returns 보정된 시간 정보
 *
 * @example
 * // 서울에서 오후 2시 30분
 * applyTrueSolarTime(14, 30, 126.978, '서울');
 * // → { adjustedHour: 13, adjustedMinute: 58, correctionMinutes: -32.088, ... }
 */
export function applyTrueSolarTime(
  hour: number,
  minute: number,
  longitude: number,
  locationName: string = '사용자 지정',
): TrueSolarTimeResult {
  // 보정량 계산 (분 단위)
  const correctionMinutes = calculateTrueSolarTimeCorrection(longitude);

  // 총 분으로 변환
  let totalMinutes = hour * 60 + minute + correctionMinutes;

  // 음수 처리 (전날로 넘어가는 경우)
  while (totalMinutes < 0) {
    totalMinutes += 24 * 60; // +24시간
  }

  // 24시간 초과 처리 (다음날로 넘어가는 경우)
  while (totalMinutes >= 24 * 60) {
    totalMinutes -= 24 * 60; // -24시간
  }

  // 시간과 분으로 분리
  const adjustedHour = Math.floor(totalMinutes / 60);
  const adjustedMinute = Math.floor(totalMinutes % 60);

  return {
    adjustedHour,
    adjustedMinute,
    correctionMinutes,
    longitude,
    locationName,
  };
}

/**
 * 주요 도시 이름으로 진태양시 적용
 *
 * @param hour 원본 시간 (0-23)
 * @param minute 원본 분 (0-59)
 * @param cityName 도시명 (예: '서울', '부산', '평양')
 * @returns 보정된 시간 정보
 *
 * @example
 * applyTrueSolarTimeByCity(14, 30, '서울'); // 서울 경도 자동 적용
 * applyTrueSolarTimeByCity(14, 30, '부산'); // 부산 경도 자동 적용
 */
export function applyTrueSolarTimeByCity(
  hour: number,
  minute: number,
  cityName: string,
): TrueSolarTimeResult {
  const city = MAJOR_CITIES[cityName] || MAJOR_CITIES['기본'];
  return applyTrueSolarTime(hour, minute, city.longitude, city.name);
}

/**
 * 진태양시 보정량만 계산 (도시명으로)
 *
 * @param cityName 도시명
 * @returns 보정량 (분 단위)
 *
 * @example
 * getTrueSolarTimeCorrectionByCity('서울'); // -32.088분
 * getTrueSolarTimeCorrectionByCity('부산'); // -23.696분
 * getTrueSolarTimeCorrectionByCity('평양'); // -37.050분
 */
export function getTrueSolarTimeCorrectionByCity(cityName: string): number {
  const city = MAJOR_CITIES[cityName] || MAJOR_CITIES['기본'];
  return calculateTrueSolarTimeCorrection(city.longitude);
}

// ============================================================
// 헬퍼 함수
// ============================================================

/**
 * 도시 목록 조회
 *
 * @returns 사용 가능한 도시 목록
 */
export function getAvailableCities(): string[] {
  return Object.keys(MAJOR_CITIES).filter(city => city !== '기본');
}

/**
 * 도시 정보 조회
 *
 * @param cityName 도시명
 * @returns 도시 위치 정보 (없으면 기본값)
 */
export function getCityInfo(cityName: string): Location {
  return MAJOR_CITIES[cityName] || MAJOR_CITIES['기본'];
}

/**
 * 진태양시 보정 설명 텍스트 생성
 *
 * @param cityName 도시명
 * @returns 사용자 친화적 설명 문자열
 *
 * @example
 * getTrueSolarTimeDescription('서울');
 * // → "서울(경도 126.98°)은 한국 표준시보다 약 32분 느립니다."
 */
export function getTrueSolarTimeDescription(cityName: string): string {
  const city = getCityInfo(cityName);
  const correction = calculateTrueSolarTimeCorrection(city.longitude);
  const absCorrection = Math.abs(correction);
  const direction = correction < 0 ? '느립니다' : '빠릅니다';

  return `${city.name}(경도 ${city.longitude.toFixed(2)}°)은 한국 표준시보다 약 ${absCorrection.toFixed(0)}분 ${direction}.`;
}

// ============================================================
// 내보내기
// ============================================================

export default {
  calculateTrueSolarTimeCorrection,
  applyTrueSolarTime,
  applyTrueSolarTimeByCity,
  getTrueSolarTimeCorrectionByCity,
  getAvailableCities,
  getCityInfo,
  getTrueSolarTimeDescription,
  MAJOR_CITIES,
  KST_STANDARD_LONGITUDE,
};
