/**
 * Server-side Supabase client helpers for API routes
 * Used by Next.js API Routes to call Supabase directly
 */

import { createClient, SupabaseClient } from '@supabase/supabase-js'
import { NextRequest } from 'next/server'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

/**
 * Create a Supabase client with the user's JWT for RLS-protected queries
 */
export function createUserClient(token: string): SupabaseClient {
  return createClient(supabaseUrl, supabaseAnonKey, {
    global: {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    },
  })
}

/**
 * Create a Supabase client with anon key (for auth operations)
 */
export function createAnonClient(): SupabaseClient {
  return createClient(supabaseUrl, supabaseAnonKey)
}

/**
 * Extract Bearer token from request and validate the user
 * Returns { user, token } or throws
 */
export async function getAuthUser(request: NextRequest) {
  const authorization = request.headers.get('Authorization')

  if (!authorization || !authorization.startsWith('Bearer ')) {
    throw new AuthError(401, '인증 토큰이 필요합니다.')
  }

  const token = authorization.split(' ')[1]
  const supabase = createAnonClient()

  const { data, error } = await supabase.auth.getUser(token)

  if (error || !data.user) {
    throw new AuthError(401, '유효하지 않은 토큰입니다.')
  }

  return { user: data.user, token }
}

export class AuthError extends Error {
  constructor(
    public status: number,
    message: string
  ) {
    super(message)
    this.name = 'AuthError'
  }
}
