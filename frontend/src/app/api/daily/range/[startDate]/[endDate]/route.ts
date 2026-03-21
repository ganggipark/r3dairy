import { NextRequest, NextResponse } from 'next/server'
import { getAuthUser, createUserClient, AuthError } from '@/lib/supabase-server'

/**
 * Daily Content Range API Route
 * Returns daily content for each date in the given range (max 31 days)
 */

export async function GET(
  request: NextRequest,
  { params }: { params: { startDate: string; endDate: string } }
) {
  try {
    const { startDate, endDate } = params
    const searchParams = request.nextUrl.searchParams
    const role = searchParams.get('role')
    const { user, token } = await getAuthUser(request)

    // Validate date formats
    const startMatch = startDate.match(/^\d{4}-\d{2}-\d{2}$/)
    const endMatch = endDate.match(/^\d{4}-\d{2}-\d{2}$/)
    if (!startMatch || !endMatch) {
      return NextResponse.json(
        { detail: '날짜 형식이 올바르지 않습니다. (YYYY-MM-DD)' },
        { status: 400 }
      )
    }

    // Max 31 days
    const start = new Date(startDate)
    const end = new Date(endDate)
    const diffDays = Math.ceil((end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24)) + 1
    if (diffDays < 1 || diffDays > 31) {
      return NextResponse.json(
        { detail: '날짜 범위는 1~31일이어야 합니다.' },
        { status: 400 }
      )
    }

    const supabase = createUserClient(token)

    // Get user profile
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

    // Generate content for each date in range
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

      const results = []
      const current = new Date(startDate)

      while (current <= end) {
        const dateStr = current.toISOString().split('T')[0]

        try {
          const sajuData = calculateSaju(birthInfo, dateStr)
          const dailyRhythm = analyzeDailyFortune(birthInfo, dateStr, sajuData)

          // Qimen (non-blocking)
          let qimenSlots = null
          let qimenSummary: Record<string, unknown> = {}
          try {
            qimenSlots = calculateDailyQimen(profile.birth_date, dateStr)
            const summary = getDailySummary(profile.birth_date, dateStr)
            qimenSummary = {
              best_direction: summary.best_direction,
              avoid_direction: summary.avoid_direction,
              peak_hours: summary.peak_hours,
            }
          } catch (e: unknown) {
            console.warn(`Qimen calculation skipped for ${dateStr}:`, e instanceof Error ? e.message : String(e))
          }

          let dailyContent = assembleDailyContent(dateStr, sajuData, dailyRhythm, qimenSummary)

          if (role && dailyContent) {
            dailyContent = translateDailyContent(dailyContent, role as UserRole)
          }

          results.push({
            date: dateStr,
            role: role || null,
            content: dailyContent,
            qimen_slots: qimenSlots,
            best_direction: qimenSummary.best_direction || null,
            avoid_direction: qimenSummary.avoid_direction || null,
            peak_hours: qimenSummary.peak_hours || null,
          })
        } catch (dayError: unknown) {
          // Skip failed dates but continue
          console.error(`Date ${dateStr} content error:`, dayError instanceof Error ? dayError.message : String(dayError))
          results.push({
            date: dateStr,
            role: role || null,
            content: null,
            qimen_slots: null,
            best_direction: null,
            avoid_direction: null,
            peak_hours: null,
          })
        }

        current.setDate(current.getDate() + 1)
      }

      return NextResponse.json(results)
    } catch (importError: unknown) {
      console.error('Content library not available:', importError instanceof Error ? importError.message : String(importError))
      // Return empty array with minimal data for each date
      const results = []
      const current = new Date(startDate)
      while (current <= end) {
        results.push({
          date: current.toISOString().split('T')[0],
          role: role || null,
          content: {
            date: current.toISOString().split('T')[0],
            summary: '콘텐츠 생성 엔진이 준비 중입니다.',
            keywords: ['준비중'],
            rhythm_description: '',
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
        current.setDate(current.getDate() + 1)
      }
      return NextResponse.json(results)
    }
  } catch (error: unknown) {
    if (error instanceof AuthError) {
      return NextResponse.json({ detail: error.message }, { status: error.status })
    }
    console.error('Daily range content error:', error)
    return NextResponse.json(
      { detail: '일간 콘텐츠 범위 조회 중 오류가 발생했습니다.' },
      { status: 500 }
    )
  }
}
