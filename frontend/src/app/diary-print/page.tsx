'use client'

/**
 * Diary Print Page
 * 다이어리 기간별 인쇄 페이지
 * 프로필의 diary_period 기반으로 다중 날짜 콘텐츠를 로드하여 인쇄 레이아웃으로 표시
 */

import { useState, useEffect, useRef } from 'react'
import { useRouter } from 'next/navigation'
import { api } from '@/lib/api'
import type { DailyContentResponse, Profile } from '@/types'
import PaperSizeSelector, { PAPER_SIZES, PaperSize } from '@/components/PaperSizeSelector'
import { getQimenSlotForHour, QIMEN_QUALITY_COLORS, QIMEN_QUALITY_INDICATORS, renderEnergyBar } from '@/lib/qimen-print'

const MM_TO_PX = 3.7795

/** 날짜 범위를 31일 단위 청크로 분할 */
function chunkDateRange(startDate: string, endDate: string): Array<{ start: string; end: string }> {
  const chunks: Array<{ start: string; end: string }> = []
  let current = new Date(startDate)
  const end = new Date(endDate)

  while (current <= end) {
    const chunkEnd = new Date(current)
    chunkEnd.setDate(chunkEnd.getDate() + 30) // 31일 (0-based)
    if (chunkEnd > end) chunkEnd.setTime(end.getTime())
    chunks.push({
      start: current.toISOString().split('T')[0],
      end: chunkEnd.toISOString().split('T')[0],
    })
    current = new Date(chunkEnd)
    current.setDate(current.getDate() + 1)
  }
  return chunks
}

/** diary_period에서 종료일 계산 */
function calcEndDate(startDate: string, period: string, customEndDate?: string): string {
  if (period === 'custom' && customEndDate) return customEndDate
  const start = new Date(startDate)
  if (period === '3months') start.setMonth(start.getMonth() + 3)
  else if (period === '6months') start.setMonth(start.getMonth() + 6)
  else if (period === '1year') start.setFullYear(start.getFullYear() + 1)
  return start.toISOString().split('T')[0]
}

// Returns array of 'YYYY-MM' strings for each month overlapping the range
function getMonthsInRange(startDate: string, endDate: string): string[] {
  const months: string[] = []
  const start = new Date(startDate)
  const end = new Date(endDate)
  const cur = new Date(start.getFullYear(), start.getMonth(), 1)
  while (cur <= end) {
    months.push(`${cur.getFullYear()}-${String(cur.getMonth() + 1).padStart(2, '0')}`)
    cur.setMonth(cur.getMonth() + 1)
  }
  return months
}

// Returns effective start/end dates for a month, clamped to period boundaries
function getMonthDateRange(yearMonth: string, periodStart: string, periodEnd: string): { start: string, end: string } {
  const [y, m] = yearMonth.split('-').map(Number)
  const monthFirst = `${y}-${String(m).padStart(2, '0')}-01`
  const lastDay = new Date(y, m, 0).getDate()
  const monthLast = `${y}-${String(m).padStart(2, '0')}-${lastDay}`
  return {
    start: monthFirst < periodStart ? periodStart : monthFirst,
    end: monthLast > periodEnd ? periodEnd : monthLast,
  }
}

// Format 'YYYY-MM' to Korean '2026년 2월'
function formatYearMonth(yearMonth: string): string {
  const [y, m] = yearMonth.split('-')
  return `${y}년 ${parseInt(m)}월`
}

export default function DiaryPrintPage() {
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(true)
  const [loadingProgress, setLoadingProgress] = useState({ loaded: 0, total: 0 })
  const [error, setError] = useState('')
  const [days, setDays] = useState<DailyContentResponse[]>([])
  const [paperSize, setPaperSize] = useState<PaperSize>('A4')
  const [profileName, setProfileName] = useState('')
  const [diaryPeriod, setDiaryPeriod] = useState('')
  const [dateRange, setDateRange] = useState({ start: '', end: '' })
  const [printMode, setPrintMode] = useState<'full' | 'monthly'>('full')
  const [selectedMonth, setSelectedMonth] = useState<string | null>(null)
  const [availableMonths, setAvailableMonths] = useState<string[]>([])
  const profileRef = useRef<Profile | null>(null)

  /** Reusable data loading: fetch content for a date range */
  const loadData = async (startDate: string, endDate: string, profile: Profile, token: string) => {
    setIsLoading(true)
    setError('')

    try {
      const chunks = chunkDateRange(startDate, endDate)
      setLoadingProgress({ loaded: 0, total: chunks.length })

      const allDays: DailyContentResponse[] = []
      for (let i = 0; i < chunks.length; i++) {
        const { start, end } = chunks[i]
        try {
          const rangeData = await api.daily.getContentRange(token, start, end, profile.roles?.[0])
          if (Array.isArray(rangeData)) {
            allDays.push(...rangeData)
          }
        } catch (err) {
          console.warn(`청크 로드 실패: ${start}~${end}`, err)
        }
        setLoadingProgress({ loaded: i + 1, total: chunks.length })
      }

      setDays(allDays)
    } catch (err: any) {
      if (err?.status === 401) { router.push('/login'); return }
      setError(err?.message || '데이터 로드에 실패했습니다')
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    const loadAll = async () => {
      const token = localStorage.getItem('access_token')
      if (!token) { router.push('/login'); return }

      try {
        const profile = await api.profile.get(token)
        setProfileName(profile.name || '')
        profileRef.current = profile

        const today = new Date().toISOString().split('T')[0]
        const period = profile.preferences?.diary_period || ''
        const startDate = profile.preferences?.diary_start_date || today
        const endDate = calcEndDate(startDate, period, profile.preferences?.diary_end_date)

        setDiaryPeriod(period)
        setDateRange({ start: startDate, end: endDate })

        // compute availableMonths
        const months = getMonthsInRange(startDate, endDate)
        setAvailableMonths(months)

        // default selectedMonth to current month if in range, else first
        const todayYM = today.slice(0, 7)
        const defaultMonth = months.includes(todayYM) ? todayYM : months[0] || null
        setSelectedMonth(defaultMonth)

        if (!period) {
          setError('프로필에 다이어리 기간이 설정되지 않았습니다. 프로필 설정에서 기간을 선택해주세요.')
          setIsLoading(false)
          return
        }

        await loadData(startDate, endDate, profile, token)
      } catch (err: any) {
        if (err?.status === 401) { router.push('/login'); return }
        setError(err?.message || '데이터 로드에 실패했습니다')
        setIsLoading(false)
      }
    }

    loadAll()
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [router])

  const loadMonthData = async (yearMonth: string) => {
    const profile = profileRef.current
    const token = localStorage.getItem('access_token')
    if (!profile || !token) return

    try {
      const today = new Date().toISOString().split('T')[0]
      const periodStart = profile.preferences?.diary_start_date || today
      const periodEnd = calcEndDate(
        periodStart,
        profile.preferences?.diary_period || '3months',
        profile.preferences?.diary_end_date
      )
      const range = getMonthDateRange(yearMonth, periodStart, periodEnd)
      setDateRange(range)
      await loadData(range.start, range.end, profile, token)
    } catch (err: any) {
      setError(err?.message || '월별 데이터 로드에 실패했습니다')
      setIsLoading(false)
    }
  }

  const paper = PAPER_SIZES[paperSize]
  const pageWidthPx = paper.widthMm * MM_TO_PX
  const pageHeightPx = paper.heightMm * MM_TO_PX

  if (isLoading) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: '16px', fontFamily: 'sans-serif' }}>
        <div style={{ fontSize: '18px', color: '#374151' }}>다이어리를 불러오는 중...</div>
        {loadingProgress.total > 0 && (
          <div style={{ fontSize: '14px', color: '#6b7280' }}>
            {loadingProgress.loaded * 31}일 / 약 {loadingProgress.total * 31}일 로드 중
          </div>
        )}
        <div style={{ width: '200px', height: '8px', background: '#e5e7eb', borderRadius: '4px' }}>
          <div style={{ width: `${loadingProgress.total > 0 ? (loadingProgress.loaded / loadingProgress.total) * 100 : 0}%`, height: '100%', background: '#3b82f6', borderRadius: '4px', transition: 'width 0.3s' }} />
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: '16px', fontFamily: 'sans-serif' }}>
        <div style={{ color: '#dc2626', fontSize: '16px' }}>{error}</div>
        <button onClick={() => router.push('/profile?edit=true')} style={{ padding: '8px 16px', background: '#3b82f6', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontSize: '14px' }}>
          프로필 설정하기
        </button>
        <button onClick={() => router.push('/today')} style={{ padding: '8px 16px', background: '#e5e7eb', color: '#374151', border: 'none', borderRadius: '6px', cursor: 'pointer', fontSize: '14px' }}>
          오늘로 돌아가기
        </button>
      </div>
    )
  }

  return (
    <>
      {/* Print CSS */}
      <style>{`
        @media print {
          .diary-controls { display: none !important; }
          .diary-page { page-break-after: always; break-after: page; }
          body { margin: 0; padding: 0; }
        }
        @media screen {
          body { background: #9ca3af; }
        }
      `}</style>

      {/* Controls (화면에서만 표시, 인쇄 시 숨김) */}
      <div className="diary-controls" style={{ position: 'fixed', top: 0, left: 0, right: 0, background: 'white', borderBottom: '1px solid #e5e7eb', padding: '12px 24px', display: 'flex', gap: '12px', alignItems: 'center', zIndex: 100, fontFamily: 'sans-serif' }}>
        <button onClick={() => router.push('/today')} style={{ padding: '6px 12px', background: '#e5e7eb', color: '#374151', border: 'none', borderRadius: '4px', cursor: 'pointer', fontSize: '13px' }}>
          ← 오늘로
        </button>

        {/* Mode toggle */}
        <div style={{ display: 'flex', gap: '4px', marginLeft: '8px' }}>
          <button
            onClick={() => {
              if (printMode !== 'full') {
                setPrintMode('full')
                // reload full period
                const profile = profileRef.current
                const token = localStorage.getItem('access_token')
                if (profile && token) {
                  const start = profile.preferences?.diary_start_date || new Date().toISOString().split('T')[0]
                  const end = calcEndDate(start, profile.preferences?.diary_period || '3months', profile.preferences?.diary_end_date)
                  setDateRange({ start, end })
                  loadData(start, end, profile, token)
                }
              }
            }}
            className={`px-3 py-1 text-sm rounded ${printMode === 'full' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700'}`}
          >
            전체 기간
          </button>
          <button
            onClick={() => {
              if (printMode !== 'monthly') {
                setPrintMode('monthly')
                if (selectedMonth) loadMonthData(selectedMonth)
              }
            }}
            className={`px-3 py-1 text-sm rounded ${printMode === 'monthly' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700'}`}
          >
            월별
          </button>
        </div>

        {/* Month selector (monthly mode only) */}
        {printMode === 'monthly' && availableMonths.length > 0 && (
          <select
            value={selectedMonth || ''}
            onChange={e => {
              setSelectedMonth(e.target.value)
              loadMonthData(e.target.value)
            }}
            className="ml-2 px-2 py-1 text-sm border border-gray-300 rounded"
          >
            {availableMonths.map(ym => (
              <option key={ym} value={ym}>{formatYearMonth(ym)}</option>
            ))}
          </select>
        )}

        <span style={{ fontSize: '14px', color: '#6b7280' }}>{days.length}일 로드됨 ({dateRange.start} ~ {dateRange.end})</span>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginLeft: 'auto' }}>
          <span style={{ fontSize: '13px', color: '#6b7280' }}>용지:</span>
          <PaperSizeSelector paperSize={paperSize} onChange={setPaperSize} />
        </div>
        <button onClick={() => window.print()} style={{ padding: '6px 16px', background: '#3b82f6', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', fontSize: '13px' }}>
          인쇄
        </button>
      </div>

      {/* Content area */}
      <div style={{ paddingTop: '60px', fontFamily: 'serif' }}>
        {/* Cover Page */}
        <div className="diary-page" style={{ width: `${pageWidthPx}px`, height: `${pageHeightPx}px`, margin: '16px auto', background: 'white', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '24px', boxShadow: '0 4px 12px rgba(0,0,0,0.15)' }}>
          <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#1f2937', letterSpacing: '0.05em' }}>나의 리듬 다이어리</div>
          <div style={{ fontSize: '20px', color: '#374151' }}>{profileName}</div>
          <div style={{ fontSize: '16px', color: '#6b7280', borderTop: '1px solid #e5e7eb', paddingTop: '16px', textAlign: 'center' }}>
            <div>
              {printMode === 'monthly' && selectedMonth
                ? formatYearMonth(selectedMonth)
                : `${dateRange.start} ~ ${dateRange.end}`}
            </div>
            <div style={{ marginTop: '8px', fontSize: '14px' }}>총 {days.length}일</div>
          </div>
          <div style={{ fontSize: '12px', color: '#9ca3af', marginTop: '32px' }}>생성일: {new Date().toISOString().split('T')[0]}</div>
        </div>

        {/* Empty state for monthly mode */}
        {days.length === 0 && (
          <div style={{ textAlign: 'center', padding: '40px', color: '#6b7280' }}>선택한 달에 데이터가 없습니다.</div>
        )}

        {/* Each day spread */}
        {days.map((day, dayIndex) => {
          const content = day.content
          const qimenSlots = day.qimen_slots

          return (
            <div key={day.date}>
              {/* Left page: Today's guide */}
              <div className="diary-page" style={{ width: `${pageWidthPx}px`, height: `${pageHeightPx}px`, margin: '16px auto', background: 'white', padding: '20px', boxSizing: 'border-box', overflow: 'hidden', fontSize: '11px', fontFamily: 'serif', display: 'flex', flexDirection: 'column', gap: '8px', boxShadow: '0 4px 12px rgba(0,0,0,0.15)' }}>
                {/* Header */}
                <div style={{ borderBottom: '2px solid #1f2937', paddingBottom: '8px', marginBottom: '4px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
                    <span style={{ fontSize: '14px', fontWeight: 'bold', color: '#1f2937' }}>{day.date}</span>
                    <span style={{ fontSize: '10px', color: '#6b7280' }}>Day {dayIndex + 1} / {days.length}</span>
                  </div>
                </div>

                {/* Summary */}
                {content?.summary && (
                  <div>
                    <div style={{ fontWeight: 'bold', fontSize: '10px', color: '#374151', marginBottom: '2px' }}>요약</div>
                    <div style={{ color: '#4b5563', lineHeight: '1.5' }}>{content.summary}</div>
                  </div>
                )}

                {/* Keywords */}
                {content?.keywords && content.keywords.length > 0 && (
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
                    {content.keywords.map((kw: string, i: number) => (
                      <span key={i} style={{ padding: '1px 6px', border: '1px solid #d1d5db', borderRadius: '10px', fontSize: '9px', color: '#374151' }}>{kw}</span>
                    ))}
                  </div>
                )}

                {/* Rhythm description */}
                {content?.rhythm_description && (
                  <div style={{ flex: '1', overflow: 'hidden' }}>
                    <div style={{ fontWeight: 'bold', fontSize: '10px', color: '#374151', marginBottom: '2px' }}>리듬 해설</div>
                    <div style={{ color: '#4b5563', lineHeight: '1.5', fontSize: '10px' }}>{content.rhythm_description.slice(0, 300)}</div>
                  </div>
                )}

                {/* Action guide */}
                {content?.action_guide && (
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
                    <div>
                      <div style={{ fontWeight: 'bold', fontSize: '9px', color: '#16a34a', marginBottom: '2px' }}>오늘 할 일</div>
                      {content.action_guide.do?.slice(0, 3).map((item: string, i: number) => (
                        <div key={i} style={{ fontSize: '9px', color: '#374151', paddingLeft: '8px' }}>&#8226; {item}</div>
                      ))}
                    </div>
                    <div>
                      <div style={{ fontWeight: 'bold', fontSize: '9px', color: '#dc2626', marginBottom: '2px' }}>피할 것</div>
                      {content.action_guide.avoid?.slice(0, 3).map((item: string, i: number) => (
                        <div key={i} style={{ fontSize: '9px', color: '#374151', paddingLeft: '8px' }}>&#8226; {item}</div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Direction / Time */}
                {(day.best_direction || content?.time_direction?.good_time) && (
                  <div style={{ display: 'flex', gap: '12px', fontSize: '9px', color: '#6b7280', borderTop: '1px solid #e5e7eb', paddingTop: '4px' }}>
                    {day.best_direction && <span>좋은 방향: {day.best_direction}</span>}
                    {content?.time_direction?.good_time && <span>집중 시간: {content.time_direction.good_time}</span>}
                  </div>
                )}

                {/* Rhythm question */}
                {content?.rhythm_question && (
                  <div style={{ borderTop: '1px solid #e5e7eb', paddingTop: '6px', fontStyle: 'italic', fontSize: '10px', color: '#6b7280' }}>
                    {content.rhythm_question}
                  </div>
                )}
              </div>

              {/* Right page: User recording area with qimen time grid */}
              <div className="diary-page" style={{ width: `${pageWidthPx}px`, height: `${pageHeightPx}px`, margin: '16px auto', background: 'white', padding: '20px', boxSizing: 'border-box', display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '11px', boxShadow: '0 4px 12px rgba(0,0,0,0.15)' }}>
                {/* Header */}
                <div style={{ borderBottom: '2px solid #1f2937', paddingBottom: '6px', fontWeight: 'bold', fontSize: '13px' }}>
                  오늘의 기록
                </div>

                {/* Qimen Time Grid */}
                <div style={{ border: '1px solid #d1d5db', borderRadius: '4px', padding: '6px', flex: '1' }}>
                  <div style={{ fontWeight: 'bold', fontSize: '10px', marginBottom: '4px', color: '#374151' }}>시간대별 흐름</div>
                  <div style={{ display: 'flex', flexDirection: 'column', height: 'calc(100% - 20px)', overflow: 'hidden' }}>
                    {['05','06','07','08','09','10','11','12','13','14','15','16','17','18','19','20','21','22','23'].map(h => {
                      const hourNum = parseInt(h, 10)
                      const slot = getQimenSlotForHour(qimenSlots, hourNum)
                      const indicator = slot ? QIMEN_QUALITY_INDICATORS[slot.quality] : null
                      const energyBar = slot ? renderEnergyBar(slot.energy_level) : null
                      return (
                        <div key={h} style={{ display: 'flex', alignItems: 'center', height: '24px', minHeight: '24px', flexShrink: 1, backgroundColor: slot ? QIMEN_QUALITY_COLORS[slot.quality] : 'transparent' }}>
                          <span style={{ fontSize: '9px', fontWeight: 'bold', color: '#374151', width: '30px', flexShrink: 0 }}>{h}:00</span>
                          {slot ? (
                            <>
                              <span style={{ fontSize: '9px', fontWeight: 'bold', color: indicator!.color, width: '10px', flexShrink: 0 }}>{indicator!.symbol}</span>
                              {energyBar && (
                                <span style={{ ...energyBar.containerStyle, flexShrink: 0, marginRight: '4px' }}>
                                  <span style={energyBar.fillStyle} />
                                </span>
                              )}
                              <span style={{ fontSize: '8px', color: '#6b7280', width: '24px', flexShrink: 0 }}>{slot.direction}</span>
                              <div style={{ flex: 1, borderBottom: '1px dashed #d1d5db', height: '100%' }} />
                            </>
                          ) : (
                            <div style={{ flex: 1, borderBottom: '1px dashed #d1d5db', height: '100%' }} />
                          )}
                        </div>
                      )
                    })}
                  </div>
                </div>

                {/* Todos */}
                <div style={{ border: '1px solid #d1d5db', borderRadius: '4px', padding: '6px', flex: '0 0 auto' }}>
                  <div style={{ fontWeight: 'bold', fontSize: '10px', marginBottom: '4px' }}>오늘의 할 일</div>
                  {[1,2,3,4].map(i => (
                    <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '4px', borderBottom: '1px dashed #e5e7eb', padding: '2px 0' }}>
                      <div style={{ width: '10px', height: '10px', border: '1px solid #9ca3af', borderRadius: '2px', flexShrink: 0 }} />
                      <div style={{ flex: 1, height: '1px', background: '#e5e7eb' }} />
                    </div>
                  ))}
                </div>

                {/* Notes */}
                <div style={{ flex: '0 0 auto' }}>
                  <div style={{ fontWeight: 'bold', fontSize: '10px', marginBottom: '2px' }}>감사한 일</div>
                  {[1,2,3].map(i => <div key={i} style={{ borderBottom: '1px dashed #e5e7eb', height: '16px' }} />)}
                </div>
                <div style={{ borderBottom: '2px solid #9ca3af', padding: '4px 0', flex: '0 0 auto' }}>
                  <span style={{ fontWeight: 'bold', fontSize: '10px' }}>오늘의 한 줄: </span>
                  <span style={{ color: '#d1d5db' }}>_________________________</span>
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </>
  )
}
