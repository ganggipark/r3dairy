import { NextRequest, NextResponse } from 'next/server'
import { getAuthUser, createUserClient, AuthError } from '@/lib/supabase-server'

/**
 * Monthly Content API Route
 */

export async function GET(
  request: NextRequest,
  { params }: { params: { year: string; month: string } }
) {
  try {
    const { year, month } = params
    const yearNum = parseInt(year)
    const monthNum = parseInt(month)
    const searchParams = request.nextUrl.searchParams
    const role = searchParams.get('role')
    const { user, token } = await getAuthUser(request)

    if (yearNum < 2000 || yearNum > 2100) {
      return NextResponse.json(
        { detail: '연도는 2000-2100 범위여야 합니다.' },
        { status: 400 }
      )
    }
    if (monthNum < 1 || monthNum > 12) {
      return NextResponse.json(
        { detail: '월은 1-12 범위여야 합니다.' },
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
      const { calculateSaju, analyzeMonthlyRhythm } = await import('@/lib/content/saju-engine')
      const { assembleMonthlyContent } = await import('@/lib/content/assembly')
      const { translateMonthlyContent } = await import('@/lib/content/translator')
      type UserRole = 'student' | 'office_worker' | 'freelancer'

      const birthInfo = {
        name: profile.name,
        birthDate: profile.birth_date,
        birthTime: profile.birth_time,
        gender: profile.gender as 'male' | 'female',
        birthPlace: profile.birth_place || '서울',
      }

      const targetDate = `${year}-${month.padStart(2, '0')}-01`
      const sajuData = calculateSaju(birthInfo, targetDate)
      const monthlyRhythm = analyzeMonthlyRhythm(birthInfo, yearNum, monthNum, sajuData)
      let monthlyContent = assembleMonthlyContent(yearNum, monthNum, monthlyRhythm)

      if (role && monthlyContent) {
        monthlyContent = translateMonthlyContent(monthlyContent, role as UserRole)
      }

      return NextResponse.json({
        year: yearNum,
        month: monthNum,
        role: role || null,
        content: monthlyContent,
      })
    } catch (importError: any) {
      console.error('Content library not available:', importError.message)
      return NextResponse.json({
        year: yearNum,
        month: monthNum,
        role: role || null,
        content: {
          year_month: `${yearNum}년 ${monthNum}월`,
          theme: '콘텐츠 엔진 준비 중',
          summary: '콘텐츠 생성 엔진이 준비 중입니다.',
          keywords: [],
          priorities: [],
          calendar_data: {},
          opportunities: [],
          challenges: [],
        },
      })
    }
  } catch (error: any) {
    if (error instanceof AuthError) {
      return NextResponse.json({ detail: error.message }, { status: error.status })
    }
    console.error('Monthly content error:', error)
    return NextResponse.json(
      { detail: '월간 콘텐츠 생성 중 오류가 발생했습니다.' },
      { status: 500 }
    )
  }
}
