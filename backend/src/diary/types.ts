/**
 * 다이어리 페이로드 타입 정의
 * 
 * 하루치 다이어리 데이터를 표준화된 JSON 형식으로 정의
 */

// ============================================================
// Calendar Section Types
// ============================================================

export interface CalendarInfo {
  /** 양력 날짜 (YYYY-MM-DD) */
  solarDate: string;
  /** 요일 (월, 화, 수, 목, 금, 토, 일) */
  weekday: string;
  /** 음력 날짜 정보 */
  lunarDate: LunarDateInfo | null;
  /** 절기 정보 */
  solarTerm?: string;
  /** 특별한 날 (공휴일 등) */
  specialDay?: string;
}

export interface LunarDateInfo {
  /** 음력 년 */
  year: number;
  /** 음력 월 */
  month: number;
  /** 음력 일 */
  day: number;
  /** 윤달 여부 */
  isLeapMonth: boolean;
  /** 음력 날짜 문자열 표현 */
  displayText: string;
}

// ============================================================
// Saju Section Types
// ============================================================

export interface SajuInfo {
  /** 사주 팔자 */
  pillars: FourPillars;
  /** 일주 (일간) */
  dayMaster: string;
  /** 사주 요약 */
  summary: SajuSummary;
  /** 주요 영역별 분석 */
  domains: SajuDomains;
  /** 운세 레이어 (대운, 세운, 월운, 일운) */
  fortuneLayers: FortuneLayers | null;
}

export interface FourPillars {
  /** 년주 */
  year: Pillar | null;
  /** 월주 */
  month: Pillar | null;
  /** 일주 */
  day: Pillar;
  /** 시주 */
  hour: Pillar | null;
}

export interface Pillar {
  /** 천간 */
  heavenlyStem: string;
  /** 지지 */
  earthlyBranch: string;
  /** 간지 조합 */
  combined: string;
  /** 오행 속성 */
  element?: string;
}

export interface SajuSummary {
  /** 주요 특성 */
  mainCharacteristics: string[];
  /** 오행 분포 */
  elementBalance: {
    wood: number;
    fire: number;
    earth: number;
    metal: number;
    water: number;
  };
  /** 강약 판단 */
  dayMasterStrength: 'strong' | 'weak' | 'balanced';
}

export interface SajuDomains {
  /** 건강운 */
  health: DomainAnalysis;
  /** 재물운 */
  wealth: DomainAnalysis;
  /** 관계운 */
  relationship: DomainAnalysis;
  /** 사업/직업운 */
  career: DomainAnalysis;
}

export interface DomainAnalysis {
  /** 점수 (0-100) */
  score: number;
  /** 상태 */
  status: 'excellent' | 'good' | 'neutral' | 'caution' | 'warning';
  /** 조언 */
  advice: string;
}

export interface FortuneLayers {
  /** 대운 (10년 운) */
  majorFortune?: FortuneInfo;
  /** 세운 (연운) */
  yearlyFortune?: FortuneInfo;
  /** 월운 */
  monthlyFortune?: FortuneInfo;
  /** 일운 */
  dailyFortune?: FortuneInfo;
}

export interface FortuneInfo {
  /** 간지 */
  stemBranch: string;
  /** 시작 시기 */
  startPeriod: string;
  /** 종료 시기 */
  endPeriod: string;
  /** 영향도 */
  influence: 'positive' | 'neutral' | 'negative';
  /** 설명 */
  description: string;
}

// ============================================================
// QiMen Section Types
// ============================================================

export interface QimenInfo {
  /** 하루 전체 요약 */
  dailySummary: QimenDailySummary;
  /** 시간대별 분석 (12시진) */
  hourlyAnalysis: HourlyQimen[];
  /** 최적 활동 */
  bestActivities: Activity[];
  /** 회피 활동 */
  avoidActivities: Activity[];
}

export interface QimenDailySummary {
  /** 최적 시간대 */
  bestHour: string;
  /** 최적 방향 */
  bestDirection: string;
  /** 회피 시간대 */
  avoidHour: string;
  /** 회피 방향 */
  avoidDirection: string;
  /** 전체 품질 */
  overallQuality: 'excellent' | 'good' | 'neutral' | 'caution';
  /** 하루 가이드 */
  guidance: string;
}

export interface HourlyQimen {
  /** 시간대 (예: "09-11시") */
  timeSlot: string;
  /** 시지 (자, 축, 인, 묘...) */
  branch: string;
  /** 품질 */
  quality: 'good' | 'neutral' | 'avoid';
  /** 방향 */
  direction: string;
  /** 에너지 레벨 (1-10) */
  energyLevel: number;
  /** 설명 */
  description: string;
}

export interface Activity {
  /** 활동 유형 */
  type: string;
  /** 설명 */
  description: string;
  /** 우선순위 (1-5) */
  priority: number;
}

// ============================================================
// NLP Section Types
// ============================================================

export interface NlpContent {
  /** 오늘의 주제 */
  dailyTheme: string;
  /** 핵심 메시지 */
  coreMessage: string;
  /** 마음가짐 */
  mindset: MindsetGuide;
  /** 행동 가이드 */
  actionGuides: ActionGuide[];
  /** 성찰 질문 */
  reflectionQuestions: string[];
  /** 오늘의 명언 */
  dailyQuote?: Quote;
}

export interface MindsetGuide {
  /** 집중할 감정 */
  focusEmotion: string;
  /** 주의할 감정 */
  cautionEmotion: string;
  /** 감정 조절 팁 */
  emotionTip: string;
}

export interface ActionGuide {
  /** 시간대 */
  timeOfDay: 'morning' | 'afternoon' | 'evening';
  /** 추천 활동 */
  recommendation: string;
  /** 이유 */
  reason: string;
}

export interface Quote {
  /** 명언 내용 */
  text: string;
  /** 출처/저자 */
  author: string;
}

// ============================================================
// Page Layout Types (for Diary Display)
// ============================================================

export interface TimeSlot {
  /** 시간 (HH:mm) */
  time: string;
  /** 시간대 라벨 (예: "09-11시") */
  label: string;
  /** 기문 품질 정보 */
  qimenLabel?: string;
  /** 사용자 메모 공간 */
  note?: string;
}

export interface LeftPage {
  /** 사주 요약 */
  sajuSummary: SajuSummary;
  /** 운세 레이어 */
  fortuneLayers: FortuneLayers | null;
  /** 생활 영역별 분석 */
  lifeAreas: SajuDomains;
  /** 주의사항 */
  cautions: string[];
  /** 권장사항 */
  recommendations: string[];
}

export interface RightPage {
  /** 시간대별 슬롯 (일정 입력용) */
  timeSlots: TimeSlot[];
  /** 좋은 시간대 */
  goodHours: string[];
  /** 나쁜 시간대 */
  badHours: string[];
  /** 좋은 방향 */
  goodDirections: string[];
  /** 나쁜 방향 */
  badDirections: string[];
}

export interface BottomPanel {
  /** 마음가짐 */
  mindset: MindsetGuide;
  /** 일기 프롬프트 */
  journalPrompt: string[];
  /** 오늘의 확언 */
  affirmation: string;
}

// ============================================================
// Main Payload Type
// ============================================================

export interface DailyDiaryPayload {
  /** 날짜 (YYYY-MM-DD) */
  date: string;
  /** 생성 타임스탬프 */
  generatedAt: string;
  /** 버전 */
  version: string;
  /** 달력 정보 */
  calendar: CalendarInfo;
  /** 왼쪽 페이지 */
  leftPage: LeftPage;
  /** 오른쪽 페이지 */
  rightPage: RightPage;
  /** 하단 패널 */
  bottomPanel: BottomPanel;
  /** 메타데이터 */
  metadata?: {
    /** 사용자 ID */
    userId?: string;
    /** 생성 방식 */
    generationMethod: 'realtime' | 'batch' | 'cached';
    /** 캐시 만료 시간 */
    cacheExpiry?: string;
  };
}

// ============================================================
// Builder Input Types
// ============================================================

export interface BuilderInput {
  /** 대상 날짜 (YYYY-MM-DD) */
  date: string;
  /** 생년월일 정보 */
  birth?: BirthInfo;
  /** 옵션 */
  options?: BuilderOptions;
}

export interface BirthInfo {
  /** 년 */
  year: number;
  /** 월 (1-12) */
  month: number;
  /** 일 (1-31) */
  day: number;
  /** 시 (0-23) */
  hour?: number;
  /** 분 (0-59) */
  minute?: number;
  /** 양력/음력 구분 */
  isLunar?: boolean;
  /** 출생 지역 (진태양시 계산용) */
  birthPlace?: string;
}

export interface BuilderOptions {
  /** 사주 계산 포함 여부 */
  includeSaju?: boolean;
  /** 기문둔갑 계산 포함 여부 */
  includeQimen?: boolean;
  /** NLP 콘텐츠 생성 포함 여부 */
  includeNlp?: boolean;
  /** 운세 레이어 포함 여부 */
  includeFortuneLayers?: boolean;
  /** 언어 설정 */
  language?: 'ko' | 'en';
}