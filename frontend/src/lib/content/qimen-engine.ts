/**
 * Qimen (기문둔갑) Engine - Simplified stub
 *
 * Full qimen calculation is complex and optional.
 * This provides a basic implementation that returns directional data
 * based on the birth date and target date relationship.
 */

export interface QimenSlot {
  hour_start: string
  hour_end: string
  quality: string
  direction: string
  direction_en: string
  energy_level: number
  label: string
}

export interface QimenSummary {
  best_direction: string | null
  avoid_direction: string | null
  peak_hours: string | null
}

const DIRECTIONS = ['동쪽', '남동쪽', '남쪽', '남서쪽', '서쪽', '북서쪽', '북쪽', '북동쪽']
const DIRECTIONS_EN = ['east', 'southeast', 'south', 'southwest', 'west', 'northwest', 'north', 'northeast']

function dateToDayIndex(dateStr: string): number {
  const JIAZI = new Date(1900, 0, 31)
  const target = new Date(dateStr)
  const diff = Math.floor((target.getTime() - JIAZI.getTime()) / (1000 * 60 * 60 * 24))
  return ((diff % 60) + 60) % 60
}

export function calculateDailyQimen(birthDate: string, targetDate: string): QimenSlot[] {
  const dayIdx = dateToDayIndex(targetDate)
  const birthIdx = dateToDayIndex(birthDate)
  const combined = (dayIdx + birthIdx) % 8

  const slots: QimenSlot[] = []
  const timeSlots = [
    ['05:00', '07:00', '묘시'],
    ['07:00', '09:00', '진시'],
    ['09:00', '11:00', '사시'],
    ['11:00', '13:00', '오시'],
    ['13:00', '15:00', '미시'],
    ['15:00', '17:00', '신시'],
    ['17:00', '19:00', '유시'],
    ['19:00', '21:00', '술시'],
  ]

  for (let i = 0; i < timeSlots.length; i++) {
    const [start, end, label] = timeSlots[i]
    const dirIdx = (combined + i) % 8
    const energyBase = 3 + ((combined + i) % 3) - 1 // 2-4 range
    const quality = energyBase >= 4 ? '길' : energyBase <= 2 ? '흉' : '평'

    slots.push({
      hour_start: start,
      hour_end: end,
      quality,
      direction: DIRECTIONS[dirIdx],
      direction_en: DIRECTIONS_EN[dirIdx],
      energy_level: Math.max(1, Math.min(5, energyBase)),
      label,
    })
  }

  return slots
}

export function getDailySummary(birthDate: string, targetDate: string): QimenSummary {
  const slots = calculateDailyQimen(birthDate, targetDate)

  // Find best slot (highest energy)
  let bestSlot = slots[0]
  let worstSlot = slots[0]
  for (const slot of slots) {
    if (slot.energy_level > bestSlot.energy_level) bestSlot = slot
    if (slot.energy_level < worstSlot.energy_level) worstSlot = slot
  }

  return {
    best_direction: bestSlot.direction,
    avoid_direction: worstSlot.direction !== bestSlot.direction ? worstSlot.direction : null,
    peak_hours: `${bestSlot.hour_start}-${bestSlot.hour_end}`,
  }
}
