/**
 * MonthSummaryPage - 인쇄 전용 월간 요약 A4 페이지
 * diary-print에서 각 월의 일간 페이지 앞에 삽입되는 요약 페이지
 */

import type { MonthlyContent } from '@/lib/content/types'

interface MonthSummaryPageProps {
  monthlyContent: MonthlyContent
  yearMonth: string // 'YYYY-MM'
  scaler: { s: (basePx: number, min?: number) => number; si: (basePx: number, min?: number) => number }
  pageWidth: number
  pageHeight: number
  style?: React.CSSProperties
}

function getEnergyColor(energy: number): string {
  const colors: Record<number, string> = {
    1: '#e5e7eb', 2: '#fef3c7', 3: '#d1fae5', 4: '#dbeafe', 5: '#ede9fe',
  }
  return colors[energy] || colors[3]
}

function getEnergyLabel(energy: number): string {
  const labels: Record<number, string> = {
    1: '낮음', 2: '보통↓', 3: '보통', 4: '높음', 5: '매우 높음',
  }
  return labels[energy] || '보통'
}

export default function MonthSummaryPage({ monthlyContent, yearMonth, scaler, pageWidth, pageHeight, style }: MonthSummaryPageProps) {
  const { s, si } = scaler
  const [yearStr, monthStr] = yearMonth.split('-')
  const year = parseInt(yearStr)
  const month = parseInt(monthStr)
  const daysInMonth = new Date(year, month, 0).getDate()
  const firstDayOfWeek = new Date(year, month - 1, 1).getDay() // 0=Sun
  const startOffset = firstDayOfWeek === 0 ? 6 : firstDayOfWeek - 1 // Mon=0

  return (
    <div
      className="diary-page"
      style={{
        width: `${pageWidth}px`,
        height: `${pageHeight}px`,
        margin: '16px auto',
        background: 'white',
        padding: `${si(20)}px ${si(22)}px`,
        boxSizing: 'border-box',
        overflow: 'clip',
        fontFamily: 'serif',
        display: 'flex',
        flexDirection: 'column',
        gap: `${si(7)}px`,
        boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
        ...style,
      }}
    >
      {/* Header */}
      <div style={{ borderBottom: '2px solid #1f2937', paddingBottom: `${si(5)}px` }}>
        <div style={{ fontSize: `${s(16)}px`, fontWeight: 'bold', color: '#1f2937' }}>
          {year}년 {month}월
        </div>
        <div style={{ fontSize: `${s(10)}px`, color: '#6b7280', marginTop: '2px' }}>월간 요약</div>
      </div>

      {/* Theme */}
      {monthlyContent.theme && (
        <div style={{ background: '#eef2ff', borderRadius: `${si(4)}px`, padding: `${si(6)}px ${si(8)}px` }}>
          <div style={{ fontWeight: 'bold', fontSize: `${s(11)}px`, color: '#3730a3' }}>{monthlyContent.theme}</div>
          {monthlyContent.summary && (
            <div style={{ fontSize: `${s(9)}px`, color: '#4b5563', lineHeight: '1.5', marginTop: '3px' }}>{monthlyContent.summary}</div>
          )}
        </div>
      )}

      {/* Keywords */}
      {monthlyContent.keywords?.length > 0 && (
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: `${si(3)}px` }}>
          {monthlyContent.keywords.map((kw, i) => (
            <span key={i} style={{ padding: `1px ${si(6)}px`, border: '1px solid #c7d2fe', borderRadius: `${si(8)}px`, fontSize: `${s(8)}px`, color: '#4338ca', background: '#eef2ff' }}>{kw}</span>
          ))}
        </div>
      )}

      {/* Energy Calendar Grid */}
      <div style={{ border: '1px solid #d1d5db', borderRadius: `${si(4)}px`, padding: `${si(5)}px ${si(6)}px` }}>
        <div style={{ fontWeight: 'bold', fontSize: `${s(9)}px`, color: '#374151', marginBottom: `${si(3)}px` }}>에너지 캘린더</div>
        {/* Day headers */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: '2px', marginBottom: '3px' }}>
          {['월', '화', '수', '목', '금', '토', '일'].map(d => (
            <div key={d} style={{ textAlign: 'center', fontSize: `${s(7)}px`, color: '#9ca3af', fontWeight: 'bold' }}>{d}</div>
          ))}
        </div>
        {/* Calendar cells */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: '2px' }}>
          {Array.from({ length: startOffset }, (_, i) => (
            <div key={`e-${i}`} />
          ))}
          {Array.from({ length: daysInMonth }, (_, i) => {
            const day = i + 1
            const energy = monthlyContent.calendar_data?.[day] ?? 3
            return (
              <div
                key={day}
                style={{
                  background: getEnergyColor(energy),
                  borderRadius: `${si(2)}px`,
                  padding: `${si(1)}px`,
                  textAlign: 'center',
                  fontSize: `${s(7)}px`,
                  color: '#374151',
                  fontWeight: energy >= 4 ? 'bold' : 'normal',
                }}
              >
                {day}
              </div>
            )
          })}
        </div>
        {/* Legend */}
        <div style={{ display: 'flex', gap: `${si(6)}px`, marginTop: `${si(3)}px`, fontSize: `${s(6.5)}px`, color: '#6b7280' }}>
          {[1, 2, 3, 4, 5].map(e => (
            <div key={e} style={{ display: 'flex', alignItems: 'center', gap: '2px' }}>
              <div style={{ width: `${si(6)}px`, height: `${si(6)}px`, background: getEnergyColor(e), borderRadius: '1px' }} />
              <span>{getEnergyLabel(e)}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Priorities + Opportunities + Challenges */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: `${si(6)}px` }}>
        {/* Priorities */}
        {(monthlyContent.priorities?.length ?? 0) > 0 && (
          <div style={{ background: '#f0f9ff', borderRadius: `${si(3)}px`, padding: `${si(4)}px ${si(6)}px` }}>
            <div style={{ fontWeight: 'bold', fontSize: `${s(8.5)}px`, color: '#1e40af', marginBottom: '2px' }}>이달의 우선순위</div>
            {monthlyContent.priorities.map((p, i) => (
              <div key={i} style={{ fontSize: `${s(8)}px`, color: '#374151', lineHeight: '1.5' }}>{i + 1}. {p}</div>
            ))}
          </div>
        )}

        {/* Opportunities */}
        {(monthlyContent.opportunities?.length ?? 0) > 0 && (
          <div style={{ background: '#f0fdf4', borderRadius: `${si(3)}px`, padding: `${si(4)}px ${si(6)}px` }}>
            <div style={{ fontWeight: 'bold', fontSize: `${s(8.5)}px`, color: '#16a34a', marginBottom: '2px' }}>기회 요소</div>
            {monthlyContent.opportunities.map((o, i) => (
              <div key={i} style={{ fontSize: `${s(8)}px`, color: '#374151', lineHeight: '1.5' }}>&#10003; {o}</div>
            ))}
          </div>
        )}

        {/* Challenges */}
        {(monthlyContent.challenges?.length ?? 0) > 0 && (
          <div style={{ background: '#fef2f2', borderRadius: `${si(3)}px`, padding: `${si(4)}px ${si(6)}px` }}>
            <div style={{ fontWeight: 'bold', fontSize: `${s(8.5)}px`, color: '#dc2626', marginBottom: '2px' }}>주의 요소</div>
            {monthlyContent.challenges.map((c, i) => (
              <div key={i} style={{ fontSize: `${s(8)}px`, color: '#374151', lineHeight: '1.5' }}>&#9888; {c}</div>
            ))}
          </div>
        )}

        {/* Weekly focus/caution */}
        {((monthlyContent.weekly_focus?.length ?? 0) > 0 || (monthlyContent.weekly_caution?.length ?? 0) > 0) && (
          <div style={{ background: '#fffbeb', borderRadius: `${si(3)}px`, padding: `${si(4)}px ${si(6)}px` }}>
            <div style={{ fontWeight: 'bold', fontSize: `${s(8.5)}px`, color: '#b45309', marginBottom: '2px' }}>주간 포커스</div>
            {(monthlyContent.weekly_focus?.length ?? 0) > 0 && (
              <div style={{ marginBottom: '3px' }}>
                <div style={{ fontSize: `${s(7.5)}px`, color: '#16a34a', fontWeight: 'bold' }}>집중</div>
                {monthlyContent.weekly_focus!.map((w, i) => (
                  <div key={i} style={{ fontSize: `${s(7.5)}px`, color: '#374151', lineHeight: '1.4' }}>{w}</div>
                ))}
              </div>
            )}
            {(monthlyContent.weekly_caution?.length ?? 0) > 0 && (
              <div>
                <div style={{ fontSize: `${s(7.5)}px`, color: '#dc2626', fontWeight: 'bold' }}>주의</div>
                {monthlyContent.weekly_caution!.map((w, i) => (
                  <div key={i} style={{ fontSize: `${s(7.5)}px`, color: '#374151', lineHeight: '1.4' }}>{w}</div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Flow Description */}
      {monthlyContent.flow_description && (
        <div style={{ borderTop: '1px solid #e5e7eb', paddingTop: `${si(4)}px`, marginTop: 'auto' }}>
          <div style={{ fontWeight: 'bold', fontSize: `${s(8.5)}px`, color: '#374151', marginBottom: '2px' }}>이달의 흐름</div>
          <div style={{ fontSize: `${s(8.5)}px`, color: '#4b5563', lineHeight: '1.5' }}>{monthlyContent.flow_description}</div>
        </div>
      )}
    </div>
  )
}
