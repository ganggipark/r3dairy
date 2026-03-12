import { NextRequest, NextResponse } from 'next/server'
import { getAuthUser, createUserClient, AuthError } from '@/lib/supabase-server'

/**
 * Daily Content API Route - Saju calculation pipeline
 * Fetches user profile, runs saju calculation, assembles content
 */

export async function GET(
  request: NextRequest,
  { params }: { params: { date: string } }
) {
  try {
    const { date } = params
    const searchParams = request.nextUrl.searchParams
    const role = searchParams.get('role')
    const { user, token } = await getAuthUser(request)

    const supabase = createUserClient(token)

    // 1. Get user profile
    const { data: profile, error: profileError } = await supabase
      .from('profiles')
      .select('*')
      .eq('id', user.id)
      .single()

    if (profileError || !profile) {
      return NextResponse.json(
        { detail: '프로필이 존재하지 않습니다. 먼저 프로필을 생성해주세요.' },
        { status: 404 }
      )
    }

    // 2. Run saju calculation pipeline
    try {
      const { calculateSaju, analyzeDailyFortune } = await import('@/lib/content/saju-engine')
      const { assembleDailyContent } = await import('@/lib/content/assembly')
      const { translateDailyContent } = await import('@/lib/content/translator')
      type UserRole = 'student' | 'office_worker' | 'freelancer'
      const { calculateDailyQimen, getDailySummary } = await import('@/lib/content/qimen-engine')

      const birthInfo = {
        name: profile.name,
        birthDate: profile.birth_date,
        birthTime: profile.birth_time,
        gender: profile.gender as 'male' | 'female',
        birthPlace: profile.birth_place || '서울',
      }

      // Saju calculation
      const sajuData = calculateSaju(birthInfo, date)
      if (!sajuData) {
        return NextResponse.json(
          { detail: '사주 계산에 실패했습니다.' },
          { status: 500 }
        )
      }

      // Daily rhythm analysis
      const dailyRhythm = analyzeDailyFortune(birthInfo, date, sajuData)

      // Qimen calculation (non-blocking)
      let qimenSlots = null
      let qimenSummary: Record<string, any> = {}
      try {
        const qimenResults = calculateDailyQimen(profile.birth_date, date)
        qimenSlots = qimenResults
        const summary = getDailySummary(profile.birth_date, date)
        qimenSummary = {
          best_direction: summary.best_direction,
          avoid_direction: summary.avoid_direction,
          peak_hours: summary.peak_hours,
        }
      } catch {
        // Qimen failure is non-blocking
      }

      // Content assembly
      let dailyContent = assembleDailyContent(date, sajuData, dailyRhythm, qimenSummary)

      // Role translation
      if (role && dailyContent) {
        dailyContent = translateDailyContent(dailyContent, role as UserRole)
      }

      return NextResponse.json({
        date,
        role: role || null,
        content: dailyContent,
        qimen_slots: qimenSlots,
        best_direction: qimenSummary.best_direction || null,
        avoid_direction: qimenSummary.avoid_direction || null,
        peak_hours: qimenSummary.peak_hours || null,
      })
    } catch (importError: any) {
      // Content library not yet available - return minimal response
      console.error('Content library not available:', importError.message)
      return NextResponse.json({
        date,
        role: role || null,
        content: {
          date,
          summary: '콘텐츠 생성 엔진이 준비 중입니다. 잠시 후 다시 시도해주세요.',
          keywords: ['준비중'],
          rhythm_description: '콘텐츠 엔진이 초기화되는 중입니다.',
          focus_caution: { focus: [], caution: [] },
          action_guide: { do: [], avoid: [] },
          time_direction: { good_time: '', avoid_time: '', good_direction: '', avoid_direction: '', notes: '' },
          state_trigger: { gesture: '', phrase: '', how_to: '' },
          meaning_shift: '',
          rhythm_question: '',
        },
        qimen_slots: null,
        best_direction: null,
        avoid_direction: null,
        peak_hours: null,
      })
    }
  } catch (error: any) {
    if (error instanceof AuthError) {
      return NextResponse.json({ detail: error.message }, { status: error.status })
    }
    console.error('Daily content error:', error)
    return NextResponse.json(
      { detail: '일간 콘텐츠를 생성하는 중 오류가 발생했습니다.' },
      { status: 500 }
    )
  }
}
