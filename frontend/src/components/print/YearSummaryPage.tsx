/**
 * YearSummaryPage - 인쇄 전용 연간 요약 A4 페이지
 * diary-print에서 연간 요약으로 삽입되는 페이지
 */

import type { YearlyContent, MonthlySignal } from '@/lib/content/types'

interface YearSummaryPageProps {
  yearlyContent: YearlyContent
  year: number
  scaler: { s: (basePx: number, min?: number) => number; si: (basePx: number, min?: number) => number }
  pageWidth: number
  pageHeight: number
  style?: React.CSSProperties
}

function getEnergyBarColor(energy: number): string {
  const colors: Record<number, string> = {
    1: '#6b7280', 2: '#f59e0b', 3: '#10b981', 4: '#3b82f6', 5: '#8b5cf6',
  }
  return colors[energy] || colors[3]
}

export default function YearSummaryPage({ yearlyContent, year, scaler, pageWidth, pageHeight, style }: YearSummaryPageProps) {
  const { s, si } = scaler

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
          {year}년 연간 요약
        </div>
      </div>

      {/* Theme */}
      {yearlyContent.theme && (
        <div style={{ background: '#f5f3ff', borderRadius: `${si(4)}px`, padding: `${si(6)}px ${si(8)}px` }}>
          <div style={{ fontWeight: 'bold', fontSize: `${s(11)}px`, color: '#5b21b6' }}>{yearlyContent.theme}</div>
          {yearlyContent.summary && (
            <div style={{ fontSize: `${s(9)}px`, color: '#4b5563', lineHeight: '1.5', marginTop: '3px' }}>{yearlyContent.summary}</div>
          )}
        </div>
      )}

      {/* Keywords */}
      {yearlyContent.keywords?.length > 0 && (
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: `${si(3)}px` }}>
          {yearlyContent.keywords.map((kw, i) => (
            <span key={i} style={{ padding: `1px ${si(6)}px`, border: '1px solid #c4b5fd', borderRadius: `${si(8)}px`, fontSize: `${s(8)}px`, color: '#6d28d9', background: '#f5f3ff' }}>{kw}</span>
          ))}
        </div>
      )}

      {/* 12-Month Energy Bar Chart */}
      <div style={{ border: '1px solid #d1d5db', borderRadius: `${si(4)}px`, padding: `${si(5)}px ${si(6)}px` }}>
        <div style={{ fontWeight: 'bold', fontSize: `${s(9)}px`, color: '#374151', marginBottom: `${si(4)}px` }}>월별 에너지 흐름</div>
        <div style={{ display: 'flex', alignItems: 'flex-end', gap: `${si(3)}px`, height: `${si(60)}px` }}>
          {Array.from({ length: 12 }, (_, i) => {
            const signal: MonthlySignal | undefined = yearlyContent.monthly_signals?.[i + 1]
            const energy = signal?.energy ?? 3
            const heightPct = energy * 20
            return (
              <div key={i} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', height: '100%', justifyContent: 'flex-end' }}>
                <div
                  style={{
                    width: '100%',
                    height: `${heightPct}%`,
                    backgroundColor: getEnergyBarColor(energy),
                    borderRadius: `${si(2)}px ${si(2)}px 0 0`,
                    minHeight: '2px',
                  }}
                />
                <span style={{ fontSize: `${s(6.5)}px`, color: '#6b7280', marginTop: '2px' }}>{i + 1}월</span>
              </div>
            )
          })}
        </div>
        {/* Month themes below chart */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', gap: `${si(3)}px`, marginTop: `${si(4)}px` }}>
          {Array.from({ length: 12 }, (_, i) => {
            const signal = yearlyContent.monthly_signals?.[i + 1]
            return (
              <div key={i} style={{ fontSize: `${s(6.5)}px`, color: '#4b5563', lineHeight: '1.3' }}>
                <span style={{ fontWeight: 'bold', color: '#374151' }}>{i + 1}월</span>{' '}
                {signal?.theme || '-'}
              </div>
            )
          })}
        </div>
      </div>

      {/* Half-year focus */}
      {(yearlyContent.first_half_focus || yearlyContent.second_half_focus) && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: `${si(6)}px` }}>
          {yearlyContent.first_half_focus && (
            <div style={{ background: '#eff6ff', borderRadius: `${si(3)}px`, padding: `${si(4)}px ${si(6)}px` }}>
              <div style={{ fontWeight: 'bold', fontSize: `${s(8.5)}px`, color: '#1e40af', marginBottom: '2px' }}>상반기 (1-6월)</div>
              <div style={{ fontSize: `${s(8)}px`, color: '#374151', lineHeight: '1.5' }}>{yearlyContent.first_half_focus}</div>
            </div>
          )}
          {yearlyContent.second_half_focus && (
            <div style={{ background: '#eef2ff', borderRadius: `${si(3)}px`, padding: `${si(4)}px ${si(6)}px` }}>
              <div style={{ fontWeight: 'bold', fontSize: `${s(8.5)}px`, color: '#4338ca', marginBottom: '2px' }}>하반기 (7-12월)</div>
              <div style={{ fontSize: `${s(8)}px`, color: '#374151', lineHeight: '1.5' }}>{yearlyContent.second_half_focus}</div>
            </div>
          )}
        </div>
      )}

      {/* Core Tasks */}
      {(yearlyContent.core_tasks?.length ?? 0) > 0 && (
        <div style={{ border: '1px solid #d1d5db', borderRadius: `${si(4)}px`, padding: `${si(4)}px ${si(6)}px` }}>
          <div style={{ fontWeight: 'bold', fontSize: `${s(9)}px`, color: '#374151', marginBottom: `${si(3)}px` }}>올해의 핵심 과제</div>
          {yearlyContent.core_tasks.map((task, i) => (
            <div key={i} style={{ display: 'flex', gap: `${si(4)}px`, fontSize: `${s(8.5)}px`, color: '#374151', lineHeight: '1.5' }}>
              <span style={{ fontWeight: 'bold', color: '#6d28d9', flexShrink: 0 }}>{i + 1}.</span>
              <span>{task}</span>
            </div>
          ))}
        </div>
      )}

      {/* Flow Summary */}
      {yearlyContent.flow_summary && (
        <div style={{ borderTop: '1px solid #e5e7eb', paddingTop: `${si(4)}px`, marginTop: 'auto' }}>
          <div style={{ fontWeight: 'bold', fontSize: `${s(8.5)}px`, color: '#374141', marginBottom: '2px' }}>올해의 흐름</div>
          <div style={{ fontSize: `${s(8.5)}px`, color: '#4b5563', lineHeight: '1.5' }}>{yearlyContent.flow_summary}</div>
        </div>
      )}
    </div>
  )
}
