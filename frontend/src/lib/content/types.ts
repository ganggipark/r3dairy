/**
 * Content System Types
 *
 * 사주 분석 + 콘텐츠 조합 + 역할 번역에 사용되는 타입 정의
 */

// ============================================================
// 기본 입력 타입
// ============================================================

export interface BirthInfo {
  name: string
  birthDate: string // YYYY-MM-DD
  birthTime: string // HH:mm
  gender: 'male' | 'female'
  birthPlace: string
}

// ============================================================
// 사주 데이터 (내부 구조화된 결과)
// ============================================================

export interface PillarData {
  천간: string
  지지: string
  간지: string
}

export interface SajuData {
  사주: {
    년주: PillarData
    월주: PillarData
    일주: PillarData
    시주: PillarData
  }
  오행: Record<string, number>
  십성: Record<string, number>
  격국: {
    일간: string
    일간오행: string
    강약: string
    계절: string
  }
  용신: {
    용신: string[]
    기신: string[]
  }
  대운: {
    startAge: number
    direction: '순행' | '역행'
    list: Array<{
      cycle: number
      startAge: number
      endAge: number
      gan: string
      ji: string
      ganJi: string
      ohHaeng: string
      score: number
      description: string
      isYongSin: boolean
      isGiSin: boolean
    }>
    current: {
      cycle: number
      startAge: number
      endAge: number
      gan: string
      ji: string
      ganJi: string
      ohHaeng: string
      score: number
      description: string
      isYongSin: boolean
      isGiSin: boolean
    } | null
    currentAge: number
    bestPeriod: { gan: string; ji: string; ganJi: string; startAge: number; endAge: number; score: number } | null
    worstPeriod: { gan: string; ji: string; ganJi: string; startAge: number; endAge: number; score: number } | null
  } | null
  세운: {
    year: number
    age: number
    gan: string
    ji: string
    ganJi: string
    ohHaeng: string
    animal: string
    score: number
    description: string
    isYongSin: boolean
    daewoonInteraction: number
  } | null
  신살: {
    gilSin: string[]
    hyungSin: string[]
    hasCheonEulGuiIn: boolean
    hasMunChangGuiIn: boolean
    hasYeokMaSal: boolean
    hasDoHwaSal: boolean
    hasGongMang: boolean
    hasYangInSal: boolean
    hasGeopSal: boolean
    summary: string
  } | null
  성격: {
    dayMasterTraits: {
      keyword: string
      strengths: string[]
      weaknesses: string[]
      advice: string
    }
    dominantSipsung: {
      type: string
      traits: string[]
    }
    careerAptitude: string[]
    relationshipStyle: string
  } | null
  원본데이터: Record<string, unknown>
}

// ============================================================
// 일간 리듬 분석 결과
// ============================================================

export interface DailyRhythm {
  에너지_수준: number
  집중력: number
  사회운: number
  결정력: number
  유리한_시간: string[]
  주의_시간: string[]
  유리한_방향: string[]
  주요_흐름: string
  기회_요소: string[]
  도전_요소: string[]
  격국: {
    일간: string
    일간오행: string
    강약: string
    계절: string
  } | Record<string, string>
  세운점수: number
  일진: {
    천간: string
    지지: string
    관계: string
  }
}

// ============================================================
// 월간 리듬 분석 결과
// ============================================================

export interface MonthlyRhythm {
  년월: string
  주제: string
  우선순위: string[]
  일별_에너지: Record<number, number>
  기회_요소: string[]
  도전_요소: string[]
  월주_정보: {
    천간: string
    지지: string
    간지: string
  }
  전체_흐름: string
}

// ============================================================
// 연간 리듬 분석 결과
// ============================================================

export interface YearlyRhythm {
  년도: number
  주제: string
  대운_정보: {
    cycle: number
    startAge: number
    endAge: number
    gan: string
    ji: string
    ganJi: string
    ohHaeng: string
    score: number
    description: string
    isYongSin: boolean
    isGiSin: boolean
  } | null
  세운_정보: {
    year: number
    age: number
    gan: string
    ji: string
    ganJi: string
    ohHaeng: string
    animal: string
    score: number
    description: string
    isYongSin: boolean
    daewoonInteraction: number
  } | null
  월별_신호: Record<number, { 월: number; 테마: string; 에너지: number }>
  용신: string[]
  기신: string[]
  전체_흐름: string
  핵심_과제: string[]
}

// ============================================================
// 콘텐츠 출력 타입
// ============================================================

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

export interface QimenTimeSlot {
  hour_start: number    // 시작 시각 (0-23)
  hour_end: number      // 종료 시각 (2-25)
  quality: 'good' | 'neutral' | 'avoid'
  direction: string     // 한국어 방위 (예: "북동")
  direction_en: string  // 영문 코드 (예: "NE")
  energy_level: number  // 1-10
  label: string         // 사용자 노출 라벨
}

export interface HealthSports {
  recommended_activities: string[]
  health_tips: string[]
  wellness_focused: string[]
  explanation: string
}

export interface MealNutrition {
  flavor_profile: string[]
  recommended_foods: string[]
  avoid_foods: string[]
  explanation: string
}

export interface FashionBeauty {
  clothing_style: string[]
  color_suggestions: string[]
  beauty_tips: string[]
  explanation: string
}

export interface ShoppingFinance {
  good_to_buy: string[]
  finance_advice: string[]
  investment_focus: string[]
  explanation: string
}

export interface LivingSpace {
  space_organization: string[]
  plants_decor: string[]
  environmental_tips: string[]
  explanation: string
}

export interface DailyRoutines {
  sleep_schedule: string[]
  morning_routine: string[]
  evening_routine: string[]
  explanation: string
}

export interface DigitalCommunication {
  device_usage: string[]
  social_media: string[]
  online_focus_areas: string[]
  explanation: string
}

export interface HobbiesCreativity {
  creative_activities: string[]
  learning_recommendations: string[]
  entertainment_options: string[]
  explanation: string
}

export interface RelationshipsSocial {
  communication_style: string[]
  social_energies: string[]
  relationship_tips: string[]
  explanation: string
}

export interface SeasonalEnvironment {
  weather_adaptation: string[]
  seasonal_activities: string[]
  environmental_focus: string[]
  explanation: string
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
  daily_health_sports: HealthSports
  daily_meal_nutrition: MealNutrition
  daily_fashion_beauty: FashionBeauty
  daily_shopping_finance: ShoppingFinance
  daily_living_space: LivingSpace
  daily_routines: DailyRoutines
  digital_communication: DigitalCommunication
  hobbies_creativity: HobbiesCreativity
  relationships_social: RelationshipsSocial
  seasonal_environment: SeasonalEnvironment
  fourPillars: Record<string, { heavenlyStem: string; earthlyBranch: string; gan: string; ji: string }> | null
  gyeokGuk: { dayMaster: string; strength: string; monthBranch: string; season: string } | null
  yongSin: { yongSin: string[] } | null
  // Extended saju fields (optional — only present when extra data is available)
  saju_summary?: string
  sinsal_influence?: string
  direction_detail?: string
  palace_insight?: string
  yongsin_utilization?: string
  daewoon_entry?: string
  sewon_summary?: string
  // 기문둔갑 시간/방위 데이터 (optional — structured qimen data)
  qimen_slots?: QimenTimeSlot[]
  best_direction?: string
  avoid_direction?: string
  peak_hours?: string
}

export interface MonthlyContent {
  year_month: string
  theme: string
  priorities: string[]
  calendar_data: Record<number, number>
  opportunities: string[]
  challenges: string[]
  summary: string
  keywords: string[]
  weekly_focus: string[]
  weekly_caution: string[]
  flow_description: string
}

export interface MonthlySignal {
  month: number
  theme: string
  energy: number
}

export interface YearlyContent {
  year: number
  theme: string
  flow_summary: string
  monthly_signals: Record<number, MonthlySignal>
  core_tasks: string[]
  summary: string
  keywords: string[]
  first_half_focus: string
  second_half_focus: string
}

// ============================================================
// 역할 타입
// ============================================================

export type UserRole = 'student' | 'office_worker' | 'freelancer'
