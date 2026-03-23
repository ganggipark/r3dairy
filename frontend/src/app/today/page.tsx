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
import DailyMarkdown from '@/components/DailyMarkdown'
import RecipientSelector from '@/components/RecipientSelector'

export default function TodayPage() {
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')

  // 콘텐츠 상태
  const [dailyContent, setDailyContent] = useState<DailyContentResponse | null>(null)
  const [selectedRole, setSelectedRole] = useState<Role | null>(null)
  const [userRoles, setUserRoles] = useState<Role[]>([])
  const [selectedRecipientId, setSelectedRecipientId] = useState<string | null>(null)
  const [viewMode, setViewMode] = useState<'standard' | 'markdown'>('standard')
  const [hasDiaryPeriod, setHasDiaryPeriod] = useState(false)

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

  // 토큰 갱신 후 유효한 토큰 반환
  const getValidToken = (): string | null => {
    const token = localStorage.getItem('access_token')
    if (!token) {
      router.push('/login')
      return null
    }
    return token
  }

  // 토큰 갱신
  const refreshAccessToken = async (): Promise<string | null> => {
    const refreshToken = localStorage.getItem('refresh_token')
    if (!refreshToken) {
      router.push('/login')
      return null
    }
    try {
      const response = await api.auth.refreshToken(refreshToken)
      if (response.access_token) {
        localStorage.setItem('access_token', response.access_token)
        if (response.refresh_token) {
          localStorage.setItem('refresh_token', response.refresh_token)
        }
        return response.access_token
      }
    } catch (err) {
      console.error('토큰 갱신 실패:', err)
    }
    router.push('/login')
    return null
  }

  // 초기 데이터 로드
  useEffect(() => {
    const loadData = async () => {
      let token = localStorage.getItem('access_token')
      if (!token) {
        router.push('/login')
        return
      }

      try {
        // 프로필에서 역할 정보 가져오기
        let roles: Role[] = [Role.STUDENT]
        let profileData = null

        try {
          profileData = await api.profile.get(token)
          console.log('[DEBUG] Profile loaded:', profileData)
          if (profileData && profileData.roles) {
            roles = profileData.roles
          }
          if (profileData?.preferences?.diary_period) {
            setHasDiaryPeriod(true)
          }
        } catch (err: any) { // TODO: type this — use unknown with type guard
          console.error('[ERROR] Profile load failed:', err)
          if (err.status === 401) {
            // 토큰 만료 → 갱신 시도
            const newToken = await refreshAccessToken()
            if (!newToken) return
            token = newToken
            try {
              profileData = await api.profile.get(token)
              console.log('[DEBUG] Profile loaded after refresh:', profileData)
              if (profileData && profileData.roles) roles = profileData.roles
            } catch (retryErr) {
              console.error('[ERROR] Profile load failed after refresh:', retryErr)
            }
          } else if (err.status === 404) {
            // 프로필이 없음 - 사용자를 프로필 생성 페이지로 리다이렉트
            setError('프로필이 존재하지 않습니다. 프로필을 먼저 생성해주세요.')
            setIsLoading(false)
            setTimeout(() => router.push('/profile'), 2000)
            return
          } else {
            console.warn('프로필 로드 실패, 기본값 사용:', err)
          }
        }

        // 프로필 확인
        if (!profileData) {
          setError('프로필 정보를 불러올 수 없습니다.')
          setIsLoading(false)
          return
        }

        setUserRoles(roles)
        setSelectedRole(roles[0])

        // 일간 콘텐츠 로드 (목업 데이터 사용 금지 - 실제 API만 사용)
        let content
        try {
          console.log('[DEBUG] Fetching daily content for:', today, 'role:', roles[0])
          content = await api.daily.getContent(token, today, roles[0], selectedRecipientId)
          console.log('[DEBUG] Daily content response:', {
            date: content.date,
            role: content.role,
            hasContent: !!content.content,
            hasFourPillars: !!(content.content as any)?.fourPillars,
            hasGyeokGuk: !!(content.content as any)?.gyeokGuk,
            summary: content.content?.summary?.substring(0, 50)
          })
        } catch (err: any) { // TODO: type this — use unknown with type guard
          console.error('[ERROR] Daily content load failed:', err)
          if (err.status === 401) {
            const newToken = await refreshAccessToken()
            if (!newToken) return
            token = newToken
            try {
              content = await api.daily.getContent(token, today, roles[0], selectedRecipientId)
              console.log('[DEBUG] Daily content loaded after refresh')
            } catch (retryErr) {
              console.error('[ERROR] Daily content failed after refresh:', retryErr)
              throw retryErr
            }
          } else {
            throw err
          }
        }

        // 콘텐츠 검증
        if (!content || !content.content) {
          setError('일간 콘텐츠를 생성하는데 실패했습니다.')
          setIsLoading(false)
          return
        }

        setDailyContent(content)

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
      } catch (err: any) { // TODO: type this — use unknown with type guard
        console.error('데이터 로드 오류:', err)
        if (err.status === 401) {
          router.push('/login')
        } else {
          setError(err.message || '데이터를 불러오는 데 실패했습니다')
          setIsLoading(false)
        }
      }
    }

    loadData()
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [router, today, selectedRecipientId])

  // 역할 변경 시 콘텐츠 다시 로드
  const handleRoleChange = async (newRole: Role) => {
    const token = localStorage.getItem('access_token')
    if (!token) return

    setSelectedRole(newRole)
    try {
      const content = await api.daily.getContent(token, today, newRole, selectedRecipientId)
      setDailyContent(content)
    } catch (err: any) { // TODO: type this — use unknown with type guard
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
    } catch (err: any) { // TODO: type this — use unknown with type guard
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

  // Markdown 뷰 렌더링
  if (viewMode === 'markdown') {
    return <DailyMarkdown date={today} />
  }

  return (
    <div className="min-h-screen bg-gray-50 print:bg-white">
      {/* 헤더 (인쇄 시 숨김) */}
      <header className="bg-white shadow-sm border-b print:hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 sm:gap-0">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">오늘의 리듬</h1>
              <p className="text-sm text-gray-600 mt-1">{today}</p>
            </div>

            <div className="flex flex-wrap gap-2 sm:gap-3">
              {/* 뷰 모드 토글 */}
              <div className="flex gap-2 sm:border-r sm:pr-3">
                <Button
                  onClick={() => setViewMode('standard')}
                  variant={viewMode === 'standard' ? 'default' : 'outline'}
                  size="sm"
                >
                  표준 뷰
                </Button>
                <Button
                  onClick={() => setViewMode('markdown')}
                  variant={(viewMode as string) === 'markdown' ? 'default' : 'outline'}
                  size="sm"
                >
                  Markdown
                </Button>
              </div>

              {/* 기간별 인쇄 버튼 */}
              {hasDiaryPeriod && (
                <div className="hidden md:flex items-center gap-2 print:hidden">
                  <Button
                    onClick={() => router.push('/diary-print')}
                    variant="outline"
                    size="sm"
                  >
                    기간별 인쇄
                  </Button>
                </div>
              )}

              {/* 수신자 선택 */}
              <RecipientSelector
                value={selectedRecipientId}
                onChange={setSelectedRecipientId}
                className="w-48"
              />

              {/* 역할 선택 */}
              {userRoles.length > 1 && (
                <div className="flex gap-2">
                  {userRoles.map(role => (
                    <Button
                      key={role}
                      onClick={() => handleRoleChange(role)}
                      variant={selectedRole === role ? "default" : "outline"}
                      size="sm"
                    >
                      {role === Role.STUDENT ? '학생' : role === Role.OFFICE_WORKER ? '직장인' : '프리랜서'}
                    </Button>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* 메인 콘텐츠: WYSIWYG 좌우 레이아웃 — 화면 그대로 인쇄 */}
      <main className="max-w-7xl mx-auto px-3 sm:px-4 md:px-6 lg:px-8 py-8 print:max-w-none print:p-0 print:m-0">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-5 lg:gap-6 print:block">
          {/* 좌측: 오늘의 안내 */}
          <div className="w-full h-full min-h-0 md:min-h-[600px] lg:min-h-[900px] print-page">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 h-full print:shadow-none print:border print:border-gray-300 print-card">
              {/* 제목 */}
              <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border-b border-gray-200 px-6 py-3 print:bg-white print:border-b-2 print:border-gray-800">
                <h2 className="text-xl font-bold text-gray-900">오늘의 안내</h2>
              </div>

              <div className="p-3 sm:p-4 space-y-2 sm:space-y-3 print:p-3 print:space-y-2 flex flex-col h-full">
                {/* 요약 */}
                <section className="pb-2 border-b border-gray-100 print:border-gray-300">
                  <h3 className="text-sm sm:text-base font-semibold text-gray-800 mb-2 print:text-sm">요약</h3>
                  <p className="text-sm text-gray-700 leading-relaxed print:text-xs">{content.summary}</p>
                </section>

                {/* 키워드 */}
                <section className="pb-2 border-b border-gray-100 print:border-gray-300">
                  <h3 className="text-sm sm:text-base font-semibold text-gray-800 mb-2 print:text-sm">키워드</h3>
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
                <section className="pb-2 border-b border-gray-100 print:border-gray-300">
                  <h3 className="text-sm sm:text-base font-semibold text-gray-800 mb-2 print:text-sm">리듬 해설</h3>
                  <p className="text-sm text-gray-700 whitespace-pre-line leading-relaxed print:text-xs">{content.rhythm_description}</p>
                </section>

              {/* 집중/주의 포인트 */}
              <section className="pb-2 border-b border-gray-100 print:border-gray-300">
                <h3 className="text-sm sm:text-base font-semibold text-gray-800 mb-2 print:text-sm">집중/주의 포인트</h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 sm:gap-4 print:gap-2">
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
              <section className="pb-2 border-b border-gray-100 print:border-gray-300">
                <h3 className="text-sm sm:text-base font-semibold text-gray-800 mb-2 print:text-sm">행동 가이드</h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 sm:gap-4 print:gap-2">
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
              {content.time_direction && (
                <section className="pb-2 border-b border-gray-100 print:border-gray-300">
                  <h3 className="text-xs sm:text-sm font-semibold text-gray-800 mb-1 print:text-xs">시간/방향</h3>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-1 sm:gap-2 text-xs text-gray-700 print:text-[10px]">
                    <p><span className="font-medium">좋은 시간:</span> {content.time_direction.good_time}</p>
                    <p><span className="font-medium">피할 시간:</span> {content.time_direction.avoid_time}</p>
                    <p><span className="font-medium">좋은 방향:</span> {content.time_direction.good_direction}</p>
                  </div>
                </section>
              )}

              {/* 라이프스타일 블록 - 2컬럼 그리드 */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 sm:gap-3 pb-3 border-b border-gray-100 print:border-gray-300">
                {(content as any).daily_health_sports && (
                  <section className="pb-2">
                    <h3 className="text-sm font-semibold text-gray-800 mb-1 print:text-xs">🏃 건강/운동</h3>
                    <div className="text-xs text-gray-700 space-y-0.5 print:text-[10px]">
                      <p><span className="font-medium">추천:</span> {(content as any).daily_health_sports.recommended_activities.join(', ')}</p>
                      <p><span className="font-medium">팁:</span> {(content as any).daily_health_sports.health_tips.join(', ')}</p>
                    </div>
                  </section>
                )}

                {(content as any).daily_meal_nutrition && (
                  <section className="pb-2">
                    <h3 className="text-sm font-semibold text-gray-800 mb-1 print:text-xs">🍽️ 음식/영양</h3>
                    <div className="text-xs text-gray-700 space-y-0.5 print:text-[10px]">
                      <p><span className="font-medium">권장:</span> {(content as any).daily_meal_nutrition.recommended_foods.join(', ')}</p>
                      <p><span className="font-medium">피하기:</span> {(content as any).daily_meal_nutrition.avoid_foods.join(', ')}</p>
                    </div>
                  </section>
                )}

                {(content as any).daily_fashion_beauty && (
                  <section className="pb-2">
                    <h3 className="text-sm font-semibold text-gray-800 mb-1 print:text-xs">👔 패션/뷰티</h3>
                    <div className="text-xs text-gray-700 space-y-0.5 print:text-[10px]">
                      <p><span className="font-medium">색상:</span> {(content as any).daily_fashion_beauty.color_suggestions.join(', ')}</p>
                      <p><span className="font-medium">스타일:</span> {(content as any).daily_fashion_beauty.clothing_style.join(', ')}</p>
                    </div>
                  </section>
                )}

                {(content as any).daily_shopping_finance && (
                  <section className="pb-2">
                    <h3 className="text-sm font-semibold text-gray-800 mb-1 print:text-xs">💰 쇼핑/금융</h3>
                    <div className="text-xs text-gray-700 space-y-0.5 print:text-[10px]">
                      <p><span className="font-medium">구매:</span> {(content as any).daily_shopping_finance.good_to_buy.join(', ')}</p>
                      <p><span className="font-medium">조언:</span> {(content as any).daily_shopping_finance.finance_advice.join(', ')}</p>
                    </div>
                  </section>
                )}

                {(content as any).daily_living_space && (
                  <section className="pb-2">
                    <h3 className="text-sm font-semibold text-gray-800 mb-1 print:text-xs">🏡 생활 공간</h3>
                    <div className="text-xs text-gray-700 space-y-0.5 print:text-[10px]">
                      <p><span className="font-medium">정리:</span> {(content as any).daily_living_space.space_organization.join(', ')}</p>
                      <p><span className="font-medium">환경:</span> {(content as any).daily_living_space.environmental_tips.join(', ')}</p>
                    </div>
                  </section>
                )}

                {(content as any).daily_routines && (
                  <section className="pb-2">
                    <h3 className="text-sm font-semibold text-gray-800 mb-1 print:text-xs">⏰ 일상 루틴</h3>
                    <div className="text-xs text-gray-700 space-y-0.5 print:text-[10px]">
                      <p><span className="font-medium">아침:</span> {(content as any).daily_routines.morning_routine.join(', ')}</p>
                      <p><span className="font-medium">저녁:</span> {(content as any).daily_routines.evening_routine.join(', ')}</p>
                    </div>
                  </section>
                )}

                {(content as any).digital_communication && (
                  <section className="pb-2">
                    <h3 className="text-sm font-semibold text-gray-800 mb-1 print:text-xs">📱 디지털 소통</h3>
                    <div className="text-xs text-gray-700 space-y-0.5 print:text-[10px]">
                      <p><span className="font-medium">기기:</span> {(content as any).digital_communication.device_usage.join(', ')}</p>
                      <p><span className="font-medium">SNS:</span> {(content as any).digital_communication.social_media.join(', ')}</p>
                    </div>
                  </section>
                )}

                {(content as any).hobbies_creativity && (
                  <section className="pb-2">
                    <h3 className="text-sm font-semibold text-gray-800 mb-1 print:text-xs">🎨 취미/창작</h3>
                    <div className="text-xs text-gray-700 space-y-0.5 print:text-[10px]">
                      <p><span className="font-medium">창작:</span> {(content as any).hobbies_creativity.creative_activities.join(', ')}</p>
                      <p><span className="font-medium">학습:</span> {(content as any).hobbies_creativity.learning_recommendations.join(', ')}</p>
                    </div>
                  </section>
                )}

                {(content as any).relationships_social && (
                  <section className="pb-2">
                    <h3 className="text-sm font-semibold text-gray-800 mb-1 print:text-xs">👥 관계/사회</h3>
                    <div className="text-xs text-gray-700 space-y-0.5 print:text-[10px]">
                      <p><span className="font-medium">소통:</span> {(content as any).relationships_social.communication_style.join(', ')}</p>
                      <p><span className="font-medium">팁:</span> {(content as any).relationships_social.relationship_tips.join(', ')}</p>
                    </div>
                  </section>
                )}

                {(content as any).seasonal_environment && (
                  <section className="pb-2">
                    <h3 className="text-sm font-semibold text-gray-800 mb-1 print:text-xs">🌤️ 계절/환경</h3>
                    <div className="text-xs text-gray-700 space-y-0.5 print:text-[10px]">
                      <p><span className="font-medium">날씨:</span> {(content as any).seasonal_environment.weather_adaptation.join(', ')}</p>
                      <p><span className="font-medium">활동:</span> {(content as any).seasonal_environment.seasonal_activities.join(', ')}</p>
                    </div>
                  </section>
                )}
              </div>

              {/* === NLP 섹션 (가장 아래) === */}
              <div className="pt-4 mt-4 border-t-2 border-gray-300">
                <h3 className="text-xs font-bold text-purple-700 mb-2 print:text-[10px]">🧠 마음 설계</h3>

                {/* 앵커링 (상태 전환 트리거) */}
                <section className="pb-2 border-b border-gray-100 print:border-gray-300 mb-2">
                  <h4 className="text-xs font-semibold text-gray-800 mb-1 print:text-[10px]">앵커링 <span className="font-normal text-gray-500">(상태 전환 스위치)</span></h4>
                  <div className="space-y-0.5 text-xs text-gray-700 print:text-[10px]">
                    <p><span className="font-medium">제스처:</span> {content.state_trigger.gesture}</p>
                    <p><span className="font-medium">문구:</span> {content.state_trigger.phrase}</p>
                    <p><span className="font-medium">방법:</span> {content.state_trigger.how_to}</p>
                  </div>
                </section>

                {/* 리프레이밍 (의미 전환) */}
                <section className="pb-2 border-b border-gray-100 print:border-gray-300 mb-2">
                  <h4 className="text-xs font-semibold text-gray-800 mb-1 print:text-[10px]">리프레이밍 <span className="font-normal text-gray-500">(상황 재해석)</span></h4>
                  <p className="text-xs text-gray-700 whitespace-pre-line print:text-[10px]">{content.meaning_shift}</p>
                </section>

                {/* 메타 질문 (리듬 질문) */}
                <section>
                  <h4 className="text-xs font-semibold text-gray-800 mb-1 print:text-[10px]">메타 질문 <span className="font-normal text-gray-500">(관점 전환)</span></h4>
                  <p className="text-xs text-gray-700 italic print:text-[10px]">{content.rhythm_question}</p>
                </section>
              </div>
              </div>
            </div>
          </div>

          {/* 우측: 사용자 기록 (시간 그리드 포함) */}
          <div className="w-full h-full min-h-0 md:min-h-[600px] lg:min-h-[900px] print-page">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 h-full print:shadow-none print:border print:border-gray-300 print-card">
              {/* 제목 */}
              <div className="bg-gradient-to-r from-green-50 to-emerald-50 border-b border-gray-200 px-3 sm:px-4 lg:px-6 py-2 sm:py-3 print:bg-white print:border-b-2 print:border-gray-800">
                <h2 className="text-xl font-bold text-gray-900">오늘의 기록</h2>
              </div>

              <div className="p-3 sm:p-4 lg:p-6 space-y-3 sm:space-y-4 print:p-4 print:space-y-3 flex flex-col h-full">
                {/* 시간대별 그리드 (30분 단위) */}
                <div className="print:mb-3 print:max-h-[200px] print:overflow-hidden">
                  <TimeGrid
                    schedule={logForm.schedule}
                    height="full"
                    goodTime={content.time_direction.good_time}
                    avoidTime={content.time_direction.avoid_time}
                    qimenSlots={dailyContent?.qimen_slots}
                    bestDirection={dailyContent?.best_direction}
                    avoidDirection={dailyContent?.avoid_direction}
                  />
                </div>

                {/* 기분/에너지 (인쇄 시 간소화) */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4 print:gap-2 print:hidden">
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

                {/* 오늘의 기록 - 자유 기록 공간 */}
                <div className="flex-1 flex flex-col gap-3">
                  {/* 메모 - 크게 */}
                  <div className="flex-1">
                    <label className="block text-sm font-medium text-gray-700 mb-1 print:text-xs">
                      오늘의 기록
                    </label>
                    <textarea
                      value={logForm.notes}
                      onChange={e => setLogForm({ ...logForm, notes: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 text-sm print:text-xs resize-none min-h-[100px] sm:min-h-[120px] lg:min-h-[150px] print:min-h-[120px]"
                      placeholder="오늘 하루를 되돌아보며 자유롭게 기록하세요"
                    />
                  </div>

                  {/* 오늘의 할 일 */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1 print:text-xs">
                      오늘의 할 일
                    </label>
                    <div className="border border-gray-300 rounded-md p-2 print:min-h-[100px]">
                      {[1,2,3,4,5].map(i => (
                        <div key={i} className="flex items-center gap-2 py-1 border-b border-gray-100 last:border-0">
                          <div className="w-4 h-4 border border-gray-400 rounded-sm flex-shrink-0 print:border-gray-500"></div>
                          <div className="flex-1 h-5 border-b border-dashed border-gray-300 print:border-gray-400"></div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* 감사한 일 */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1 print:text-xs">
                      감사한 일
                    </label>
                    <textarea
                      value={logForm.gratitude}
                      onChange={e => setLogForm({ ...logForm, gratitude: e.target.value })}
                      rows={3}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 text-sm print:text-xs print:min-h-[80px]"
                      placeholder="오늘 감사한 일이 있나요?"
                    />
                  </div>

                  {/* 오늘의 한 줄 */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1 print:text-xs">
                      오늘의 한 줄
                    </label>
                    <div className="border-b-2 border-gray-400 py-2 print:min-h-[32px]">
                      <input
                        type="text"
                        className="w-full border-none outline-none text-sm print:text-xs bg-transparent"
                        placeholder="오늘을 한 문장으로..."
                      />
                    </div>
                  </div>
                </div>

                {/* 저장 버튼 (인쇄 시 숨김) */}
                <div className="print:hidden sticky bottom-0 sm:static bg-white sm:bg-transparent py-3 sm:py-0 border-t sm:border-0">
                  <Button
                    onClick={handleSaveLog}
                    disabled={isSavingLog}
                    className="w-full"
                  >
                    {isSavingLog ? '저장 중...' : '기록 저장'}
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* 인쇄용 CSS — WYSIWYG: 화면 레이아웃 그대로 인쇄 */}
      <style jsx global>{`
        @media print {
          @page {
            size: A4;
            margin: 8mm;
          }

          body {
            margin: 0;
            padding: 0;
            print-color-adjust: exact;
            -webkit-print-color-adjust: exact;
          }

          /* 헤더 및 인터랙티브 요소 숨김 */
          header, .no-print, .print\\:hidden { display: none !important; }

          /* 각 패널을 독립 페이지로 분리 */
          .print-page {
            page-break-after: always;
            break-after: page;
            page-break-inside: avoid;
            break-inside: avoid;
          }
          .print-page:last-child {
            page-break-after: auto;
            break-after: auto;
          }

          /* 그리드를 블록으로 전환 (각 컬럼이 별도 페이지) */
          main > div { display: block !important; }

          /* 카드 스타일 인쇄 최적화 */
          .print-card {
            box-shadow: none !important;
            border: 1px solid #d1d5db !important;
          }

          main { padding: 0 !important; margin: 0 !important; max-width: none !important; }
        }
      `}</style>
    </div>
  )
}
