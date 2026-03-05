'use client'

/**
 * Profile Page
 * 프로필 생성/수정 + 사주 분석 결과 + 다이어리 기간 선택
 * 3단계 스텝 위저드: Step1(기본정보) -> Step2(사주분석결과) -> Step3(다이어리기간)
 */

import { useState, useEffect, useCallback, Suspense } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { api } from '@/lib/api'
import type {
  Profile,
  ProfileCreate,
  ProfileUpdate,
  DiaryPeriod,
  DailyContentResponse,
  DailyContent,
} from '@/types'
import { Gender, Role } from '@/types'

// ---------------------------------------------------------------------------
// Types local to this page
// ---------------------------------------------------------------------------

interface SajuAnalysis {
  fourPillars?: DailyContent['fourPillars']
  gyeokGuk?: DailyContent['gyeokGuk']
  yongSin?: DailyContent['yongSin']
  summary?: string
  keywords?: string[]
  bestDirection?: string
  avoidDirection?: string
}

type Step = 1 | 2 | 3

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** Map strength to recommended diary period */
function getRecommendedPeriod(strength?: string): {
  period: DiaryPeriod
  label: string
  reason: string
} {
  if (!strength) {
    return {
      period: '6months',
      label: '6개월',
      reason: '균형 잡힌 중기 계획이 효과적입니다',
    }
  }

  const s = strength.toLowerCase()

  if (s.includes('강') || s === 'strong') {
    return {
      period: '1year',
      label: '1년',
      reason: '강한 추진력으로 장기 계획에 유리합니다',
    }
  }
  if (s.includes('약') || s === 'weak') {
    return {
      period: '3months',
      label: '3개월',
      reason: '단기 집중이 효과적입니다',
    }
  }

  return {
    period: '6months',
    label: '6개월',
    reason: '균형 잡힌 중기 계획이 효과적입니다',
  }
}

/** Get today as YYYY-MM-DD */
function todayISO(): string {
  return new Date().toISOString().split('T')[0]
}

/** Format a pillar (gan + ji) for display */
function formatPillar(pillar?: {
  heavenlyStem?: string
  earthlyBranch?: string
  gan?: string
  ji?: string
}): string | null {
  if (!pillar) return null
  const gan = pillar.gan || pillar.heavenlyStem || ''
  const ji = pillar.ji || pillar.earthlyBranch || ''
  if (!gan && !ji) return null
  return `${gan}${ji}`
}

const PILLAR_LABELS = ['년주', '월주', '일주', '시주'] as const
const PILLAR_KEYS = ['year', 'month', 'day', 'hour'] as const

// Subtle background colors per pillar position
const PILLAR_BG = [
  'bg-emerald-50 border-emerald-200',
  'bg-sky-50 border-sky-200',
  'bg-amber-50 border-amber-200',
  'bg-rose-50 border-rose-200',
] as const

const PERIOD_OPTIONS: { value: DiaryPeriod; label: string }[] = [
  { value: '3months', label: '3개월' },
  { value: '6months', label: '6개월' },
  { value: '1year', label: '1년' },
  { value: 'custom', label: '직접 설정' },
]

// ---------------------------------------------------------------------------
// Main form component (wrapped in Suspense at export)
// ---------------------------------------------------------------------------

function ProfileForm() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const editMode = searchParams.get('edit') === 'true'

  // UI state
  const [currentStep, setCurrentStep] = useState<Step>(1)
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [isFetchingSaju, setIsFetchingSaju] = useState(false)
  const [error, setError] = useState('')

  // Profile state
  const [isEditMode, setIsEditMode] = useState(false)
  const [existingProfile, setExistingProfile] = useState<Profile | null>(null)
  const [sajuAnalysis, setSajuAnalysis] = useState<SajuAnalysis | null>(null)

  // Form data
  const [formData, setFormData] = useState({
    name: '',
    birth_date: '',
    birth_time: '',
    gender: '' as Gender | '',
    birth_place: '',
    roles: [] as Role[],
    diary_period: '' as DiaryPeriod | '',
    diary_start_date: todayISO(),
    diary_end_date: '',
    preferences: {} as Record<string, unknown>,
  })

  // -------------------------------------------------------------------------
  // Load existing profile
  // -------------------------------------------------------------------------

  useEffect(() => {
    const loadProfile = async () => {
      const token = localStorage.getItem('access_token')
      if (!token) {
        router.push('/login')
        return
      }

      try {
        const profile = await api.profile.get(token)

        if (editMode) {
          // Edit mode: populate form + show all steps
          setExistingProfile(profile)
          setIsEditMode(true)
          setFormData({
            name: profile.name || '',
            birth_date: profile.birth_date || '',
            birth_time: profile.birth_time || '',
            gender: (profile.gender as Gender) || '',
            birth_place: profile.birth_place || '',
            roles: (profile.roles as Role[]) || [],
            diary_period:
              (profile.preferences?.diary_period as DiaryPeriod) || '',
            diary_start_date:
              (profile.preferences?.diary_start_date as string) || todayISO(),
            diary_end_date:
              (profile.preferences?.diary_end_date as string) || '',
            preferences: profile.preferences || {},
          })

          // In edit mode, also try to fetch saju data to show steps 2+3
          await fetchSajuAnalysis(
            token,
            (profile.roles as Role[]) || [Role.STUDENT],
          )
          // Show step 1 for editing, but all sections visible
          setCurrentStep(1)
          setIsLoading(false)
        } else {
          // Profile already exists, redirect
          router.push('/today')
        }
      } catch (err: unknown) {
        const apiErr = err as { status?: number }
        if (apiErr.status === 404) {
          // No profile - new user creation mode
          setIsEditMode(false)
        } else {
          setError('프로필을 불러오는 데 실패했습니다')
        }
        setIsLoading(false)
      }
    }

    loadProfile()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [router, editMode])

  // -------------------------------------------------------------------------
  // Fetch saju analysis from daily content API
  // -------------------------------------------------------------------------

  const fetchSajuAnalysis = useCallback(
    async (token: string, roles: Role[]) => {
      setIsFetchingSaju(true)
      try {
        const today = todayISO()
        const role = roles.length > 0 ? roles[0] : undefined
        const response: DailyContentResponse = await api.daily.getContent(
          token,
          today,
          role,
        )

        const content = response.content
        const analysis: SajuAnalysis = {
          fourPillars: content.fourPillars,
          gyeokGuk: content.gyeokGuk,
          yongSin: content.yongSin,
          summary: content.summary,
          keywords: content.keywords,
          bestDirection:
            response.best_direction || content.best_direction,
          avoidDirection:
            response.avoid_direction || content.avoid_direction,
        }

        // Only set if we have meaningful data
        const hasMeaningfulData =
          analysis.fourPillars || analysis.gyeokGuk || analysis.yongSin
        if (hasMeaningfulData) {
          setSajuAnalysis(analysis)
        } else if (analysis.summary || analysis.keywords?.length) {
          // Even without pillar data, show summary/keywords
          setSajuAnalysis(analysis)
        }
      } catch {
        // Saju analysis is optional - graceful degradation
        console.warn('사주 분석 데이터를 불러올 수 없습니다')
      } finally {
        setIsFetchingSaju(false)
      }
    },
    [],
  )

  // -------------------------------------------------------------------------
  // Form handlers
  // -------------------------------------------------------------------------

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>,
  ) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    })
  }

  const handleRoleToggle = (role: Role) => {
    const currentRoles = formData.roles
    if (currentRoles.includes(role)) {
      setFormData({
        ...formData,
        roles: currentRoles.filter((r) => r !== role),
      })
    } else {
      setFormData({
        ...formData,
        roles: [...currentRoles, role],
      })
    }
  }

  const validateForm = (): boolean => {
    if (
      !formData.name ||
      !formData.birth_date ||
      !formData.birth_time ||
      !formData.gender ||
      !formData.birth_place
    ) {
      setError('모든 필수 필드를 입력해주세요')
      return false
    }
    if (formData.roles.length === 0) {
      setError('최소 1개 이상의 역할을 선택해주세요')
      return false
    }
    return true
  }

  // -------------------------------------------------------------------------
  // Submit: save profile, then fetch saju, then advance step
  // -------------------------------------------------------------------------

  const handleSubmitStep1 = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (!validateForm()) return

    const token = localStorage.getItem('access_token')
    if (!token) {
      router.push('/login')
      return
    }

    setIsSaving(true)

    try {
      const preferencesPayload = {
        ...formData.preferences,
        ...(formData.diary_period
          ? {
              diary_period: formData.diary_period,
              diary_start_date: formData.diary_start_date,
              ...(formData.diary_period === 'custom' && formData.diary_end_date
                ? { diary_end_date: formData.diary_end_date }
                : {}),
            }
          : {}),
      }

      if (isEditMode) {
        const updateData: ProfileUpdate = {
          name: formData.name,
          birth_date: formData.birth_date,
          birth_time: formData.birth_time,
          gender: formData.gender as Gender,
          birth_place: formData.birth_place,
          roles: formData.roles,
          preferences: preferencesPayload,
        }
        await api.profile.update(token, updateData)
      } else {
        const createData: ProfileCreate = {
          name: formData.name,
          birth_date: formData.birth_date,
          birth_time: formData.birth_time,
          gender: formData.gender as Gender,
          birth_place: formData.birth_place,
          roles: formData.roles,
          preferences: preferencesPayload,
        }
        await api.profile.create(token, createData)
      }

      // After save, fetch saju analysis
      await fetchSajuAnalysis(token, formData.roles)

      // Advance to step 2
      setCurrentStep(2)
    } catch (err: unknown) {
      const apiErr = err as { message?: string }
      setError(apiErr.message || '프로필 저장에 실패했습니다')
    } finally {
      setIsSaving(false)
    }
  }

  // Step 2 -> Step 3
  const handleAdvanceToStep3 = () => {
    // Pre-fill recommended period if analysis available
    if (sajuAnalysis?.gyeokGuk?.strength && !formData.diary_period) {
      const rec = getRecommendedPeriod(sajuAnalysis.gyeokGuk.strength)
      setFormData((prev) => ({ ...prev, diary_period: rec.period }))
    }
    setCurrentStep(3)
  }

  // Step 3 -> save period and go to /today
  const handleSaveDiaryPeriod = async () => {
    const token = localStorage.getItem('access_token')
    if (!token) {
      router.push('/login')
      return
    }

    if (!formData.diary_period) {
      // Skip period selection, go straight to today
      router.push('/today')
      return
    }

    setIsSaving(true)
    try {
      const updateData: ProfileUpdate = {
        preferences: {
          ...formData.preferences,
          diary_period: formData.diary_period,
          diary_start_date: formData.diary_start_date,
          ...(formData.diary_period === 'custom' && formData.diary_end_date
            ? { diary_end_date: formData.diary_end_date }
            : {}),
        },
      }
      await api.profile.update(token, updateData)
      router.push('/today')
    } catch (err: unknown) {
      const apiErr = err as { message?: string }
      setError(apiErr.message || '다이어리 기간 저장에 실패했습니다')
    } finally {
      setIsSaving(false)
    }
  }

  // Skip saju and go to step 3 or today
  const handleSkipToToday = () => {
    router.push('/today')
  }

  // -------------------------------------------------------------------------
  // Computed values
  // -------------------------------------------------------------------------

  const recommendation = sajuAnalysis?.gyeokGuk?.strength
    ? getRecommendedPeriod(sajuAnalysis.gyeokGuk.strength)
    : null

  const computedEndDate = (period: DiaryPeriod | '', startDate: string) => {
    if (!period || period === 'custom' || !startDate) return ''
    const d = new Date(startDate)
    const months =
      period === '3months' ? 3 : period === '6months' ? 6 : 12
    d.setMonth(d.getMonth() + months)
    return d.toISOString().split('T')[0]
  }

  // -------------------------------------------------------------------------
  // Render: loading
  // -------------------------------------------------------------------------

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 border-2 border-gray-300 border-t-gray-800 rounded-full animate-spin" />
          <p className="text-sm text-gray-500">프로필을 불러오는 중...</p>
        </div>
      </div>
    )
  }

  // -------------------------------------------------------------------------
  // Render: Step indicator
  // -------------------------------------------------------------------------

  const stepLabels = ['기본 정보', '나의 분석', '다이어리 기간']

  const renderStepIndicator = () => (
    <div className="flex items-center justify-center gap-1 mb-8" role="navigation" aria-label="프로필 설정 단계">
      {stepLabels.map((label, idx) => {
        const stepNum = (idx + 1) as Step
        const isActive = currentStep === stepNum
        const isCompleted = currentStep > stepNum
        return (
          <div key={label} className="flex items-center">
            {idx > 0 && (
              <div
                className={`w-8 h-px mx-1 transition-colors duration-300 ${
                  isCompleted ? 'bg-gray-800' : 'bg-gray-200'
                }`}
              />
            )}
            <div className="flex flex-col items-center gap-1.5">
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-semibold transition-all duration-300 ${
                  isActive
                    ? 'bg-gray-900 text-white ring-4 ring-gray-900/10'
                    : isCompleted
                      ? 'bg-gray-800 text-white'
                      : 'bg-gray-100 text-gray-400 border border-gray-200'
                }`}
                aria-current={isActive ? 'step' : undefined}
              >
                {isCompleted ? (
                  <svg
                    className="w-4 h-4"
                    viewBox="0 0 20 20"
                    fill="currentColor"
                  >
                    <path
                      fillRule="evenodd"
                      d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                      clipRule="evenodd"
                    />
                  </svg>
                ) : (
                  stepNum
                )}
              </div>
              <span
                className={`text-[11px] font-medium transition-colors duration-300 ${
                  isActive
                    ? 'text-gray-900'
                    : isCompleted
                      ? 'text-gray-600'
                      : 'text-gray-400'
                }`}
              >
                {label}
              </span>
            </div>
          </div>
        )
      })}
    </div>
  )

  // -------------------------------------------------------------------------
  // Render: Step 1 - Basic Info Form
  // -------------------------------------------------------------------------

  const renderStep1 = () => (
    <form onSubmit={handleSubmitStep1} className="space-y-5">
      {/* 이름 */}
      <div>
        <label
          htmlFor="name"
          className="block text-sm font-medium text-gray-700 mb-1"
        >
          이름 *
        </label>
        <input
          type="text"
          id="name"
          name="name"
          required
          value={formData.name}
          onChange={handleChange}
          disabled={isSaving}
          className="block w-full px-3 py-2.5 border border-gray-300 rounded-lg shadow-sm text-sm focus:outline-none focus:ring-2 focus:ring-gray-900/10 focus:border-gray-400 transition-shadow disabled:bg-gray-50 disabled:text-gray-500"
          placeholder="홍길동"
        />
      </div>

      {/* 생년월일 + 출생시간 (한 줄) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label
            htmlFor="birth_date"
            className="block text-sm font-medium text-gray-700 mb-1"
          >
            생년월일 *
          </label>
          <input
            type="date"
            id="birth_date"
            name="birth_date"
            required
            value={formData.birth_date}
            onChange={handleChange}
            disabled={isSaving}
            className="block w-full px-3 py-2.5 border border-gray-300 rounded-lg shadow-sm text-sm focus:outline-none focus:ring-2 focus:ring-gray-900/10 focus:border-gray-400 transition-shadow disabled:bg-gray-50"
          />
        </div>
        <div>
          <label
            htmlFor="birth_time"
            className="block text-sm font-medium text-gray-700 mb-1"
          >
            출생 시간 *
          </label>
          <input
            type="time"
            id="birth_time"
            name="birth_time"
            required
            value={formData.birth_time}
            onChange={handleChange}
            disabled={isSaving}
            className="block w-full px-3 py-2.5 border border-gray-300 rounded-lg shadow-sm text-sm focus:outline-none focus:ring-2 focus:ring-gray-900/10 focus:border-gray-400 transition-shadow disabled:bg-gray-50"
          />
          <p className="mt-1 text-[11px] text-gray-400">
            정확하지 않으면 추정 시간을 입력하세요
          </p>
        </div>
      </div>

      {/* 성별 + 출생장소 */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label
            htmlFor="gender"
            className="block text-sm font-medium text-gray-700 mb-1"
          >
            성별 *
          </label>
          <select
            id="gender"
            name="gender"
            required
            value={formData.gender}
            onChange={handleChange}
            disabled={isSaving}
            className="block w-full px-3 py-2.5 border border-gray-300 rounded-lg shadow-sm text-sm focus:outline-none focus:ring-2 focus:ring-gray-900/10 focus:border-gray-400 transition-shadow disabled:bg-gray-50"
          >
            <option value="">선택</option>
            <option value="male">남성</option>
            <option value="female">여성</option>
          </select>
        </div>
        <div>
          <label
            htmlFor="birth_place"
            className="block text-sm font-medium text-gray-700 mb-1"
          >
            출생 장소 *
          </label>
          <input
            type="text"
            id="birth_place"
            name="birth_place"
            required
            value={formData.birth_place}
            onChange={handleChange}
            disabled={isSaving}
            placeholder="서울특별시"
            className="block w-full px-3 py-2.5 border border-gray-300 rounded-lg shadow-sm text-sm focus:outline-none focus:ring-2 focus:ring-gray-900/10 focus:border-gray-400 transition-shadow disabled:bg-gray-50"
          />
        </div>
      </div>

      {/* 역할 선택 */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          역할 * <span className="font-normal text-gray-400">(복수 선택 가능)</span>
        </label>
        <div className="flex flex-wrap gap-2">
          {(
            [
              { value: Role.STUDENT, label: '학생' },
              { value: Role.OFFICE_WORKER, label: '직장인' },
              { value: Role.FREELANCER, label: '프리랜서' },
            ] as const
          ).map((option) => {
            const selected = formData.roles.includes(option.value)
            return (
              <button
                key={option.value}
                type="button"
                onClick={() => handleRoleToggle(option.value)}
                disabled={isSaving}
                className={`px-4 py-2 rounded-lg text-sm font-medium border transition-all duration-200 ${
                  selected
                    ? 'bg-gray-900 text-white border-gray-900 shadow-sm'
                    : 'bg-white text-gray-600 border-gray-200 hover:border-gray-400 hover:text-gray-900'
                } disabled:opacity-50`}
              >
                {option.label}
              </button>
            )
          })}
        </div>
        <p className="mt-1.5 text-[11px] text-gray-400">
          선택한 역할에 맞는 표현으로 콘텐츠가 제공됩니다
        </p>
      </div>

      {/* 에러 */}
      {error && (
        <div className="text-red-600 text-sm bg-red-50 border border-red-100 rounded-lg px-4 py-2.5">
          {error}
        </div>
      )}

      {/* 제출 */}
      <div className="flex gap-3 pt-2">
        <button
          type="submit"
          disabled={isSaving}
          className="flex-1 py-2.5 px-4 text-sm font-semibold rounded-lg text-white bg-gray-900 hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-900 disabled:bg-gray-300 transition-colors"
        >
          {isSaving
            ? '저장 중...'
            : isEditMode
              ? '수정 완료'
              : '프로필 저장 후 분석 보기'}
        </button>
        {isEditMode && (
          <button
            type="button"
            onClick={() => router.push('/today')}
            className="px-4 py-2.5 text-sm font-medium rounded-lg border border-gray-200 text-gray-600 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-400 transition-colors"
          >
            취소
          </button>
        )}
      </div>
    </form>
  )

  // -------------------------------------------------------------------------
  // Render: Step 2 - Saju Analysis Results
  // -------------------------------------------------------------------------

  const renderStep2 = () => {
    if (isFetchingSaju) {
      return (
        <div className="flex flex-col items-center justify-center py-16 gap-4">
          <div className="w-10 h-10 border-2 border-gray-200 border-t-gray-800 rounded-full animate-spin" />
          <p className="text-sm text-gray-500">나의 리듬을 분석하고 있습니다...</p>
        </div>
      )
    }

    if (!sajuAnalysis) {
      // No saju data available - graceful degradation
      return (
        <div className="text-center py-12">
          <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gray-100 flex items-center justify-center">
            <svg className="w-8 h-8 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
            </svg>
          </div>
          <p className="text-gray-600 text-sm mb-1">
            분석 결과를 아직 불러올 수 없습니다
          </p>
          <p className="text-gray-400 text-xs mb-6">
            다이어리 기간 설정으로 바로 이동할 수 있습니다
          </p>
          <div className="flex gap-3 justify-center">
            <button
              onClick={handleAdvanceToStep3}
              className="px-5 py-2.5 text-sm font-semibold rounded-lg bg-gray-900 text-white hover:bg-gray-800 transition-colors"
            >
              다이어리 기간 설정
            </button>
            <button
              onClick={handleSkipToToday}
              className="px-5 py-2.5 text-sm font-medium rounded-lg border border-gray-200 text-gray-600 hover:bg-gray-50 transition-colors"
            >
              건너뛰기
            </button>
          </div>
        </div>
      )
    }

    return (
      <div className="space-y-6">
        {/* Four Pillars */}
        {sajuAnalysis.fourPillars && (
          <div>
            <h3 className="text-sm font-semibold text-gray-800 mb-3">
              나의 에너지 구조
            </h3>
            <div className="grid grid-cols-4 gap-2">
              {PILLAR_KEYS.map((key, idx) => {
                const text = formatPillar(sajuAnalysis.fourPillars?.[key])
                return (
                  <div
                    key={key}
                    className={`rounded-lg border p-3 text-center ${PILLAR_BG[idx]}`}
                  >
                    <div className="text-[10px] font-medium text-gray-500 uppercase tracking-wider mb-1">
                      {PILLAR_LABELS[idx]}
                    </div>
                    <div className="text-lg font-bold text-gray-900 leading-tight">
                      {text || '--'}
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        )}

        {/* GyeokGuk + YongSin */}
        {(sajuAnalysis.gyeokGuk || sajuAnalysis.yongSin) && (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {sajuAnalysis.gyeokGuk && (
              <div className="rounded-lg bg-gray-50 border border-gray-100 p-4">
                <div className="text-[10px] font-semibold text-gray-400 uppercase tracking-wider mb-2">
                  핵심 에너지
                </div>
                <div className="space-y-1.5">
                  {sajuAnalysis.gyeokGuk.dayMaster && (
                    <div className="flex items-baseline gap-2">
                      <span className="text-xs text-gray-500">일간</span>
                      <span className="text-sm font-bold text-gray-900">
                        {sajuAnalysis.gyeokGuk.dayMaster}
                      </span>
                    </div>
                  )}
                  {sajuAnalysis.gyeokGuk.strength && (
                    <div className="flex items-baseline gap-2">
                      <span className="text-xs text-gray-500">강약</span>
                      <span className="text-sm font-semibold text-gray-800">
                        {sajuAnalysis.gyeokGuk.strength}
                      </span>
                    </div>
                  )}
                  {sajuAnalysis.gyeokGuk.season && (
                    <div className="flex items-baseline gap-2">
                      <span className="text-xs text-gray-500">계절</span>
                      <span className="text-sm text-gray-700">
                        {sajuAnalysis.gyeokGuk.season}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            )}
            {sajuAnalysis.yongSin?.yongSin &&
              sajuAnalysis.yongSin.yongSin.length > 0 && (
                <div className="rounded-lg bg-gray-50 border border-gray-100 p-4">
                  <div className="text-[10px] font-semibold text-gray-400 uppercase tracking-wider mb-2">
                    보완 에너지
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {sajuAnalysis.yongSin.yongSin.map((ys, i) => (
                      <span
                        key={i}
                        className="px-2.5 py-1 rounded-md bg-white border border-gray-200 text-xs font-medium text-gray-700"
                      >
                        {ys}
                      </span>
                    ))}
                  </div>
                </div>
              )}
          </div>
        )}

        {/* Direction info */}
        {(sajuAnalysis.bestDirection || sajuAnalysis.avoidDirection) && (
          <div className="grid grid-cols-2 gap-3">
            {sajuAnalysis.bestDirection && (
              <div className="rounded-lg bg-emerald-50/50 border border-emerald-100 p-3">
                <div className="text-[10px] font-semibold text-emerald-600 uppercase tracking-wider mb-1">
                  좋은 방향
                </div>
                <div className="text-sm font-medium text-gray-800">
                  {sajuAnalysis.bestDirection}
                </div>
              </div>
            )}
            {sajuAnalysis.avoidDirection && (
              <div className="rounded-lg bg-rose-50/50 border border-rose-100 p-3">
                <div className="text-[10px] font-semibold text-rose-500 uppercase tracking-wider mb-1">
                  주의 방향
                </div>
                <div className="text-sm font-medium text-gray-800">
                  {sajuAnalysis.avoidDirection}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Summary */}
        {sajuAnalysis.summary && (
          <div className="rounded-lg bg-gray-50 border border-gray-100 p-4">
            <div className="text-[10px] font-semibold text-gray-400 uppercase tracking-wider mb-2">
              오늘의 흐름
            </div>
            <p className="text-sm text-gray-700 leading-relaxed">
              {sajuAnalysis.summary}
            </p>
          </div>
        )}

        {/* Keywords */}
        {sajuAnalysis.keywords && sajuAnalysis.keywords.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {sajuAnalysis.keywords.map((kw, i) => (
              <span
                key={i}
                className="px-2.5 py-1 rounded-full bg-gray-100 text-xs font-medium text-gray-600"
              >
                #{kw}
              </span>
            ))}
          </div>
        )}

        {/* Navigation buttons */}
        <div className="flex gap-3 pt-3 border-t border-gray-100">
          <button
            onClick={handleAdvanceToStep3}
            className="flex-1 py-2.5 px-4 text-sm font-semibold rounded-lg bg-gray-900 text-white hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-900 transition-colors"
          >
            다이어리 기간 설정
          </button>
          <button
            onClick={handleSkipToToday}
            className="px-4 py-2.5 text-sm font-medium rounded-lg border border-gray-200 text-gray-600 hover:bg-gray-50 transition-colors"
          >
            건너뛰기
          </button>
        </div>
      </div>
    )
  }

  // -------------------------------------------------------------------------
  // Render: Step 3 - Diary Period Selection
  // -------------------------------------------------------------------------

  const renderStep3 = () => (
    <div className="space-y-6">
      {/* Recommendation banner */}
      {recommendation && (
        <div className="rounded-lg bg-amber-50 border border-amber-200 p-4">
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 rounded-full bg-amber-100 flex items-center justify-center flex-shrink-0 mt-0.5">
              <svg className="w-4 h-4 text-amber-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.455 2.456L21.75 6l-1.036.259a3.375 3.375 0 00-2.455 2.456z" />
              </svg>
            </div>
            <div>
              <p className="text-sm font-semibold text-amber-900">
                {recommendation.label} 다이어리 추천
              </p>
              <p className="text-xs text-amber-700 mt-0.5">
                {recommendation.reason}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Period options */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-3">
          다이어리 기간 선택
        </label>
        <div className="grid grid-cols-2 gap-2">
          {PERIOD_OPTIONS.map((option) => {
            const isSelected = formData.diary_period === option.value
            const isRecommended = recommendation?.period === option.value
            return (
              <button
                key={option.value}
                type="button"
                onClick={() =>
                  setFormData({ ...formData, diary_period: option.value })
                }
                className={`relative flex items-center gap-2 p-3 rounded-lg border-2 text-left transition-all duration-200 ${
                  isSelected
                    ? 'border-gray-900 bg-gray-50 ring-1 ring-gray-900/5'
                    : 'border-gray-150 bg-white hover:border-gray-300'
                }`}
              >
                <div
                  className={`w-4 h-4 rounded-full border-2 flex items-center justify-center flex-shrink-0 ${
                    isSelected
                      ? 'border-gray-900'
                      : 'border-gray-300'
                  }`}
                >
                  {isSelected && (
                    <div className="w-2 h-2 rounded-full bg-gray-900" />
                  )}
                </div>
                <span
                  className={`text-sm font-medium ${
                    isSelected ? 'text-gray-900' : 'text-gray-600'
                  }`}
                >
                  {option.label}
                </span>
                {isRecommended && (
                  <span className="ml-auto text-[10px] font-semibold text-amber-600 bg-amber-50 px-1.5 py-0.5 rounded">
                    추천
                  </span>
                )}
              </button>
            )
          })}
        </div>
      </div>

      {/* Start date */}
      <div>
        <label
          htmlFor="diary_start_date"
          className="block text-sm font-medium text-gray-700 mb-1"
        >
          시작일
        </label>
        <input
          type="date"
          id="diary_start_date"
          value={formData.diary_start_date}
          onChange={(e) =>
            setFormData({ ...formData, diary_start_date: e.target.value })
          }
          className="block w-full px-3 py-2.5 border border-gray-300 rounded-lg shadow-sm text-sm focus:outline-none focus:ring-2 focus:ring-gray-900/10 focus:border-gray-400 transition-shadow"
        />
      </div>

      {/* End date display or custom input */}
      {formData.diary_period && formData.diary_period !== 'custom' && (
        <div className="flex items-center gap-3 text-sm text-gray-600 bg-gray-50 rounded-lg px-4 py-3 border border-gray-100">
          <svg className="w-4 h-4 text-gray-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 012.25-2.25h13.5A2.25 2.25 0 0121 7.5v11.25m-18 0A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75m-18 0v-7.5A2.25 2.25 0 015.25 9h13.5A2.25 2.25 0 0121 11.25v7.5" />
          </svg>
          <span>
            {formData.diary_start_date} ~{' '}
            {computedEndDate(
              formData.diary_period,
              formData.diary_start_date,
            )}
          </span>
        </div>
      )}

      {formData.diary_period === 'custom' && (
        <div>
          <label
            htmlFor="diary_end_date"
            className="block text-sm font-medium text-gray-700 mb-1"
          >
            종료일
          </label>
          <input
            type="date"
            id="diary_end_date"
            value={formData.diary_end_date}
            min={formData.diary_start_date}
            onChange={(e) =>
              setFormData({ ...formData, diary_end_date: e.target.value })
            }
            className="block w-full px-3 py-2.5 border border-gray-300 rounded-lg shadow-sm text-sm focus:outline-none focus:ring-2 focus:ring-gray-900/10 focus:border-gray-400 transition-shadow"
          />
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="text-red-600 text-sm bg-red-50 border border-red-100 rounded-lg px-4 py-2.5">
          {error}
        </div>
      )}

      {/* Actions */}
      <div className="flex gap-3 pt-2">
        <button
          onClick={handleSaveDiaryPeriod}
          disabled={isSaving}
          className="flex-1 py-2.5 px-4 text-sm font-semibold rounded-lg text-white bg-gray-900 hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-900 disabled:bg-gray-300 transition-colors"
        >
          {isSaving ? '저장 중...' : '다이어리 시작하기'}
        </button>
        <button
          onClick={() => setCurrentStep(2)}
          className="px-4 py-2.5 text-sm font-medium rounded-lg border border-gray-200 text-gray-600 hover:bg-gray-50 transition-colors"
        >
          이전
        </button>
      </div>
      <p className="text-center text-[11px] text-gray-400">
        기간은 나중에 프로필 편집에서 언제든 변경할 수 있습니다
      </p>
    </div>
  )

  // -------------------------------------------------------------------------
  // Render: Page titles per step
  // -------------------------------------------------------------------------

  const stepTitles: Record<Step, { title: string; desc: string }> = {
    1: {
      title: isEditMode ? '프로필 수정' : '프로필 생성',
      desc: '정확한 출생 정보를 입력해주세요. 이 정보를 바탕으로 나만의 리듬을 분석합니다.',
    },
    2: {
      title: '나의 분석 결과',
      desc: '입력한 정보를 바탕으로 분석한 오늘의 에너지 흐름입니다.',
    },
    3: {
      title: '다이어리 기간 선택',
      desc: '나에게 맞는 다이어리 기간을 선택하세요.',
    },
  }

  // -------------------------------------------------------------------------
  // Render: Full page (edit mode shows all sections)
  // -------------------------------------------------------------------------

  // In edit mode, show all sections stacked
  if (isEditMode && currentStep === 1) {
    return (
      <div className="min-h-screen bg-gray-50 py-10 px-4 sm:px-6 lg:px-8">
        <div className="max-w-xl mx-auto space-y-6">
          {/* Header */}
          <div className="text-center mb-2">
            <h1 className="text-2xl font-bold text-gray-900 tracking-tight">
              R3 다이어리
            </h1>
          </div>

          {renderStepIndicator()}

          {/* Step 1: Form */}
          <div className="bg-white shadow-sm rounded-xl border border-gray-100 p-6">
            <div className="mb-5">
              <h2 className="text-lg font-bold text-gray-900">
                {stepTitles[1].title}
              </h2>
              <p className="mt-0.5 text-sm text-gray-500">
                {stepTitles[1].desc}
              </p>
            </div>
            {renderStep1()}
          </div>

          {/* Step 2: Saju (if data available) */}
          {sajuAnalysis && (
            <div className="bg-white shadow-sm rounded-xl border border-gray-100 p-6">
              <div className="mb-5">
                <h2 className="text-lg font-bold text-gray-900">
                  {stepTitles[2].title}
                </h2>
                <p className="mt-0.5 text-sm text-gray-500">
                  {stepTitles[2].desc}
                </p>
              </div>
              {/* Read-only display of analysis (no nav buttons) */}
              <div className="space-y-6">
                {sajuAnalysis.fourPillars && (
                  <div>
                    <h3 className="text-sm font-semibold text-gray-800 mb-3">
                      나의 에너지 구조
                    </h3>
                    <div className="grid grid-cols-4 gap-2">
                      {PILLAR_KEYS.map((key, idx) => {
                        const text = formatPillar(
                          sajuAnalysis.fourPillars?.[key],
                        )
                        return (
                          <div
                            key={key}
                            className={`rounded-lg border p-3 text-center ${PILLAR_BG[idx]}`}
                          >
                            <div className="text-[10px] font-medium text-gray-500 uppercase tracking-wider mb-1">
                              {PILLAR_LABELS[idx]}
                            </div>
                            <div className="text-lg font-bold text-gray-900 leading-tight">
                              {text || '--'}
                            </div>
                          </div>
                        )
                      })}
                    </div>
                  </div>
                )}
                {(sajuAnalysis.gyeokGuk || sajuAnalysis.yongSin) && (
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    {sajuAnalysis.gyeokGuk && (
                      <div className="rounded-lg bg-gray-50 border border-gray-100 p-4">
                        <div className="text-[10px] font-semibold text-gray-400 uppercase tracking-wider mb-2">
                          핵심 에너지
                        </div>
                        <div className="space-y-1.5">
                          {sajuAnalysis.gyeokGuk.dayMaster && (
                            <div className="flex items-baseline gap-2">
                              <span className="text-xs text-gray-500">일간</span>
                              <span className="text-sm font-bold text-gray-900">
                                {sajuAnalysis.gyeokGuk.dayMaster}
                              </span>
                            </div>
                          )}
                          {sajuAnalysis.gyeokGuk.strength && (
                            <div className="flex items-baseline gap-2">
                              <span className="text-xs text-gray-500">강약</span>
                              <span className="text-sm font-semibold text-gray-800">
                                {sajuAnalysis.gyeokGuk.strength}
                              </span>
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                    {sajuAnalysis.yongSin?.yongSin &&
                      sajuAnalysis.yongSin.yongSin.length > 0 && (
                        <div className="rounded-lg bg-gray-50 border border-gray-100 p-4">
                          <div className="text-[10px] font-semibold text-gray-400 uppercase tracking-wider mb-2">
                            보완 에너지
                          </div>
                          <div className="flex flex-wrap gap-1.5">
                            {sajuAnalysis.yongSin.yongSin.map((ys, i) => (
                              <span
                                key={i}
                                className="px-2.5 py-1 rounded-md bg-white border border-gray-200 text-xs font-medium text-gray-700"
                              >
                                {ys}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                  </div>
                )}
                {sajuAnalysis.summary && (
                  <div className="rounded-lg bg-gray-50 border border-gray-100 p-4">
                    <div className="text-[10px] font-semibold text-gray-400 uppercase tracking-wider mb-2">
                      오늘의 흐름
                    </div>
                    <p className="text-sm text-gray-700 leading-relaxed">
                      {sajuAnalysis.summary}
                    </p>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    )
  }

  // Standard stepped flow (new user or navigating steps)
  return (
    <div className="min-h-screen bg-gray-50 py-10 px-4 sm:px-6 lg:px-8">
      <div className="max-w-xl mx-auto">
        {/* Header */}
        <div className="text-center mb-2">
          <h1 className="text-2xl font-bold text-gray-900 tracking-tight">
            R3 다이어리
          </h1>
        </div>

        {renderStepIndicator()}

        {/* Card */}
        <div className="bg-white shadow-sm rounded-xl border border-gray-100 p-6">
          <div className="mb-5">
            <h2 className="text-lg font-bold text-gray-900">
              {stepTitles[currentStep].title}
            </h2>
            <p className="mt-0.5 text-sm text-gray-500">
              {stepTitles[currentStep].desc}
            </p>
          </div>

          {currentStep === 1 && renderStep1()}
          {currentStep === 2 && renderStep2()}
          {currentStep === 3 && renderStep3()}
        </div>
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Export with Suspense boundary
// ---------------------------------------------------------------------------

export default function ProfilePage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen flex items-center justify-center bg-gray-50">
          <div className="flex flex-col items-center gap-3">
            <div className="w-8 h-8 border-2 border-gray-300 border-t-gray-800 rounded-full animate-spin" />
            <p className="text-sm text-gray-500">프로필을 불러오는 중...</p>
          </div>
        </div>
      }
    >
      <ProfileForm />
    </Suspense>
  )
}
