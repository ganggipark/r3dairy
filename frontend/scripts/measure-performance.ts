/**
 * 성능 측정 스크립트 (US-106)
 *
 * assembleDailyContent를 1일/30일/365일 호출하여
 * 메모리 사용량과 렌더 시간을 측정합니다.
 *
 * 실행: npx tsx scripts/measure-performance.ts
 */

import * as path from 'path'
import * as fs from 'fs'

// tsx는 CJS 모드로 실행되므로 __dirname 사용 가능
const __dirnameResolved: string = __dirname

// ── alias 해소 (@ → src/) ──────────────────────────────────────
// tsx는 tsconfig paths를 자동으로 해소하지 않으므로 require hook 없이
// 상대경로로 직접 import 합니다.
import { assembleDailyContent, assembleMonthlyContent } from '../src/lib/content/assembly'
import { calculateSaju, analyzeDailyFortune, analyzeMonthlyRhythm } from '../src/lib/content/saju-engine'
import type { BirthInfo } from '../src/lib/content/types'

// ── 테스트 프로필 ─────────────────────────────────────────────
const BIRTH_INFO: BirthInfo = {
  name: '테스트',
  birthDate: '1971-11-17',
  birthTime: '04:00',
  gender: 'male',
  birthPlace: '서울',
}

const BASE_DATE = '2026-01-01'

// ── 유틸 ──────────────────────────────────────────────────────

function getMB(): number {
  return process.memoryUsage().heapUsed / 1024 / 1024
}

function addDays(dateStr: string, n: number): string {
  const d = new Date(dateStr)
  d.setDate(d.getDate() + n)
  return d.toISOString().split('T')[0]
}

interface MeasureResult {
  label: string
  count: number
  elapsedMs: number
  memBeforeMB: number
  memAfterMB: number
  memDeltaMB: number
}

// ── 단일 배치 측정 ────────────────────────────────────────────

function measureBatch(label: string, count: number): MeasureResult {
  // GC 유도 (가능하면)
  if (global.gc) global.gc()

  const memBefore = getMB()
  const t0 = performance.now()

  // 사주 계산은 캐시되므로 1회만 수행 (원국 불변)
  const sajuData = calculateSaju(BIRTH_INFO, BASE_DATE)

  for (let i = 0; i < count; i++) {
    const targetDate = addDays(BASE_DATE, i)
    const dailyRhythm = analyzeDailyFortune(BIRTH_INFO, targetDate, sajuData)
    assembleDailyContent(targetDate, sajuData, dailyRhythm)
  }

  const elapsed = performance.now() - t0
  const memAfter = getMB()

  return {
    label,
    count,
    elapsedMs: Math.round(elapsed * 10) / 10,
    memBeforeMB: Math.round(memBefore * 10) / 10,
    memAfterMB: Math.round(memAfter * 10) / 10,
    memDeltaMB: Math.round((memAfter - memBefore) * 10) / 10,
  }
}

// ── 월간 배치 측정 ────────────────────────────────────────────

function measureMonthlyBatch(label: string, monthCount: number): MeasureResult {
  if (global.gc) global.gc()

  const memBefore = getMB()
  const t0 = performance.now()

  const sajuData = calculateSaju(BIRTH_INFO, BASE_DATE)
  const baseYear = 2026

  for (let i = 0; i < monthCount; i++) {
    const year = baseYear + Math.floor(i / 12)
    const month = (i % 12) + 1
    const monthlyRhythm = analyzeMonthlyRhythm(BIRTH_INFO, year, month, sajuData)
    assembleMonthlyContent(year, month, monthlyRhythm)
  }

  const elapsed = performance.now() - t0
  const memAfter = getMB()

  return {
    label,
    count: monthCount,
    elapsedMs: Math.round(elapsed * 10) / 10,
    memBeforeMB: Math.round(memBefore * 10) / 10,
    memAfterMB: Math.round(memAfter * 10) / 10,
    memDeltaMB: Math.round((memAfter - memBefore) * 10) / 10,
  }
}

// ── 임계값 평가 ───────────────────────────────────────────────

interface ThresholdCheck {
  metric: string
  value: number
  threshold: number
  unit: string
  passed: boolean
  note: string
}

function evaluateThresholds(results: MeasureResult[]): ThresholdCheck[] {
  const checks: ThresholdCheck[] = []

  for (const r of results) {
    if (r.label === '365일') {
      // 4x CPU 스로틀링 추정: 실측값 × 4
      const throttled365ms = r.elapsedMs * 4
      checks.push({
        metric: '365일 렌더 시간 (4x 스로틀링 추정)',
        value: Math.round(throttled365ms),
        threshold: 3000,
        unit: 'ms',
        passed: throttled365ms <= 3000,
        note: `실측 ${r.elapsedMs}ms × 4 = ${Math.round(throttled365ms)}ms`,
      })
      checks.push({
        metric: '365일 메모리 사용량',
        value: r.memAfterMB,
        threshold: 200,
        unit: 'MB (heap)',
        passed: r.memAfterMB <= 200,
        note: `delta: +${r.memDeltaMB}MB`,
      })
    }
    if (r.label === '30일') {
      checks.push({
        metric: '30일(월간) 렌더 시간',
        value: r.elapsedMs,
        threshold: 1000,
        unit: 'ms',
        passed: r.elapsedMs <= 1000,
        note: '1초 이내 완료 기준',
      })
    }
  }

  return checks
}

// ── DOM 노드 추정 ─────────────────────────────────────────────
// diary-print/page.tsx 분석:
//   Left page 블록 수: 약 10개 (summary, keywords, rhythm, focus_caution,
//     action_guide, time_direction, state_trigger, meaning_shift,
//     rhythm_question, lifestyle)
//   Right page 블록 수: 약 6개 (header, qimen_bar, time_grid×19rows,
//     todos×4, gratitude×3, memo×8)
//   Left page 예상 DOM 노드: ~120
//   Right page 예상 DOM 노드: ~80
//   커버(1) + 빈페이지(1) + 일별 × 2페이지

function estimateDomNodes(dayCount: number): {
  perDayLeft: number
  perDayRight: number
  totalNodes: number
  totalPages: number
} {
  const perDayLeft = 120   // left page (10 blocks × ~12 nodes avg)
  const perDayRight = 80   // right page (time grid 19행 + 기타)
  const coverNodes = 20
  const totalPages = 2 + dayCount * 2
  const totalNodes = coverNodes + dayCount * (perDayLeft + perDayRight)
  return { perDayLeft, perDayRight, totalNodes, totalPages }
}

// ── 메인 ─────────────────────────────────────────────────────

async function main() {
  console.log('=== 성능 측정 시작 ===')
  console.log(`Node.js: ${process.version}`)
  console.log(`OS: ${process.platform} ${process.arch}`)
  console.log(`테스트 기준일: ${BASE_DATE}`)
  console.log(`테스트 프로필: ${BIRTH_INFO.birthDate} ${BIRTH_INFO.birthTime} ${BIRTH_INFO.gender}`)
  console.log('')

  const dailyResults: MeasureResult[] = []

  console.log('--- 일별 콘텐츠 생성 측정 ---')

  for (const count of [1, 30, 365]) {
    const label = count === 1 ? '1일' : count === 30 ? '30일' : '365일'
    process.stdout.write(`  ${label} 측정 중...`)
    const r = measureBatch(label, count)
    dailyResults.push(r)
    console.log(` 완료: ${r.elapsedMs}ms, heap ${r.memAfterMB}MB (+${r.memDeltaMB}MB)`)
  }

  console.log('')
  console.log('--- 월간 콘텐츠 생성 측정 (1개월) ---')
  const monthlyResult = measureMonthlyBatch('1개월(월간)', 1)
  console.log(`  완료: ${monthlyResult.elapsedMs}ms, heap ${monthlyResult.memAfterMB}MB`)

  // DOM 추정
  console.log('')
  console.log('--- DOM 노드 추정 ---')
  for (const count of [1, 30, 365]) {
    const est = estimateDomNodes(count)
    console.log(`  ${count}일: 총 ${est.totalPages}페이지, ~${est.totalNodes.toLocaleString()}개 DOM 노드`)
  }

  // 임계값 평가
  console.log('')
  console.log('--- 임계값 평가 ---')
  const checks = evaluateThresholds(dailyResults)
  for (const c of checks) {
    const status = c.passed ? 'PASS' : 'FAIL'
    console.log(`  [${status}] ${c.metric}: ${c.value}${c.unit} (임계값: ${c.threshold}${c.unit}) — ${c.note}`)
  }

  // 권장 사항
  const needs365Pagination = checks.find(c => c.metric.includes('365일 렌더') && !c.passed)
  const needs365Memory = checks.find(c => c.metric.includes('365일 메모리') && !c.passed)
  const needs30Optimization = checks.find(c => c.metric.includes('30일') && !c.passed)

  const recommendations: string[] = []
  if (needs365Pagination) {
    recommendations.push('365일 렌더 시간이 3초 초과 예상 → 페이지네이션 또는 레이지 로딩 구현 필요')
  }
  if (needs365Memory) {
    recommendations.push('365일 메모리가 200MB 초과 → 콘텐츠 윈도잉 구현 필요')
  }
  if (needs30Optimization) {
    recommendations.push('30일 로딩이 1초 초과 → API 레벨 최적화 검토 필요')
  }
  if (recommendations.length === 0) {
    recommendations.push('현재 임계값 이내 — 추가 최적화 불필요')
  }

  console.log('')
  console.log('--- 권장 사항 ---')
  for (const r of recommendations) {
    console.log(`  - ${r}`)
  }

  // ── 문서 저장 ──────────────────────────────────────────────
  const allResults = [...dailyResults, monthlyResult]
  const domEst365 = estimateDomNodes(365)
  const dom30 = estimateDomNodes(30)
  const dom1 = estimateDomNodes(1)

  const md = `# 성능 기준선 (Performance Baseline)

## 측정 정보

- **측정 날짜**: ${new Date().toISOString().split('T')[0]}
- **Node.js 버전**: ${process.version}
- **OS**: ${process.platform} ${process.arch}
- **테스트 기준일**: ${BASE_DATE}
- **테스트 프로필**: 생년월일 ${BIRTH_INFO.birthDate}, 시간 ${BIRTH_INFO.birthTime}, 성별 ${BIRTH_INFO.gender}

## 측정 결과

### 콘텐츠 생성 시간 및 메모리

| 구분 | 생성 건수 | 소요 시간 (ms) | Heap 사용 (MB) | Heap 증가 (MB) |
|------|----------|--------------|--------------|--------------|
${allResults.map(r =>
  `| ${r.label} | ${r.count}건 | ${r.elapsedMs} | ${r.memAfterMB} | +${r.memDeltaMB} |`
).join('\n')}

> **참고**: 사주 원국(사주팔자) 계산은 동일 프로필에 대해 캐시됩니다.
> 위 시간은 캐시 히트 이후 일진/콘텐츠 조합 비용만 포함합니다.

### DOM 노드 추정 (diary-print/page.tsx 기준)

| 구분 | 페이지 수 | 예상 DOM 노드 수 |
|------|----------|----------------|
| 1일 | ${dom1.totalPages}페이지 | ~${dom1.totalNodes}개 |
| 30일 | ${dom30.totalPages}페이지 | ~${dom30.totalNodes.toLocaleString()}개 |
| 365일 | ${domEst365.totalPages}페이지 | ~${domEst365.totalNodes.toLocaleString()}개 |

**추정 근거**:
- Left page: 10개 블록 × 평균 12 DOM 노드 = 약 120노드/페이지
- Right page: 시간 그리드(19행) + 할 일(4행) + 감사(3행) + 메모(8행) 등 = 약 80노드/페이지
- 커버 + 빈 페이지: 약 20노드

### 4x CPU 스로틀링 추정

| 구분 | 실측 (ms) | 4x 스로틀링 추정 (ms) | 임계값 (ms) | 결과 |
|------|----------|---------------------|------------|------|
${checks.filter(c => c.metric.includes('렌더')).map(c => {
  const raw = dailyResults.find(r => r.label === '365일')
  return `| 365일 | ${raw?.elapsedMs ?? '-'} | ${c.value} | ${c.threshold} | ${c.passed ? 'PASS' : 'FAIL'} |`
}).join('\n')}

## 임계값 평가

| 항목 | 측정값 | 임계값 | 결과 | 비고 |
|------|-------|-------|------|------|
${checks.map(c =>
  `| ${c.metric} | ${c.value}${c.unit} | ${c.threshold}${c.unit} | ${c.passed ? '✅ PASS' : '❌ FAIL'} | ${c.note} |`
).join('\n')}

## 현재 렌더링 구조 분석 (diary-print/page.tsx)

### 렌더링 방식
- 모든 날짜의 페이지를 **한번에 DOM에 생성** (가상화/윈도잉 없음)
- preview 모드: \`display: none\` CSS로 비활성 페이지 숨김 (DOM은 유지)
- scroll 모드: 전체 페이지 동시 렌더링

### 현재 최적화 현황
- 사주 원국 계산: LRU 캐시 (최대 200개 항목) 적용
- 날짜 범위 API 호출: 31일 청크 단위 분할 로딩 (프로그레스바 표시)
- React 컴포넌트 가상화: **미적용**
- 콘텐츠 윈도잉: **미적용**

## 권장 사항

${recommendations.map(r => `- ${r}`).join('\n')}

${needs365Pagination ? `
### 365일 최적화 방안 (필요 시)

1. **페이지네이션** (권장): preview 모드에서 현재 페이지 ±2 범위만 렌더링
2. **레이지 로딩**: IntersectionObserver로 viewport 진입 시점에 렌더링
3. **콘텐츠 윈도잉**: react-virtual 등으로 visible 범위만 DOM 유지
` : ''}
${needs365Memory ? `
### 메모리 최적화 방안 (필요 시)

1. **콘텐츠 윈도잉**: 현재 ±5일 범위만 메모리에 유지
2. **페이지 언마운트**: 스크롤 이탈 시 콘텐츠 해제
` : ''}

---
*이 문서는 \`scripts/measure-performance.ts\`로 자동 생성되었습니다.*
`

  const docsDir = path.join(__dirnameResolved, '..', 'docs')
  if (!fs.existsSync(docsDir)) fs.mkdirSync(docsDir, { recursive: true })
  const outPath = path.join(docsDir, 'performance-baseline.md')
  fs.writeFileSync(outPath, md, 'utf-8')
  console.log('')
  console.log(`=== 완료: ${outPath} ===`)
}

main().catch(err => {
  console.error('측정 실패:', err)
  process.exit(1)
})
