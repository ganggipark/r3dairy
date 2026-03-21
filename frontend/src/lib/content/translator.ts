/**
 * Role Translation Layer (TypeScript 포트)
 *
 * Python backend/src/translation/translator.py 로직을 TypeScript로 포팅.
 * 동일한 리듬 콘텐츠를 역할에 맞게 재표현합니다.
 * 의미는 동일하게 유지하되, 표현만 변경합니다.
 *
 * 지원 역할:
 * - student (학생): 학습/집중/페이스 관리
 * - office_worker (직장인): 업무/관계/결정/보고
 * - freelancer (프리랜서/자영업): 결정/계약/창작/체력
 */

import type { DailyContent, MonthlyContent, YearlyContent, UserRole } from './types'

// ============================================================
// 역할별 표현 매핑
// ============================================================

const ROLE_EXPRESSIONS: Record<UserRole, Record<string, string>> = {
  student: {
    // 활동 관련
    '활동': '공부',
    '프로젝트': '과제',
    '업무': '학습',
    '작업': '학습',
    '교류': '토론',
    '네트워킹': '스터디',
    // 시간 관련
    '일정': '수업',
    '약속': '모임',
    // 결과 관련
    '성과': '성적',
    '결과물': '과제물',
    '보고': '발표',
    // 에너지 관련
    '체력': '집중력',
    '에너지': '학습 의욕',
  },

  office_worker: {
    // 활동 관련
    '학습': '업무',
    '과제': '프로젝트',
    '토론': '회의',
    '스터디': '협업',
    // 시간 관련
    '수업': '일정',
    '모임': '미팅',
    // 결과 관련
    '성적': '성과',
    '과제물': '결과물',
    '발표': '보고',
    // 관계 관련
    '친구': '동료',
    '선생님': '상사',
    // 결정/에너지 관련
    '결정': '판단',
    '에너지': '업무 집중도',
  },

  freelancer: {
    // 활동 관련
    '업무': '작업',
    '과제': '의뢰',
    '회의': '미팅',
    '협업': '파트너십',
    // 시간 관련
    '일정': '스케줄',
    '수업': '워크숍',
    // 결과 관련
    '성과': '수익',
    '결과물': '납품물',
    '보고': '피드백',
    // 관계 관련
    '동료': '클라이언트',
    '상사': '발주처',
    // 결정 관련
    '결정': '계약',
    // 체력 관련
    '체력': '작업 에너지',
  },
}

// ============================================================
// 한국어 조사 유틸리티
// ============================================================

/**
 * 한국어 문자의 받침(종성) 유무 확인
 * @param char 한글 문자 1개
 * @returns true if the character has a final consonant (받침)
 */
function hasBatchim(char: string): boolean {
  const code = char.charCodeAt(0)
  // 한글 유니코드 범위: 0xAC00 ~ 0xD7A3
  if (code < 0xAC00 || code > 0xD7A3) return false
  // (code - 0xAC00) % 28 === 0 means no batchim
  return (code - 0xAC00) % 28 !== 0
}

/**
 * 대체된 단어 뒤의 조사를 받침에 맞게 조정
 *
 * 조사 쌍:
 * - 은/는 (topic marker)
 * - 이/가 (subject marker)
 * - 을/를 (object marker)
 * - 으로/로 (direction/method marker)
 * - 과/와 (and)
 *
 * 주의: 이/가 패턴은 한글 직후에만 적용하여 일반 단어 오염 방지
 */
function adaptJosa(text: string): string {
  // 조사 쌍 정의: [받침 있을 때, 받침 없을 때]
  // 이/가는 오탐이 많아 별도로 신중하게 처리
  const josaPairs: [string, string][] = [
    ['은', '는'],
    ['을', '를'],
    ['으로', '로'],
    ['과', '와'],
  ]

  let result = text

  for (const [withBatchim, withoutBatchim] of josaPairs) {
    const escWith = withBatchim.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
    const escWithout = withoutBatchim.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
    const followBoundary = '(?=[\\s\\.,!?;:\\)\\]\\}가-힣]|$)'

    // 받침 없는 글자 + 받침 있는 조사 → 받침 없는 조사로 교정
    const patternWrong1 = new RegExp(`([가-힣])${escWith}${followBoundary}`, 'g')
    result = result.replace(patternWrong1, (match, prevChar) => {
      if (!hasBatchim(prevChar)) {
        return prevChar + withoutBatchim
      }
      return match
    })

    // 받침 있는 글자 + 받침 없는 조사 → 받침 있는 조사로 교정
    const patternWrong2 = new RegExp(`([가-힣])${escWithout}${followBoundary}`, 'g')
    result = result.replace(patternWrong2, (match, prevChar) => {
      if (hasBatchim(prevChar)) {
        return prevChar + withBatchim
      }
      return match
    })
  }

  // 이/가 는 오탐 위험이 높으므로 별도 보수적 처리:
  // 받침 없는 글자 + 이 → 가 (단, 뒤가 공백/문장부호/문자열 끝인 경우만)
  result = result.replace(/([가-힣])이(?=[\s\.,!?;:\)\]\}]|$)/g, (match, prevChar) => {
    if (!hasBatchim(prevChar)) return prevChar + '가'
    return match
  })
  // 받침 있는 글자 + 가 → 이 (단, 뒤가 공백/문장부호/문자열 끝인 경우만)
  result = result.replace(/([가-힣])가(?=[\s\.,!?;:\)\]\}]|$)/g, (match, prevChar) => {
    if (hasBatchim(prevChar)) return prevChar + '이'
    return match
  })

  return result
}

// ============================================================
// 텍스트 번역 함수
// ============================================================

/**
 * 텍스트 번역 (표현 매핑 적용)
 *
 * 한국어 단어 경계를 고려하여 치환합니다.
 * 앞뒤가 공백/문장부호/문자열 시작/끝인 경우에만 치환하여
 * "스타일", "일어나기" 같은 단어 내부 오염을 방지합니다.
 * 단어 치환 후 조사를 받침에 맞게 자동 조정합니다.
 */
function translateText(text: string, expressionMap: Record<string, string>): string {
  let translated = text

  // 긴 표현부터 먼저 치환 (부분 매치 방지)
  const sortedExpressions = Object.entries(expressionMap).sort(
    (a, b) => b[0].length - a[0].length,
  )

  // 단어 경계로 인정하는 문자들 (한국어 조사 포함)
  const boundary = '[\\s\\(\\[\\{\\u300C\\u300E\\u3010\\.,!?;:\\u00B7\\-]'
  // 한국어 조사: 을/를/이/가/은/는/에/에서/으로/로/와/과/의/도/만/까지/부터/처럼/보다
  // 긴 조사가 짧은 접두사보다 먼저 매칭되도록 정렬 (에서 before 에, 으로 before 로)
  const koreanJosa = '(?:에서|으로|까지|부터|처럼|보다|을|를|이|가|은|는|에|로|와|과|의|도|만)?'

  for (const [originalExpr, roleExpr] of sortedExpressions) {
    // 앞: 문자열 시작 또는 경계 문자 (캡처 그룹으로 유지)
    // 뒤: 조사(옵션) + 문자열 끝 또는 경계 문자 (lookahead)
    const escapedOriginal = originalExpr.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
    const pattern = new RegExp(
      `(^|${boundary})${escapedOriginal}(?=${koreanJosa}(?:${boundary}|$))`,
      'gm',
    )
    translated = translated.replace(pattern, `$1${roleExpr}`)
  }

  // 조사 적응 적용 (단어 교체 후)
  translated = adaptJosa(translated)

  return translated
}

/**
 * 질문 번역 (역할별 맥락 추가)
 */
function translateQuestion(
  question: string,
  expressionMap: Record<string, string>,
  _targetRole: UserRole,
): string {
  // 기본 번역 적용
  const translated = translateText(question, expressionMap)

  // 역할별 맥락 추가 (현재는 불필요)
  const roleContexts: Record<UserRole, string> = {
    student: '',
    office_worker: '',
    freelancer: '',
  }

  const context = roleContexts[_targetRole] || ''
  if (context) {
    return `${translated} ${context}`
  }

  return translated
}

// ============================================================
// 문자열 배열 번역 헬퍼
// ============================================================

function translateStringArray(items: string[], expressionMap: Record<string, string>): string[] {
  return items.map(item => typeof item === 'string' ? translateText(item, expressionMap) : item)
}

// ============================================================
// 일간 콘텐츠 번역
// ============================================================

/**
 * 일간 콘텐츠를 역할에 맞게 번역
 *
 * @param content 원본 일간 콘텐츠 (중립적 표현)
 * @param targetRole 대상 역할
 * @returns 역할에 맞게 변환된 콘텐츠
 */
export function translateDailyContent(
  content: DailyContent,
  targetRole: UserRole,
): DailyContent {
  if (!ROLE_EXPRESSIONS[targetRole]) {
    return content
  }

  // Deep copy
  const translated: DailyContent = JSON.parse(JSON.stringify(content))
  const map = ROLE_EXPRESSIONS[targetRole]

  // 1. Summary
  translated.summary = translateText(translated.summary, map)

  // 2. Keywords
  translated.keywords = translateStringArray(translated.keywords, map)

  // 3. Rhythm Description
  translated.rhythm_description = translateText(translated.rhythm_description, map)

  // 4. Focus/Caution
  translated.focus_caution.focus = translateStringArray(translated.focus_caution.focus, map)
  translated.focus_caution.caution = translateStringArray(translated.focus_caution.caution, map)

  // 5. Action Guide
  translated.action_guide.do = translateStringArray(translated.action_guide.do, map)
  translated.action_guide.avoid = translateStringArray(translated.action_guide.avoid, map)

  // 6. Time/Direction notes
  translated.time_direction.notes = translateText(translated.time_direction.notes, map)

  // 7. State Trigger
  translated.state_trigger.gesture = translateText(translated.state_trigger.gesture, map)
  translated.state_trigger.phrase = translateText(translated.state_trigger.phrase, map)
  translated.state_trigger.how_to = translateText(translated.state_trigger.how_to, map)

  // 8. Meaning Shift
  translated.meaning_shift = translateText(translated.meaning_shift, map)

  // 9. Rhythm Question
  translated.rhythm_question = translateQuestion(translated.rhythm_question, map, targetRole)

  // 10. Daily Health Sports
  if (translated.daily_health_sports) {
    const block = translated.daily_health_sports
    block.recommended_activities = translateStringArray(block.recommended_activities, map)
    block.health_tips = translateStringArray(block.health_tips, map)
    block.wellness_focused = translateStringArray(block.wellness_focused, map)
    block.explanation = translateText(block.explanation, map)
  }

  // 11. Daily Meal Nutrition
  if (translated.daily_meal_nutrition) {
    const block = translated.daily_meal_nutrition
    block.flavor_profile = translateStringArray(block.flavor_profile, map)
    block.recommended_foods = translateStringArray(block.recommended_foods, map)
    block.avoid_foods = translateStringArray(block.avoid_foods, map)
    block.explanation = translateText(block.explanation, map)
  }

  // 12. Daily Fashion Beauty
  if (translated.daily_fashion_beauty) {
    const block = translated.daily_fashion_beauty
    block.clothing_style = translateStringArray(block.clothing_style, map)
    block.color_suggestions = translateStringArray(block.color_suggestions, map)
    block.beauty_tips = translateStringArray(block.beauty_tips, map)
    block.explanation = translateText(block.explanation, map)
  }

  // 13. Daily Shopping Finance
  if (translated.daily_shopping_finance) {
    const block = translated.daily_shopping_finance
    block.good_to_buy = translateStringArray(block.good_to_buy, map)
    block.finance_advice = translateStringArray(block.finance_advice, map)
    block.investment_focus = translateStringArray(block.investment_focus, map)
    block.explanation = translateText(block.explanation, map)
  }

  // 14. Daily Living Space
  if (translated.daily_living_space) {
    const block = translated.daily_living_space
    block.space_organization = translateStringArray(block.space_organization, map)
    block.plants_decor = translateStringArray(block.plants_decor, map)
    block.environmental_tips = translateStringArray(block.environmental_tips, map)
    block.explanation = translateText(block.explanation, map)
  }

  // 15. Daily Routines
  if (translated.daily_routines) {
    const block = translated.daily_routines
    block.sleep_schedule = translateStringArray(block.sleep_schedule, map)
    block.morning_routine = translateStringArray(block.morning_routine, map)
    block.evening_routine = translateStringArray(block.evening_routine, map)
    block.explanation = translateText(block.explanation, map)
  }

  // 16. Digital Communication
  if (translated.digital_communication) {
    const block = translated.digital_communication
    block.device_usage = translateStringArray(block.device_usage, map)
    block.social_media = translateStringArray(block.social_media, map)
    block.online_focus_areas = translateStringArray(block.online_focus_areas, map)
    block.explanation = translateText(block.explanation, map)
  }

  // 17. Hobbies Creativity
  if (translated.hobbies_creativity) {
    const block = translated.hobbies_creativity
    block.creative_activities = translateStringArray(block.creative_activities, map)
    block.learning_recommendations = translateStringArray(block.learning_recommendations, map)
    block.entertainment_options = translateStringArray(block.entertainment_options, map)
    block.explanation = translateText(block.explanation, map)
  }

  // 18. Relationships Social
  if (translated.relationships_social) {
    const block = translated.relationships_social
    block.communication_style = translateStringArray(block.communication_style, map)
    block.social_energies = translateStringArray(block.social_energies, map)
    block.relationship_tips = translateStringArray(block.relationship_tips, map)
    block.explanation = translateText(block.explanation, map)
  }

  // 19. Seasonal Environment
  if (translated.seasonal_environment) {
    const block = translated.seasonal_environment
    block.weather_adaptation = translateStringArray(block.weather_adaptation, map)
    block.seasonal_activities = translateStringArray(block.seasonal_activities, map)
    block.environmental_focus = translateStringArray(block.environmental_focus, map)
    block.explanation = translateText(block.explanation, map)
  }

  return translated
}

// ============================================================
// 월간 콘텐츠 번역
// ============================================================

/**
 * 월간 콘텐츠를 역할에 맞게 번역
 */
export function translateMonthlyContent(
  content: MonthlyContent,
  targetRole: UserRole,
): MonthlyContent {
  if (!ROLE_EXPRESSIONS[targetRole]) return content

  const translated: MonthlyContent = JSON.parse(JSON.stringify(content))
  const map = ROLE_EXPRESSIONS[targetRole]

  if (typeof translated.theme === 'string') {
    translated.theme = translateText(translated.theme, map)
  }

  if (Array.isArray(translated.priorities)) {
    translated.priorities = translateStringArray(translated.priorities, map)
  }

  if (Array.isArray(translated.opportunities)) {
    translated.opportunities = translateStringArray(translated.opportunities, map)
  }

  if (Array.isArray(translated.challenges)) {
    translated.challenges = translateStringArray(translated.challenges, map)
  }

  if (typeof translated.summary === 'string') {
    translated.summary = translateText(translated.summary, map)
  }

  if (Array.isArray(translated.keywords)) {
    translated.keywords = translateStringArray(translated.keywords, map)
  }

  if (Array.isArray(translated.weekly_focus)) {
    translated.weekly_focus = translateStringArray(translated.weekly_focus, map)
  }

  if (Array.isArray(translated.weekly_caution)) {
    translated.weekly_caution = translateStringArray(translated.weekly_caution, map)
  }

  if (typeof translated.flow_description === 'string') {
    translated.flow_description = translateText(translated.flow_description, map)
  }

  return translated
}

// ============================================================
// 연간 콘텐츠 번역
// ============================================================

/**
 * 연간 콘텐츠를 역할에 맞게 번역
 */
export function translateYearlyContent(
  content: YearlyContent,
  targetRole: UserRole,
): YearlyContent {
  if (!ROLE_EXPRESSIONS[targetRole]) return content

  const translated: YearlyContent = JSON.parse(JSON.stringify(content))
  const map = ROLE_EXPRESSIONS[targetRole]

  if (typeof translated.theme === 'string') {
    translated.theme = translateText(translated.theme, map)
  }

  if (typeof translated.flow_summary === 'string') {
    translated.flow_summary = translateText(translated.flow_summary, map)
  }

  if (Array.isArray(translated.core_tasks)) {
    translated.core_tasks = translateStringArray(translated.core_tasks, map)
  }

  if (typeof translated.summary === 'string') {
    translated.summary = translateText(translated.summary, map)
  }

  if (Array.isArray(translated.keywords)) {
    translated.keywords = translateStringArray(translated.keywords, map)
  }

  if (typeof translated.first_half_focus === 'string') {
    translated.first_half_focus = translateText(translated.first_half_focus, map)
  }

  if (typeof translated.second_half_focus === 'string') {
    translated.second_half_focus = translateText(translated.second_half_focus, map)
  }

  return translated
}

// ============================================================
// 의미 불변성 검증
// ============================================================

/**
 * 의미 불변성 검증
 *
 * 원본과 번역본이 구조적으로 동일한지 확인
 */
export function validateSemanticPreservation(
  original: DailyContent,
  translated: DailyContent,
): { valid: boolean; issues: string[] } {
  const issues: string[] = []

  // 1. 날짜 동일 확인
  if (original.date !== translated.date) {
    issues.push('날짜가 다릅니다')
  }

  // 2. 키워드 개수 확인
  if (original.keywords.length !== translated.keywords.length) {
    issues.push(
      `키워드 개수 불일치: ${original.keywords.length} vs ${translated.keywords.length}`,
    )
  }

  // 3. Focus/Caution 개수 확인
  if (original.focus_caution.focus.length !== translated.focus_caution.focus.length) {
    issues.push('집중 포인트 개수 불일치')
  }
  if (original.focus_caution.caution.length !== translated.focus_caution.caution.length) {
    issues.push('주의 포인트 개수 불일치')
  }

  // 4. Action Guide 개수 확인
  if (original.action_guide.do.length !== translated.action_guide.do.length) {
    issues.push('추천 행동 개수 불일치')
  }
  if (original.action_guide.avoid.length !== translated.action_guide.avoid.length) {
    issues.push('피할 행동 개수 불일치')
  }

  // 5. 콘텐츠 길이 비교 (+/-30% 이내)
  const origLen = calculateContentLength(original)
  const transLen = calculateContentLength(translated)

  if (origLen > 0) {
    const ratio = Math.abs(transLen - origLen) / origLen
    if (ratio > 0.3) {
      issues.push(
        `콘텐츠 길이 차이가 30%를 초과합니다: ${origLen} -> ${transLen} (${(ratio * 100).toFixed(1)}%)`,
      )
    }
  }

  // 6. 핵심 블록 존재 여부
  if (!translated.rhythm_description) issues.push('리듬 해설이 비어있습니다')
  if (!translated.meaning_shift) issues.push('의미 전환이 비어있습니다')
  if (!translated.rhythm_question) issues.push('리듬 질문이 비어있습니다')

  return { valid: issues.length === 0, issues }
}

function calculateContentLength(content: DailyContent): number {
  let total = 0

  total += (content.summary || '').length
  total += (content.rhythm_description || '').length
  total += (content.meaning_shift || '').length
  total += (content.rhythm_question || '').length

  // Focus/Caution
  for (const item of content.focus_caution?.focus || []) total += item.length
  for (const item of content.focus_caution?.caution || []) total += item.length

  // Action Guide
  for (const item of content.action_guide?.do || []) total += item.length
  for (const item of content.action_guide?.avoid || []) total += item.length

  // State Trigger
  total += (content.state_trigger?.how_to || '').length

  return total
}
