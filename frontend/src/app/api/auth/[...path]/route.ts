import { NextRequest, NextResponse } from 'next/server'
import { createAnonClient, createUserClient, AuthError } from '@/lib/supabase-server'

/**
 * Auth API Routes - Direct Supabase Auth calls
 * Handles: signup, login, logout, refresh, change-password
 */

export async function POST(
  request: NextRequest,
  { params }: { params: { path: string[] } }
) {
  const path = params.path.join('/')

  try {
    const supabase = createAnonClient()

    if (path === 'signup') {
      const { email, password, name } = await request.json()
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
        options: { data: { name } },
      })

      if (error) {
        return NextResponse.json(
          { detail: error.message },
          { status: error.status || 400 }
        )
      }

      if (!data.user) {
        return NextResponse.json(
          { detail: '회원가입에 실패했습니다.' },
          { status: 400 }
        )
      }

      // No session = email confirmation required
      if (!data.session) {
        return NextResponse.json({
          user_id: data.user.id,
          email: data.user.email || email,
          requires_email_confirmation: true,
          message: '회원가입이 완료되었습니다. 이메일을 확인해주세요.',
        })
      }

      return NextResponse.json({
        access_token: data.session.access_token,
        refresh_token: data.session.refresh_token,
        user_id: data.user.id,
        email: data.user.email || email,
        requires_email_confirmation: false,
      })
    }

    if (path === 'login') {
      const { email, password } = await request.json()
      const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password,
      })

      if (error) {
        return NextResponse.json(
          { detail: '이메일 또는 비밀번호가 올바르지 않습니다.' },
          { status: 401 }
        )
      }

      if (!data.user || !data.session) {
        return NextResponse.json(
          { detail: '로그인에 실패했습니다.' },
          { status: 401 }
        )
      }

      return NextResponse.json({
        access_token: data.session.access_token,
        refresh_token: data.session.refresh_token,
        user_id: data.user.id,
        email: data.user.email,
      })
    }

    if (path === 'logout') {
      const { error } = await supabase.auth.signOut()
      if (error) {
        return NextResponse.json(
          { detail: '로그아웃 중 오류가 발생했습니다.' },
          { status: 500 }
        )
      }
      return NextResponse.json({ success: true, message: '로그아웃되었습니다.' })
    }

    if (path === 'refresh') {
      const { refresh_token } = await request.json()
      const { data, error } = await supabase.auth.refreshSession({
        refresh_token,
      })

      if (error || !data.session) {
        return NextResponse.json(
          { detail: '유효하지 않은 리프레시 토큰입니다.' },
          { status: 401 }
        )
      }

      return NextResponse.json({
        access_token: data.session.access_token,
        refresh_token: data.session.refresh_token,
        user_id: data.user?.id,
        email: data.user?.email,
      })
    }

    return NextResponse.json({ detail: 'Not found' }, { status: 404 })
  } catch (error: any) {
    console.error('Auth API error:', error)
    return NextResponse.json(
      { detail: '인증 처리 중 오류가 발생했습니다.' },
      { status: 500 }
    )
  }
}

export async function PUT(
  request: NextRequest,
  { params }: { params: { path: string[] } }
) {
  const path = params.path.join('/')

  try {
    if (path === 'change-password') {
      const authorization = request.headers.get('Authorization')
      if (!authorization || !authorization.startsWith('Bearer ')) {
        return NextResponse.json(
          { detail: '인증 토큰이 필요합니다.' },
          { status: 401 }
        )
      }

      const token = authorization.split(' ')[1]
      const supabase = createAnonClient()

      // Validate current user
      const { data: userData, error: userError } = await supabase.auth.getUser(token)
      if (userError || !userData.user) {
        return NextResponse.json(
          { detail: '인증이 필요합니다.' },
          { status: 401 }
        )
      }

      const { current_password, new_password } = await request.json()

      // Verify current password by signing in
      const { error: loginError } = await supabase.auth.signInWithPassword({
        email: userData.user.email!,
        password: current_password,
      })

      if (loginError) {
        return NextResponse.json(
          { detail: '현재 비밀번호가 올바르지 않습니다.' },
          { status: 401 }
        )
      }

      // Update password using admin-level client with user's session
      const userSupabase = createUserClient(token)
      const { error: updateError } = await userSupabase.auth.updateUser({
        password: new_password,
      })

      if (updateError) {
        return NextResponse.json(
          { detail: '비밀번호 변경에 실패했습니다.' },
          { status: 500 }
        )
      }

      return NextResponse.json({
        success: true,
        message: '비밀번호가 성공적으로 변경되었습니다.',
      })
    }

    return NextResponse.json({ detail: 'Not found' }, { status: 404 })
  } catch (error: any) {
    console.error('Auth API error:', error)
    return NextResponse.json(
      { detail: '인증 처리 중 오류가 발생했습니다.' },
      { status: 500 }
    )
  }
}

export async function GET(
  request: NextRequest,
  { params }: { params: { path: string[] } }
) {
  const path = params.path.join('/')

  try {
    if (path === 'me') {
      const authorization = request.headers.get('Authorization')
      if (!authorization || !authorization.startsWith('Bearer ')) {
        return NextResponse.json(
          { detail: '인증 토큰이 필요합니다.' },
          { status: 401 }
        )
      }

      const token = authorization.split(' ')[1]
      const supabase = createAnonClient()
      const { data, error } = await supabase.auth.getUser(token)

      if (error || !data.user) {
        return NextResponse.json(
          { detail: '유효하지 않은 토큰입니다.' },
          { status: 401 }
        )
      }

      return NextResponse.json({
        user_id: data.user.id,
        email: data.user.email,
        name: data.user.user_metadata?.name,
      })
    }

    return NextResponse.json({ detail: 'Not found' }, { status: 404 })
  } catch (error: any) {
    return NextResponse.json(
      { detail: '인증 처리 중 오류가 발생했습니다.' },
      { status: 500 }
    )
  }
}

export async function OPTIONS() {
  return new NextResponse(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    },
  })
}
