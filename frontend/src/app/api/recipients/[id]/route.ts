import { NextRequest, NextResponse } from 'next/server'
import { getAuthUser, createUserClient, AuthError } from '@/lib/supabase-server'

/**
 * Recipients [id] API Routes - Direct Supabase queries
 */

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const { user, token } = await getAuthUser(request)
    const supabase = createUserClient(token)
    const { id } = params

    const { data, error } = await supabase
      .from('diary_recipients')
      .select('*')
      .eq('id', id)
      .single()

    if (error || !data) {
      return NextResponse.json(
        { detail: '대상자를 찾을 수 없습니다.' },
        { status: 404 }
      )
    }

    if (data.owner_id !== user.id) {
      return NextResponse.json(
        { detail: '접근 권한이 없습니다.' },
        { status: 403 }
      )
    }

    return NextResponse.json(data)
  } catch (error: unknown) {
    if (error instanceof AuthError) {
      return NextResponse.json({ detail: error.message }, { status: error.status })
    }
    console.error('Recipient GET error:', error)
    return NextResponse.json(
      { detail: '대상자 조회 중 오류가 발생했습니다.' },
      { status: 500 }
    )
  }
}

export async function PUT(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const { user, token } = await getAuthUser(request)
    const supabase = createUserClient(token)
    const { id } = params
    const body = await request.json()

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

    // If setting as default, clear existing default first
    if (body.is_default === true) {
      const { error: clearError } = await supabase
        .from('diary_recipients')
        .update({ is_default: false })
        .eq('owner_id', user.id)
        .eq('is_default', true)

      if (clearError) {
        console.error('Recipient PUT clear default error:', clearError)
        return NextResponse.json(
          { detail: '기본 대상자 해제에 실패했습니다.' },
          { status: 500 }
        )
      }
    }

    // Build update data (only provided fields)
    const updateData: Record<string, unknown> = {}
    const fields = [
      'name', 'birth_date', 'birth_time', 'gender', 'birth_place',
      'role', 'relationship', 'notes', 'diary_period', 'is_default',
    ]
    for (const field of fields) {
      if (body[field] !== undefined && body[field] !== null) {
        updateData[field] = body[field]
      }
    }

    const { data, error } = await supabase
      .from('diary_recipients')
      .update(updateData)
      .eq('id', id)
      .select()
      .single()

    if (error || !data) {
      console.error('Recipient PUT error:', error)
      return NextResponse.json(
        { detail: '대상자 수정에 실패했습니다.' },
        { status: 500 }
      )
    }

    return NextResponse.json(data)
  } catch (error: unknown) {
    if (error instanceof AuthError) {
      return NextResponse.json({ detail: error.message }, { status: error.status })
    }
    console.error('Recipient PUT error:', error)
    return NextResponse.json(
      { detail: '대상자 수정 중 오류가 발생했습니다.' },
      { status: 500 }
    )
  }
}

export async function DELETE(
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

    const { error } = await supabase
      .from('diary_recipients')
      .delete()
      .eq('id', id)

    if (error) {
      console.error('Recipient DELETE error:', error)
      return NextResponse.json(
        { detail: '대상자 삭제에 실패했습니다.' },
        { status: 500 }
      )
    }

    return NextResponse.json({ success: true, message: '대상자가 삭제되었습니다.' })
  } catch (error: unknown) {
    if (error instanceof AuthError) {
      return NextResponse.json({ detail: error.message }, { status: error.status })
    }
    console.error('Recipient DELETE error:', error)
    return NextResponse.json(
      { detail: '대상자 삭제 중 오류가 발생했습니다.' },
      { status: 500 }
    )
  }
}
