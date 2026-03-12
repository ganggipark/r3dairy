/**
 * Content Assembly Engine (TypeScript 포트)
 *
 * Python backend/src/content/assembly.py 로직을 TypeScript로 포팅.
 * 리듬 신호를 사용자 노출 콘텐츠 블록으로 변환합니다.
 *
 * **중요**: 이 모듈은 사용자 노출 텍스트만 생성합니다.
 * 내부 전문 용어(사주명리, NLP 등)는 절대 사용 금지.
 */

import type {
  SajuData,
  DailyRhythm,
  MonthlyRhythm,
  YearlyRhythm,
  DailyContent,
  MonthlyContent,
  YearlyContent,
  FocusCaution,
  ActionGuide,
  TimeDirection,
  StateTrigger,
  HealthSports,
  MealNutrition,
  FashionBeauty,
  ShoppingFinance,
  LivingSpace,
  DailyRoutines,
  DigitalCommunication,
  HobbiesCreativity,
  RelationshipsSocial,
  SeasonalEnvironment,
} from './types'

// ============================================================
// 메인 함수: assembleDailyContent
// ============================================================

/**
 * 일간 콘텐츠 조합
 *
 * @param targetDate 대상 날짜 (YYYY-MM-DD)
 * @param sajuData 사주 계산 결과 (내부 데이터)
 * @param dailyRhythm 일간 리듬 분석 결과 (내부 데이터)
 * @param qimenSummary 기문둔갑 요약 데이터 (옵션)
 * @returns DAILY_CONTENT_SCHEMA.json 준수하는 사용자 노출 콘텐츠
 */
export function assembleDailyContent(
  targetDate: string,
  sajuData: SajuData,
  dailyRhythm: DailyRhythm,
  qimenSummary?: { best_direction?: string; avoid_direction?: string; peak_hours?: string },
): DailyContent {
  // 1. 요약
  const summary = generateSummary(dailyRhythm)

  // 2. 키워드
  const keywords = generateKeywords(dailyRhythm, sajuData)

  // 3. 리듬 해설
  const rhythmDescription = generateRhythmDescription(dailyRhythm, sajuData)

  // 4. 집중/주의 포인트
  const focusCaution = generateFocusCaution(dailyRhythm)

  // 5. 행동 가이드
  const actionGuide = generateActionGuide(dailyRhythm, sajuData)

  // 6. 시간/방향
  const timeDirection = generateTimeDirection(dailyRhythm, qimenSummary || {})

  // 7. 상태 트리거
  const stateTrigger = generateStateTrigger(dailyRhythm)

  // 8. 의미 전환
  const meaningShift = generateMeaningShift(dailyRhythm, sajuData)

  // 9. 리듬 질문
  const rhythmQuestion = generateRhythmQuestion(dailyRhythm)

  // 10-19. 라이프스타일 블록
  const healthSports = generateDailyHealthSports(dailyRhythm)
  const mealNutrition = generateDailyMealNutrition(dailyRhythm)
  const fashionBeauty = generateDailyFashionBeauty(dailyRhythm, sajuData)
  const shoppingFinance = generateDailyShoppingFinance(dailyRhythm)
  const livingSpace = generateDailyLivingSpace(dailyRhythm)
  const dailyRoutines = generateDailyRoutines(dailyRhythm)
  const digitalComm = generateDigitalCommunication(dailyRhythm)
  const hobbies = generateHobbiesCreativity(dailyRhythm)
  const relationships = generateRelationshipsSocial(dailyRhythm)
  const seasonal = generateSeasonalEnvironment(dailyRhythm, targetDate)

  // 사주 데이터를 프론트엔드 형식으로 변환
  let fourPillars: DailyContent['fourPillars'] = null
  if (sajuData?.사주) {
    const saju = sajuData.사주
    const pillarMapping: Record<string, string> = {
      '년주': 'year', '월주': 'month', '일주': 'day', '시주': 'hour',
    }
    fourPillars = {}
    for (const [korKey, engKey] of Object.entries(pillarMapping)) {
      const pillarData = saju[korKey as keyof typeof saju]
      if (pillarData) {
        fourPillars[engKey] = {
          heavenlyStem: pillarData.천간 || '',
          earthlyBranch: pillarData.지지 || '',
          gan: pillarData.천간 || '',
          ji: pillarData.지지 || '',
        }
      }
    }
  }

  let gyeokGuk: DailyContent['gyeokGuk'] = null
  if (sajuData?.격국) {
    gyeokGuk = {
      dayMaster: sajuData.격국.일간 || '',
      strength: sajuData.격국.강약 || '',
      monthBranch: '',
      season: sajuData.격국.계절 || '',
    }
  }

  let yongSin: DailyContent['yongSin'] = null
  if (sajuData?.용신) {
    yongSin = {
      yongSin: sajuData.용신.용신 || [],
    }
  }

  let content: DailyContent = {
    date: targetDate,
    summary,
    keywords,
    rhythm_description: rhythmDescription,
    focus_caution: focusCaution,
    action_guide: actionGuide,
    time_direction: timeDirection,
    state_trigger: stateTrigger,
    meaning_shift: meaningShift,
    rhythm_question: rhythmQuestion,
    daily_health_sports: healthSports,
    daily_meal_nutrition: mealNutrition,
    daily_fashion_beauty: fashionBeauty,
    daily_shopping_finance: shoppingFinance,
    daily_living_space: livingSpace,
    daily_routines: dailyRoutines,
    digital_communication: digitalComm,
    hobbies_creativity: hobbies,
    relationships_social: relationships,
    seasonal_environment: seasonal,
    fourPillars,
    gyeokGuk,
    yongSin,
  }

  // 좌측 페이지 최소 700자 보장
  content = ensureMinimumContentLength(content, dailyRhythm)

  return content
}

// ============================================================
// 요약 생성
// ============================================================

function generateSummary(dailyRhythm: DailyRhythm): string {
  const energy = dailyRhythm.에너지_수준 ?? 3
  const flow = dailyRhythm.주요_흐름 ?? '균형의 시기'

  const energyText: Record<number, string> = {
    5: '매우 활기찬', 4: '충만한', 3: '안정적인', 2: '차분한', 1: '고요한',
  }
  const et = energyText[energy] || '평온한'

  if (energy >= 4) {
    return (
      `오늘은 ${et} 에너지가 흐르는 날입니다. ` +
      `${flow}의 시간을 맞이하여, 준비해온 일들을 적극적으로 펼치기에 좋은 하루입니다. ` +
      '활기차게 시작하고 과감히 움직여 보세요.'
    )
  } else if (energy <= 2) {
    return (
      `오늘은 ${et} 에너지의 날입니다. ` +
      `${flow}의 흐름 속에서 자신을 조용히 돌보는 시간이 필요합니다. ` +
      '무리하기보다 내면의 목소리에 귀를 기울이며 차분히 하루를 보내세요.'
    )
  } else {
    return (
      `오늘은 ${et} 에너지가 흐르는 날입니다. ` +
      `${flow}을 경험하며, 지나치게 힘을 쏟지도, 너무 물러서지도 않는 균형 잡힌 하루를 설계해보세요. ` +
      '안정 속에서 꾸준한 성과를 만들 수 있습니다.'
    )
  }
}

// ============================================================
// 키워드 생성
// ============================================================

function generateKeywords(dailyRhythm: DailyRhythm, sajuData: SajuData): string[] {
  const keywords: string[] = []
  const energy = dailyRhythm.에너지_수준 ?? 3
  const concentration = dailyRhythm.집중력 ?? 3
  const social = dailyRhythm.사회운 ?? 3
  const decision = dailyRhythm.결정력 ?? 3

  // 에너지 기반
  if (energy >= 4) keywords.push('활동')
  else if (energy <= 2) keywords.push('휴식')
  else keywords.push('균형')

  // 집중력 기반
  if (concentration >= 4) keywords.push('집중', '학습')
  else keywords.push('유연함')

  // 사회운 기반
  if (social >= 4) keywords.push('관계', '소통')
  else keywords.push('내면')

  // 결정력 기반
  if (decision >= 4) keywords.push('실행', '결단')
  else keywords.push('준비')

  // 기회 요소
  const opportunities = dailyRhythm.기회_요소 || []
  if (opportunities.length > 0) keywords.push('기회')

  // 사주 격국 강약 기반
  if (sajuData) {
    const strength = sajuData.격국?.강약 || ''
    if (strength === '신강') keywords.push('도전')
    else if (strength === '신약') keywords.push('안정')
    else if (strength === '중화') keywords.push('조화')
  }

  // 중복 제거 및 최대 8개
  const unique = Array.from(new Set(keywords)).slice(0, 8)

  // 최소 3개 보장
  while (unique.length < 3) unique.push('조화')

  return unique
}

// ============================================================
// 리듬 해설 생성
// ============================================================

function generateRhythmDescription(dailyRhythm: DailyRhythm, sajuData: SajuData): string {
  const energy = dailyRhythm.에너지_수준 ?? 3
  const concentration = dailyRhythm.집중력 ?? 3
  const social = dailyRhythm.사회운 ?? 3
  const decision = dailyRhythm.결정력 ?? 3
  const flow = dailyRhythm.주요_흐름 ?? '균형의 시기'

  // 사주 일간 기반 개인화
  let dayStem = ''
  if (sajuData) {
    dayStem = sajuData.사주?.일주?.천간 || ''
  }

  const stemTendency: Record<string, string> = {
    '갑': '추진력과 리더십', '을': '유연한 적응력',
    '병': '열정과 표현력', '정': '섬세한 집중력',
    '무': '안정적인 포용력', '기': '실용적 섬세함',
    '경': '결단력과 실행력', '신': '정밀한 완벽주의',
    '임': '깊은 통찰력', '계': '직관적 감수성',
    '甲': '추진력과 리더십', '乙': '유연한 적응력',
    '丙': '열정과 표현력', '丁': '섬세한 집중력',
    '戊': '안정적인 포용력', '己': '실용적 섬세함',
    '庚': '결단력과 실행력', '辛': '정밀한 완벽주의',
    '壬': '깊은 통찰력', '癸': '직관적 감수성',
  }
  const personalTendency = stemTendency[dayStem] || ''

  let description = `오늘의 흐름은 '${flow}'으로 요약됩니다. `
  if (personalTendency) {
    description += `당신의 본래 기질인 ${personalTendency}이(가) 오늘의 리듬과 어떻게 어우러지는지 살펴보겠습니다. `
  } else {
    description += '이 흐름이 어떤 의미를 가지는지, 하루 동안 어떻게 활용할 수 있는지 살펴보겠습니다. '
  }

  if (energy >= 4) {
    description += '현재 에너지 수준이 매우 높아, 활동적이고 적극적인 하루가 될 가능성이 큽니다. '
    if (personalTendency) {
      description += `특히 ${personalTendency}을(를) 살려 주도적으로 움직이면 더 큰 성과를 얻을 수 있습니다. `
    }
    description += '이 시기에는 오랫동안 미뤄두었던 과제나 새로운 시도를 실행에 옮기는 것이 효과적입니다. '
  } else if (energy <= 2) {
    description += '에너지가 낮은 상태로, 몸과 마음 모두 충분한 쉼을 요청하고 있는 신호입니다. '
    if (personalTendency) {
      description += `이런 날은 ${personalTendency}을(를) 내면으로 돌려 자기 성찰에 활용하면 좋습니다. `
    }
    description += '이런 날은 생산성보다 회복을 우선순위로 삼고, 가벼운 일만 처리하는 것이 지혜롭습니다. '
  } else {
    description += '에너지가 안정적으로 유지되는 날입니다. '
    if (personalTendency) {
      description += `타고난 ${personalTendency}의 강점을 꾸준하게 발휘하기에 좋은 조건입니다. `
    }
    description += '급격한 변화보다는 꾸준한 흐름을 유지하면서 하루의 과업을 착실히 처리해나가기에 좋습니다. '
  }

  if (concentration >= 4) {
    description += '오늘은 특히 집중력이 뛰어난 상태입니다. '
    description += '깊은 사고가 필요한 작업이나 학습, 창작 활동에 이 에너지를 적극 활용해보세요. '
  } else if (concentration <= 2) {
    description += '집중력이 다소 분산되는 경향이 있으니, 너무 오래 한 가지 일에 매달리지 않는 것이 좋습니다. '
    description += '짧은 휴식과 함께 여러 가지 가벼운 작업을 번갈아 처리하는 방식을 추천합니다. '
  }

  if (social >= 4) {
    description += '대인관계 에너지가 활발하여 사람들과의 교류가 원활하게 이뤄질 수 있습니다. '
    description += '중요한 미팅이나 협력이 필요한 일을 오늘 진행하면 좋은 결과를 기대할 수 있습니다. '
  } else if (social <= 2) {
    description += '오늘은 혼자만의 시간을 갖거나 소수의 가까운 사람들과 조용히 교류하는 것이 편안합니다. '
  }

  if (decision >= 4) {
    description += '결단력이 강화된 날로, 오랫동안 고민해온 선택을 내리기에 적합한 시기입니다. '
  }

  const opportunities = dailyRhythm.기회_요소 || []
  if (opportunities.length > 0) {
    const oppText = opportunities.slice(0, 2).join(', ')
    description += `특히 ${oppText} 방면에서 긍정적인 기회가 열릴 수 있으니 주의 깊게 살펴보세요. `
  }

  description += '오늘 하루를 이 흐름에 맞게 설계한다면, 더 자연스럽고 의미 있는 하루가 될 것입니다.'

  // 최소 200자 보장
  while (description.length < 200) {
    description += ' 오늘의 흐름을 온전히 받아들이고, 자신만의 속도로 나아가세요.'
  }

  return description.trim()
}

// ============================================================
// 집중/주의 포인트
// ============================================================

function generateFocusCaution(dailyRhythm: DailyRhythm): FocusCaution {
  const energy = dailyRhythm.에너지_수준 ?? 3
  const concentration = dailyRhythm.집중력 ?? 3
  const social = dailyRhythm.사회운 ?? 3
  const decision = dailyRhythm.결정력 ?? 3

  const focus: string[] = []
  const caution: string[] = []

  if (energy >= 4) focus.push('높은 에너지를 활용한 적극적 활동')
  if (concentration >= 4) focus.push('중요한 작업에 대한 깊은 집중')
  if (social >= 4) focus.push('관계 형성과 네트워킹')
  if (decision >= 4) focus.push('결정이 필요한 사안의 처리')

  if (focus.length < 2) focus.push('일상 루틴 유지', '균형 잡힌 하루 설계')

  if (energy <= 2) caution.push('무리한 활동으로 인한 피로 누적')
  if (concentration <= 2) caution.push('주의력 분산 가능성')
  if (social <= 2) caution.push('대인 관계에서의 오해')

  if (caution.length < 1) caution.push('과도한 욕심이나 조급함')

  return {
    focus: focus.slice(0, 5),
    caution: caution.slice(0, 5),
  }
}

// ============================================================
// 행동 가이드
// ============================================================

function generateActionGuide(dailyRhythm: DailyRhythm, sajuData: SajuData): ActionGuide {
  const energy = dailyRhythm.에너지_수준 ?? 3

  const doItems: string[] = []
  const avoidItems: string[] = []

  if (energy >= 4) {
    doItems.push('중요한 프로젝트 진행하기', '새로운 시도나 도전 계획하기', '활발한 움직임과 교류')
  } else if (energy >= 3) {
    doItems.push('일상 업무를 차분히 처리하기', '계획 점검 및 정리', '편안한 대화와 소통')
  } else {
    doItems.push('충분한 휴식 취하기', '내면 성찰과 기록', '가벼운 정리 활동')
  }

  // 사주 성격 기반 강점 Do 추가
  if (sajuData) {
    const personality = sajuData.성격 || {}
    const dayMasterTraits = personality.dayMasterTraits || {}
    const advice = dayMasterTraits.advice || ''
    if (advice) doItems.push(advice)
  }

  if (energy <= 2) {
    avoidItems.push('과도한 일정 잡기', '중요한 결정 서두르기', '무리한 약속')
  } else {
    avoidItems.push('충동적 선택', '피로를 무시한 활동', '불필요한 갈등')
  }

  // 사주 성격 기반 약점 Avoid 추가
  if (sajuData) {
    const personality = sajuData.성격 || {}
    const dayMasterTraits = personality.dayMasterTraits || {}
    const weaknesses: string[] = dayMasterTraits.weaknesses || []
    for (const w of weaknesses.slice(0, 2)) {
      const avoidItem = `${w}에 빠지지 않도록 주의`
      if (!avoidItems.includes(avoidItem)) avoidItems.push(avoidItem)
    }
  }

  return {
    do: doItems.slice(0, 5),
    avoid: avoidItems.slice(0, 5),
  }
}

// ============================================================
// 시간/방향
// ============================================================

function generateTimeDirection(
  dailyRhythm: DailyRhythm,
  qimenSummary: { best_direction?: string; avoid_direction?: string; peak_hours?: string },
): TimeDirection {
  let goodTimes = [...(dailyRhythm.유리한_시간 || [])]
  const cautionTimes = dailyRhythm.주의_시간 || []
  let goodDirections = [...(dailyRhythm.유리한_방향 || [])]

  let avoidDirectionStr = ''

  if (qimenSummary) {
    if (qimenSummary.peak_hours && !goodTimes.includes(qimenSummary.peak_hours)) {
      goodTimes = [qimenSummary.peak_hours, ...goodTimes]
    }
    if (qimenSummary.best_direction && !goodDirections.includes(qimenSummary.best_direction)) {
      goodDirections = [qimenSummary.best_direction, ...goodDirections]
    }
    if (qimenSummary.avoid_direction) {
      avoidDirectionStr = qimenSummary.avoid_direction
    }
  }

  const goodTimeStr = goodTimes.slice(0, 2).join(', ') || '오전 시간대'
  const avoidTimeStr = cautionTimes.slice(0, 1).join(', ') || '늦은 밤'
  const goodDirectionStr = goodDirections.slice(0, 2).join(', ') || '동쪽'

  let notes = `오늘은 ${goodTimeStr}에 집중력과 효율이 높아집니다. `
  notes += `가능하다면 ${goodDirectionStr} 방향으로의 활동이나 이동을 고려해보세요. `
  notes += `${avoidTimeStr}에는 중요한 일을 피하는 것이 좋습니다.`

  return {
    good_time: goodTimeStr,
    avoid_time: avoidTimeStr,
    good_direction: goodDirectionStr,
    avoid_direction: avoidDirectionStr,
    notes,
  }
}

// ============================================================
// 상태 트리거
// ============================================================

function generateStateTrigger(dailyRhythm: DailyRhythm): StateTrigger {
  const energy = dailyRhythm.에너지_수준 ?? 3

  if (energy >= 4) {
    return {
      gesture: '두 손을 가슴에 모으고 깊게 호흡하기',
      phrase: '"오늘의 에너지를 온전히 느낀다"',
      how_to:
        '활기찬 에너지가 흐를 때, 잠시 멈춰 두 손을 가슴에 모으고 깊은 호흡을 세 번 반복하세요. ' +
        '이 동작은 넘치는 에너지를 내면으로 안정화시켜 과도한 흥분이나 조급함을 조절하는 데 도움이 됩니다.',
    }
  } else if (energy <= 2) {
    return {
      gesture: '어깨를 가볍게 으쓱이며 긴장 풀기',
      phrase: '"충분한 휴식이 나를 채운다"',
      how_to:
        '에너지가 낮게 느껴질 때, 의자에 앉아 어깨를 천천히 으쓱이며 긴장을 풀어주세요. ' +
        "이 동작과 함께 '휴식도 생산적인 활동이다'라는 인식을 상기하면 불필요한 죄책감을 내려놓을 수 있습니다.",
    }
  } else {
    return {
      gesture: '양손을 가볍게 펴고 균형 확인하기',
      phrase: '"지금 이대로 충분하다"',
      how_to:
        '평온한 에너지 속에서 양손을 앞으로 펴고 좌우 균형을 느껴보세요. ' +
        '이 간단한 동작은 현재 상태를 인식하고 받아들이는 마음가짐을 강화해줍니다.',
    }
  }
}

// ============================================================
// 의미 전환
// ============================================================

function generateMeaningShift(dailyRhythm: DailyRhythm, sajuData: SajuData): string {
  const energy = dailyRhythm.에너지_수준 ?? 3

  // 격국 강약에 따른 보조 문구
  let strengthHint = ''
  if (sajuData) {
    const strength = sajuData.격국?.강약 || ''
    if (strength === '신강') {
      strengthHint = '당신은 본래 강한 에너지를 가진 사람입니다. 때로는 그 힘을 의식적으로 절제하는 것이 오히려 더 큰 성장을 가져옵니다. '
    } else if (strength === '신약') {
      strengthHint = '당신은 섬세하고 깊은 내면을 가진 사람입니다. 외부의 속도에 맞추기보다 자신의 리듬을 존중할 때 가장 빛나게 됩니다. '
    } else if (strength === '중화') {
      strengthHint = '당신은 균형 잡힌 기질을 가진 사람입니다. 이 안정감을 활용하여 주변을 조율하는 역할에서 강점을 발휘할 수 있습니다. '
    }
  }

  let shift: string
  if (energy <= 2) {
    shift =
      '에너지가 낮다는 것은 무능력이 아니라, 충전이 필요한 자연스러운 신호입니다. ' +
      '휴식을 선택하는 것도 자기 돌봄의 적극적 행동입니다. ' +
      '지금 이 순간 쉬어가는 것이 내일의 나를 위한 가장 현명한 투자라는 점을 기억하세요. ' +
      '오늘의 쉼이 내일의 나를 위한 준비임을 잊지 마세요. ' +
      '억지로 활동하려 하지 말고, 필요한 것이 무엇인지 자신에게 솔직하게 물어보세요.'
  } else if (energy >= 4) {
    shift =
      '넘치는 에너지는 무조건 소모해야 할 대상이 아닙니다. ' +
      '방향성 있는 활용이 중요하며, 때로는 내일을 위해 보존하는 것도 현명한 선택입니다. ' +
      '에너지의 흐름을 자각하고, 가장 의미 있는 곳에 집중하여 활용해보세요. ' +
      '지금의 이 에너지가 언제나 지속되지는 않습니다. ' +
      '오늘의 힘을 현명하게 배분하여, 시작한 일을 마무리하는 데 집중해보세요.'
  } else {
    shift =
      '평범한 하루라는 느낌은 오히려 안정의 증거입니다. ' +
      '특별함을 강요하지 않고 지금 이 순간을 있는 그대로 받아들이는 것도 중요한 성장입니다. ' +
      '일상 속 작은 순간들에 감사하며, 오늘의 평온함이 주는 힘을 느껴보세요. ' +
      '조용하지만 단단한 이 흐름 속에서, 오늘 당신이 내리는 선택들이 앞으로의 방향을 만들어갑니다. ' +
      '작더라도 의식적인 선택을 해보세요.'
  }

  if (strengthHint) {
    shift += ' ' + strengthHint
  }

  return shift
}

// ============================================================
// 리듬 질문
// ============================================================

function generateRhythmQuestion(dailyRhythm: DailyRhythm): string {
  const energy = dailyRhythm.에너지_수준 ?? 3

  if (energy >= 4) {
    return '오늘의 높은 에너지를 어떤 방향으로 사용하고 싶나요?'
  } else if (energy <= 2) {
    return '지금 나에게 필요한 휴식의 형태는 무엇일까요?'
  } else {
    return '오늘 하루 동안 가장 소중하게 여기고 싶은 순간은 무엇인가요?'
  }
}

// ============================================================
// 라이프스타일 블록
// ============================================================

function generateDailyHealthSports(dailyRhythm: DailyRhythm): HealthSports {
  const energy = dailyRhythm.에너지_수준 ?? 3

  if (energy >= 4) {
    return {
      recommended_activities: ['조깅', '수영'],
      health_tips: ['활동적인 운동으로 에너지 발산', '충분한 수분 섭취'],
      wellness_focused: ['심폐 기능 강화', '체력 향상'],
      explanation: '오늘은 에너지가 높은 날입니다. 활동적인 운동으로 에너지를 건강하게 발산하세요.',
    }
  } else {
    return {
      recommended_activities: ['걷기', '요가'],
      health_tips: ['가벼운 운동으로 컨디션 유지', '충분한 휴식'],
      wellness_focused: ['유연성 향상', '스트레스 해소'],
      explanation: '오늘은 편안한 운동이 좋습니다. 몸과 마음을 부드럽게 풀어주는 활동을 선택하세요.',
    }
  }
}

function generateDailyMealNutrition(dailyRhythm: DailyRhythm): MealNutrition {
  const energy = dailyRhythm.에너지_수준 ?? 3

  if (energy >= 4) {
    return {
      flavor_profile: ['신선한 맛', '상큼한 맛'],
      recommended_foods: ['과일', '샐러드', '생선'],
      avoid_foods: ['기름진 음식', '과도한 당분'],
      explanation: '오늘은 가벼우면서 영양가 있는 음식이 좋습니다. 신선한 재료로 에너지를 보충하세요.',
    }
  } else {
    return {
      flavor_profile: ['따뜻한 맛', '편안한 맛'],
      recommended_foods: ['따뜻한 국물', '죽', '야채'],
      avoid_foods: ['자극적인 음식', '차가운 음식'],
      explanation: '오늘은 소화가 편안한 음식이 좋습니다. 따뜻하고 부드러운 음식으로 컨디션을 회복하세요.',
    }
  }
}

function generateDailyFashionBeauty(dailyRhythm: DailyRhythm, sajuData: SajuData): FashionBeauty {
  const energy = dailyRhythm.에너지_수준 ?? 3
  const social = dailyRhythm.사회운 ?? 3

  // 용신 오행 기반 행운 색상
  const ohhaengColors: Record<string, string[]> = {
    '목': ['초록색', '연두색'], '화': ['빨간색', '주황색'], '토': ['노란색', '갈색'],
    '금': ['흰색', '은색'], '수': ['검정색', '남색'],
  }
  const yongsinColors: string[] = []
  if (sajuData) {
    const yongsinList = sajuData.용신?.용신 || []
    for (const yong of yongsinList.slice(0, 2)) {
      yongsinColors.push(...(ohhaengColors[yong] || []))
    }
  }

  if (energy >= 4 && social >= 4) {
    const colors = yongsinColors.length > 0
      ? [...yongsinColors.slice(0, 2), '연한 파란색']
      : ['하얀색', '연한 파란색', '연두색']
    let explanation = '오늘은 밝고 활기찬 스타일이 어울립니다. '
    explanation += yongsinColors.length > 0
      ? `특히 ${yongsinColors[0]} 계열이 당신의 기운을 강화해줍니다.`
      : '깨끗하고 밝은 컬러로 좋은 인상을 주세요.'
    return {
      clothing_style: ['화사한 스타일', '밝은 컬러'],
      color_suggestions: colors.slice(0, 3),
      beauty_tips: ['자연스러운 메이크업', '생기있는 표정'],
      explanation,
    }
  } else if (energy <= 2 || social <= 2) {
    const colors = yongsinColors.length > 0
      ? [...yongsinColors.slice(0, 1), '베이지', '회색']
      : ['베이지', '회색', '네이비']
    let explanation = '오늘은 편안하고 차분한 스타일이 좋습니다. '
    explanation += yongsinColors.length > 0
      ? `${yongsinColors[0]} 포인트를 더하면 기운 보충에 도움이 됩니다.`
      : '무리하지 않는 자연스러움을 유지하세요.'
    return {
      clothing_style: ['편안한 스타일', '차분한 컬러'],
      color_suggestions: colors.slice(0, 3),
      beauty_tips: ['자연스러운 피부 표현', '편안한 헤어'],
      explanation,
    }
  } else {
    const colors = yongsinColors.length > 0
      ? [...yongsinColors.slice(0, 2), '흰색']
      : ['하늘색', '연한 노란색', '흰색']
    let explanation = '오늘은 부담 없는 스타일이 어울립니다. '
    explanation += yongsinColors.length > 0
      ? `${yongsinColors[0]} 계열 소품으로 포인트를 주면 좋습니다.`
      : '간편하면서도 정돈된 모습을 유지하세요.'
    return {
      clothing_style: ['캐주얼한 스타일', '중간 톤'],
      color_suggestions: colors.slice(0, 3),
      beauty_tips: ['깔끔한 스타일', '간단한 정리'],
      explanation,
    }
  }
}

function generateDailyShoppingFinance(dailyRhythm: DailyRhythm): ShoppingFinance {
  const decision = dailyRhythm.결정력 ?? 3

  if (decision >= 4) {
    return {
      good_to_buy: ['필요한 생활용품', '건강 관련 용품'],
      finance_advice: ['계획적인 소비', '가치 있는 투자 검토'],
      investment_focus: ['장기적 관점', '신중한 판단'],
      explanation: '오늘은 결정력이 좋은 날입니다. 필요한 것을 계획적으로 구매하기 좋은 시기입니다.',
    }
  } else {
    return {
      good_to_buy: ['긴급하지 않으면 보류', '충동구매 자제'],
      finance_advice: ['지출 기록하기', '예산 점검하기'],
      investment_focus: ['관망', '정보 수집'],
      explanation: '오늘은 큰 지출을 미루는 것이 좋습니다. 계획을 세우고 다음을 기약하세요.',
    }
  }
}

function generateDailyLivingSpace(dailyRhythm: DailyRhythm): LivingSpace {
  const energy = dailyRhythm.에너지_수준 ?? 3

  if (energy >= 4) {
    return {
      space_organization: ['불필요한 물건 정리', '공간 재배치'],
      plants_decor: ['공기정화 식물 배치', '화분 관리'],
      environmental_tips: ['환기하기', '자연광 활용'],
      explanation: '오늘은 공간을 정리하기 좋은 날입니다. 깨끗하고 상쾌한 환경을 만들어보세요.',
    }
  } else {
    return {
      space_organization: ['작은 영역만 정리', '필수 정돈'],
      plants_decor: ['관상용 식물 감상', '물주기'],
      environmental_tips: ['편안한 조명', '쾌적한 온도 유지'],
      explanation: '오늘은 편안한 공간 유지에 집중하세요. 무리한 정리보다 현상 유지가 좋습니다.',
    }
  }
}

function generateDailyRoutines(dailyRhythm: DailyRhythm): DailyRoutines {
  const energy = dailyRhythm.에너지_수준 ?? 3

  if (energy >= 4) {
    return {
      sleep_schedule: ['일찍 자고 일찍 일어나기', '규칙적인 수면 패턴'],
      morning_routine: ['가벼운 스트레칭', '충분한 아침 식사'],
      evening_routine: ['활동 정리', '내일 준비'],
      explanation: '오늘은 활동적인 루틴이 어울립니다. 아침부터 활기차게 시작하세요.',
    }
  } else {
    return {
      sleep_schedule: ['충분한 수면 시간 확보', '편안한 취침 환경'],
      morning_routine: ['천천히 일어나기', '가벼운 식사'],
      evening_routine: ['이완 활동', '명상이나 음악 감상'],
      explanation: '오늘은 여유로운 루틴이 좋습니다. 서두르지 말고 자신의 페이스를 유지하세요.',
    }
  }
}

function generateDigitalCommunication(dailyRhythm: DailyRhythm): DigitalCommunication {
  const social = dailyRhythm.사회운 ?? 3
  const concentration = dailyRhythm.집중력 ?? 3

  if (social >= 4) {
    return {
      device_usage: ['적극적인 소통', '영상 통화 활용'],
      social_media: ['긍정적인 게시물 공유', '댓글 소통'],
      online_focus_areas: ['네트워킹', '정보 교환'],
      explanation: '오늘은 디지털 소통이 활발한 날입니다. 적극적으로 연락하고 교류하세요.',
    }
  } else if (concentration <= 2) {
    return {
      device_usage: ['스마트폰 사용 제한', '필수 연락만'],
      social_media: ['SNS 휴식', '알림 끄기'],
      online_focus_areas: ['집중 시간 확보', '디지털 디톡스'],
      explanation: '오늘은 디지털 기기 사용을 줄이는 것이 좋습니다. 집중력을 보호하세요.',
    }
  } else {
    return {
      device_usage: ['적정 수준 사용', '시간 제한 설정'],
      social_media: ['필요한 정보만 확인', '수동적 소비 줄이기'],
      online_focus_areas: ['업무 관련 소통', '실용적인 정보'],
      explanation: '오늘은 디지털 사용을 적절히 조절하세요. 필요한 것만 선택적으로 이용하세요.',
    }
  }
}

function generateHobbiesCreativity(dailyRhythm: DailyRhythm): HobbiesCreativity {
  const energy = dailyRhythm.에너지_수준 ?? 3
  const concentration = dailyRhythm.집중력 ?? 3

  if (energy >= 4 && concentration >= 4) {
    return {
      creative_activities: ['그림 그리기', '글쓰기'],
      learning_recommendations: ['새로운 기술 배우기', '온라인 강의 수강'],
      entertainment_options: ['영화 감상', '전시회 관람'],
      explanation: '오늘은 창작 활동에 집중하기 좋은 날입니다. 새로운 것을 배우고 표현해보세요.',
    }
  } else if (concentration <= 2) {
    return {
      creative_activities: ['자유로운 낙서', '음악 듣기'],
      learning_recommendations: ['가벼운 독서', '팟캐스트 듣기'],
      entertainment_options: ['편안한 영상 시청', '음악 감상'],
      explanation: '오늘은 가벼운 취미 활동이 어울립니다. 부담 없이 즐길 수 있는 것을 선택하세요.',
    }
  } else {
    return {
      creative_activities: ['사진 찍기', '간단한 공예'],
      learning_recommendations: ['관심 분야 탐색', '짧은 학습'],
      entertainment_options: ['드라마 시청', '책 읽기'],
      explanation: '오늘은 적당한 취미 활동이 좋습니다. 흥미로운 것을 찾아 시간을 보내세요.',
    }
  }
}

function generateRelationshipsSocial(dailyRhythm: DailyRhythm): RelationshipsSocial {
  const social = dailyRhythm.사회운 ?? 3

  if (social >= 4) {
    return {
      communication_style: ['적극적인 대화', '진솔한 표현'],
      social_energies: ['모임 참여', '새로운 인연', '협력 활동'],
      relationship_tips: ['긍정적인 태도 유지', '경청하기'],
      explanation: '오늘은 관계 운이 좋은 날입니다. 사람들과 적극적으로 교류하세요.',
    }
  } else if (social <= 2) {
    return {
      communication_style: ['필요한 말만', '간결한 대화'],
      social_energies: ['혼자만의 시간', '소수와의 만남', '조용한 활동'],
      relationship_tips: ['무리하지 않기', '거절할 줄 알기'],
      explanation: '오늘은 관계에서 에너지를 아끼는 것이 좋습니다. 혼자만의 시간을 가지세요.',
    }
  } else {
    return {
      communication_style: ['자연스러운 대화', '편안한 소통'],
      social_energies: ['가까운 사람들과', '익숙한 장소에서', '부담 없는 만남'],
      relationship_tips: ['적당한 거리 유지', '선택적 교류'],
      explanation: '오늘은 편안한 관계에 집중하세요. 가까운 사람들과 자연스럽게 어울리세요.',
    }
  }
}

function generateSeasonalEnvironment(dailyRhythm: DailyRhythm, targetDate: string): SeasonalEnvironment {
  const month = parseInt(targetDate.split('-')[1], 10) || new Date().getMonth() + 1

  if (month >= 3 && month <= 5) {
    return {
      weather_adaptation: ['가벼운 외출복 준비', '일교차 대비'],
      seasonal_activities: ['봄나물 먹기', '꽃 구경', '산책'],
      environmental_focus: ['환절기 건강 관리', '꽃가루 알레르기 주의'],
      explanation: '봄철입니다. 화사한 계절을 즐기되, 일교차와 알레르기에 주의하세요.',
    }
  } else if (month >= 6 && month <= 8) {
    return {
      weather_adaptation: ['통풍 잘되는 옷', '자외선 차단'],
      seasonal_activities: ['시원한 음식', '수분 보충', '물놀이'],
      environmental_focus: ['에어컨 적정 온도 유지', '실내외 온도차 조절'],
      explanation: '여름철입니다. 더위를 식히되, 과도한 냉방은 피하세요.',
    }
  } else if (month >= 9 && month <= 11) {
    return {
      weather_adaptation: ['겹쳐 입기', '환절기 대비'],
      seasonal_activities: ['단풍 구경', '독서', '가을 과일'],
      environmental_focus: ['건조함 주의', '환기 자주 하기'],
      explanation: '가을철입니다. 선선한 날씨를 즐기되, 건조함에 대비하세요.',
    }
  } else {
    return {
      weather_adaptation: ['방한복 준비', '보온 철저'],
      seasonal_activities: ['따뜻한 차', '실내 활동', '겨울 운동'],
      environmental_focus: ['실내 습도 유지', '체온 관리'],
      explanation: '겨울철입니다. 따뜻하게 지내고, 실내 습도를 유지하세요.',
    }
  }
}

// ============================================================
// 최소 콘텐츠 길이 보장
// ============================================================

function ensureMinimumContentLength(content: DailyContent, dailyRhythm: DailyRhythm): DailyContent {
  const MIN_CHARS = 700

  function leftPageLength(c: DailyContent): number {
    return (
      c.summary.length +
      c.rhythm_description.length +
      c.meaning_shift.length +
      c.rhythm_question.length
    )
  }

  if (leftPageLength(content) >= MIN_CHARS) return content

  const energy = dailyRhythm.에너지_수준 ?? 3
  const concentration = dailyRhythm.집중력 ?? 3
  const social = dailyRhythm.사회운 ?? 3

  const expansionParagraphs: string[] = []

  if (concentration <= 3) {
    expansionParagraphs.push(
      '집중력이 고르게 분산되는 흐름이므로, 한 가지 일에 오래 매달리기보다는 ' +
      '여러 가지 작은 작업을 번갈아 처리하는 방식이 효율적입니다. ' +
      '짧은 휴식을 자주 취하며 리듬을 유지해보세요.',
    )
  }

  if (social <= 3) {
    expansionParagraphs.push(
      '대인 관계에서는 무리하게 에너지를 쏟기보다 자연스러운 교류에 집중하는 것이 좋습니다. ' +
      '가까운 사람과의 편안한 대화가 오늘의 관계 에너지를 채워줄 것입니다.',
    )
  }

  if (energy <= 3) {
    expansionParagraphs.push(
      '오늘은 자신의 페이스를 존중하는 것이 중요합니다. ' +
      '외부의 기대나 속도에 맞추려 하기보다, 내면의 리듬에 귀 기울여보세요. ' +
      '작은 성취를 하나씩 쌓아가는 것이 오늘의 가장 현명한 전략입니다.',
    )
  }

  // 일반 보강 블록
  expansionParagraphs.push(
    '하루를 시작하기 전 잠시 멈추어 오늘 가장 중요한 일 한 가지를 떠올려보세요. ' +
    '그 한 가지에 마음을 모으는 것만으로도 하루의 방향이 달라질 수 있습니다. ' +
    '완벽하지 않아도 괜찮으니, 오늘 할 수 있는 만큼만 정성을 다해보세요.',
  )

  // 리듬 해설에 보강 문단 추가
  for (const para of expansionParagraphs) {
    if (leftPageLength(content) >= MIN_CHARS) break
    content = { ...content, rhythm_description: content.rhythm_description + ' ' + para }
  }

  // 그래도 부족하면 의미 전환 확장
  if (leftPageLength(content) < MIN_CHARS) {
    content = {
      ...content,
      meaning_shift: content.meaning_shift + ' ' +
        '오늘 하루의 의미는 결과가 아니라 과정에 있습니다. ' +
        '지금 이 순간 느끼는 감정과 생각을 있는 그대로 인정하고, ' +
        '그 안에서 작은 배움을 찾아보세요. 매일의 작은 깨달음이 모여 큰 변화를 만듭니다.',
    }
  }

  return content
}

// ============================================================
// assembleMonthlyContent
// ============================================================

/**
 * 월간 콘텐츠 조합
 *
 * @param year 년도
 * @param month 월
 * @param monthlyRhythm 월간 리듬 분석 결과
 * @returns 월간 콘텐츠
 */
export function assembleMonthlyContent(
  year: number,
  month: number,
  monthlyRhythm: MonthlyRhythm,
): MonthlyContent {
  const theme = monthlyRhythm.주제 || '균형과 조화'
  const priorities = monthlyRhythm.우선순위 || []
  const dailyEnergy = monthlyRhythm.일별_에너지 || {}
  const opportunities = monthlyRhythm.기회_요소 || []
  const challenges = monthlyRhythm.도전_요소 || []

  // summary (300+ chars)
  let summary = ''
  try {
    const prioritiesText = priorities.slice(0, 3).join(', ')
    const opportunitiesText = opportunities.slice(0, 2).join(', ')
    const challengesText = challenges.slice(0, 2).join(', ')
    const energies = Object.values(dailyEnergy)
    const avgEnergy = energies.length > 0 ? energies.reduce((a, b) => a + b, 0) / energies.length : 3
    const energyDesc = avgEnergy >= 4 ? '활발한 에너지' : (avgEnergy >= 3 ? '안정적인 흐름' : '차분한 시기')

    summary =
      `이번 달은 '${theme}'의 시기입니다. ` +
      `${prioritiesText} 등이 주요 우선순위이며, ${energyDesc}가 지속됩니다. ` +
      `특히 ${opportunitiesText} 등의 기회 요소를 적극 활용하면 좋습니다. ` +
      `반면 ${challengesText} 등의 도전 요소에 유의하며 균형을 유지하는 것이 중요합니다. ` +
      `이달의 평균 에너지는 ${avgEnergy.toFixed(1)}점(5점 만점)으로, ` +
      `전반적으로 ${avgEnergy >= 3.5 ? '긍정적인' : '신중한'} 접근이 효과적입니다. ` +
      `매일의 에너지 흐름에 맞춰 중요한 결정과 휴식을 조율하시기 바랍니다. ` +
      `에너지가 높은 날에는 중요한 업무와 대화를 배치하고, 낮은 날에는 정리와 재충전에 집중하는 것이 ` +
      `이달을 가장 효율적으로 보내는 방법입니다. 이번 달도 자신의 리듬을 존중하며 나아가세요.`
  } catch {
    summary = ''
  }

  // keywords (5+ items)
  let keywords: string[] = []
  try {
    const kwSources = [...priorities, ...opportunities, theme]
    const rawKeywords: string[] = []
    for (const src of kwSources) {
      const words = src.replace(/과/g, ' ').replace(/와/g, ' ').replace(/의/g, ' ')
        .split(/\s+/)
        .filter(w => w.trim().length >= 2)
        .map(w => w.trim())
      rawKeywords.push(...words.slice(0, 2))
    }
    keywords = Array.from(new Set(rawKeywords)).slice(0, 8)
    if (keywords.length < 5) {
      const defaults = ['에너지', '흐름', '균형', '집중', '성장']
      keywords.push(...defaults.slice(0, 5 - keywords.length))
    }
  } catch {
    keywords = []
  }

  // weekly_focus / weekly_caution
  let weeklyFocus: string[] = []
  let weeklyCaution: string[] = []
  try {
    const cal = dailyEnergy
    const weeks: [string, number[]][] = [
      ['첫째 주 (1-7일)', Array.from({ length: 7 }, (_, i) => cal[i + 1] ?? 3)],
      ['둘째 주 (8-14일)', Array.from({ length: 7 }, (_, i) => cal[i + 8] ?? 3)],
      ['셋째 주 (15-21일)', Array.from({ length: 7 }, (_, i) => cal[i + 15] ?? 3)],
      ['넷째 주 (22-28일)', Array.from({ length: 7 }, (_, i) => cal[i + 22] ?? 3)],
    ]
    weeklyFocus = weeks
      .filter(([, days]) => days.length > 0 && days.reduce((a, b) => a + b, 0) / days.length >= 4)
      .map(([label]) => label)
    weeklyCaution = weeks
      .filter(([, days]) => days.length > 0 && days.reduce((a, b) => a + b, 0) / days.length <= 2)
      .map(([label]) => label)
  } catch {
    weeklyFocus = []
    weeklyCaution = []
  }

  // flow_description (200+ chars)
  let flowDescription = ''
  try {
    const energies = Object.values(dailyEnergy)
    const highDays = energies.filter(e => e >= 4).length
    const lowDays = energies.filter(e => e <= 2).length
    const totalDays = energies.length || 1
    const firstHalfSum = energies.slice(0, 15).reduce((a, b) => a + b, 0)
    const secondHalfSum = energies.slice(15).reduce((a, b) => a + b, 0)

    flowDescription =
      `이달의 에너지 흐름을 살펴보면, 전체 ${totalDays}일 중 ` +
      `에너지가 높은 날이 ${highDays}일, 낮은 날이 ${lowDays}일입니다. ` +
      (firstHalfSum > secondHalfSum
        ? '상반부에 에너지가 집중되어 초반에 중요한 일을 처리하는 것이 유리합니다. '
        : '하반부로 갈수록 에너지가 상승하므로 중요한 결정은 월 중반 이후로 조율하세요. ') +
      '주간 흐름을 미리 파악하고 에너지 높은 날에 집중 작업, 낮은 날에 휴식과 정리를 배분하면 이달을 더욱 효율적으로 보낼 수 있습니다.'
  } catch {
    flowDescription = ''
  }

  return {
    year_month: `${year}년 ${month}월`,
    theme,
    priorities,
    calendar_data: dailyEnergy,
    opportunities,
    challenges,
    summary,
    keywords,
    weekly_focus: weeklyFocus,
    weekly_caution: weeklyCaution,
    flow_description: flowDescription,
  }
}

// ============================================================
// assembleYearlyContent
// ============================================================

/**
 * 연간 콘텐츠 조합
 *
 * @param year 년도
 * @param yearlyRhythm 연간 리듬 분석 결과
 * @returns 연간 콘텐츠
 */
export function assembleYearlyContent(
  year: number,
  yearlyRhythm: YearlyRhythm,
): YearlyContent {
  const theme = yearlyRhythm.주제 || '안정과 성장의 해'
  const flow = yearlyRhythm.전체_흐름 || ''
  const monthlySignals = yearlyRhythm.월별_신호 || {}
  const coreTasks = yearlyRhythm.핵심_과제 || []

  // summary (500+ chars)
  let summary = ''
  try {
    const energies = Object.values(monthlySignals).map(sig => sig.에너지 ?? 3)
    const avgEnergy = energies.length > 0 ? energies.reduce((a, b) => a + b, 0) / energies.length : 3
    const h1Avg = energies.length >= 6 ? energies.slice(0, 6).reduce((a, b) => a + b, 0) / 6 : avgEnergy
    const h2Avg = energies.length >= 12 ? energies.slice(6).reduce((a, b) => a + b, 0) / 6 : avgEnergy
    const coreTasksText = coreTasks.slice(0, 3).join(', ')

    summary =
      `${year}년은 '${theme}'의 해입니다. ` +
      `${flow} ` +
      `상반기는 평균 에너지 ${h1Avg.toFixed(1)}점으로 ${h1Avg >= 3.5 ? '활발한 추진력을 발휘하기 좋은 시기' : '차분히 기반을 다지는 시기'}이며, ` +
      `하반기는 평균 에너지 ${h2Avg.toFixed(1)}점으로 ${h2Avg >= 3.5 ? '결실을 맺고 완성도를 높이는 시기' : '내실을 다지고 정리하는 시기'}입니다. ` +
      `올해의 핵심 과제는 ${coreTasksText} 등이며, 이를 중심으로 한 해를 설계하는 것이 효과적입니다. ` +
      `월별 에너지 흐름을 미리 파악하고 에너지가 높은 달에 중요한 결정과 도전을 배치하며, ` +
      `에너지가 낮은 달에는 휴식과 재정비를 통해 지속 가능한 페이스를 유지하시기 바랍니다. ` +
      `연간 흐름을 큰 그림으로 바라보고 분기별 목표를 설정하면, 방향 없이 흘러가는 시간을 줄이고 ` +
      `의미 있는 성취를 쌓아갈 수 있습니다. 올 한 해도 자신만의 속도와 리듬을 소중히 여기며 ` +
      `앞으로 나아가시기 바랍니다. 매월의 에너지를 점검하며 유연하게 계획을 조정하는 것이 핵심입니다. ` +
      `계획은 유연하게, 실행은 꾸준하게 — 이 두 가지 균형이 한 해를 풍성하게 만드는 비결입니다. ` +
      `자신을 믿고 한 걸음씩 나아가다 보면, 연말에는 의미 있는 결실을 마주하게 될 것입니다.`
  } catch {
    summary = ''
  }

  // keywords (5+ items)
  let keywords: string[] = []
  try {
    const kwSources = [...coreTasks, theme, flow.substring(0, 20)]
    const rawKeywords: string[] = []
    for (const src of kwSources) {
      const words = String(src).replace(/과/g, ' ').replace(/와/g, ' ').replace(/의/g, ' ')
        .split(/\s+/)
        .filter(w => w.trim().length >= 2)
        .map(w => w.trim())
      rawKeywords.push(...words.slice(0, 2))
    }
    keywords = Array.from(new Set(rawKeywords)).slice(0, 8)
    if (keywords.length < 5) {
      const defaults = ['성장', '변화', '균형', '완성', '도약']
      keywords.push(...defaults.slice(0, 5 - keywords.length))
    }
  } catch {
    keywords = []
  }

  // first_half_focus / second_half_focus
  let firstHalfFocus = ''
  let secondHalfFocus = ''
  try {
    const energies = Object.values(monthlySignals).map(sig => sig.에너지 ?? 3)
    const h1Avg = energies.length >= 6 ? energies.slice(0, 6).reduce((a, b) => a + b, 0) / 6 : 3
    const h2Avg = energies.length >= 12 ? energies.slice(6).reduce((a, b) => a + b, 0) / 6 : 3
    firstHalfFocus = `상반기(1-6월)는 평균 에너지 ${h1Avg.toFixed(1)}점 — ${h1Avg >= 3.5 ? '적극적인 추진과 새로운 시작에 집중하세요.' : '내실을 다지고 기반을 강화하는 시기입니다.'}`
    secondHalfFocus = `하반기(7-12월)는 평균 에너지 ${h2Avg.toFixed(1)}점 — ${h2Avg >= 3.5 ? '상반기의 성과를 결실로 이어가는 시기입니다.' : '마무리와 정리에 집중하며 다음 해를 준비하세요.'}`
  } catch {
    firstHalfFocus = ''
    secondHalfFocus = ''
  }

  return {
    year,
    theme,
    flow_summary: flow,
    monthly_signals: monthlySignals,
    core_tasks: coreTasks,
    summary,
    keywords,
    first_half_focus: firstHalfFocus,
    second_half_focus: secondHalfFocus,
  }
}
