/**
 * 진태양시(真太陽時) 계산 모듈
 *
 * 한국 표준시(KST)는 동경 135도 기준이지만,
 * 실제 한국의 경도는 125~131도 사이로 지역마다 다릅니다.
 *
 * 계산 공식:
 * - 진태양시 = 표준시 + (지역경도 - 표준경도) × 4분
 * - 한국 표준경도: 135° (동경 135도)
 * - 1도당 4분 시차
 *
 * @author SajuApp
 * @version 1.0.0
 */
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
/** 한국 표준시 기준 경도 (동경 135도) */
export declare const KST_STANDARD_LONGITUDE = 135;
/** 주요 도시 경도 데이터 */
export declare const MAJOR_CITIES: Record<string, Location>;
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
export declare function calculateTrueSolarTimeCorrection(longitude: number): number;
/**
 * 진태양시 적용 (시간 보정)
 *
 * @param hour 원본 시간 (0-23)
 * @param minute 원본 분 (0-59)
 * @param longitude 지역 경도 (동경, 도)
 * @param locationName 지역명 (선택)
 * @returns 보정된 시간 정보
 */
export declare function applyTrueSolarTime(hour: number, minute: number, longitude: number, locationName?: string): TrueSolarTimeResult;
/**
 * 주요 도시 이름으로 진태양시 적용
 *
 * @param hour 원본 시간 (0-23)
 * @param minute 원본 분 (0-59)
 * @param cityName 도시명 (예: '서울', '부산', '평양')
 * @returns 보정된 시간 정보
 */
export declare function applyTrueSolarTimeByCity(hour: number, minute: number, cityName: string): TrueSolarTimeResult;
/**
 * 진태양시 보정량만 계산 (도시명으로)
 */
export declare function getTrueSolarTimeCorrectionByCity(cityName: string): number;
/**
 * 도시 목록 조회
 */
export declare function getAvailableCities(): string[];
/**
 * 도시 정보 조회
 */
export declare function getCityInfo(cityName: string): Location;
/**
 * 진태양시 보정 설명 텍스트 생성
 */
export declare function getTrueSolarTimeDescription(cityName: string): string;
//# sourceMappingURL=trueSolarTimeCalculator.d.ts.map