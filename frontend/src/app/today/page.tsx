'use client'

/**
 * Today Page
 * 일간 콘텐츠 + 사용자 기록 페이지 (좌/우 레이아웃)
 */

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { api } from '@/lib/api'
import type { DailyContentResponse, DailyLog, DailyLogCreate, DailyLogUpdate } from '@/types'
import { Role } from '@/types'

export default function TodayPage() {
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')

  // 콘텐츠 상태
  const [dailyContent, setDailyContent] = useState<DailyContentResponse | null>(null)
  const [selectedRole, setSelectedRole] = useState<Role | null>(null)
  const [userRoles, setUserRoles] = useState<Role[]>([])

  // 기록 상태
  const [log, setLog] = useState<DailyLog | null>(null)
  const [logForm, setLogForm] = useState({
    schedule: '',
    todos: [] as string[],
    mood: 0,
    energy: 0,
    notes: '',
    gratitude: ''
  })
  const [isSavingLog, setIsSavingLog] = useState(false)

  // 오늘 날짜
  const today = new Date().toISOString().split('T')[0]

  // 초기 데이터 로드
  useEffect(() => {
    const loadData = async () => {
      const token = localStorage.getItem('access_token')
      if (!token) {
        router.push('/login')
        return
      }

      try {
        // 프로필에서 역할 정보 가져오기
        const profile = await api.profile.get(token)
        setUserRoles(profile.roles)
        setSelectedRole(profile.roles[0]) // 첫 번째 역할을 기본값으로

        // 일간 콘텐츠 로드
        const content = await api.daily.getContent(token, today, profile.roles[0])
        setDailyContent(content)

        // 기존 기록 로드 (있으면)
        try {
          const existingLog = await api.logs.get(token, today)
          setLog(existingLog)
          setLogForm({
            schedule: existingLog.schedule || '',
            todos: existingLog.todos || [],
            mood: existingLog.mood || 0,
            energy: existingLog.energy || 0,
            notes: existingLog.notes || '',
            gratitude: existingLog.gratitude || ''
          })
        } catch (err) {
          // 기록이 없으면 빈 폼 유지
        }
      } catch (err: any) {
        setError(err.message || '데이터를 불러오는 데 실패했습니다')
      } finally {
        setIsLoading(false)
      }
    }

    loadData()
  }, [router, today])

  // 역할 변경 시 콘텐츠 다시 로드
  const handleRoleChange = async (newRole: Role) => {
    const token = localStorage.getItem('access_token')
    if (!token) return

    setSelectedRole(newRole)
    try {
      const content = await api.daily.getContent(token, today, newRole)
      setDailyContent(content)
    } catch (err: any) {
      setError('콘텐츠를 불러오는 데 실패했습니다')
    }
  }

  // 기록 저장
  const handleSaveLog = async () => {
    const token = localStorage.getItem('access_token')
    if (!token) {
      router.push('/login')
      return
    }

    setIsSavingLog(true)

    try {
      if (log) {
        // 기존 기록 수정
        const updateData: DailyLogUpdate = {
          schedule: logForm.schedule || undefined,
          todos: logForm.todos.length > 0 ? logForm.todos : undefined,
          mood: logForm.mood > 0 ? logForm.mood : undefined,
          energy: logForm.energy > 0 ? logForm.energy : undefined,
          notes: logForm.notes || undefined,
          gratitude: logForm.gratitude || undefined
        }
        const updated = await api.logs.update(token, today, updateData)
        setLog(updated)
      } else {
        // 새 기록 생성
        const createData: DailyLogCreate = {
          date: today,
          schedule: logForm.schedule || undefined,
          todos: logForm.todos.length > 0 ? logForm.todos : undefined,
          mood: logForm.mood > 0 ? logForm.mood : undefined,
          energy: logForm.energy > 0 ? logForm.energy : undefined,
          notes: logForm.notes || undefined,
          gratitude: logForm.gratitude || undefined
        }
        const created = await api.logs.create(token, today, createData)
        setLog(created)
      }
      alert('기록이 저장되었습니다')
    } catch (err: any) {
      alert(err.message || '기록 저장에 실패했습니다')
    } finally {
      setIsSavingLog(false)
    }
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-gray-600">오늘의 리듬을 불러오는 중...</div>
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

  if (!dailyContent) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-gray-600">콘텐츠를 불러올 수 없습니다</div>
      </div>
    )
  }

  const content = dailyContent.content

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 헤더 */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">오늘의 리듬</h1>
              <p className="text-sm text-gray-600">{today}</p>
            </div>

            {/* 역할 선택 */}
            {userRoles.length > 1 && (
              <div className="flex gap-2">
                {userRoles.map(role => (
                  <button
                    key={role}
                    onClick={() => handleRoleChange(role)}
                    className={`px-4 py-2 rounded-md text-sm font-medium ${
                      selectedRole === role
                        ? 'bg-blue-600 text-white'
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
      </header>

      {/* 메인 콘텐츠: 좌우 레이아웃 */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* 좌측: 오늘의 안내 */}
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">오늘의 안내</h2>

              {/* 요약 */}
              <section className="mb-6">
                <h3 className="text-lg font-semibold text-gray-800 mb-2">요약</h3>
                <p className="text-gray-700">{content.summary}</p>
              </section>

              {/* 키워드 */}
              <section className="mb-6">
                <h3 className="text-lg font-semibold text-gray-800 mb-2">키워드</h3>
                <div className="flex flex-wrap gap-2">
                  {content.keywords.map((keyword, index) => (
                    <span
                      key={index}
                      className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm"
                    >
                      {keyword}
                    </span>
                  ))}
                </div>
              </section>

              {/* 리듬 해설 */}
              <section className="mb-6">
                <h3 className="text-lg font-semibold text-gray-800 mb-2">리듬 해설</h3>
                <p className="text-gray-700 whitespace-pre-line">{content.rhythm_description}</p>
              </section>

              {/* 집중/주의 포인트 */}
              <section className="mb-6">
                <h3 className="text-lg font-semibold text-gray-800 mb-2">집중/주의 포인트</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <h4 className="font-medium text-green-700 mb-1">집중</h4>
                    <ul className="list-disc list-inside text-sm text-gray-700">
                      {content.focus_caution.focus.map((item, index) => (
                        <li key={index}>{item}</li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <h4 className="font-medium text-red-700 mb-1">주의</h4>
                    <ul className="list-disc list-inside text-sm text-gray-700">
                      {content.focus_caution.caution.map((item, index) => (
                        <li key={index}>{item}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              </section>

              {/* 행동 가이드 */}
              <section className="mb-6">
                <h3 className="text-lg font-semibold text-gray-800 mb-2">행동 가이드</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <h4 className="font-medium text-green-700 mb-1">권장</h4>
                    <ul className="list-disc list-inside text-sm text-gray-700">
                      {content.action_guide.do.map((item, index) => (
                        <li key={index}>{item}</li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <h4 className="font-medium text-red-700 mb-1">지양</h4>
                    <ul className="list-disc list-inside text-sm text-gray-700">
                      {content.action_guide.avoid.map((item, index) => (
                        <li key={index}>{item}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              </section>

              {/* 시간/방향 */}
              <section className="mb-6">
                <h3 className="text-lg font-semibold text-gray-800 mb-2">시간/방향</h3>
                <div className="space-y-2 text-sm text-gray-700">
                  <p><span className="font-medium">좋은 시간:</span> {content.time_direction.good_time}</p>
                  <p><span className="font-medium">피할 시간:</span> {content.time_direction.avoid_time}</p>
                  <p><span className="font-medium">좋은 방향:</span> {content.time_direction.good_direction}</p>
                  <p><span className="font-medium">피할 방향:</span> {content.time_direction.avoid_direction}</p>
                  <p><span className="font-medium">참고:</span> {content.time_direction.notes}</p>
                </div>
              </section>

              {/* 상태 트리거 */}
              <section className="mb-6">
                <h3 className="text-lg font-semibold text-gray-800 mb-2">상태 전환 트리거</h3>
                <div className="space-y-2 text-sm text-gray-700">
                  <p><span className="font-medium">제스처:</span> {content.state_trigger.gesture}</p>
                  <p><span className="font-medium">문구:</span> {content.state_trigger.phrase}</p>
                  <p><span className="font-medium">방법:</span> {content.state_trigger.how_to}</p>
                </div>
              </section>

              {/* 의미 전환 */}
              <section className="mb-6">
                <h3 className="text-lg font-semibold text-gray-800 mb-2">의미 전환</h3>
                <p className="text-gray-700 whitespace-pre-line">{content.meaning_shift}</p>
              </section>

              {/* 리듬 질문 */}
              <section>
                <h3 className="text-lg font-semibold text-gray-800 mb-2">리듬 질문</h3>
                <p className="text-gray-700 italic">{content.rhythm_question}</p>
              </section>
            </div>
          </div>

          {/* 우측: 사용자 기록 */}
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">오늘의 기록</h2>

              <div className="space-y-4">
                {/* 일정 */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    오늘의 일정
                  </label>
                  <textarea
                    value={logForm.schedule}
                    onChange={e => setLogForm({ ...logForm, schedule: e.target.value })}
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    placeholder="오늘 계획한 일정을 적어보세요"
                  />
                </div>

                {/* 기분 */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    기분 (1-5)
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="5"
                    value={logForm.mood}
                    onChange={e => setLogForm({ ...logForm, mood: parseInt(e.target.value) })}
                    className="w-full"
                  />
                  <div className="flex justify-between text-xs text-gray-500">
                    <span>없음</span>
                    <span>매우 나쁨</span>
                    <span>보통</span>
                    <span>좋음</span>
                    <span>매우 좋음</span>
                  </div>
                </div>

                {/* 에너지 */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    에너지 (1-5)
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="5"
                    value={logForm.energy}
                    onChange={e => setLogForm({ ...logForm, energy: parseInt(e.target.value) })}
                    className="w-full"
                  />
                  <div className="flex justify-between text-xs text-gray-500">
                    <span>없음</span>
                    <span>매우 낮음</span>
                    <span>보통</span>
                    <span>높음</span>
                    <span>매우 높음</span>
                  </div>
                </div>

                {/* 메모 */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    메모
                  </label>
                  <textarea
                    value={logForm.notes}
                    onChange={e => setLogForm({ ...logForm, notes: e.target.value })}
                    rows={4}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    placeholder="오늘 하루를 되돌아보며 자유롭게 기록하세요"
                  />
                </div>

                {/* 감사 */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    감사한 일
                  </label>
                  <textarea
                    value={logForm.gratitude}
                    onChange={e => setLogForm({ ...logForm, gratitude: e.target.value })}
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    placeholder="오늘 감사한 일이 있나요?"
                  />
                </div>

                {/* 저장 버튼 */}
                <button
                  onClick={handleSaveLog}
                  disabled={isSavingLog}
                  className="w-full py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:bg-gray-400"
                >
                  {isSavingLog ? '저장 중...' : '기록 저장'}
                </button>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
