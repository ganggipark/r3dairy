'use client'

/**
 * TimeGrid Component
 * 시간대별 30분 단위 그리드 (05:00 - 21:30)
 * 기문둔갑 시간대 슬롯 데이터 및 방위 정보 지원
 * 인쇄 친화적 디자인
 */

import type { QimenTimeSlot } from '@/types'

interface TimeGridProps {
  /** 기록된 일정 텍스트 (선택사항) */
  schedule?: string
  /** 그리드 높이 커스터마이징 (기본: full) */
  height?: 'full' | 'compact'
  /** 좋은 시간 (기존 폴백용) */
  goodTime?: string
  /** 피할 시간 (기존 폴백용) */
  avoidTime?: string
  /** 기문둔갑 시간대 슬롯 데이터 (신규) */
  qimenSlots?: QimenTimeSlot[]
  /** 오늘의 최고 방위 (신규) */
  bestDirection?: string
  /** 오늘의 피할 방위 (신규) */
  avoidDirection?: string
}

/** 방위 한국어 → 방향 아이콘 매핑 */
const DIRECTION_ICONS: Record<string, string> = {
  '북': '↑',
  '남': '↓',
  '동': '→',
  '서': '←',
  '북동': '↗',
  '북서': '↖',
  '남동': '↘',
  '남서': '↙',
  '중앙': '·',
}

export default function TimeGrid({
  schedule,
  height = 'full',
  goodTime,
  avoidTime,
  qimenSlots,
  bestDirection,
  avoidDirection,
}: TimeGridProps) {
  // 5시부터 21시 30분까지 (34개 슬롯)
  const timeSlots = Array.from({ length: 34 }, (_, i) => {
    const hour = Math.floor(i / 2) + 5
    const minute = i % 2 === 0 ? '00' : '30'
    return `${hour.toString().padStart(2, '0')}:${minute}`
  })

  /**
   * 시간대별 길흉 판정
   * qimenSlots 우선, 없으면 goodTime/avoidTime 파싱 폴백
   */
  const getSlotInfo = (
    hour: number
  ): { quality: string; direction?: string; label?: string } | null => {
    // qimenSlots 우선 사용
    if (qimenSlots && qimenSlots.length > 0) {
      const slot = qimenSlots.find((s) => {
        if (s.hour_end > s.hour_start) {
          return hour >= s.hour_start && hour < s.hour_end
        } else {
          // 자시처럼 자정 넘기는 경우 (예: 23-01)
          return hour >= s.hour_start || hour < s.hour_end
        }
      })
      if (slot) {
        return {
          quality: slot.quality,
          direction: slot.direction,
          label: slot.label,
        }
      }
      return null
    }

    // 폴백: 기존 goodTime / avoidTime 문자열 파싱
    if (goodTime?.includes(`${hour}`) || goodTime?.includes(`${hour - 12}`)) {
      return { quality: 'good' }
    }
    if (avoidTime?.includes(`${hour}`) || avoidTime?.includes(`${hour - 12}`)) {
      return { quality: 'avoid' }
    }
    return null
  }

  return (
    <div
      className={`border border-gray-300 rounded-md bg-white ${
        height === 'full' ? 'min-h-[300px] sm:min-h-[400px] lg:min-h-[500px]' : 'min-h-[300px] sm:min-h-[400px]'
      } print:min-h-[600px]`}
    >
      {/* 제목 행 */}
      <div className="bg-gray-50 border-b border-gray-300 px-4 py-2 print:bg-white">
        <h3 className="text-sm font-semibold text-gray-700">시간대별 일정</h3>
      </div>

      {/* 상단 방위 배지 — bestDirection 또는 avoidDirection이 있을 때만 표시 */}
      {(bestDirection || avoidDirection) && (
        <div className="flex gap-3 px-4 py-2 bg-gray-50 border-b border-gray-200 text-xs print:bg-white">
          {bestDirection && (
            <span className="flex items-center gap-1 text-green-700 font-medium">
              <span>{DIRECTION_ICONS[bestDirection] ?? '↑'}</span>
              <span>좋은 방향: {bestDirection}</span>
            </span>
          )}
          {avoidDirection && (
            <span className="flex items-center gap-1 text-red-600">
              <span>{DIRECTION_ICONS[avoidDirection] ?? '↓'}</span>
              <span>피할 방향: {avoidDirection}</span>
            </span>
          )}
        </div>
      )}

      {/* 시간 그리드 */}
      <div className="divide-y divide-gray-200 overflow-y-auto max-h-[350px] sm:max-h-[450px] lg:max-h-none print:max-h-none print:overflow-visible">
        {timeSlots.map((time, index) => {
          const isHourMark = index % 2 === 0
          const hourNum = Math.floor(index / 2) + 5
          const slotInfo = isHourMark ? getSlotInfo(hourNum) : null

          // 반시간 슬롯은 정각 슬롯과 동일한 시간대 슬롯 정보로 배경색만 적용
          const halfHourSlotInfo =
            !isHourMark ? getSlotInfo(hourNum) : null

          const activeSloatInfo = isHourMark ? slotInfo : halfHourSlotInfo

          const bgClass =
            activeSloatInfo?.quality === 'good'
              ? 'bg-green-50'
              : activeSloatInfo?.quality === 'avoid'
              ? 'bg-red-50'
              : activeSloatInfo?.quality === 'neutral'
              ? 'bg-yellow-50'
              : ''

          return (
            <div
              key={time}
              className={`flex relative ${bgClass} ${
                isHourMark
                  ? 'border-gray-300 print:border-gray-400 min-h-[28px] sm:min-h-[32px] lg:min-h-[40px] print:min-h-[18px]'
                  : 'border-gray-100 print:border-gray-200 min-h-[16px] sm:min-h-[18px] lg:min-h-[20px] print:min-h-[12px]'
              }`}
              style={{
                borderTopWidth: isHourMark ? '1px' : '0.5px',
              }}
              title={slotInfo?.label || ''}
            >
              {/* 시간 레이블 + 길흉 표시 (정각만) */}
              {isHourMark ? (
                <div className="w-14 sm:w-16 lg:w-20 flex-shrink-0 px-3 py-1 text-xs print:w-16 print:px-2">
                  <div className="font-medium text-gray-500">{time}</div>
                  {slotInfo?.quality === 'good' && (
                    <span className="text-[10px] text-green-600">✓ 좋음</span>
                  )}
                  {slotInfo?.quality === 'avoid' && (
                    <span className="text-[10px] text-red-600">✗ 주의</span>
                  )}
                  {slotInfo?.quality === 'neutral' && (
                    <span className="text-[10px] text-yellow-600">~ 보통</span>
                  )}
                </div>
              ) : (
                <div className="w-14 sm:w-16 lg:w-20 flex-shrink-0 print:w-16" />
              )}

              {/* 방위 표시 — 정각 슬롯에만, direction이 있을 때만 */}
              {isHourMark && slotInfo?.direction && (
                <div
                  className={`absolute right-2 top-1 text-[10px] font-medium ${
                    slotInfo.quality === 'good'
                      ? 'text-green-600'
                      : slotInfo.quality === 'avoid'
                      ? 'text-red-500'
                      : 'text-yellow-600'
                  }`}
                >
                  {DIRECTION_ICONS[slotInfo.direction] || ''}{' '}
                  {slotInfo.direction}
                </div>
              )}

              {/* 메모 공간 */}
              <div className="flex-1 px-3 py-1 text-xs text-gray-600 print:px-2" />
            </div>
          )
        })}
      </div>

      {/* 피해야 할 시간 표시 — qimenSlots 없을 때 avoidTime 폴백 */}
      {avoidTime && (
        <div className="border-t border-red-100 bg-red-50 p-3 print:bg-white print:p-2 print:border-red-200">
          <div className="flex items-center gap-2">
            <span className="text-xs font-medium text-red-700">⚠️ 피해야 할 시간:</span>
            <span className="text-xs text-red-600">{avoidTime}</span>
          </div>
        </div>
      )}

      {/* 일정 텍스트가 있으면 하단에 표시 */}
      {schedule && (
        <div className="border-t border-gray-300 bg-gray-50 p-4 print:bg-white print:p-3">
          <p className="text-sm text-gray-700 whitespace-pre-line">{schedule}</p>
        </div>
      )}
    </div>
  )
}
