'use client'

/**
 * TimeGrid Component
 * 시간대별 30분 단위 그리드 (00:00 - 23:30)
 * 인쇄 친화적 디자인
 */

interface TimeGridProps {
  /** 기록된 일정 텍스트 (선택사항) */
  schedule?: string
  /** 그리드 높이 커스터마이징 (기본: full) */
  height?: 'full' | 'compact'
  /** 좋은 시간 (예: "오전 9-11시, 오후 3-5시") */
  goodTime?: string
  /** 피할 시간 (예: "오후 1-3시") */
  avoidTime?: string
}

export default function TimeGrid({ schedule, height = 'full', goodTime, avoidTime }: TimeGridProps) {
  // 5시부터 21시 30분까지 (오전 5시 ~ 오후 9시 30분)
  const timeSlots = Array.from({ length: 34 }, (_, i) => {
    const hour = Math.floor(i / 2) + 5 // 5시부터 시작
    const minute = i % 2 === 0 ? '00' : '30'
    return `${hour.toString().padStart(2, '0')}:${minute}`
  })

  // 시간대별 길흉 판정 (간단한 파싱)
  const getTimeStatus = (hour: number): '좋음' | '주의' | null => {
    if (!goodTime && !avoidTime) return null

    // 예: "오전 9-11시" -> 9~11
    // 간단한 구현: 시간 범위 체크
    if (goodTime?.includes(`${hour}`) || goodTime?.includes(`${hour-12}`)) {
      return '좋음'
    }
    if (avoidTime?.includes(`${hour}`) || avoidTime?.includes(`${hour-12}`)) {
      return '주의'
    }
    return null
  }

  return (
    <div className={`border border-gray-300 rounded-md bg-white ${height === 'full' ? 'min-h-[500px]' : 'min-h-[400px]'} print:min-h-[600px]`}>
      {/* 제목 */}
      <div className="bg-gray-50 border-b border-gray-300 px-4 py-2 print:bg-white">
        <h3 className="text-sm font-semibold text-gray-700">시간대별 일정</h3>
      </div>

      {/* 시간 그리드 */}
      <div className="divide-y divide-gray-200">
        {timeSlots.map((time, index) => {
          const isHourMark = index % 2 === 0
          const hour = Math.floor(index / 2)

          return (
            <div
              key={time}
              className={`flex ${
                isHourMark
                  ? 'border-gray-300 print:border-gray-400'
                  : 'border-gray-100 print:border-gray-200'
              } ${isHourMark ? 'min-h-[40px]' : 'min-h-[20px]'} print:min-h-[18px]`}
              style={{
                borderTopWidth: isHourMark ? '1px' : '0.5px'
              }}
            >
              {/* 시간 레이블 (정각만) + 길흉 */}
              {isHourMark && (
                <div className="w-20 flex-shrink-0 px-3 py-1 text-xs print:w-16 print:px-2">
                  <div className="font-medium text-gray-500">{time}</div>
                  {(() => {
                    const hourNum = Math.floor(index / 2) + 5
                    const status = getTimeStatus(hourNum)
                    if (status === '좋음') {
                      return <span className="text-[10px] text-green-600">✓ 길</span>
                    } else if (status === '주의') {
                      return <span className="text-[10px] text-red-600">✗ 흉</span>
                    }
                    return null
                  })()}
                </div>
              )}
              {!isHourMark && <div className="w-20 flex-shrink-0 print:w-16"></div>}

              {/* 메모 공간 */}
              <div className="flex-1 px-3 py-1 text-xs text-gray-600 print:px-2">
                {/* 여기에 일정 내용이 표시될 수 있음 */}
              </div>
            </div>
          )
        })}
      </div>

      {/* 피해야 할 시간 표시 */}
      {avoidTime && (
        <div className="border-t border-red-100 bg-red-50 p-3 print:bg-white print:p-2 print:border-red-200">
          <div className="flex items-center gap-2">
            <span className="text-xs font-medium text-red-700">⚠️ 피해야 할 시간:</span>
            <span className="text-xs text-red-600">{avoidTime}</span>
          </div>
        </div>
      )}

      {/* 선택: 일정 텍스트가 있으면 하단에 표시 */}
      {schedule && (
        <div className="border-t border-gray-300 bg-gray-50 p-4 print:bg-white print:p-3">
          <p className="text-sm text-gray-700 whitespace-pre-line">{schedule}</p>
        </div>
      )}
    </div>
  )
}
