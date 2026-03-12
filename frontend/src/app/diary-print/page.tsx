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
          if (process.env.NODE_ENV === 'development') {
            console.warn(`청크 로드 실패: ${start}~${end}`, err)
          }
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
          @page {
            size: ${paper.widthMm}mm ${paper.heightMm}mm;
            margin: 8mm;
          }
          body {
            margin: 0;
            padding: 0;
            print-color-adjust: exact;
            -webkit-print-color-adjust: exact;
          }
          .diary-controls { display: none !important; }
          .diary-content-area { padding-top: 0 !important; }
          .diary-page {
            width: ${paper.widthMm - 16}mm !important;
            height: ${paper.heightMm - 16}mm !important;
            max-height: ${paper.heightMm - 16}mm !important;
            overflow: hidden !important;
            page-break-after: always;
            break-after: page;
            page-break-inside: avoid;
            break-inside: avoid;
            margin: 0 !important;
            padding: 10px 12px !important;
            box-shadow: none !important;
            box-sizing: border-box;
          }
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
      <div className="diary-content-area" style={{ paddingTop: '60px', fontFamily: 'serif' }}>
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

        {/* Blank page after cover for duplex printing alignment */}
        <div className="diary-page" style={{ width: `${pageWidthPx}px`, height: `${pageHeightPx}px`, margin: '16px auto', background: 'white', boxShadow: '0 4px 12px rgba(0,0,0,0.15)' }} />

        {/* Empty state for monthly mode */}
        {days.length === 0 && (
          <div style={{ textAlign: 'center', padding: '40px', color: '#6b7280' }}>선택한 달에 데이터가 없습니다.</div>
        )}

        {/* Each day spread */}
        {days.map((day, dayIndex) => {
          const content = day.content
          const qimenSlots = day.qimen_slots

          // Helper: render a compact lifestyle line (icon + title + items in one line)
          const renderCompactLifestyleCard = (title: string, icon: string, block: { explanation?: string; [key: string]: any } | undefined, listKeys: string[]) => {
            if (!block) return null
            const items = listKeys.flatMap(k => {
              const arr = block[k]
              return Array.isArray(arr) ? arr.slice(0, 2) : []
            })
            if (items.length === 0) return null
            return (
              <div style={{ fontSize: '7.5px', color: '#4b5563', lineHeight: '1.4', overflow: 'hidden', whiteSpace: 'nowrap', textOverflow: 'ellipsis' }}>
                <span style={{ fontWeight: 'bold', color: '#374151' }}>{icon} {title}:</span>{' '}
                {items.join(' · ')}
              </div>
            )
          }

          // Helper: render inline chip for small paper
          const renderLifestyleChip = (title: string, icon: string, block: { [key: string]: any } | undefined, listKeys: string[]) => {
            if (!block) return null
            const items = listKeys.flatMap(k => {
              const arr = block[k]
              return Array.isArray(arr) ? arr.slice(0, 1) : []
            })
            if (items.length === 0) return null
            return (
              <span style={{ fontSize: '7px', color: '#374151', background: '#f3f4f6', borderRadius: '6px', padding: '1px 4px', whiteSpace: 'nowrap' }}>
                {icon} {items[0]}
              </span>
            )
          }

          const isSmallPaper = paper.heightMm <= 220
          const timeSlotHeight = isSmallPaper ? 14 : 16

          return (
            <div key={day.date} className="diary-day-spread">
              {/* Left page: 오늘의 안내 (표준 10개 블록 + 압축 라이프스타일) */}
              <div className="diary-page" style={{ width: `${pageWidthPx}px`, height: `${pageHeightPx}px`, margin: '16px auto', background: 'white', padding: '16px 18px', boxSizing: 'border-box', overflow: 'hidden', fontSize: '10px', fontFamily: 'serif', display: 'flex', flexDirection: 'column', gap: '5px', boxShadow: '0 4px 12px rgba(0,0,0,0.15)' }}>
                {/* Header */}
                <div style={{ borderBottom: '2px solid #1f2937', paddingBottom: '4px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
                    <span style={{ fontSize: '13px', fontWeight: 'bold', color: '#1f2937' }}>{day.date}</span>
                    <span style={{ fontSize: '9px', color: '#6b7280' }}>Day {dayIndex + 1} / {days.length}</span>
                  </div>
                </div>

                {/* 1. 요약 */}
                {content?.summary && (
                  <div>
                    <div style={{ fontWeight: 'bold', fontSize: '9px', color: '#1f2937', marginBottom: '1px' }}>오늘의 요약</div>
                    <div style={{ color: '#4b5563', lineHeight: '1.5', fontSize: '9.5px' }}>{content.summary}</div>
                  </div>
                )}

                {/* 2. 키워드 */}
                {content?.keywords && content.keywords.length > 0 && (
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '3px' }}>
                    {content.keywords.map((kw: string, i: number) => (
                      <span key={i} style={{ padding: '1px 5px', border: '1px solid #d1d5db', borderRadius: '8px', fontSize: '8px', color: '#374151', background: '#f9fafb' }}>{kw}</span>
                    ))}
                  </div>
                )}

                {/* 3. 리듬 해설 */}
                {content?.rhythm_description && (
                  <div>
                    <div style={{ fontWeight: 'bold', fontSize: '9px', color: '#1f2937', marginBottom: '1px' }}>리듬 해설</div>
                    <div style={{ color: '#4b5563', lineHeight: '1.5', fontSize: '9px' }}>{content.rhythm_description}</div>
                  </div>
                )}

                {/* 4. 집중/주의 포인트 */}
                {content?.focus_caution && (
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '6px' }}>
                    <div style={{ background: '#f0fdf4', borderRadius: '3px', padding: '3px 5px' }}>
                      <div style={{ fontWeight: 'bold', fontSize: '8px', color: '#16a34a', marginBottom: '1px' }}>집중 포인트</div>
                      {content.focus_caution.focus?.map((item: string, i: number) => (
                        <div key={i} style={{ fontSize: '8px', color: '#374151', lineHeight: '1.4' }}>&#10003; {item}</div>
                      ))}
                    </div>
                    <div style={{ background: '#fef2f2', borderRadius: '3px', padding: '3px 5px' }}>
                      <div style={{ fontWeight: 'bold', fontSize: '8px', color: '#dc2626', marginBottom: '1px' }}>주의 포인트</div>
                      {content.focus_caution.caution?.map((item: string, i: number) => (
                        <div key={i} style={{ fontSize: '8px', color: '#374151', lineHeight: '1.4' }}>&#9888; {item}</div>
                      ))}
                    </div>
                  </div>
                )}

                {/* 5. 행동 가이드 */}
                {content?.action_guide && (
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '6px' }}>
                    <div>
                      <div style={{ fontWeight: 'bold', fontSize: '8px', color: '#16a34a', marginBottom: '1px' }}>오늘 할 일</div>
                      {content.action_guide.do?.slice(0, 4).map((item: string, i: number) => (
                        <div key={i} style={{ fontSize: '8px', color: '#374151', paddingLeft: '6px', lineHeight: '1.4' }}>&#8226; {item}</div>
                      ))}
                    </div>
                    <div>
                      <div style={{ fontWeight: 'bold', fontSize: '8px', color: '#dc2626', marginBottom: '1px' }}>피할 것</div>
                      {content.action_guide.avoid?.slice(0, 4).map((item: string, i: number) => (
                        <div key={i} style={{ fontSize: '8px', color: '#374151', paddingLeft: '6px', lineHeight: '1.4' }}>&#8226; {item}</div>
                      ))}
                    </div>
                  </div>
                )}

                {/* 6. 시간/방향 */}
                {content?.time_direction && (
                  <div style={{ background: '#eff6ff', borderRadius: '3px', padding: '4px 6px' }}>
                    <div style={{ fontWeight: 'bold', fontSize: '8px', color: '#1d4ed8', marginBottom: '2px' }}>시간 · 방향 안내</div>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '4px', fontSize: '8px', color: '#374151' }}>
                      {content.time_direction.good_time && <div>집중 시간: {content.time_direction.good_time}</div>}
                      {content.time_direction.avoid_time && <div>주의 시간: {content.time_direction.avoid_time}</div>}
                      {(content.time_direction.good_direction || day.best_direction) && <div>좋은 방향: {content.time_direction.good_direction || day.best_direction}</div>}
                      {(content.time_direction.avoid_direction || day.avoid_direction) && <div>피할 방향: {content.time_direction.avoid_direction || day.avoid_direction}</div>}
                    </div>
                    {content.time_direction.notes && (
                      <div style={{ fontSize: '7.5px', color: '#6b7280', marginTop: '2px' }}>{content.time_direction.notes}</div>
                    )}
                    {day.peak_hours && (
                      <div style={{ fontSize: '7.5px', color: '#1d4ed8', marginTop: '1px' }}>에너지 최고 시간대: {day.peak_hours}</div>
                    )}
                  </div>
                )}

                {/* 7. 상태 트리거 */}
                {content?.state_trigger && (content.state_trigger.gesture || content.state_trigger.phrase) && (
                  <div style={{ background: '#faf5ff', borderRadius: '3px', padding: '3px 5px' }}>
                    <div style={{ fontWeight: 'bold', fontSize: '8px', color: '#7c3aed', marginBottom: '1px' }}>상태 전환 트리거</div>
                    <div style={{ fontSize: '8px', color: '#374151', lineHeight: '1.5' }}>
                      {content.state_trigger.gesture && <div>동작: {content.state_trigger.gesture}</div>}
                      {content.state_trigger.phrase && <div>문구: &ldquo;{content.state_trigger.phrase}&rdquo;</div>}
                      {content.state_trigger.how_to && <div style={{ fontSize: '7.5px', color: '#6b7280' }}>방법: {content.state_trigger.how_to}</div>}
                    </div>
                  </div>
                )}

                {/* 8. 의미 전환 */}
                {content?.meaning_shift && (
                  <div style={{ borderLeft: '3px solid #f59e0b', paddingLeft: '6px' }}>
                    <div style={{ fontWeight: 'bold', fontSize: '8px', color: '#b45309', marginBottom: '1px' }}>오늘의 의미 전환</div>
                    <div style={{ fontSize: '8.5px', color: '#4b5563', lineHeight: '1.5' }}>{content.meaning_shift}</div>
                  </div>
                )}

                {/* 9. 리듬 질문 */}
                {content?.rhythm_question && (
                  <div style={{ borderTop: '1px solid #e5e7eb', paddingTop: '4px', fontStyle: 'italic', fontSize: '9px', color: '#6b7280' }}>
                    &ldquo;{content.rhythm_question}&rdquo;
                  </div>
                )}

                {/* 10. 압축 라이프스타일 가이드 */}
                <div style={{ borderTop: '1px solid #d1d5db', paddingTop: '3px', marginTop: 'auto' }}>
                  <div style={{ fontWeight: 'bold', fontSize: '8px', color: '#1f2937', marginBottom: '2px' }}>라이프스타일 가이드</div>
                  {isSmallPaper ? (
                    /* Small paper (A5/B5): inline chips, 5 categories only */
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '3px' }}>
                      {renderLifestyleChip('건강', '💪', content?.daily_health_sports, ['recommended_activities', 'health_tips'])}
                      {renderLifestyleChip('식사', '🍽', content?.daily_meal_nutrition, ['recommended_foods'])}
                      {renderLifestyleChip('패션', '👔', content?.daily_fashion_beauty, ['color_suggestions', 'clothing_style'])}
                      {renderLifestyleChip('루틴', '⏰', content?.daily_routines, ['morning_routine', 'evening_routine'])}
                      {renderLifestyleChip('관계', '🤝', content?.relationships_social, ['communication_style', 'relationship_tips'])}
                    </div>
                  ) : (
                    /* Large paper (A4/B4/Letter): 2-column compact cards */
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1px 12px' }}>
                      {renderCompactLifestyleCard('건강·운동', '💪', content?.daily_health_sports, ['recommended_activities', 'health_tips'])}
                      {renderCompactLifestyleCard('식사·영양', '🍽', content?.daily_meal_nutrition, ['recommended_foods', 'flavor_profile'])}
                      {renderCompactLifestyleCard('패션·뷰티', '👔', content?.daily_fashion_beauty, ['clothing_style', 'color_suggestions'])}
                      {renderCompactLifestyleCard('쇼핑·재정', '💰', content?.daily_shopping_finance, ['good_to_buy', 'finance_advice'])}
                      {renderCompactLifestyleCard('생활·공간', '🏠', content?.daily_living_space, ['space_organization', 'environmental_tips'])}
                      {renderCompactLifestyleCard('일과·루틴', '⏰', content?.daily_routines, ['morning_routine', 'evening_routine'])}
                      {renderCompactLifestyleCard('디지털·소통', '📱', content?.digital_communication, ['device_usage', 'social_media'])}
                      {renderCompactLifestyleCard('취미·창작', '🎨', content?.hobbies_creativity, ['creative_activities', 'learning_recommendations'])}
                      {renderCompactLifestyleCard('관계·사회', '🤝', content?.relationships_social, ['communication_style', 'relationship_tips'])}
                      {renderCompactLifestyleCard('계절·환경', '🌿', content?.seasonal_environment, ['weather_adaptation', 'seasonal_activities'])}
                    </div>
                  )}
                </div>
              </div>

              {/* Right page: User recording area with qimen time grid */}
              <div className="diary-page" style={{ width: `${pageWidthPx}px`, height: `${pageHeightPx}px`, margin: '16px auto', background: 'white', padding: '16px 18px', boxSizing: 'border-box', overflow: 'hidden', display: 'flex', flexDirection: 'column', gap: '6px', fontSize: '10px', boxShadow: '0 4px 12px rgba(0,0,0,0.15)' }}>
                {/* Header */}
                <div style={{ borderBottom: '2px solid #1f2937', paddingBottom: '4px', fontWeight: 'bold', fontSize: '12px' }}>
                  오늘의 기록
                </div>

                {/* Qimen summary bar */}
                {(day.best_direction || day.peak_hours) && (
                  <div style={{ display: 'flex', gap: '8px', fontSize: '8px', color: '#1d4ed8', background: '#eff6ff', padding: '3px 6px', borderRadius: '3px' }}>
                    {day.best_direction && <span>최적 방향: {day.best_direction}</span>}
                    {day.avoid_direction && <span>주의 방향: {day.avoid_direction}</span>}
                    {day.peak_hours && <span>에너지 피크: {day.peak_hours}</span>}
                  </div>
                )}

                {/* Qimen Time Grid */}
                <div style={{ border: '1px solid #d1d5db', borderRadius: '4px', padding: '4px 6px' }}>
                  <div style={{ fontWeight: 'bold', fontSize: '9px', marginBottom: '3px', color: '#374151' }}>시간대별 흐름</div>
                  <div style={{ display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
                    {['05','06','07','08','09','10','11','12','13','14','15','16','17','18','19','20','21','22','23'].map(h => {
                      const hourNum = parseInt(h, 10)
                      const slot = getQimenSlotForHour(qimenSlots, hourNum)
                      const indicator = slot ? QIMEN_QUALITY_INDICATORS[slot.quality] : null
                      const energyBar = slot ? renderEnergyBar(slot.energy_level) : null
                      return (
                        <div key={h} style={{ display: 'flex', alignItems: 'center', height: `${timeSlotHeight}px`, minHeight: `${timeSlotHeight}px`, backgroundColor: slot ? QIMEN_QUALITY_COLORS[slot.quality] : 'transparent' }}>
                          <span style={{ fontSize: '8px', fontWeight: 'bold', color: '#374151', width: '28px', flexShrink: 0 }}>{h}:00</span>
                          {slot ? (
                            <>
                              <span style={{ fontSize: '8px', fontWeight: 'bold', color: indicator!.color, width: '10px', flexShrink: 0 }}>{indicator!.symbol}</span>
                              {energyBar && (
                                <span style={{ ...energyBar.containerStyle, flexShrink: 0, marginRight: '3px' }}>
                                  <span style={energyBar.fillStyle} />
                                </span>
                              )}
                              <span style={{ fontSize: '7px', color: '#6b7280', width: '22px', flexShrink: 0 }}>{slot.direction}</span>
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
                <div style={{ border: '1px solid #d1d5db', borderRadius: '4px', padding: '4px 6px', flex: '0 0 auto' }}>
                  <div style={{ fontWeight: 'bold', fontSize: '9px', marginBottom: '3px' }}>오늘의 할 일</div>
                  {[1,2,3,4].map(i => (
                    <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '4px', borderBottom: '1px dashed #e5e7eb', padding: '2px 0' }}>
                      <div style={{ width: '9px', height: '9px', border: '1px solid #9ca3af', borderRadius: '2px', flexShrink: 0 }} />
                      <div style={{ flex: 1, height: '1px', background: '#e5e7eb' }} />
                    </div>
                  ))}
                </div>

                {/* Gratitude */}
                <div style={{ flex: '0 0 auto' }}>
                  <div style={{ fontWeight: 'bold', fontSize: '9px', marginBottom: '2px' }}>감사한 일</div>
                  {[1,2,3].map(i => <div key={i} style={{ borderBottom: '1px dashed #e5e7eb', height: '14px' }} />)}
                </div>

                {/* One-liner */}
                <div style={{ flex: '0 0 auto' }}>
                  <span style={{ fontWeight: 'bold', fontSize: '9px' }}>오늘의 한 줄: </span>
                  <span style={{ color: '#d1d5db' }}>_________________________</span>
                </div>

                {/* Memo - fills remaining space */}
                <div style={{ flex: 1, borderTop: '1px solid #d1d5db', paddingTop: '3px', display: 'flex', flexDirection: 'column' }}>
                  <div style={{ fontWeight: 'bold', fontSize: '9px', marginBottom: '3px', color: '#374151' }}>메모</div>
                  <div style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                    {[1,2,3,4,5,6,7,8].map(i => <div key={i} style={{ borderBottom: '1px dashed #e5e7eb', flex: 1 }} />)}
                  </div>
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </>
  )
}
