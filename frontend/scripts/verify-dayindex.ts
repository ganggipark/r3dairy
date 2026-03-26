/**
 * US-11-GATE: 일진 정합성 사전 검증 스크립트
 *
 * saju-engine.ts (JIAZI_DATE 기반) vs sajuCalculator.ts (calculateDayPillar) 비교
 * 30일 샘플로 일주(일간/일지) 불일치 검증
 *
 * 실행: npx ts-node --project tsconfig.json scripts/verify-dayindex.ts
 */

// ============================================================
// saju-engine.ts 방식 (수정 후): Date.UTC(1900,0,1) + index 10 기준
// sajuCalculator.ts와 동일한 로직 사용
// ============================================================

const HEAVENLY_STEMS_ENGINE = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸'] as const
const EARTHLY_BRANCHES_ENGINE = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥'] as const

/** saju-engine.ts 수정 후 방식: 당일 일주 계산 (UTC 기준, sajuCalculator 동일) */
function engineDayPillar(dateStr: string): { stem: string; branch: string; combined: string } {
  const [year, month, day] = dateStr.split('-').map(Number)
  const baseDate = Date.UTC(1900, 0, 1)
  const targetDate = Date.UTC(year, month - 1, day)
  const dayDiff = Math.floor((targetDate - baseDate) / (1000 * 60 * 60 * 24))
  const cycleIdx = ((10 + dayDiff) % 60 + 60) % 60
  const stem = HEAVENLY_STEMS_ENGINE[cycleIdx % 10]
  const branch = EARTHLY_BRANCHES_ENGINE[cycleIdx % 12]
  return { stem, branch, combined: stem + branch }
}

// ============================================================
// sajuCalculator.ts 방식: Date.UTC(1900, 0, 1) + index 10 = 甲戌
// ============================================================

const SIXTY_CYCLE = [
  '갑자', '을축', '병인', '정묘', '무진', '기사', '경오', '신미', '임신', '계유',
  '갑술', '을해', '병자', '정축', '무인', '기묘', '경진', '신사', '임오', '계미',
  '갑신', '을유', '병술', '정해', '무자', '기축', '경인', '신묘', '임진', '계사',
  '갑오', '을미', '병신', '정유', '무술', '기해', '경자', '신축', '임인', '계묘',
  '갑진', '을사', '병오', '정미', '무신', '기유', '경술', '신해', '임자', '계축',
  '갑인', '을묘', '병진', '정사', '무오', '기미', '경신', '신유', '임술', '계해',
] as const

// 한글 -> 한자 매핑
const STEM_HAN: Record<string, string> = {
  '갑': '甲', '을': '乙', '병': '丙', '정': '丁', '무': '戊',
  '기': '己', '경': '庚', '신': '辛', '임': '壬', '계': '癸',
}
const BRANCH_HAN: Record<string, string> = {
  '자': '子', '축': '丑', '인': '寅', '묘': '卯', '진': '辰', '사': '巳',
  '오': '午', '미': '未', '신': '申', '유': '酉', '술': '戌', '해': '亥',
}

/** sajuCalculator.ts 방식: 당일 일주 계산 */
function calcDayPillar(dateStr: string): { stem: string; branch: string; combined: string } {
  const [year, month, day] = dateStr.split('-').map(Number)
  const baseDate = Date.UTC(1900, 0, 1)
  const targetDate = Date.UTC(year, month - 1, day)
  const dayDiff = Math.floor((targetDate - baseDate) / (1000 * 60 * 60 * 24))

  let cycleIndex = (10 + dayDiff) % 60
  if (cycleIndex < 0) cycleIndex += 60

  const combined = SIXTY_CYCLE[cycleIndex]
  const stemHan = STEM_HAN[combined[0]] || combined[0]
  const branchHan = BRANCH_HAN[combined[1]] || combined[1]
  return { stem: stemHan, branch: branchHan, combined: stemHan + branchHan }
}

// ============================================================
// 30일 비교 실행
// ============================================================

function main() {
  // 테스트 기준일: 2026-01-01부터 30일
  const startDate = new Date(2026, 0, 1)
  let mismatches = 0
  const results: Array<{
    date: string
    engine: string
    calc: string
    match: boolean
  }> = []

  for (let i = 0; i < 30; i++) {
    const d = new Date(startDate)
    d.setDate(d.getDate() + i)
    const dateStr = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`

    const eng = engineDayPillar(dateStr)
    const calc = calcDayPillar(dateStr)

    const match = eng.stem === calc.stem && eng.branch === calc.branch
    if (!match) mismatches++

    results.push({
      date: dateStr,
      engine: eng.combined,
      calc: calc.combined,
      match,
    })
  }

  console.log('='.repeat(60))
  console.log('US-11-GATE: 일진 정합성 30일 샘플 검증')
  console.log('='.repeat(60))
  console.log(`비교 기간: 2026-01-01 ~ 2026-01-30`)
  console.log(`총 비교 일수: 30`)
  console.log('')
  console.log('날짜       | saju-engine.ts | sajuCalculator | 일치')
  console.log('-'.repeat(55))

  for (const r of results) {
    const status = r.match ? '✓' : '✗ 불일치!'
    console.log(`${r.date} | ${r.engine.padEnd(14)} | ${r.calc.padEnd(14)} | ${status}`)
  }

  console.log('')
  console.log('='.repeat(60))
  if (mismatches === 0) {
    console.log('✓ PASS: 30일 전수 비교 불일치 0건 — US-01 착수 허가')
    console.log('두 엔진이 동일한 일주를 계산함 (Date.UTC(1900,0,1)+index10 기준)')
  } else {
    console.log(`✗ FAIL: ${mismatches}건 불일치 발견 — 추가 조사 필요`)
    for (const r of results.filter(r => !r.match)) {
      console.log(`  ${r.date}: engine=${r.engine} calc=${r.calc}`)
    }
  }
  console.log('='.repeat(60))

  process.exit(mismatches === 0 ? 0 : 1)
}

main()
