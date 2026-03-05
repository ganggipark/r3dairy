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

export interface QimenTimeSlot {
  hour_start: number    // 시작 시각 (0-23)
  hour_end: number      // 종료 시각 (2-25)
  quality: 'good' | 'neutral' | 'avoid'
  direction: string     // 한국어 방위 (예: "북동")
  direction_en: string  // 영문 코드 (예: "NE")
  energy_level: number  // 1-10
  label: string         // 사용자 노출 라벨
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
  // Extended content blocks (optional)
  saju_summary?: string
  sinsal_influence?: string
  direction_detail?: string
  palace_insight?: string
  yongsin_utilization?: string
  daewoon_entry?: string
  sewon_summary?: string
  // 사주 4기둥 데이터
  fourPillars?: {
    year?: { heavenlyStem?: string; earthlyBranch?: string; gan?: string; ji?: string }
    month?: { heavenlyStem?: string; earthlyBranch?: string; gan?: string; ji?: string }
    day?: { heavenlyStem?: string; earthlyBranch?: string; gan?: string; ji?: string }
    hour?: { heavenlyStem?: string; earthlyBranch?: string; gan?: string; ji?: string }
  }
  gyeokGuk?: {
    dayMaster?: string
    strength?: string
    monthBranch?: string
    season?: string
    [key: string]: any
  }
  yongSin?: {
    yongSin?: string[]
    [key: string]: any
  }
  // 기문둔갑 시간/방위 데이터 (구조화)
  qimen_slots?: QimenTimeSlot[]
  best_direction?: string
  avoid_direction?: string
  peak_hours?: string
}

export interface DailyContentResponse {
  date: string
  role: Role | null
  content: DailyContent
  qimen_slots?: QimenTimeSlot[]
  best_direction?: string
  avoid_direction?: string
}

export interface DailyMarkdownResponse {
  date: string
  role: Role | null
  markdown: string
}

export interface MonthlySignal {
  month: number
  theme: string
  energy: number
}

export interface MonthlyContent {
  year_month: string
  theme: string
  summary: string
  keywords: string[]
  priorities: string[]
  calendar_data: Record<number, number>
  opportunities: string[]
  challenges: string[]
  weekly_focus?: string[]
  weekly_caution?: string[]
  flow_description?: string
}

export interface YearlyContent {
  year: number
  theme: string
  summary: string
  keywords: string[]
  flow_summary: string
  monthly_signals: Record<number, MonthlySignal>
  core_tasks: string[]
  first_half_focus?: string
  second_half_focus?: string
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
