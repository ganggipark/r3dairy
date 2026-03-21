/**
 * generate-review-sample.ts
 *
 * 콘텐츠 리뷰용 샘플 마크다운 파일 생성 스크립트
 *
 * 사용법:
 *   npx tsx scripts/generate-review-sample.ts
 *
 * 테스트 프로필: 1971-11-17 04:00 남자 (양력)
 * 오늘 날짜부터 7일 연속으로 review-samples/YYYY-MM-DD.md 생성
 */

import * as fs from 'fs'
import * as path from 'path'

// 상대 경로로 import (@ alias 사용 불가 - Node.js 직접 실행)
import { calculateSaju, analyzeDailyFortune } from '../src/lib/content/saju-engine'
import { assembleDailyContent } from '../src/lib/content/assembly'
import { translateDailyContent } from '../src/lib/content/translator'
import type { BirthInfo, DailyContent, UserRole } from '../src/lib/content/types'

// ============================================================
// 테스트 프로필
// ============================================================

const TEST_PROFILE: BirthInfo = {
  name: '테스트',
  birthDate: '1971-11-17',
  birthTime: '04:00',
  gender: 'male',
  birthPlace: '서울',
}

const ROLES: UserRole[] = ['student', 'office_worker', 'freelancer']
const ROLE_LABELS: Record<UserRole, string> = {
  student: '학생',
  office_worker: '직장인',
  freelancer: '프리랜서',
}

// ============================================================
// 날짜 유틸리티
// ============================================================

function getDateString(offsetDays: number): string {
  const d = new Date()
  d.setDate(d.getDate() + offsetDays)
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

function getKoreanDateLabel(dateStr: string): string {
  const [y, m, d] = dateStr.split('-').map(Number)
  const date = new Date(y, m - 1, d)
  const weekdays = ['일', '월', '화', '수', '목', '금', '토']
  return `${y}년 ${m}월 ${d}일 (${weekdays[date.getDay()]})`
}

// ============================================================
// 콘텐츠 길이 계산
// ============================================================

function calcContentLength(content: DailyContent): number {
  let total = 0
  total += (content.summary || '').length
  total += (content.rhythm_description || '').length
  total += (content.meaning_shift || '').length
  total += (content.rhythm_question || '').length
  for (const item of content.focus_caution?.focus || []) total += item.length
  for (const item of content.focus_caution?.caution || []) total += item.length
  for (const item of content.action_guide?.do || []) total += item.length
  for (const item of content.action_guide?.avoid || []) total += item.length
  total += (content.state_trigger?.how_to || '').length
  total += (content.state_trigger?.gesture || '').length
  total += (content.state_trigger?.phrase || '').length
  total += (content.time_direction?.notes || '').length
  return total
}

// ============================================================
// 마크다운 생성
// ============================================================

function renderBlock(title: string, items: string | string[], emoji = ''): string {
  const header = emoji ? `### ${emoji} ${title}` : `### ${title}`
  if (typeof items === 'string') {
    return `${header}\n${items || '(없음)'}\n`
  }
  if (!items || items.length === 0) {
    return `${header}\n(없음)\n`
  }
  return `${header}\n${items.map(i => `- ${i}`).join('\n')}\n`
}

function renderContentSection(content: DailyContent, roleLabel: string): string {
  const lines: string[] = []

  lines.push(`## [${roleLabel}] 역할 번역`)
  lines.push('')

  // 1. 요약
  lines.push(renderBlock('01. 요약 (Summary)', content.summary, '📌'))

  // 2. 키워드
  lines.push(renderBlock('02. 키워드 (Keywords)', content.keywords, '🏷️'))

  // 3. 리듬 해설
  lines.push(renderBlock('03. 리듬 해설 (Rhythm Description)', content.rhythm_description, '🔄'))

  // 4. 집중 포인트
  lines.push(renderBlock('04. 집중 포인트 (Focus)', content.focus_caution?.focus || [], '🎯'))

  // 5. 주의 포인트
  lines.push(renderBlock('05. 주의 포인트 (Caution)', content.focus_caution?.caution || [], '⚠️'))

  // 6. 행동 가이드 - Do
  lines.push(renderBlock('06. 추천 행동 (Do)', content.action_guide?.do || [], '✅'))

  // 7. 행동 가이드 - Avoid
  lines.push(renderBlock('07. 피할 행동 (Avoid)', content.action_guide?.avoid || [], '🚫'))

  // 8. 시간/방향
  const td = content.time_direction
  if (td) {
    lines.push(`### ⏰ 08. 시간/방향 (Time & Direction)`)
    lines.push(`- 좋은 시간: ${td.good_time || '(없음)'}`)
    lines.push(`- 피할 시간: ${td.avoid_time || '(없음)'}`)
    lines.push(`- 좋은 방향: ${td.good_direction || '(없음)'}`)
    lines.push(`- 피할 방향: ${td.avoid_direction || '(없음)'}`)
    lines.push(`- 참고: ${td.notes || '(없음)'}`)
    lines.push('')
  }

  // 9. 상태 트리거
  const st = content.state_trigger
  if (st) {
    lines.push(`### 💡 09. 상태 트리거 (State Trigger)`)
    lines.push(`- 제스처: ${st.gesture || '(없음)'}`)
    lines.push(`- 문구: ${st.phrase || '(없음)'}`)
    lines.push(`- 방법: ${st.how_to || '(없음)'}`)
    lines.push('')
  }

  // 10. 의미 전환
  lines.push(renderBlock('10. 의미 전환 (Meaning Shift)', content.meaning_shift, '🔀'))

  // 11. 리듬 질문
  lines.push(renderBlock('11. 리듬 질문 (Rhythm Question)', content.rhythm_question, '❓'))

  // 12. 건강/운동
  if (content.daily_health_sports) {
    const h = content.daily_health_sports
    lines.push(`### 🏃 12. 건강/운동 (Health & Sports)`)
    lines.push(`- 추천 활동: ${h.recommended_activities?.join(', ') || '(없음)'}`)
    lines.push(`- 건강 팁: ${h.health_tips?.join(', ') || '(없음)'}`)
    lines.push(`- 웰니스: ${h.wellness_focused?.join(', ') || '(없음)'}`)
    lines.push(`- 설명: ${h.explanation || '(없음)'}`)
    lines.push('')
  }

  // 13. 식사/영양
  if (content.daily_meal_nutrition) {
    const m = content.daily_meal_nutrition
    lines.push(`### 🍽️ 13. 식사/영양 (Meal & Nutrition)`)
    lines.push(`- 맛 프로필: ${m.flavor_profile?.join(', ') || '(없음)'}`)
    lines.push(`- 추천 음식: ${m.recommended_foods?.join(', ') || '(없음)'}`)
    lines.push(`- 피할 음식: ${m.avoid_foods?.join(', ') || '(없음)'}`)
    lines.push(`- 설명: ${m.explanation || '(없음)'}`)
    lines.push('')
  }

  // 14. 패션/뷰티
  if (content.daily_fashion_beauty) {
    const f = content.daily_fashion_beauty
    lines.push(`### 👗 14. 패션/뷰티 (Fashion & Beauty)`)
    lines.push(`- 의상 스타일: ${f.clothing_style?.join(', ') || '(없음)'}`)
    lines.push(`- 색상 제안: ${f.color_suggestions?.join(', ') || '(없음)'}`)
    lines.push(`- 뷰티 팁: ${f.beauty_tips?.join(', ') || '(없음)'}`)
    lines.push(`- 설명: ${f.explanation || '(없음)'}`)
    lines.push('')
  }

  // 15. 쇼핑/재정
  if (content.daily_shopping_finance) {
    const s = content.daily_shopping_finance
    lines.push(`### 💰 15. 쇼핑/재정 (Shopping & Finance)`)
    lines.push(`- 구매 추천: ${s.good_to_buy?.join(', ') || '(없음)'}`)
    lines.push(`- 재정 조언: ${s.finance_advice?.join(', ') || '(없음)'}`)
    lines.push(`- 투자 집중: ${s.investment_focus?.join(', ') || '(없음)'}`)
    lines.push(`- 설명: ${s.explanation || '(없음)'}`)
    lines.push('')
  }

  // 16. 생활 공간
  if (content.daily_living_space) {
    const ls = content.daily_living_space
    lines.push(`### 🏠 16. 생활 공간 (Living Space)`)
    lines.push(`- 공간 정리: ${ls.space_organization?.join(', ') || '(없음)'}`)
    lines.push(`- 식물/인테리어: ${ls.plants_decor?.join(', ') || '(없음)'}`)
    lines.push(`- 환경 팁: ${ls.environmental_tips?.join(', ') || '(없음)'}`)
    lines.push(`- 설명: ${ls.explanation || '(없음)'}`)
    lines.push('')
  }

  // 17. 일상 루틴
  if (content.daily_routines) {
    const dr = content.daily_routines
    lines.push(`### ⏱️ 17. 일상 루틴 (Daily Routines)`)
    lines.push(`- 수면 스케줄: ${dr.sleep_schedule?.join(', ') || '(없음)'}`)
    lines.push(`- 아침 루틴: ${dr.morning_routine?.join(', ') || '(없음)'}`)
    lines.push(`- 저녁 루틴: ${dr.evening_routine?.join(', ') || '(없음)'}`)
    lines.push(`- 설명: ${dr.explanation || '(없음)'}`)
    lines.push('')
  }

  // 18. 디지털/커뮤니케이션
  if (content.digital_communication) {
    const dc = content.digital_communication
    lines.push(`### 📱 18. 디지털/커뮤니케이션 (Digital Communication)`)
    lines.push(`- 기기 사용: ${dc.device_usage?.join(', ') || '(없음)'}`)
    lines.push(`- 소셜 미디어: ${dc.social_media?.join(', ') || '(없음)'}`)
    lines.push(`- 온라인 집중: ${dc.online_focus_areas?.join(', ') || '(없음)'}`)
    lines.push(`- 설명: ${dc.explanation || '(없음)'}`)
    lines.push('')
  }

  // 19. 취미/창의성
  if (content.hobbies_creativity) {
    const hc = content.hobbies_creativity
    lines.push(`### 🎨 19. 취미/창의성 (Hobbies & Creativity)`)
    lines.push(`- 창의 활동: ${hc.creative_activities?.join(', ') || '(없음)'}`)
    lines.push(`- 학습 추천: ${hc.learning_recommendations?.join(', ') || '(없음)'}`)
    lines.push(`- 엔터테인먼트: ${hc.entertainment_options?.join(', ') || '(없음)'}`)
    lines.push(`- 설명: ${hc.explanation || '(없음)'}`)
    lines.push('')
  }

  // 20. 관계/사교 (relationships_social — 19번째 DailyContent 블록)
  if (content.relationships_social) {
    const rs = content.relationships_social
    lines.push(`### 🤝 20. 관계/사교 (Relationships & Social)`)
    lines.push(`- 소통 스타일: ${rs.communication_style?.join(', ') || '(없음)'}`)
    lines.push(`- 사교 에너지: ${rs.social_energies?.join(', ') || '(없음)'}`)
    lines.push(`- 관계 팁: ${rs.relationship_tips?.join(', ') || '(없음)'}`)
    lines.push(`- 설명: ${rs.explanation || '(없음)'}`)
    lines.push('')
  }

  // 21. 계절/환경 (seasonal_environment)
  if (content.seasonal_environment) {
    const se = content.seasonal_environment
    lines.push(`### 🌿 21. 계절/환경 (Seasonal Environment)`)
    lines.push(`- 날씨 적응: ${se.weather_adaptation?.join(', ') || '(없음)'}`)
    lines.push(`- 계절 활동: ${se.seasonal_activities?.join(', ') || '(없음)'}`)
    lines.push(`- 환경 집중: ${se.environmental_focus?.join(', ') || '(없음)'}`)
    lines.push(`- 설명: ${se.explanation || '(없음)'}`)
    lines.push('')
  }

  const charCount = calcContentLength(content)
  lines.push(`> **콘텐츠 길이 (좌측 핵심 블록 합산)**: ${charCount}자`)
  lines.push('')

  return lines.join('\n')
}

function generateMarkdown(dateStr: string, base: DailyContent, translated: Record<UserRole, DailyContent>): string {
  const lines: string[] = []
  const dateLabel = getKoreanDateLabel(dateStr)

  // 헤더
  lines.push(`# 콘텐츠 리뷰 샘플 — ${dateLabel}`)
  lines.push('')
  lines.push(`> **생성 일시**: ${new Date().toLocaleString('ko-KR')}`)
  lines.push(`> **테스트 프로필**: 1971-11-17 04:00 남자 (양력)`)
  lines.push(`> **대상 날짜**: ${dateStr}`)
  lines.push('')
  lines.push('---')
  lines.push('')

  // 기본 메타 (사주 정보)
  if (base.fourPillars) {
    lines.push('## 사주 원국 (내부 참고용)')
    lines.push('')
    const pillars = base.fourPillars
    const keys = ['year', 'month', 'day', 'hour']
    const labels = ['년주', '월주', '일주', '시주']
    const row = keys.map(k => {
      const p = pillars[k]
      return p ? `${p.gan}${p.ji}` : '-'
    })
    lines.push(`| 년주 | 월주 | 일주 | 시주 |`)
    lines.push(`|------|------|------|------|`)
    lines.push(`| ${row[0]} | ${row[1]} | ${row[2]} | ${row[3]} |`)
    lines.push('')
  }

  if (base.gyeokGuk) {
    const g = base.gyeokGuk
    lines.push(`- 일간: ${g.dayMaster} / 강약: ${g.strength} / 계절: ${g.season}`)
    lines.push('')
  }

  lines.push('---')
  lines.push('')

  // 3개 역할 번역 병렬 표시
  for (const role of ROLES) {
    const label = ROLE_LABELS[role]
    const content = translated[role]
    lines.push(renderContentSection(content, label))
    lines.push('---')
    lines.push('')
  }

  // 중립(원본) 콘텐츠 참고
  lines.push('## [원본] 중립 콘텐츠 (번역 전)')
  lines.push('')
  lines.push(renderContentSection(base, '원본'))

  return lines.join('\n')
}

// ============================================================
// 메인 실행
// ============================================================

async function main() {
  const outputDir = path.resolve(__dirname, '../review-samples')

  // review-samples 디렉토리 생성
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true })
    console.log(`디렉토리 생성: ${outputDir}`)
  }

  console.log('콘텐츠 리뷰 샘플 생성 시작...')
  console.log(`테스트 프로필: ${TEST_PROFILE.birthDate} ${TEST_PROFILE.birthTime} ${TEST_PROFILE.gender}`)
  console.log('')

  for (let i = 0; i < 7; i++) {
    const dateStr = getDateString(i)
    console.log(`[${i + 1}/7] ${dateStr} 생성 중...`)

    try {
      // 1. 사주 계산
      const sajuData = calculateSaju(TEST_PROFILE, dateStr)

      // 2. 일간 리듬 분석
      const dailyRhythm = analyzeDailyFortune(TEST_PROFILE, dateStr, sajuData)

      // 3. 콘텐츠 조합 (중립 원본)
      const baseContent = assembleDailyContent(dateStr, sajuData, dailyRhythm)

      // 4. 3개 역할 번역
      const translated: Record<UserRole, DailyContent> = {
        student: translateDailyContent(baseContent, 'student'),
        office_worker: translateDailyContent(baseContent, 'office_worker'),
        freelancer: translateDailyContent(baseContent, 'freelancer'),
      }

      // 5. 마크다운 생성
      const markdown = generateMarkdown(dateStr, baseContent, translated)

      // 6. 파일 저장
      const outputPath = path.join(outputDir, `${dateStr}.md`)
      fs.writeFileSync(outputPath, markdown, 'utf-8')
      console.log(`   저장됨: review-samples/${dateStr}.md (${markdown.length} bytes)`)
    } catch (err) {
      console.error(`   오류 발생 [${dateStr}]:`, err)
      process.exit(1)
    }
  }

  console.log('')
  console.log('완료! review-samples/ 디렉토리를 확인하세요.')
  console.log(`생성된 파일: ${Array.from({ length: 7 }, (_, i) => getDateString(i)).join(', ')}`)
}

main().catch(err => {
  console.error('스크립트 실행 실패:', err)
  process.exit(1)
})
