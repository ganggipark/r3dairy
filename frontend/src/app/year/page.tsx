'use client'

/**
 * Year Page
 * 연간 콘텐츠 페이지
 */

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { api } from '@/lib/api'
import type { YearlyContentResponse, YearlyContent } from '@/types'
import { Role } from '@/types'

function getEnergyColor(energy: number) {
  const colors = {
    1: { bg: 'bg-gray-100', text: 'text-gray-500', bar: '#6b7280' },
    2: { bg: 'bg-amber-100', text: 'text-amber-800', bar: '#f59e0b' },
    3: { bg: 'bg-emerald-100', text: 'text-emerald-800', bar: '#10b981' },
    4: { bg: 'bg-blue-100', text: 'text-blue-800', bar: '#3b82f6' },
    5: { bg: 'bg-violet-100', text: 'text-violet-800', bar: '#8b5cf6' },
  }
  return colors[energy as keyof typeof colors] || colors[3]
}

const MONTH_NAMES = ['1월','2월','3월','4월','5월','6월','7월','8월','9월','10월','11월','12월']

export default function YearPage() {
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [yearlyContent, setYearlyContent] = useState<YearlyContentResponse | null>(null)
  const [selectedRole, setSelectedRole] = useState<Role | null>(null)
  const [userRoles, setUserRoles] = useState<Role[]>([])
  const [currentYear, setCurrentYear] = useState(new Date().getFullYear())

  const navigateYear = (direction: -1 | 1) => {
    setCurrentYear(prev => prev + direction)
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
        const profile = await api.profile.get(token)
        setUserRoles(profile.roles)
        const role = selectedRole ?? profile.roles[0]
        if (!selectedRole) setSelectedRole(profile.roles[0])

        const content = await api.content.getYearly(token, currentYear, role)
        setYearlyContent(content)
      } catch (err: any) { // TODO: type this — use unknown with type guard
        setError(err.message || '데이터를 불러오는 데 실패했습니다')
      } finally {
        setIsLoading(false)
      }
    }

    loadData()
  }, [router, currentYear])

  const handleRoleChange = async (newRole: Role) => {
    const token = localStorage.getItem('access_token')
    if (!token) return

    setSelectedRole(newRole)
    try {
      const content = await api.content.getYearly(token, currentYear, newRole)
      setYearlyContent(content)
    } catch (err: any) { // TODO: type this — use unknown with type guard
      setError('콘텐츠를 불러오는 데 실패했습니다')
    }
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-gray-600">올해 콘텐츠를 불러오는 중...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-red-600">{error}</div>
      </div>
    )
  }

  const content = yearlyContent?.content as YearlyContent | undefined

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 헤더 */}
      <header className="bg-white shadow no-print">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-bold text-gray-900">올해의 흐름</h1>
              <div className="flex items-center gap-1">
                <button
                  onClick={() => navigateYear(-1)}
                  className="no-print px-2 py-1 text-gray-500 hover:text-gray-800 transition-colors"
                  aria-label="이전 년도"
                >
                  ◀
                </button>
                <span className="font-semibold text-gray-700 w-16 text-center">{currentYear}년</span>
                <button
                  onClick={() => navigateYear(1)}
                  className="no-print px-2 py-1 text-gray-500 hover:text-gray-800 transition-colors"
                  aria-label="다음 년도"
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
                🖨️ 인쇄
              </button>

              {/* 역할 선택 */}
              {userRoles.length > 1 && (
                <div className="flex gap-2">
                  {userRoles.map(role => (
                    <button
                      key={role}
                      onClick={() => handleRoleChange(role)}
                      className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
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

        {!content ? (
          <div className="bg-white rounded-xl border border-gray-200 p-8 text-center text-gray-500">
            연간 콘텐츠가 없습니다.
          </div>
        ) : (
          <>
            {/* Yearly Theme Card */}
            <div className="bg-gradient-to-r from-purple-50 to-indigo-50 rounded-xl p-6 mb-6 border border-purple-100">
              <h2 className="text-2xl font-bold text-indigo-900 mb-3">
                {content.theme}
              </h2>
              {content.summary && (
                <p className="text-gray-700 leading-relaxed mb-4">{content.summary}</p>
              )}
              {content.keywords?.length > 0 && (
                <div className="flex flex-wrap gap-2">
                  {content.keywords.map((kw, i) => (
                    <span key={i} className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-sm font-medium">
                      {kw}
                    </span>
                  ))}
                </div>
              )}
            </div>

            {/* 12-Month Energy Bar Chart */}
            <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6">
              <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-4">월별 에너지 흐름</h3>
              <div className="flex items-end gap-2 h-32">
                {Array.from({ length: 12 }, (_, i) => {
                  const signal = content.monthly_signals?.[i + 1]
                  const energy = signal?.energy ?? 3
                  const color = getEnergyColor(energy)
                  const heightPct = energy * 20
                  return (
                    <div key={i} className="flex-1 flex flex-col items-center gap-1 group relative">
                      <div className="absolute bottom-full mb-2 hidden group-hover:block bg-gray-800 text-white text-xs rounded px-2 py-1 whitespace-nowrap z-10">
                        {signal?.theme || MONTH_NAMES[i]}<br />{energy}/5
                      </div>
                      <div
                        className="w-full rounded-t-md transition-all"
                        style={{ height: `${heightPct}%`, backgroundColor: color.bar, minHeight: '4px' }}
                      />
                      <span className="text-xs text-gray-500 mt-1">{i + 1}월</span>
                    </div>
                  )
                })}
              </div>
            </div>

            {/* Half-Year Focus Cards */}
            {(content.first_half_focus || content.second_half_focus) && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                {content.first_half_focus && (
                  <div className="bg-blue-50 rounded-xl border border-blue-100 p-4">
                    <h3 className="text-sm font-semibold text-blue-700 mb-2">상반기 (1-6월)</h3>
                    <p className="text-sm text-gray-700">{content.first_half_focus}</p>
                  </div>
                )}
                {content.second_half_focus && (
                  <div className="bg-indigo-50 rounded-xl border border-indigo-100 p-4">
                    <h3 className="text-sm font-semibold text-indigo-700 mb-2">하반기 (7-12월)</h3>
                    <p className="text-sm text-gray-700">{content.second_half_focus}</p>
                  </div>
                )}
              </div>
            )}

            {/* 12-Month Detail Grid */}
            <div className="bg-white rounded-xl border border-gray-200 p-4 mb-6">
              <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-4">월별 상세</h3>
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
                {Array.from({ length: 12 }, (_, i) => {
                  const signal = content.monthly_signals?.[i + 1]
                  const energy = signal?.energy ?? 3
                  const color = getEnergyColor(energy)
                  return (
                    <div
                      key={i}
                      className={`${color.bg} rounded-lg p-3 cursor-pointer hover:opacity-80 transition-opacity`}
                      onClick={() => window.location.href = `/month?year=${currentYear}&month=${i + 1}`}
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span className={`text-xs font-bold ${color.text}`}>{i + 1}월</span>
                        <span className={`text-xs ${color.text}`}>{energy}/5</span>
                      </div>
                      <p className={`text-xs ${color.text} line-clamp-2`}>{signal?.theme || '-'}</p>
                      {/* Mini energy bar */}
                      <div className="mt-2 h-1 bg-white rounded-full overflow-hidden">
                        <div
                          className="h-full rounded-full"
                          style={{ width: `${energy * 20}%`, backgroundColor: color.bar }}
                        />
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>

            {/* Core Tasks */}
            {(content.core_tasks?.length ?? 0) > 0 && (
              <div className="bg-white rounded-xl border border-gray-200 p-4 mb-6">
                <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">올해의 핵심 과제</h3>
                <ol className="space-y-2">
                  {content.core_tasks.map((task, i) => (
                    <li key={i} className="flex items-start gap-3 text-sm text-gray-700">
                      <span className="flex-shrink-0 w-6 h-6 bg-indigo-100 text-indigo-700 rounded-full flex items-center justify-center text-xs font-bold">
                        {i + 1}
                      </span>
                      {task}
                    </li>
                  ))}
                </ol>
              </div>
            )}

            {/* Flow Summary */}
            {content.flow_summary && (
              <div className="bg-gray-50 rounded-xl border border-gray-200 p-5 mb-6">
                <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">올해의 흐름</h3>
                <p className="text-gray-700 leading-relaxed">{content.flow_summary}</p>
              </div>
            )}
          </>
        )}
      </main>

      {/* Print CSS */}
      <style jsx global>{`
        @media print {
          @page { size: 210mm 297mm; margin: 8mm; }
          .no-print { display: none !important; }
          body { background: white; }
          main > div { page-break-inside: avoid; break-inside: avoid; }
        }
      `}</style>
    </div>
  )
}
