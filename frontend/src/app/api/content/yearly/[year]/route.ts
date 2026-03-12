import { NextRequest, NextResponse } from 'next/server'
import { getAuthUser, createUserClient, AuthError } from '@/lib/supabase-server'

/**
 * Yearly Content API Route
 */

export async function GET(
  request: NextRequest,
  { params }: { params: { year: string } }
) {
  try {
    const { year } = params
    const yearNum = parseInt(year)
    const searchParams = request.nextUrl.searchParams
    const role = searchParams.get('role')
    const { user, token } = await getAuthUser(request)

    if (yearNum < 2000 || yearNum > 2100) {
      return NextResponse.json(
        { detail: '연도는 2000-2100 범위여야 합니다.' },
        { status: 400 }
      )
    }

    const supabase = createUserClient(token)

    const { data: profile, error: profileError } = await supabase
      .from('profiles')
      .select('*')
      .eq('id', user.id)
      .single()

    if (profileError || !profile) {
      return NextResponse.json(
        { detail: '프로필이 존재하지 않습니다.' },
        { status: 404 }
      )
    }

    try {
      const { calculateSaju, analyzeYearlyRhythm } = await import('@/lib/content/saju-engine')
      const { assembleYearlyContent } = await import('@/lib/content/assembly')
      const { translateYearlyContent } = await import('@/lib/content/translator')
      type UserRole = 'student' | 'office_worker' | 'freelancer'

      const birthInfo = {
        name: profile.name,
        birthDate: profile.birth_date,
        birthTime: profile.birth_time,
        gender: profile.gender as 'male' | 'female',
        birthPlace: profile.birth_place || '서울',
      }

      const targetDate = `${year}-01-01`
      const sajuData = calculateSaju(birthInfo, targetDate)
      const yearlyRhythm = analyzeYearlyRhythm(birthInfo, yearNum, sajuData)
      let yearlyContent = assembleYearlyContent(yearNum, yearlyRhythm)

      if (role && yearlyContent) {
        yearlyContent = translateYearlyContent(yearlyContent, role as UserRole)
      }

      // Transform monthly_signals Korean keys to English keys
      if (yearlyContent?.monthly_signals) {
        const transformed: Record<number, { month: number; theme: string; energy: number }> = {}
        for (const [key, signal] of Object.entries(yearlyContent.monthly_signals)) {
          const s = signal as any
          transformed[Number(key)] = {
            month: s['월'] ?? s.month ?? Number(key),
            theme: s['테마'] ?? s.theme ?? '',
            energy: s['에너지'] ?? s.energy ?? 3,
          }
        }
        ;(yearlyContent as any).monthly_signals = transformed
      }

      return NextResponse.json({
        year: yearNum,
        role: role || null,
        content: yearlyContent,
      })
    } catch (importError: any) {
      console.error('Content library not available:', importError.message)
      return NextResponse.json({
        year: yearNum,
        role: role || null,
        content: {
          year: yearNum,
          theme: '콘텐츠 엔진 준비 중',
          summary: '콘텐츠 생성 엔진이 준비 중입니다.',
          keywords: [],
          flow_summary: '',
          monthly_signals: {},
          core_tasks: [],
        },
      })
    }
  } catch (error: any) {
    if (error instanceof AuthError) {
      return NextResponse.json({ detail: error.message }, { status: error.status })
    }
    console.error('Yearly content error:', error)
    return NextResponse.json(
      { detail: '연간 콘텐츠 생성 중 오류가 발생했습니다.' },
      { status: 500 }
    )
  }
}
