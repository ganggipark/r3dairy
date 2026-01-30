'use client'

/**
 * Today Page
 * 일간 콘텐츠 + 사용자 기록 페이지 (좌/우 레이아웃)
 * 인쇄 친화적 디자인 (A4 규격)
 */

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { api } from '@/lib/api'
import type { DailyContentResponse, DailyLog, DailyLogCreate, DailyLogUpdate, Role as RoleType } from '@/types'
import { Role } from '@/types'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import TimeGrid from '@/components/TimeGrid'

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
  const today = new Date().toISOString().split('T')[0];

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
        let roles: Role[] = [Role.STUDENT]

        try {
          const profile = await api.profile.get(token)
          if (profile && profile.roles) {
            roles = profile.roles
          }
        } catch (err) {
          // API 실패 시 기본 역할 사용
          console.warn('프로필 로드 실패, 기본값 사용:', err)
        }

        setUserRoles(roles)
        setSelectedRole(roles[0])

        // 일간 콘텐츠 로드
        let content: DailyContentResponse | null = null
        try {
          content = await api.daily.getContent(token, today, roles[0])
        } catch (err) {
          // API 실패 시 mock 데이터 사용
          console.warn('콘텐츠 로드 실패, 데모 데이터 사용:', err)
          content = {
            date: today,
            role: roles[0],
            content: {
              summary: '오늘은 차분한 에너지가 흐르는 날입니다. 겨울의 에너지, 신강 상태을 경험하게 됩니다.',
              keywords: ['휴식', '집중', '업무', '관계', '소통', '실행', '결단', '기회'],
              rhythm_description: '오늘의 흐름은 \'겨울의 에너지, 신강 상태\'으로 요약됩니다. 에너지가 차분하게 흐르므로 충분한 휴식과 재충전이 필요합니다. 집중력이 뛰어나 깊은 사고와 업무에 유리한 시간입니다. 사람들과의 교류가 활발해질 수 있으니 소통의 기회를 적극 활용하세요. 결단력이 강화되어 중요한 선택이나 실행에 적합한 날입니다. 오늘은 자신의 페이스를 존중하는 것이 중요합니다. 외부의 기대나 속도에 맞추려 하기보다, 내면의 리듬에 귀 기울여보세요. 작은 성취를 하나씩 쌓아가는 것이 오늘의 가장 현명한 전략입니다.',
              focus_caution: {
                focus: ['중요한 작업에 대한 깊은 집중', '관계 형성과 네트워킹', '결정이 필요한 사안의 처리'],
                caution: ['무리한 활동으로 인한 피로 누적']
              },
              action_guide: {
                do: ['충분한 휴식 취하기', '내면 성찰과 기록', '가벼운 정리 활동'],
                avoid: ['과도한 일정 잡기', '중요한 결정 서두르기', '무리한 약속']
              },
              time_direction: {
                good_time: '오전 10-12시, 오후 3-5시',
                avoid_time: '자정 전후',
                good_direction: '중앙, 서쪽',
                avoid_direction: '특별히 피할 방향 없음',
                notes: '오늘은 오전 10-12시, 오후 3-5시에 집중력과 효율이 높아집니다. 가능하다면 중앙, 서쪽 방향으로의 활동이나 이동을 고려해보세요. 자정 전후에는 중요한 일을 피하는 것이 좋습니다.'
              },
              state_trigger: {
                gesture: '어깨를 가볍게 으쓱이며 긴장 풀기',
                phrase: '"충분한 휴식이 나를 채운다"',
                how_to: '에너지가 낮게 느껴질 때, 의자에 앉아 어깨를 천천히 으쓱이며 긴장을 풀어주세요. 이 동작과 함께 \'휴식도 생산적인 활동이다\'라는 인식을 상기하면 불필요한 죄책감을 내려놓을 수 있습니다.'
              },
              meaning_shift: '에너지가 낮다는 것은 무능력이 아니라, 충전이 필요한 자연스러운 신호입니다. 휴식을 선택하는 것도 자기 돌봄의 적극적 행동입니다. 지금 이 순간 쉬어가는 것이 내일의 나를 위한 가장 현명한 투자라는 점을 기억하세요.',
              rhythm_question: '지금 나에게 필요한 휴식의 형태는 무엇일까요?'
            }
          }
        }

        if (content) {
          setDailyContent(content)
        }

        // 기존 기록 로드 (있으면)
        try {
          const existingLog = await api.logs.get(token, today)
          if (existingLog) {
            setLog(existingLog)
            setLogForm({
              schedule: existingLog.schedule || '',
              todos: existingLog.todos || [],
              mood: existingLog.mood || 0,
              energy: existingLog.energy || 0,
              notes: existingLog.notes || '',
              gratitude: existingLog.gratitude || ''
            })
          }
        } catch (err) {
          // 기록이 없으면 빈 폼 유지
          console.warn('기록 로드 실패:', err)
        }

        setIsLoading(false)
      } catch (err: any) {
        console.error('데이터 로드 오류:', err)
        setError(err.message || '데이터를 불러오는 데 실패했습니다')
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

  const content = dailyContent.content;

  return (
    <div className="min-h-screen bg-gray-50 print:bg-white">
      {/* 헤더 (인쇄 시 숨김) */}
      <header className="bg-white shadow-sm border-b print:hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">오늘의 리듬</h1>
              <p className="text-sm text-gray-600 mt-1">{today}</p>
            </div>

            {/* 역할 선택 */}
            {userRoles.length > 1 && (
              <div className="flex gap-2">
                {userRoles.map(role => (
                  <Button
                    key={role}
                    onClick={() => handleRoleChange(role)}
                    variant={selectedRole === role ? "default" : "outline"}
                  >
                    {role === Role.STUDENT ? '학생' : role === Role.OFFICE_WORKER ? '직장인' : '프리랜서'}
                  </Button>
                ))}
              </div>
            )}
          </div>
        </div>
      </header>

      {/* 메인 콘텐츠: 좌우 레이아웃 (A4 인쇄 규격) */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 print:max-w-none print:p-0">
        {/* 인쇄용 헤더 */}
        <div className="hidden print:block mb-4 border-b-2 border-gray-800 pb-2">
          <h1 className="text-2xl font-bold text-gray-900">오늘의 리듬</h1>
          <p className="text-sm text-gray-600">{today}</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 print:grid-cols-2 print:gap-4">
          {/* 좌측: 오늘의 안내 */}
          <div className="space-y-4 print:w-[210mm] print:min-h-[297mm] print:p-4 print:border print:border-gray-300">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 print:shadow-none print:border-none">
              {/* 제목 */}
              <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border-b border-gray-200 px-6 py-3 print:bg-white print:border-b-2 print:border-gray-800">
                <h2 className="text-xl font-bold text-gray-900">오늘의 안내</h2>
              </div>

              <div className="p-6 space-y-4 print:p-4 print:space-y-3">
                {/* 요약 */}
                <section className="pb-3 border-b border-gray-100 print:border-gray-300">
                  <h3 className="text-base font-semibold text-gray-800 mb-2 print:text-sm">요약</h3>
                  <p className="text-sm text-gray-700 leading-relaxed print:text-xs">{content.summary}</p>
                </section>

                {/* 키워드 */}
                <section className="pb-3 border-b border-gray-100 print:border-gray-300">
                  <h3 className="text-base font-semibold text-gray-800 mb-2 print:text-sm">키워드</h3>
                  <div className="flex flex-wrap gap-2">
                    {content.keywords.map((keyword, index) => (
                      <span
                        key={index}
                        className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-medium print:px-2 print:py-0.5 print:bg-gray-100 print:text-gray-800 print:border print:border-gray-300"
                      >
                        {keyword}
                      </span>
                    ))}
                  </div>
                </section>

                {/* 리듬 해설 */}
                <section className="pb-3 border-b border-gray-100 print:border-gray-300">
                  <h3 className="text-base font-semibold text-gray-800 mb-2 print:text-sm">리듬 해설</h3>
                  <p className="text-sm text-gray-700 whitespace-pre-line leading-relaxed print:text-xs">{content.rhythm_description}</p>
                </section>

              {/* 집중/주의 포인트 */}
              <section className="pb-3 border-b border-gray-100 print:border-gray-300">
                <h3 className="text-base font-semibold text-gray-800 mb-2 print:text-sm">집중/주의 포인트</h3>
                <div className="grid grid-cols-2 gap-4 print:gap-2">
                  <div>
                    <h4 className="text-sm font-medium text-green-700 mb-1 print:text-xs">집중</h4>
                    <ul className="list-disc list-inside text-xs text-gray-700 space-y-0.5 print:text-[10px]">
                      {content.focus_caution.focus.map((item, index) => (
                        <li key={index}>{item}</li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <h4 className="text-sm font-medium text-red-700 mb-1 print:text-xs">주의</h4>
                    <ul className="list-disc list-inside text-xs text-gray-700 space-y-0.5 print:text-[10px]">
                      {content.focus_caution.caution.map((item, index) => (
                        <li key={index}>{item}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              </section>

              {/* 행동 가이드 */}
              <section className="pb-3 border-b border-gray-100 print:border-gray-300">
                <h3 className="text-base font-semibold text-gray-800 mb-2 print:text-sm">행동 가이드</h3>
                <div className="grid grid-cols-2 gap-4 print:gap-2">
                  <div>
                    <h4 className="text-sm font-medium text-green-700 mb-1 print:text-xs">권장</h4>
                    <ul className="list-disc list-inside text-xs text-gray-700 space-y-0.5 print:text-[10px]">
                      {content.action_guide.do.map((item, index) => (
                        <li key={index}>{item}</li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <h4 className="text-sm font-medium text-red-700 mb-1 print:text-xs">지양</h4>
                    <ul className="list-disc list-inside text-xs text-gray-700 space-y-0.5 print:text-[10px]">
                      {content.action_guide.avoid.map((item, index) => (
                        <li key={index}>{item}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              </section>

              {/* 시간/방향 */}
              <section className="pb-3 border-b border-gray-100 print:border-gray-300">
                <h3 className="text-base font-semibold text-gray-800 mb-2 print:text-sm">시간/방향</h3>
                <div className="space-y-1 text-xs text-gray-700 print:text-[10px]">
                  <p><span className="font-medium">좋은 시간:</span> {content.time_direction.good_time}</p>
                  <p><span className="font-medium">피할 시간:</span> {content.time_direction.avoid_time}</p>
                  <p><span className="font-medium">좋은 방향:</span> {content.time_direction.good_direction}</p>
                  <p><span className="font-medium">피할 방향:</span> {content.time_direction.avoid_direction}</p>
                  <p><span className="font-medium">참고:</span> {content.time_direction.notes}</p>
                </div>
              </section>

              {/* 상태 전환 트리거 */}
              <section className="pb-3 border-b border-gray-100 print:border-gray-300">
                <h3 className="text-base font-semibold text-gray-800 mb-2 print:text-sm">상태 전환 트리거</h3>
                <div className="space-y-1 text-xs text-gray-700 print:text-[10px]">
                  <p><span className="font-medium">제스처:</span> {content.state_trigger.gesture}</p>
                  <p><span className="font-medium">문구:</span> {content.state_trigger.phrase}</p>
                  <p><span className="font-medium">방법:</span> {content.state_trigger.how_to}</p>
                </div>
              </section>

              {/* 의미 전환 */}
              <section className="pb-3 border-b border-gray-100 print:border-gray-300">
                <h3 className="text-base font-semibold text-gray-800 mb-2 print:text-sm">의미 전환</h3>
                <p className="text-xs text-gray-700 whitespace-pre-line leading-relaxed print:text-[10px]">{content.meaning_shift}</p>
              </section>

              {/* 리듬 질문 */}
              <section>
                <h3 className="text-base font-semibold text-gray-800 mb-2 print:text-sm">리듬 질문</h3>
                <p className="text-xs text-gray-700 italic print:text-[10px]">{content.rhythm_question}</p>
              </section>
              </div>
            </div>
          </div>

          {/* 우측: 사용자 기록 (시간 그리드 포함) */}
          <div className="space-y-4 print:w-[210mm] print:min-h-[297mm] print:p-4 print:border print:border-gray-300 print:page-break-before">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 print:shadow-none print:border-none">
              {/* 제목 */}
              <div className="bg-gradient-to-r from-green-50 to-emerald-50 border-b border-gray-200 px-6 py-3 print:bg-white print:border-b-2 print:border-gray-800">
                <h2 className="text-xl font-bold text-gray-900">오늘의 기록</h2>
              </div>

              <div className="p-6 space-y-4 print:p-4 print:space-y-3">
                {/* 시간대별 그리드 (30분 단위) */}
                <div className="print:mb-4">
                  <TimeGrid schedule={logForm.schedule} height="full" />
                </div>

                {/* 기분/에너지 (인쇄 시 간소화) */}
                <div className="grid grid-cols-2 gap-4 print:gap-2 print:hidden">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1 print:text-xs">
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
                    <div className="flex justify-between text-xs text-gray-500 mt-1">
                      <span>없음</span>
                      <span>나쁨</span>
                      <span>보통</span>
                      <span>좋음</span>
                      <span>매우 좋음</span>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1 print:text-xs">
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
                    <div className="flex justify-between text-xs text-gray-500 mt-1">
                      <span>없음</span>
                      <span>낮음</span>
                      <span>보통</span>
                      <span>높음</span>
                      <span>매우 높음</span>
                    </div>
                  </div>
                </div>

                {/* 메모 */}
                <div className="print:mt-3">
                  <label className="block text-sm font-medium text-gray-700 mb-1 print:text-xs">
                    메모
                  </label>
                  <textarea
                    value={logForm.notes}
                    onChange={e => setLogForm({ ...logForm, notes: e.target.value })}
                    rows={4}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 text-sm print:text-xs print:min-h-[80px]"
                    placeholder="오늘 하루를 되돌아보며 자유롭게 기록하세요"
                  />
                </div>

                {/* 감사 */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1 print:text-xs">
                    감사한 일
                  </label>
                  <textarea
                    value={logForm.gratitude}
                    onChange={e => setLogForm({ ...logForm, gratitude: e.target.value })}
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 text-sm print:text-xs print:min-h-[60px]"
                    placeholder="오늘 감사한 일이 있나요?"
                  />
                </div>

                {/* 저장 버튼 (인쇄 시 숨김) */}
                <Button
                  onClick={handleSaveLog}
                  disabled={isSavingLog}
                  className="w-full print:hidden"
                >
                  {isSavingLog ? '저장 중...' : '기록 저장'}
                </Button>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* 인쇄용 CSS */}
      <style jsx global>{`
        @media print {
          @page {
            size: A4;
            margin: 10mm;
          }

          body {
            print-color-adjust: exact;
            -webkit-print-color-adjust: exact;
          }

          .print\\:page-break-before {
            page-break-before: always;
          }

          .print\\:w-\\[210mm\\] {
            width: 210mm !important;
          }

          .print\\:min-h-\\[297mm\\] {
            min-height: 297mm !important;
          }
        }
      `}</style>
    </div>
  )
}
