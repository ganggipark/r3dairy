import { NextRequest, NextResponse } from 'next/server'
import { getAuthUser, createUserClient, AuthError } from '@/lib/supabase-server'

/**
 * Recipients API Routes - Direct Supabase queries
 */

export async function GET(request: NextRequest) {
  try {
    const { user, token } = await getAuthUser(request)
    const supabase = createUserClient(token)

    const { data, error } = await supabase
      .from('diary_recipients')
      .select('*')
      .eq('owner_id', user.id)
      .order('created_at', { ascending: true })

    if (error) {
      console.error('Recipients GET error:', error)
      return NextResponse.json(
        { detail: '대상자 목록 조회에 실패했습니다.' },
        { status: 500 }
      )
    }

    return NextResponse.json(data ?? [])
  } catch (error: unknown) {
    if (error instanceof AuthError) {
      return NextResponse.json({ detail: error.message }, { status: error.status })
    }
    console.error('Recipients GET error:', error)
    return NextResponse.json(
      { detail: '대상자 목록 조회 중 오류가 발생했습니다.' },
      { status: 500 }
    )
  }
}

export async function POST(request: NextRequest) {
  try {
    const { user, token } = await getAuthUser(request)
    const supabase = createUserClient(token)
    const body = await request.json()

    // If setting as default, clear existing default first
    if (body.is_default === true) {
      const { error: clearError } = await supabase
        .from('diary_recipients')
        .update({ is_default: false })
        .eq('owner_id', user.id)
        .eq('is_default', true)

      if (clearError) {
        console.error('Recipients POST clear default error:', clearError)
        return NextResponse.json(
          { detail: '기본 대상자 해제에 실패했습니다.' },
          { status: 500 }
        )
      }
    }

    const recipientData: Record<string, unknown> = {
      owner_id: user.id,
    }

    const fields = [
      'name', 'birth_date', 'birth_time', 'gender', 'birth_place',
      'role', 'relationship', 'notes', 'diary_period', 'is_default',
    ]
    for (const field of fields) {
      if (body[field] !== undefined && body[field] !== null) {
        recipientData[field] = body[field]
      }
    }

    const { data, error } = await supabase
      .from('diary_recipients')
      .insert(recipientData)
      .select()
      .single()

    if (error || !data) {
      console.error('Recipients POST insert error:', error)
      return NextResponse.json(
        { detail: '대상자 생성에 실패했습니다.' },
        { status: 500 }
      )
    }

    return NextResponse.json(data, { status: 201 })
  } catch (error: unknown) {
    if (error instanceof AuthError) {
      return NextResponse.json({ detail: error.message }, { status: error.status })
    }
    console.error('Recipients POST error:', error)
    return NextResponse.json(
      { detail: '대상자 생성 중 오류가 발생했습니다.' },
      { status: 500 }
    )
  }
}
