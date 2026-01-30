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
}

export default function TimeGrid({ schedule, height = 'full' }: TimeGridProps) {
  // 0시부터 23시 30분까지
  const timeSlots = Array.from({ length: 48 }, (_, i) => {
    const hour = Math.floor(i / 2)
    const minute = i % 2 === 0 ? '00' : '30'
    return `${hour.toString().padStart(2, '0')}:${minute}`
  })

  return (
    <div className={`border border-gray-300 rounded-md bg-white ${height === 'full' ? 'min-h-[800px]' : 'min-h-[600px]'} print:min-h-[900px]`}>
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
              {/* 시간 레이블 (정각만) */}
              {isHourMark && (
                <div className="w-16 flex-shrink-0 px-3 py-1 text-xs text-gray-500 font-medium print:w-12 print:px-2">
                  {time}
                </div>
              )}
              {!isHourMark && <div className="w-16 flex-shrink-0 print:w-12"></div>}

              {/* 메모 공간 */}
              <div className="flex-1 px-3 py-1 text-xs text-gray-600 print:px-2">
                {/* 여기에 일정 내용이 표시될 수 있음 */}
              </div>
            </div>
          )
        })}
      </div>

      {/* 선택: 일정 텍스트가 있으면 하단에 표시 */}
      {schedule && (
        <div className="border-t border-gray-300 bg-gray-50 p-4 print:bg-white print:p-3">
          <p className="text-sm text-gray-700 whitespace-pre-line">{schedule}</p>
        </div>
      )}
    </div>
  )
}
