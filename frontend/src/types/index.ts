/**
 * TypeScript Type Definitions
 * Frontend 전역 타입 정의
 */

// ============================================================================
// Enums
// ============================================================================

export enum Gender {
  MALE = "male",
  FEMALE = "female"
}

export enum Role {
  STUDENT = "student",
  OFFICE_WORKER = "office_worker",
  FREELANCER = "freelancer"
}

export type DiaryPeriod = '3months' | '6months' | '1year' | 'custom'

// ============================================================================
// Auth Types
// ============================================================================

export interface AuthResponse {
  access_token?: string
  refresh_token?: string
  user_id: string
  email: string
  requires_email_confirmation?: boolean
  message?: string
}

export interface SignUpRequest {
  email: string
  password: string
  name: string
}

export interface LoginRequest {
  email: string
  password: string
}

// ============================================================================
// Profile Types
// ============================================================================

export interface Profile {
  id: string
  name: string
  birth_date: string  // ISO date string
  birth_time: string  // ISO time string
  gender: Gender
  birth_place: string
  roles: Role[]
  preferences?: Record<string, unknown>
  created_at: string
  updated_at: string
}

export interface ProfileCreate {
  name: string
  birth_date: string
  birth_time: string
  gender: Gender
  birth_place: string
  roles: Role[]
  preferences?: Record<string, unknown>
}

export interface ProfileUpdate {
  name?: string
  birth_date?: string
  birth_time?: string
  gender?: Gender
  birth_place?: string
  roles?: Role[]
  preferences?: Record<string, unknown>
}

// ============================================================================
// Content Types (re-exported from canonical source)
// ============================================================================

import type {
  DailyContent,
  MonthlyContent,
  YearlyContent,
  MonthlySignal,
  FocusCaution,
  ActionGuide,
  TimeDirection,
  StateTrigger,
  QimenTimeSlot,
} from '@/lib/content/types'

export type {
  DailyContent,
  MonthlyContent,
  YearlyContent,
  MonthlySignal,
  FocusCaution,
  ActionGuide,
  TimeDirection,
  StateTrigger,
  QimenTimeSlot,
}

export interface DailyContentResponse {
  date: string
  role: Role | null
  content: DailyContent
  qimen_slots?: QimenTimeSlot[]
  best_direction?: string
  avoid_direction?: string
  peak_hours?: string
}

export interface DailyMarkdownResponse {
  date: string
  role: Role | null
  markdown: string
}

export interface MonthlyContentResponse {
  year: number
  month: number
  role: Role | null
  content: MonthlyContent
}

export interface YearlyContentResponse {
  year: number
  role: Role | null
  content: YearlyContent
}

// ============================================================================
// Daily Log Types
// ============================================================================

export interface DailyLog {
  id: string
  profile_id: string
  date: string
  schedule?: string
  todos?: string[]
  mood?: number  // 1-5
  energy?: number  // 1-5
  notes?: string
  gratitude?: string
  created_at: string
  updated_at: string
}

export interface DailyLogCreate {
  date: string
  schedule?: string
  todos?: string[]
  mood?: number
  energy?: number
  notes?: string
  gratitude?: string
}

export interface DailyLogUpdate {
  schedule?: string
  todos?: string[]
  mood?: number
  energy?: number
  notes?: string
  gratitude?: string
}

// ============================================================================
// API Response Types
// ============================================================================

export interface SuccessResponse {
  success: boolean
  message: string
}

export interface ErrorResponse {
  success: boolean
  error: string
  details?: string
}

// ============================================================================
// UI State Types
// ============================================================================

export interface AuthState {
  user: AuthResponse | null
  isAuthenticated: boolean
  isLoading: boolean
}

export interface ProfileState {
  profile: Profile | null
  isLoading: boolean
  error: string | null
}

export interface ContentState {
  dailyContent: DailyContentResponse | null
  selectedRole: Role | null
  isLoading: boolean
  error: string | null
}
