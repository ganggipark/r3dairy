import type { QimenTimeSlot } from '@/types'

/**
 * 기문둔갑 인쇄 렌더링 공유 유틸리티
 * 인쇄 미리보기와 다이어리 인쇄 페이지 모두에서 사용
 */

/** 기문 품질별 배경색 (inline style용, print 호환) */
export const QIMEN_QUALITY_COLORS = {
  good: '#f0fdf4',    // green-50
  neutral: '#fefce8', // yellow-50
  avoid: '#fef2f2',   // red-50
} as const

/** 기문 품질별 표시 기호 */
export const QIMEN_QUALITY_INDICATORS = {
  good:    { symbol: '+', color: '#16a34a' },
  neutral: { symbol: '~', color: '#ca8a04' },
  avoid:   { symbol: '-', color: '#dc2626' },
} as const

/**
 * 주어진 시각(hour)에 해당하는 QimenTimeSlot 반환
 * TimeGrid의 getSlotInfo()와 동일한 매칭 로직 사용
 * 차이: full QimenTimeSlot 반환 (energy_level 포함)
 */
export function getQimenSlotForHour(
  qimenSlots: QimenTimeSlot[] | undefined | null,
  hour: number
): QimenTimeSlot | null {
  if (!qimenSlots || qimenSlots.length === 0) return null

  for (const slot of qimenSlots) {
    const { hour_start, hour_end } = slot
    // 자시(子時) 처리: hour_start=23, hour_end=1 → 23시 또는 0시 포함
    if (hour_start > hour_end) {
      if (hour >= hour_start || hour < hour_end) return slot
    } else {
      if (hour >= hour_start && hour < hour_end) return slot
    }
  }
  return null
}

/**
 * 에너지 레벨(1-10)을 인쇄용 compact bar 스타일로 변환
 */
export function renderEnergyBar(energyLevel: number, scale = 1.0): {
  containerStyle: React.CSSProperties
  fillStyle: React.CSSProperties
} {
  const pct = Math.max(0, Math.min(100, (energyLevel / 10) * 100))
  const color = energyLevel >= 7 ? '#16a34a' : energyLevel >= 4 ? '#ca8a04' : '#dc2626'
  const w = Math.round(32 * scale)
  const h = Math.max(2, Math.round(4 * scale))
  return {
    containerStyle: {
      display: 'inline-block',
      width: `${w}px`,
      height: `${h}px`,
      background: '#e5e7eb',
      borderRadius: `${Math.max(1, Math.round(2 * scale))}px`,
      overflow: 'hidden',
      verticalAlign: 'middle',
    },
    fillStyle: {
      display: 'block',
      width: `${pct}%`,
      height: '100%',
      background: color,
    },
  }
}
