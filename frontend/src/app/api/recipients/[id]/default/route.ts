import { NextRequest, NextResponse } from 'next/server'
import { getAuthUser, createUserClient, AuthError } from '@/lib/supabase-server'

/**
 * Recipients [id]/default API Route - Set recipient as default
 */

export async function PUT(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const { user, token } = await getAuthUser(request)
    const supabase = createUserClient(token)
    const { id } = params

    // Verify ownership
    const { data: existing, error: fetchError } = await supabase
      .from('diary_recipients')
      .select('owner_id')
      .eq('id', id)
      .single()

    if (fetchError || !existing) {
      return NextResponse.json(
        { detail: '대상자를 찾을 수 없습니다.' },
        { status: 404 }
      )
    }

    if (existing.owner_id !== user.id) {
      return NextResponse.json(
        { detail: '접근 권한이 없습니다.' },
        { status: 403 }
      )
    }

    // Clear existing default
    const { error: clearError } = await supabase
      .from('diary_recipients')
      .update({ is_default: false })
      .eq('owner_id', user.id)
      .eq('is_default', true)

    if (clearError) {
      console.error('Recipient default PUT clear error:', clearError)
      return NextResponse.json(
        { detail: '기존 기본 대상자 해제에 실패했습니다.' },
        { status: 500 }
      )
    }

    // Set new default
    const { data, error } = await supabase
      .from('diary_recipients')
      .update({ is_default: true })
      .eq('id', id)
      .select()
      .single()

    if (error || !data) {
      console.error('Recipient default PUT error:', error)
      return NextResponse.json(
        { detail: '기본 대상자 설정에 실패했습니다.' },
        { status: 500 }
      )
    }

    return NextResponse.json(data)
  } catch (error: unknown) {
    if (error instanceof AuthError) {
      return NextResponse.json({ detail: error.message }, { status: error.status })
    }
    console.error('Recipient default PUT error:', error)
    return NextResponse.json(
      { detail: '기본 대상자 설정 중 오류가 발생했습니다.' },
      { status: 500 }
    )
  }
}
