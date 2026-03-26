/**
 * Qimen (기문둔갑) Engine - Fallback stub
 *
 * Used only when backend qimen_slots are unavailable.
 * Types are aligned with QimenTimeSlot from @/lib/content/types.ts
 * and backend HourlyQimenResult (quality, energy_level 1-10, hour_start/end as numbers).
 */

import type { QimenTimeSlot } from '@/lib/content/types'

export interface QimenSummary {
  best_direction: string | null
  avoid_direction: string | null
  peak_hours: string | null
}

// 8방위 (백엔드 PALACE_DIRECTIONS 기준: 한국어 short form)
const DIRECTIONS = ['북', '남서', '동', '남동', '중앙', '북서', '서', '북동', '남']
const DIRECTIONS_EN = ['N', 'SW', 'E', 'SE', 'C', 'NW', 'W', 'NE', 'S']

// 12지지 시간대 [hour_start, hour_end, label]
// 자시: 23~1 (역방향), 나머지는 순방향
const TIME_SLOTS: [number, number, string][] = [
  [23, 1,  '자시'],  // 子時 23:00~01:00
  [1,  3,  '축시'],  // 丑時 01:00~03:00
  [3,  5,  '인시'],  // 寅時 03:00~05:00
  [5,  7,  '묘시'],  // 卯時 05:00~07:00
  [7,  9,  '진시'],  // 辰時 07:00~09:00
  [9,  11, '사시'],  // 巳時 09:00~11:00
  [11, 13, '오시'],  // 午時 11:00~13:00
  [13, 15, '미시'],  // 未時 13:00~15:00
  [15, 17, '신시'],  // 申時 15:00~17:00
  [17, 19, '유시'],  // 酉時 17:00~19:00
  [19, 21, '술시'],  // 戌時 19:00~21:00
  [21, 23, '해시'],  // 亥時 21:00~23:00
]

// 8문 길흉 및 에너지 (백엔드 EIGHT_GATES + GATE_BASE_ENERGY 기준)
const GATE_QUALITY: ('good' | 'neutral' | 'avoid')[] = [
  'good', 'good', 'avoid', 'neutral', 'neutral', 'avoid', 'avoid', 'good'
]
const GATE_ENERGY = [8, 9, 3, 5, 6, 2, 4, 7]
const GATE_LABELS = [
  '집중하기 좋은 시간', '에너지가 충만한 시간', '에너지가 낮은 시간', '내면 정리 시간',
  '창의적 활동에 적합한 시간', '휴식이 필요한 시간', '중요한 결정을 피해야 할 시간', '새로운 시작에 좋은 시간',
]

function dateToDayIndex(dateStr: string): number {
  const [year, month, day] = dateStr.split('-').map(Number)
  const baseDate = Date.UTC(1900, 0, 1)
  const targetDate = Date.UTC(year, month - 1, day)
  const dayDiff = Math.floor((targetDate - baseDate) / (1000 * 60 * 60 * 24))
  return ((10 + dayDiff) % 60 + 60) % 60
}

export function calculateDailyQimen(birthDate: string, targetDate: string): QimenTimeSlot[] {
  const dayIdx = dateToDayIndex(targetDate)
  const birthIdx = dateToDayIndex(birthDate)
  const combined = (dayIdx + birthIdx) % 8

  return TIME_SLOTS.map(([hour_start, hour_end, slotLabel], i) => {
    const gateIdx = (combined + i) % 8
    const dirIdx = (combined + i) % 9

    return {
      hour_start,
      hour_end,
      quality: GATE_QUALITY[gateIdx],
      direction: DIRECTIONS[dirIdx],
      direction_en: DIRECTIONS_EN[dirIdx],
      energy_level: GATE_ENERGY[gateIdx],
      label: `${slotLabel} · ${GATE_LABELS[gateIdx]}`,
    }
  })
}

export function getDailySummary(birthDate: string, targetDate: string): QimenSummary {
  const slots = calculateDailyQimen(birthDate, targetDate)

  let bestSlot = slots[0]
  let worstSlot = slots[0]
  for (const slot of slots) {
    if (slot.energy_level > bestSlot.energy_level) bestSlot = slot
    if (slot.energy_level < worstSlot.energy_level) worstSlot = slot
  }

  const peakStart = bestSlot.hour_start
  const peakEnd = bestSlot.hour_end
  const peakStr = `${String(peakStart).padStart(2, '0')}:00-${String(peakEnd).padStart(2, '0')}:00`

  return {
    best_direction: bestSlot.direction,
    avoid_direction: worstSlot.direction !== bestSlot.direction ? worstSlot.direction : null,
    peak_hours: peakStr,
  }
}
