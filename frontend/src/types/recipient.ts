/**
 * 다이어리 대상자 타입 정의
 */

export interface Recipient {
  id: string
  owner_id: string
  name: string
  birth_date: string        // YYYY-MM-DD
  birth_time: string        // HH:MM:SS
  gender: 'male' | 'female' | 'other'
  birth_place: string
  role: string              // 'student' | 'office_worker' | 'freelancer'
  relationship?: string     // 'self' | 'child' | 'spouse' | 'parent' | 'client' | 'friend'
  notes?: string
  diary_period: string      // 'monthly' | 'quarterly' | 'yearly'
  is_default: boolean
  created_at: string
  updated_at: string
}

export interface RecipientCreate {
  name: string
  birth_date: string
  birth_time?: string
  gender: 'male' | 'female' | 'other'
  birth_place?: string
  role?: string
  relationship?: string
  notes?: string
  diary_period?: string
  is_default?: boolean
}

export interface RecipientUpdate {
  name?: string
  birth_date?: string
  birth_time?: string
  gender?: 'male' | 'female' | 'other'
  birth_place?: string
  role?: string
  relationship?: string
  notes?: string
  diary_period?: string
  is_default?: boolean
}
