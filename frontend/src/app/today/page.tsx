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

export default function TodayPage() {
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')

  // 콘텐츠 상태
  const [dailyContent, setDailyContent] = useState<DailyContentResponse | null>(null)
  const [selectedRole, setSelectedRole] = useState<Role | null>(null)
  const [userRoles, setUserRoles] = useState<Role[]>([])
  const [viewMode, setViewMode] = useState<'standard' | 'markdown'>('standard')

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

        // 일간 콘텐츠 로드 (목업 데이터 사용 금지 - 실제 API만 사용)
        const content = await api.daily.getContent(token, today, roles[0])
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

  // Markdown 뷰 렌더링
  if (viewMode === 'markdown') {
    return <DailyMarkdown date={today} />
  }

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

            <div className="flex gap-3">
              {/* 뷰 모드 토글 */}
              <div className="flex gap-2 border-r pr-3">
                <Button
                  onClick={() => setViewMode('standard')}
                  variant={viewMode === 'standard' ? 'default' : 'outline'}
                  size="sm"
                >
                  표준 뷰
                </Button>
                <Button
                  onClick={() => setViewMode('markdown')}
                  variant={viewMode === 'markdown' ? 'default' : 'outline'}
                  size="sm"
                >
                  Markdown
                </Button>
              </div>

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

      {/* 메인 콘텐츠: 좌우 레이아웃 (A4 인쇄 규격) */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 print:max-w-none print:p-0">
        {/* 인쇄용 헤더 */}
        <div className="hidden print:block mb-4 border-b-2 border-gray-800 pb-2">
          <h1 className="text-2xl font-bold text-gray-900">오늘의 리듬</h1>
          <p className="text-sm text-gray-600">{today}</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 print:grid-cols-2 print:gap-4">
          {/* 좌측: 오늘의 안내 */}
          <div className="w-full h-full min-h-[900px] print:w-[210mm] print:min-h-[297mm]">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 h-full print:shadow-none print:border print:border-gray-300">
              {/* 제목 */}
              <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border-b border-gray-200 px-6 py-3 print:bg-white print:border-b-2 print:border-gray-800">
                <h2 className="text-xl font-bold text-gray-900">오늘의 안내</h2>
              </div>

              <div className="p-6 space-y-4 print:p-4 print:space-y-3">
                {/* 요약 */}
                <section className="pb-3 border-b border-gray-100 print:border-gray-300">
                  <h3 className="text-base font-semibold text-gray-800 mb-2 print:text-sm">요약</h3>
                  <p className="text-sm text-gray-700 leading-relaxed print:text-xs">{content.summary}</p>
                  <p className="text-[10px] text-gray-400 mt-1 print:hidden">
                    📐 기반: 사주(일간 {dailyContent?.content?.gyeokGuk?.dayMaster || '?'}, {dailyContent?.content?.gyeokGuk?.strength || '?'}) + 십성 분석
                  </p>
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
                  <p className="text-[10px] text-gray-400 mt-1 print:hidden">
                    📐 기반: 십성(용신 {dailyContent?.content?.yongSin?.yongSin?.join(', ') || '?'}) + 오행 균형
                  </p>
                </section>

                {/* 리듬 해설 */}
                <section className="pb-3 border-b border-gray-100 print:border-gray-300">
                  <h3 className="text-base font-semibold text-gray-800 mb-2 print:text-sm">리듬 해설</h3>
                  <p className="text-sm text-gray-700 whitespace-pre-line leading-relaxed print:text-xs">{content.rhythm_description}</p>
                  <p className="text-[10px] text-gray-400 mt-1 print:hidden">
                    📐 기반: 일주({dailyContent?.content?.fourPillars?.day?.gan}{dailyContent?.content?.fourPillars?.day?.ji}) + 월지({dailyContent?.content?.gyeokGuk?.monthBranch}) 상호작용
                  </p>
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
                <p className="text-[10px] text-gray-400 mt-1 print:hidden">
                  📐 기반: 용신(喜) vs 기신(忌) 오행 분류
                </p>
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
                <p className="text-[10px] text-gray-400 mt-1 print:hidden">
                  📐 기반: 십성 분석 + 역할({selectedRole}) 맞춤 번역
                </p>
              </section>

              {/* 라이프스타일 블록 */}
              {content.daily_health_sports && (
                <section className="pb-3 border-b border-gray-100 print:border-gray-300">
                  <h3 className="text-base font-semibold text-gray-800 mb-2 print:text-sm">🏃 건강/운동</h3>
                  <div className="text-xs text-gray-700 space-y-1 print:text-[10px]">
                    <p><span className="font-medium">추천:</span> {content.daily_health_sports.recommended_activities.join(', ')}</p>
                    <p><span className="font-medium">팁:</span> {content.daily_health_sports.health_tips.join(', ')}</p>
                    <p className="text-gray-600">{content.daily_health_sports.explanation}</p>
                  </div>
                  <p className="text-[10px] text-gray-400 mt-1 print:hidden">
                    📐 기반: 오행 균형 + 계절(월지 {dailyContent?.content?.gyeokGuk?.season})
                  </p>
                </section>
              )}

              {content.daily_meal_nutrition && (
                <section className="pb-3 border-b border-gray-100 print:border-gray-300">
                  <h3 className="text-base font-semibold text-gray-800 mb-2 print:text-sm">🍽️ 음식/영양</h3>
                  <div className="text-xs text-gray-700 space-y-1 print:text-[10px]">
                    <p><span className="font-medium">권장:</span> {content.daily_meal_nutrition.recommended_foods.join(', ')}</p>
                    <p><span className="font-medium">피하기:</span> {content.daily_meal_nutrition.avoid_foods.join(', ')}</p>
                    <p className="text-gray-600">{content.daily_meal_nutrition.explanation}</p>
                  </div>
                  <p className="text-[10px] text-gray-400 mt-1 print:hidden">
                    📐 기반: 용신 오행 매핑
                  </p>
                </section>
              )}

              {content.daily_fashion_beauty && (
                <section className="pb-3 border-b border-gray-100 print:border-gray-300">
                  <h3 className="text-base font-semibold text-gray-800 mb-2 print:text-sm">👔 패션/뷰티</h3>
                  <div className="text-xs text-gray-700 space-y-1 print:text-[10px]">
                    <p><span className="font-medium">좋은 색상:</span> {content.daily_fashion_beauty.color_suggestions.join(', ')}</p>
                    <p><span className="font-medium">스타일:</span> {content.daily_fashion_beauty.clothing_style.join(', ')}</p>
                    <p className="text-gray-600">{content.daily_fashion_beauty.explanation}</p>
                  </div>
                  <p className="text-[10px] text-gray-400 mt-1 print:hidden">
                    📐 기반: 오행 → 색상 변환
                  </p>
                </section>
              )}

              {content.daily_shopping_finance && (
                <section className="pb-3 border-b border-gray-100 print:border-gray-300">
                  <h3 className="text-base font-semibold text-gray-800 mb-2 print:text-sm">💰 쇼핑/금융</h3>
                  <div className="text-xs text-gray-700 space-y-1 print:text-[10px]">
                    <p><span className="font-medium">구매:</span> {content.daily_shopping_finance.good_to_buy.join(', ')}</p>
                    <p><span className="font-medium">조언:</span> {content.daily_shopping_finance.finance_advice.join(', ')}</p>
                    <p className="text-gray-600">{content.daily_shopping_finance.explanation}</p>
                  </div>
                  <p className="text-[10px] text-gray-400 mt-1 print:hidden">
                    📐 기반: 재성(財星) 십성 분석 + 용신 오행
                  </p>
                </section>
              )}

              {content.daily_living_space && (
                <section className="pb-3 border-b border-gray-100 print:border-gray-300">
                  <h3 className="text-base font-semibold text-gray-800 mb-2 print:text-sm">🏡 생활 공간</h3>
                  <div className="text-xs text-gray-700 space-y-1 print:text-[10px]">
                    <p><span className="font-medium">정리:</span> {content.daily_living_space.space_organization.join(', ')}</p>
                    <p><span className="font-medium">환경:</span> {content.daily_living_space.environmental_tips.join(', ')}</p>
                    <p className="text-gray-600">{content.daily_living_space.explanation}</p>
                  </div>
                  <p className="text-[10px] text-gray-400 mt-1 print:hidden">
                    📐 기반: 용신 오행 → 방위/공간 배치 + 인성(印星) 분석
                  </p>
                </section>
              )}

              {content.daily_routines && (
                <section className="pb-3 border-b border-gray-100 print:border-gray-300">
                  <h3 className="text-base font-semibold text-gray-800 mb-2 print:text-sm">⏰ 일상 루틴</h3>
                  <div className="text-xs text-gray-700 space-y-1 print:text-[10px]">
                    <p><span className="font-medium">아침:</span> {content.daily_routines.morning_routine.join(', ')}</p>
                    <p><span className="font-medium">저녁:</span> {content.daily_routines.evening_routine.join(', ')}</p>
                    <p className="text-gray-600">{content.daily_routines.explanation}</p>
                  </div>
                  <p className="text-[10px] text-gray-400 mt-1 print:hidden">
                    📐 기반: 일지(日支) 분석 + 시간대별 십이운성
                  </p>
                </section>
              )}

              {content.digital_communication && (
                <section className="pb-3 border-b border-gray-100 print:border-gray-300">
                  <h3 className="text-base font-semibold text-gray-800 mb-2 print:text-sm">📱 디지털 소통</h3>
                  <div className="text-xs text-gray-700 space-y-1 print:text-[10px]">
                    <p><span className="font-medium">기기 사용:</span> {content.digital_communication.device_usage.join(', ')}</p>
                    <p><span className="font-medium">SNS:</span> {content.digital_communication.social_media.join(', ')}</p>
                    <p className="text-gray-600">{content.digital_communication.explanation}</p>
                  </div>
                  <p className="text-[10px] text-gray-400 mt-1 print:hidden">
                    📐 기반: 식상(食傷) + 비겁(比劫) 십성 에너지
                  </p>
                </section>
              )}

              {content.hobbies_creativity && (
                <section className="pb-3 border-b border-gray-100 print:border-gray-300">
                  <h3 className="text-base font-semibold text-gray-800 mb-2 print:text-sm">🎨 취미/창작</h3>
                  <div className="text-xs text-gray-700 space-y-1 print:text-[10px]">
                    <p><span className="font-medium">창작:</span> {content.hobbies_creativity.creative_activities.join(', ')}</p>
                    <p><span className="font-medium">학습:</span> {content.hobbies_creativity.learning_recommendations.join(', ')}</p>
                    <p className="text-gray-600">{content.hobbies_creativity.explanation}</p>
                  </div>
                  <p className="text-[10px] text-gray-400 mt-1 print:hidden">
                    📐 기반: 식상(食傷) 창작력 + 인성(印星) 학습 에너지
                  </p>
                </section>
              )}

              {content.relationships_social && (
                <section className="pb-3 border-b border-gray-100 print:border-gray-300">
                  <h3 className="text-base font-semibold text-gray-800 mb-2 print:text-sm">👥 관계/사회</h3>
                  <div className="text-xs text-gray-700 space-y-1 print:text-[10px]">
                    <p><span className="font-medium">소통:</span> {content.relationships_social.communication_style.join(', ')}</p>
                    <p><span className="font-medium">관계 팁:</span> {content.relationships_social.relationship_tips.join(', ')}</p>
                    <p className="text-gray-600">{content.relationships_social.explanation}</p>
                  </div>
                  <p className="text-[10px] text-gray-400 mt-1 print:hidden">
                    📐 기반: 비겁(比劫) + 관살(官殺) 십성 상호작용
                  </p>
                </section>
              )}

              {content.seasonal_environment && (
                <section className="pb-3 border-b border-gray-100 print:border-gray-300">
                  <h3 className="text-base font-semibold text-gray-800 mb-2 print:text-sm">🌤️ 계절/환경</h3>
                  <div className="text-xs text-gray-700 space-y-1 print:text-[10px]">
                    <p><span className="font-medium">날씨:</span> {content.seasonal_environment.weather_adaptation.join(', ')}</p>
                    <p><span className="font-medium">활동:</span> {content.seasonal_environment.seasonal_activities.join(', ')}</p>
                    <p className="text-gray-600">{content.seasonal_environment.explanation}</p>
                  </div>
                  <p className="text-[10px] text-gray-400 mt-1 print:hidden">
                    📐 기반: 월지({dailyContent?.content?.gyeokGuk?.monthBranch}) 계절 오행 + 대운 흐름
                  </p>
                </section>
              )}

              {/* === NLP 섹션 (가장 아래) === */}
              <div className="pt-4 mt-4 border-t-2 border-gray-300">
                <h3 className="text-sm font-bold text-purple-700 mb-3 print:text-xs">🧠 마음 설계 (NLP)</h3>

                {/* 앵커링 (상태 전환 트리거) */}
                <section className="pb-3 border-b border-gray-100 print:border-gray-300 mb-3">
                  <div className="mb-2">
                    <h4 className="text-sm font-semibold text-gray-800 inline print:text-xs">앵커링</h4>
                    <span className="text-xs text-gray-600 ml-2 print:text-[10px]">(원하는 상태를 즉시 불러오는 스위치)</span>
                  </div>
                  <p className="text-xs text-gray-500 mb-2 italic print:text-[10px]">
                    불안할 때, 긴장될 때 특정 제스처나 문구로 평온한 상태로 전환
                  </p>
                  <div className="space-y-1 text-xs text-gray-700 print:text-[10px]">
                    <p><span className="font-medium">제스처:</span> {content.state_trigger.gesture}</p>
                    <p><span className="font-medium">문구:</span> {content.state_trigger.phrase}</p>
                    <p><span className="font-medium">방법:</span> {content.state_trigger.how_to}</p>
                  </div>
                  <p className="text-[10px] text-gray-400 mt-1 print:hidden">
                    📐 기반: NLP 앵커링 기법 + 오늘의 불안 트리거 감지
                  </p>
                </section>

                {/* 리프레이밍 (의미 전환) */}
                <section className="pb-3 border-b border-gray-100 print:border-gray-300 mb-3">
                  <div className="mb-2">
                    <h4 className="text-sm font-semibold text-gray-800 inline print:text-xs">리프레이밍</h4>
                    <span className="text-xs text-gray-600 ml-2 print:text-[10px]">(같은 상황을 다르게 해석하기)</span>
                  </div>
                  <p className="text-xs text-gray-500 mb-2 italic print:text-[10px]">
                    부정적 상황을 긍정적 의미로 재해석하여 감정 전환
                  </p>
                  <p className="text-xs text-gray-700 whitespace-pre-line leading-relaxed print:text-[10px]">{content.meaning_shift}</p>
                  <p className="text-[10px] text-gray-400 mt-1 print:hidden">
                    📐 기반: NLP 리프레이밍 + 용신/기신 관점 전환
                  </p>
                </section>

                {/* 메타 질문 (리듬 질문) */}
                <section>
                  <div className="mb-2">
                    <h4 className="text-sm font-semibold text-gray-800 inline print:text-xs">메타 질문</h4>
                    <span className="text-xs text-gray-600 ml-2 print:text-[10px]">(생각의 관점을 바꾸는 질문)</span>
                  </div>
                  <p className="text-xs text-gray-500 mb-2 italic print:text-[10px]">
                    자동 반응에서 벗어나 새로운 선택지를 발견하도록 유도
                  </p>
                  <p className="text-xs text-gray-700 italic print:text-[10px]">{content.rhythm_question}</p>
                  <p className="text-[10px] text-gray-400 mt-1 print:hidden">
                    📐 기반: NLP 메타모델 질문 + 오늘의 핵심 십성 과제
                  </p>
                </section>
              </div>
              </div>
            </div>
          </div>

          {/* 우측: 사용자 기록 (시간 그리드 포함) */}
          <div className="w-full h-full min-h-[900px] print:w-[210mm] print:min-h-[297mm] print:page-break-before">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 h-full print:shadow-none print:border print:border-gray-300">
              {/* 제목 */}
              <div className="bg-gradient-to-r from-green-50 to-emerald-50 border-b border-gray-200 px-6 py-3 print:bg-white print:border-b-2 print:border-gray-800">
                <h2 className="text-xl font-bold text-gray-900">오늘의 기록</h2>
              </div>

              <div className="p-6 space-y-4 print:p-4 print:space-y-3">
                {/* 시간대별 그리드 (30분 단위) */}
                <div className="print:mb-4">
                  <TimeGrid
                    schedule={logForm.schedule}
                    height="full"
                    goodTime={content.time_direction.good_time}
                    avoidTime={content.time_direction.avoid_time}
                  />
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
