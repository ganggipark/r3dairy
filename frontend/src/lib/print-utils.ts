/**
 * 인쇄 레이아웃 공유 유틸리티
 * diary-print과 today 페이지 모두에서 사용
 */

/** mm → px 변환 계수 (96dpi 기준) */
export const MM_TO_PX = 3.7795

/**
 * 용지 비례 스케일링 함수 생성
 * A4(297mm)를 기준(1.0)으로, 용지 높이에 비례하여 모든 px 값을 조정
 * A5: 0.707, B5: 0.865, Letter: 0.939, A4: 1.0, B4: 1.226
 */
export function createScaler(paperHeightMm: number) {
  const factor = paperHeightMm / 297
  // s(): 기본 px 값을 용지 비율로 스케일, 최소값 보장 (인쇄 판독성)
  const s = (basePx: number, min = 6) => Math.max(min, Math.round(basePx * factor * 10) / 10)
  // si(): 정수 반환 (height, width 등)
  const si = (basePx: number, min = 2) => Math.max(min, Math.round(basePx * factor))
  return { factor, s, si }
}

/** A4 세로 규격 상수 (mm) */
export const A4_PORTRAIT = { widthMm: 210, heightMm: 297, marginMm: 8 }
export const A4_USABLE = { widthMm: 194, heightMm: 281 }
