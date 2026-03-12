/**
 * Supabase Client
 * Frontend Supabase 클라이언트 설정
 */

import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error(
    'Missing Supabase environment variables. Please set NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY'
  )
}

/**
 * Supabase 클라이언트 인스턴스
 */
export const supabase = createClient(supabaseUrl, supabaseAnonKey)

/**
 * 현재 세션 가져오기
 */
export async function getSession() {
  const { data: { session } } = await supabase.auth.getSession()
  return session
}

/**
 * 현재 사용자 가져오기
 */
export async function getUser() {
  const { data: { user } } = await supabase.auth.getUser()
  return user
}

/**
 * 로그아웃
 */
export async function signOut() {
  const { error } = await supabase.auth.signOut()
  if (error) throw error
}
