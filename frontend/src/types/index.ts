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

// ============================================================================
// Auth Types
// ============================================================================

export interface AuthResponse {
  access_token: string
  refresh_token: string
  user_id: string
  email: string
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
  preferences?: Record<string, any>
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
  preferences?: Record<string, any>
}

export interface ProfileUpdate {
  name?: string
  birth_date?: string
  birth_time?: string
  gender?: Gender
  birth_place?: string
  roles?: Role[]
  preferences?: Record<string, any>
}

// ============================================================================
// Content Types
// ============================================================================

export interface FocusCaution {
  focus: string[]
  caution: string[]
}

export interface ActionGuide {
  do: string[]
  avoid: string[]
}

export interface TimeDirection {
  good_time: string
  avoid_time: string
  good_direction: string
  avoid_direction: string
  notes: string
}

export interface StateTrigger {
  gesture: string
  phrase: string
  how_to: string
}

export interface DailyContent {
  date: string
  summary: string
  keywords: string[]
  rhythm_description: string
  focus_caution: FocusCaution
  action_guide: ActionGuide
  time_direction: TimeDirection
  state_trigger: StateTrigger
  meaning_shift: string
  rhythm_question: string
}

export interface DailyContentResponse {
  date: string
  role: Role | null
  content: DailyContent
}

export interface MonthlyContentResponse {
  year: number
  month: number
  role: Role | null
  content: any  // TODO: MonthlyContent 타입 정의
}

export interface YearlyContentResponse {
  year: number
  role: Role | null
  content: any  // TODO: YearlyContent 타입 정의
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
