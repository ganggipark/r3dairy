'use client'

/**
 * Month Page
 * 월간 콘텐츠 페이지
 */

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { api } from '@/lib/api'
import type { MonthlyContentResponse, MonthlyContent } from '@/types'
import { Role } from '@/types'

function getEnergyColor(energy: number) {
  const colors = {
    1: { bg: 'bg-gray-100', text: 'text-gray-500', hex: '#f3f4f6' },
    2: { bg: 'bg-amber-100', text: 'text-amber-800', hex: '#fef3c7' },
    3: { bg: 'bg-emerald-100', text: 'text-emerald-800', hex: '#d1fae5' },
    4: { bg: 'bg-blue-100', text: 'text-blue-800', hex: '#dbeafe' },
    5: { bg: 'bg-violet-100', text: 'text-violet-800', hex: '#ede9fe' },
  }
  return colors[energy as keyof typeof colors] || colors[3]
}

export default function MonthPage() {
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [monthlyContent, setMonthlyContent] = useState<MonthlyContentResponse | null>(null)
  const [selectedRole, setSelectedRole] = useState<Role | null>(null)
  const [userRoles, setUserRoles] = useState<Role[]>([])

  // 현재 년/월 — navigable state
  const [currentYear, setCurrentYear] = useState(new Date().getFullYear())
  const [currentMonth, setCurrentMonth] = useState(new Date().getMonth() + 1)

  const navigateMonth = (direction: -1 | 1) => {
    let newMonth = currentMonth + direction
    let newYear = currentYear
    if (newMonth > 12) { newMonth = 1; newYear++ }
    if (newMonth < 1) { newMonth = 12; newYear-- }
    setCurrentMonth(newMonth)
    setCurrentYear(newYear)
  }

  useEffect(() => {
    const loadData = async () => {
      const token = localStorage.getItem('access_token')
      if (!token) {
        router.push('/login')
        return
      }

      setIsLoading(true)
      setError('')

      try {
        // 프로필에서 역할 정보 가져오기
        const profile = await api.profile.get(token)
        setUserRoles(profile.roles)
        const role = selectedRole ?? profile.roles[0]
        if (!selectedRole) setSelectedRole(role)

        // 월간 콘텐츠 로드
        const content = await api.content.getMonthly(token, currentYear, currentMonth, role)
        setMonthlyContent(content)
      } catch (err: any) { // TODO: type this — use unknown with type guard
        setError(err.message || '데이터를 불러오는 데 실패했습니다')
      } finally {
        setIsLoading(false)
      }
    }

    loadData()
  }, [router, currentYear, currentMonth])

  // 역할 변경 시 콘텐츠 다시 로드
  const handleRoleChange = async (newRole: Role) => {
    const token = localStorage.getItem('access_token')
    if (!token) return

    setSelectedRole(newRole)
    try {
      const content = await api.content.getMonthly(token, currentYear, currentMonth, newRole)
      setMonthlyContent(content)
    } catch (err: any) { // TODO: type this — use unknown with type guard
      setError('콘텐츠를 불러오는 데 실패했습니다')
    }
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-gray-600">이번 달 콘텐츠를 불러오는 중...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-red-600">{error}</div>
      </div>
    )
  }

  if (!monthlyContent) return null

  const content: MonthlyContent = monthlyContent.content

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 헤더 */}
      <header className="bg-white shadow">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-3">
              <h1 className="text-xl font-bold text-gray-900">이번 달의 흐름</h1>
              <div className="flex items-center gap-1 text-gray-700">
                <button
                  onClick={() => navigateMonth(-1)}
                  className="no-print px-2 py-1 text-gray-500 hover:text-gray-800 rounded hover:bg-gray-100 transition-colors"
                  aria-label="이전 달"
                >
                  ◀
                </button>
                <span className="font-semibold text-gray-800 min-w-[90px] text-center">
                  {currentYear}년 {currentMonth}월
                </span>
                <button
                  onClick={() => navigateMonth(1)}
                  className="no-print px-2 py-1 text-gray-500 hover:text-gray-800 rounded hover:bg-gray-100 transition-colors"
                  aria-label="다음 달"
                >
                  ▶
                </button>
              </div>
            </div>

            <div className="flex items-center gap-3">
              {/* 인쇄 버튼 */}
              <button
                onClick={() => window.print()}
                className="no-print px-3 py-1.5 text-sm text-gray-600 border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
              >
                인쇄
              </button>

              {/* 역할 선택 */}
              {userRoles.length > 1 && (
                <div className="no-print flex gap-2">
                  {userRoles.map(role => (
                    <button
                      key={role}
                      onClick={() => handleRoleChange(role)}
                      className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                        selectedRole === role
                          ? 'bg-indigo-600 text-white'
                          : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                      }`}
                    >
                      {role === Role.STUDENT ? '학생' : role === Role.OFFICE_WORKER ? '직장인' : '프리랜서'}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* 메인 콘텐츠 */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">

        {/* Monthly Theme Card */}
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-6 mb-6 border border-blue-100">
          <h2 className="text-2xl font-bold text-indigo-900 mb-3">
            {content.theme}
          </h2>
          {content.summary && (
            <p className="text-gray-700 leading-relaxed mb-4">{content.summary}</p>
          )}
          {content.keywords?.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {content.keywords.map((kw, i) => (
                <span key={i} className="px-3 py-1 bg-indigo-100 text-indigo-700 rounded-full text-sm font-medium">
                  {kw}
                </span>
              ))}
            </div>
          )}
        </div>

        {/* Calendar Grid */}
        <div className="bg-white rounded-xl border border-gray-200 p-4 mb-6">
          <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-4">이달의 에너지 캘린더</h3>
          {/* Day of week headers */}
          <div className="grid grid-cols-7 gap-1 mb-2">
            {['월', '화', '수', '목', '금', '토', '일'].map(d => (
              <div key={d} className="text-center text-xs font-medium text-gray-400 py-1">{d}</div>
            ))}
          </div>
          {/* Calendar days */}
          <div className="grid grid-cols-7 gap-1">
            {(() => {
              const firstDay = new Date(currentYear, currentMonth - 1, 1).getDay()
              const startOffset = firstDay === 0 ? 6 : firstDay - 1 // Mon=0
              const daysInMonth = new Date(currentYear, currentMonth, 0).getDate()
              const today = new Date()
              const cells = []
              // Empty cells before first day
              for (let i = 0; i < startOffset; i++) {
                cells.push(<div key={`empty-${i}`} />)
              }
              // Day cells
              for (let day = 1; day <= daysInMonth; day++) {
                const energy = content.calendar_data?.[day] ?? 3
                const color = getEnergyColor(energy)
                const isToday =
                  today.getFullYear() === currentYear &&
                  today.getMonth() + 1 === currentMonth &&
                  today.getDate() === day
                cells.push(
                  <div
                    key={day}
                    className={`${color.bg} rounded-lg p-1 text-center cursor-pointer hover:opacity-80 transition-opacity ${isToday ? 'ring-2 ring-indigo-400' : ''}`}
                    onClick={() =>
                      window.location.href = `/today?date=${currentYear}-${String(currentMonth).padStart(2, '0')}-${String(day).padStart(2, '0')}`
                    }
                  >
                    <span className={`text-xs font-medium ${color.text}`}>{day}</span>
                  </div>
                )
              }
              return cells
            })()}
          </div>
          {/* Energy legend */}
          <div className="flex flex-wrap gap-3 mt-4 pt-4 border-t border-gray-100">
            {([1, 2, 3, 4, 5] as const).map(e => {
              const c = getEnergyColor(e)
              const labels: Record<number, string> = { 1: '매우 낮음', 2: '낮음', 3: '보통', 4: '높음', 5: '매우 높음' }
              return (
                <div key={e} className="flex items-center gap-1">
                  <div className={`w-3 h-3 rounded-sm ${c.bg}`} />
                  <span className="text-xs text-gray-500">{labels[e]}</span>
                </div>
              )
            })}
          </div>
        </div>

        {/* Info Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          {/* Priorities */}
          <div className="bg-white rounded-xl border border-gray-200 p-4">
            <h3 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
              <span className="text-indigo-500">●</span> 이달의 우선순위
            </h3>
            <ol className="space-y-2">
              {(content.priorities || []).map((p, i) => (
                <li key={i} className="flex items-start gap-2 text-sm text-gray-700">
                  <span className="font-bold text-indigo-400 mt-0.5">{i + 1}.</span> {p}
                </li>
              ))}
            </ol>
          </div>

          {/* Opportunities */}
          <div className="bg-white rounded-xl border border-emerald-200 p-4">
            <h3 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
              <span className="text-emerald-500">▲</span> 기회 요소
            </h3>
            <ul className="space-y-2">
              {(content.opportunities || []).map((o, i) => (
                <li key={i} className="flex items-start gap-2 text-sm text-gray-700">
                  <span className="text-emerald-400 mt-0.5">✓</span> {o}
                </li>
              ))}
            </ul>
          </div>

          {/* Challenges */}
          <div className="bg-white rounded-xl border border-red-200 p-4">
            <h3 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
              <span className="text-red-400">▼</span> 주의 요소
            </h3>
            <ul className="space-y-2">
              {(content.challenges || []).map((c, i) => (
                <li key={i} className="flex items-start gap-2 text-sm text-gray-700">
                  <span className="text-red-400 mt-0.5">!</span> {c}
                </li>
              ))}
            </ul>
          </div>

          {/* Weekly focus/caution */}
          {((content.weekly_focus?.length ?? 0) > 0 || (content.weekly_caution?.length ?? 0) > 0) && (
            <div className="bg-white rounded-xl border border-amber-200 p-4">
              <h3 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
                <span className="text-amber-500">◆</span> 주간 포커스
              </h3>
              {(content.weekly_focus?.length ?? 0) > 0 && (
                <div className="mb-2">
                  <p className="text-xs text-emerald-600 font-medium mb-1">집중 주간</p>
                  {content.weekly_focus!.map((w, i) => (
                    <p key={i} className="text-sm text-gray-700">{w}</p>
                  ))}
                </div>
              )}
              {(content.weekly_caution?.length ?? 0) > 0 && (
                <div>
                  <p className="text-xs text-amber-600 font-medium mb-1">주의 주간</p>
                  {content.weekly_caution!.map((w, i) => (
                    <p key={i} className="text-sm text-gray-700">{w}</p>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Flow Description */}
        {content.flow_description && (
          <div className="bg-gray-50 rounded-xl border border-gray-200 p-5 mb-6">
            <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">이달의 흐름</h3>
            <p className="text-gray-700 leading-relaxed">{content.flow_description}</p>
          </div>
        )}

        {/* Print CSS */}
        <style jsx global>{`
          @media print {
            @page { size: 210mm 297mm; margin: 8mm; }
            .no-print { display: none !important; }
            body { background: white; }
            .print-compact { padding: 8px !important; }
            main > div { page-break-inside: avoid; break-inside: avoid; }
          }
        `}</style>
      </main>
    </div>
  )
}
