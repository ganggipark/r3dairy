import { NextRequest, NextResponse } from 'next/server'
import { getAuthUser, createUserClient, AuthError } from '@/lib/supabase-server'

/**
 * Profile API Routes - Direct Supabase queries
 */

export async function GET(request: NextRequest) {
  try {
    const { user, token } = await getAuthUser(request)
    const supabase = createUserClient(token)

    const { data, error } = await supabase
      .from('profiles')
      .select('*')
      .eq('id', user.id)
      .single()

    if (error || !data) {
      return NextResponse.json(
        { detail: '프로필이 존재하지 않습니다.' },
        { status: 404 }
      )
    }

    return NextResponse.json(data)
  } catch (error: unknown) {
    if (error instanceof AuthError) {
      return NextResponse.json({ detail: error.message }, { status: error.status })
    }
    console.error('Profile GET error:', error)
    return NextResponse.json(
      { detail: '프로필 조회 중 오류가 발생했습니다.' },
      { status: 500 }
    )
  }
}

export async function POST(request: NextRequest) {
  try {
    const { user, token } = await getAuthUser(request)
    const supabase = createUserClient(token)
    const body = await request.json()

    // Check existing profile
    const { data: existing } = await supabase
      .from('profiles')
      .select('id')
      .eq('id', user.id)
      .single()

    if (existing) {
      return NextResponse.json(
        { detail: '이미 프로필이 존재합니다.' },
        { status: 400 }
      )
    }

    const profileData = {
      id: user.id,
      name: body.name,
      birth_date: body.birth_date,
      birth_time: body.birth_time,
      gender: body.gender,
      birth_place: body.birth_place,
      roles: body.roles || [],
      preferences: body.preferences || {},
    }

    const { data, error } = await supabase
      .from('profiles')
      .insert(profileData)
      .select()
      .single()

    if (error || !data) {
      console.error('Profile insert error:', error)
      return NextResponse.json(
        { detail: '프로필 생성에 실패했습니다.' },
        { status: 500 }
      )
    }

    return NextResponse.json(data, { status: 201 })
  } catch (error: unknown) {
    if (error instanceof AuthError) {
      return NextResponse.json({ detail: error.message }, { status: error.status })
    }
    console.error('Profile POST error:', error)
    return NextResponse.json(
      { detail: '프로필 생성 중 오류가 발생했습니다.' },
      { status: 500 }
    )
  }
}

export async function PUT(request: NextRequest) {
  try {
    const { user, token } = await getAuthUser(request)
    const supabase = createUserClient(token)
    const body = await request.json()

    // Build update data (only non-null fields)
    const updateData: Record<string, string | string[] | boolean | number> = {}
    const fields = ['name', 'birth_date', 'birth_time', 'gender', 'birth_place', 'roles', 'preferences']
    for (const field of fields) {
      if (body[field] !== undefined && body[field] !== null) {
        updateData[field] = body[field]
      }
    }

    const { data, error } = await supabase
      .from('profiles')
      .update(updateData)
      .eq('id', user.id)
      .select()
      .single()

    if (error || !data) {
      return NextResponse.json(
        { detail: '프로필 수정에 실패했습니다.' },
        { status: error ? 500 : 404 }
      )
    }

    return NextResponse.json(data)
  } catch (error: unknown) {
    if (error instanceof AuthError) {
      return NextResponse.json({ detail: error.message }, { status: error.status })
    }
    console.error('Profile PUT error:', error)
    return NextResponse.json(
      { detail: '프로필 수정 중 오류가 발생했습니다.' },
      { status: 500 }
    )
  }
}

export async function DELETE(request: NextRequest) {
  try {
    const { user, token } = await getAuthUser(request)
    const supabase = createUserClient(token)

    const { data, error } = await supabase
      .from('profiles')
      .delete()
      .eq('id', user.id)
      .select()
      .single()

    if (error || !data) {
      return NextResponse.json(
        { detail: '프로필이 존재하지 않습니다.' },
        { status: 404 }
      )
    }

    return NextResponse.json({ success: true, message: '프로필이 삭제되었습니다.' })
  } catch (error: unknown) {
    if (error instanceof AuthError) {
      return NextResponse.json({ detail: error.message }, { status: error.status })
    }
    console.error('Profile DELETE error:', error)
    return NextResponse.json(
      { detail: '프로필 삭제 중 오류가 발생했습니다.' },
      { status: 500 }
    )
  }
}
