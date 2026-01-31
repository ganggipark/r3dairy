# 사주 계산기 분석 보고서

## 개요
`backend/saju-calculator/src/completeSajuCalculator.ts` 파일을 분석하여, 색상/음식/활동 추천에 활용할 수 있는 모든 사주 요소를 확인했습니다.

---

## 계산 가능한 모든 사주 요소

### 1. 사주팔자 (FourPillars)
```typescript
FourPillars {
  year: { gan, ji, ganJi, ganOhHaeng, jiOhHaeng }  // 년주
  month: { gan, ji, ganJi, ganOhHaeng, jiOhHaeng } // 월주
  day: { gan, ji, ganJi, ganOhHaeng, jiOhHaeng }   // 일주
  time: { gan, ji, ganJi, ganOhHaeng, jiOhHaeng }  // 시주
}
```

**활용 예시**:
- 일간(day.gan): 김태현 → 일간 '갑' (큰 나무) → 녹색 계열 추천
- 시지(time.ji): '자' (쥐띠, 수 오행) → 차가운 음식/검은색 추천

---

### 2. 오행 분석 (OhHaengAnalysis) ⭐⭐⭐ 핵심
```typescript
OhHaengAnalysis {
  balance: { 목: 20, 화: 30, 토: 15, 금: 10, 수: 25 }  // 비율
  dominant: '화'          // 가장 강한 오행
  weak: '금'              // 가장 약한 오행
  dominantScore: 30       // 최강 점수
  weakScore: 10           // 최약 점수
  isBalanced: false       // 균형 여부
}
```

**활용 예시 (색상/음식/방향)**:
| 오행 | 색상 | 음식 | 방향 | 시간대 |
|------|------|------|------|--------|
| 목(木) | 녹색, 청록 | 채소, 과일, 신맛 | 동쪽 | 오전 3-7시 |
| 화(火) | 빨강, 주황, 분홍 | 매운 음식, 고기 | 남쪽 | 오전 11시-오후 1시 |
| 토(土) | 노랑, 갈색, 베이지 | 곡물, 단맛 | 중앙 | 계절 변환기 |
| 금(金) | 흰색, 금색, 은색 | 견과류, 매콤한 음식 | 서쪽 | 오후 3-7시 |
| 수(水) | 검정, 파랑, 남색 | 해산물, 짠맛 | 북쪽 | 오후 9시-새벽 1시 |

---

### 3. 용신/기신 분석 (YongSinAnalysis) ⭐⭐⭐ 매우 핵심
```typescript
YongSinAnalysis {
  yongSin: ['목', '화']          // 용신 (도움이 되는 오행)
  giSin: ['금', '토']            // 기신 (방해하는 오행)
  huiSin: ['수']                 // 희신 (보조 오행)
  yongSinReason: "일간이 약하여 기운을 보충해주는 오행이 필요합니다."
  giSinReason: "일간을 더 약하게 하는 오행은 피해야 합니다."
  yongSinScore: { 목: 80, 화: 80, 토: 30, 금: 30, 수: 65 }
}
```

**활용 전략**:
1. **용신 오행** → 강화할 색상/음식 추천
   - 용신이 '목'이면 → 녹색 옷, 채소/과일 추천
   - 용신이 '화'이면 → 빨간색 액세서리, 매운 음식 추천

2. **기신 오행** → 피할 색상/음식 경고
   - 기신이 '금'이면 → 흰색/금색 의상 자제, 견과류 과다섭취 주의
   - 기신이 '토'이면 → 노란색/갈색 최소화, 단맛 자제

3. **희신 오행** → 보조 추천
   - 희신이 '수'이면 → 파란색 소품, 해산물 적당량 섭취

---

### 4. 격국 분석 (GyeokGukAnalysis)
```typescript
GyeokGukAnalysis {
  dayMaster: '갑'           // 일간
  dayMasterOhHaeng: '목'    // 일간 오행
  strength: '신강'          // 신강/신약/중화
  monthBranch: '인'         // 월지
  season: '봄'              // 계절
  gyeokGukType: '신강격'
  description: "일간의 기운이 강하여 재성과 관성이 필요합니다."
}
```

**활용 예시**:
- **신강(일간 강함)**: 기운을 빼주는 활동 → 운동 강도 높게, 사회 활동 활발
- **신약(일간 약함)**: 기운을 보충하는 활동 → 휴식 중심, 수면 충분히, 운동 가볍게
- **중화(균형)**: 활동성 높이기 → 창작 활동, 새로운 도전

---

### 5. 십성 분석 (SipSungAnalysis)
```typescript
SipSungAnalysis {
  balance: { 비겁: 20, 식상: 30, 재성: 15, 관성: 25, 인성: 10 }
  detail: {
    비견: 10, 겁재: 10,  // 비겁(형제/경쟁)
    식신: 20, 상관: 10,  // 식상(표현/창의)
    정재: 10, 편재: 5,   // 재성(재물/실용)
    정관: 15, 편관: 10,  // 관성(책임/리더십)
    정인: 5,  편인: 5,   // 인성(학습/자기계발)
  }
  dominant: '식상'  // 가장 강한 십성
  weak: '인성'      // 가장 약한 십성
}
```

**활용 예시 (활동/취미 추천)**:
| 십성 | 추천 활동 | 피할 활동 |
|------|-----------|-----------|
| 비겁 강함 | 경쟁 스포츠, 독립 프로젝트 | 팀 협업 과다 |
| 식상 강함 | 창작, 글쓰기, 발표 | 단순 반복 작업 |
| 재성 강함 | 투자, 쇼핑, 거래 | 비실용적 취미 |
| 관성 강함 | 리더십 역할, 조직 활동 | 무책임한 행동 |
| 인성 강함 | 독서, 강의 수강, 연구 | 실행 없는 학습만 |

---

### 6. 대운 분석 (DaewoonAnalysis)
```typescript
DaewoonAnalysis {
  startAge: 3
  direction: '순행' | '역행'
  list: [
    { cycle: 1, startAge: 3, endAge: 12, gan: '갑', ji: '자',
      ohHaeng: '목', score: 75, isYongSin: true },
    ...
  ]
  current: { startAge: 23, endAge: 32, gan: '병', ji: '인', score: 65 }
  currentAge: 33
  bestPeriod: { ... }    // 최고 대운 시기
  worstPeriod: { ... }   // 최악 대운 시기
}
```

**활용 예시**:
- **현재 대운 점수 80 이상**: "오늘은 대운의 기운을 받는 날, 중요한 결정하기 좋습니다"
- **현재 대운 점수 40 이하**: "대운 에너지가 약한 시기, 안정적인 선택 추천"
- **대운 오행이 용신**: "이번 10년은 성장기! 도전적인 목표 설정"

---

### 7. 세운 분석 (SewoonItem) ⭐⭐⭐ 매일 바뀜
```typescript
SewoonItem {
  year: 2026
  age: 33
  gan: '병'
  ji: '오'
  ganJi: '병오'
  ohHaeng: '화'           // ⭐ 올해 오행
  animal: '말'
  score: 70               // ⭐ 올해 점수
  description: "2026년은 병오년(말띠 해)입니다. 용신 오행(화)이 작용하여 유리한 해입니다."
  isYongSin: true         // ⭐ 용신 여부
  daewoonInteraction: 10  // 대운과의 조화도
}
```

**활용 예시 (매일 다른 세운 계산 가능)**:
- 2026년 1월 30일: 세운 '병오'(화) + 일진 계산 → 오늘의 오행 결정
- 오늘 세운이 용신이면 → 색상/음식 강화 추천
- 오늘 세운이 기신이면 → 해당 오행 회피 추천

---

### 8. 신살 분석 (SinsalAnalysis)
```typescript
SinsalAnalysis {
  gilSin: ['천을귀인']              // 길신 (좋은 신살)
  hyungSin: []                      // 흉신 (나쁜 신살)
  hasCheonEulGuiIn: true            // 천을귀인 (귀인의 도움)
  hasMunChangGuiIn: false           // 문창귀인 (학문)
  hasYeokMaSal: false               // 역마살 (이동/변화)
  hasDoHwaSal: false                // 도화살 (인기/매력)
  hasGongMang: false                // 공망 (허무함)
  hasYangInSal: false               // 양인살 (공격성)
  hasGeopSal: false                 // 겁살 (재물 손실)
  summary: "길신: 천을귀인. "
}
```

**활용 예시**:
- 천을귀인 있음 → "오늘은 사람들의 도움을 받기 좋은 날"
- 역마살 있음 → "이동이나 변화가 자연스러운 날"
- 도화살 있음 → "대인관계나 외모 관리에 신경 쓰기"

---

### 9. 관계 분석 (PillarRelations)
```typescript
PillarRelations {
  cheonganHap: ['년월 갑기합']     // 천간합 (조화)
  jijiYukHap: ['월일 인해합']      // 지지육합 (조화)
  jijiChung: ['일시 자오충']       // 지지충 (충돌)
  jijiSamHap: []                   // 삼합
  jijiHyung: []                    // 형
  summary: "천간합: 1개, 지지충: 1개"
}
```

**활용 예시**:
- 합(合) 많음 → "협력과 소통이 잘 되는 날, 회의/미팅 추천"
- 충(沖) 많음 → "변화나 갈등 가능성, 신중한 태도 필요"

---

### 10. 성격 분석 (PersonalityAnalysis)
```typescript
PersonalityAnalysis {
  dayMasterTraits: {
    keyword: '큰 나무, 리더',
    strengths: ['리더십', '추진력', '정의감'],
    weaknesses: ['고집', '융통성 부족'],
    advice: '유연함을 기르세요'
  }
  dominantSipsung: {
    type: '식상',
    traits: ['창의성', '표현력', '자유로움']
  }
  careerAptitude: ['예술가', '작가', '강사']
  relationshipStyle: '자유롭고 창의적인 소통을 즐깁니다.'
}
```

---

## 🎯 색상/음식/활동 추천 시스템 설계

### 우선순위 계산 알고리즘

```typescript
function calculateDailyRecommendations(
  sajuData: CompleteSajuData,
  targetDate: Date
): DailyRecommendations {

  // 1단계: 오늘의 일진 계산 (세운 + 일진)
  const todayDayPillar = calculateDayPillar(targetDate);
  const todayOhHaeng = todayDayPillar.ganOhHaeng;  // 오늘의 주 오행

  // 2단계: 용신 점수 적용
  const yongSinScore = sajuData.yongSin.yongSinScore;
  const todayScore = yongSinScore[todayOhHaeng];  // 오늘 오행의 용신 점수

  // 3단계: 대운/세운 보정
  const daewoonBonus = sajuData.daewoon.current?.isYongSin ? 10 : 0;
  const sewoonBonus = sajuData.currentYearSewoon.isYongSin ? 5 : 0;
  const finalScore = todayScore + daewoonBonus + sewoonBonus;

  // 4단계: 점수에 따른 추천 강도 결정
  let recommendationLevel: 'high' | 'medium' | 'low';
  if (finalScore >= 75) recommendationLevel = 'high';       // 강력 추천
  else if (finalScore >= 50) recommendationLevel = 'medium'; // 보통 추천
  else recommendationLevel = 'low';                          // 약한 추천 또는 회피

  // 5단계: 오행별 색상/음식 매핑
  const recommendations = {
    colors: getColorsByOhHaeng(todayOhHaeng, recommendationLevel),
    foods: getFoodsByOhHaeng(todayOhHaeng, recommendationLevel),
    directions: getDirectionByOhHaeng(todayOhHaeng),
    activities: getActivitiesByOhHaeng(todayOhHaeng, sajuData.gyeokGuk.strength),
  };

  return recommendations;
}
```

### 오행별 추천 매핑 테이블

#### 색상 매핑
```typescript
const COLOR_BY_OHAENG = {
  '목': {
    primary: ['녹색', '청록색', '연두색'],
    secondary: ['파란색', '초록색'],
    accent: ['하늘색'],
  },
  '화': {
    primary: ['빨강', '주황', '분홍'],
    secondary: ['보라색', '자주색'],
    accent: ['핑크'],
  },
  '토': {
    primary: ['노랑', '갈색', '베이지'],
    secondary: ['황토색', '오렌지'],
    accent: ['살구색'],
  },
  '금': {
    primary: ['흰색', '금색', '은색'],
    secondary: ['회색', '파스텔'],
    accent: ['아이보리'],
  },
  '수': {
    primary: ['검정', '파랑', '남색'],
    secondary: ['하늘색', '청록'],
    accent: ['민트'],
  },
};
```

#### 음식 매핑
```typescript
const FOOD_BY_OHAENG = {
  '목': {
    category: '채소/과일',
    examples: ['샐러드', '과일', '녹즙', '허브티'],
    taste: '신맛',
    avoid: '매운맛(금극목)',
  },
  '화': {
    category: '고기/매운음식',
    examples: ['고기 구이', '매운 요리', '커피', '홍차'],
    taste: '쓴맛',
    avoid: '짠맛(수극화)',
  },
  '토': {
    category: '곡물/단맛',
    examples: ['밥', '빵', '고구마', '단호박', '꿀'],
    taste: '단맛',
    avoid: '신맛(목극토)',
  },
  '금': {
    category: '견과류/매콤한맛',
    examples: ['견과류', '무', '백김치', '생강차'],
    taste: '매운맛',
    avoid: '쓴맛(화극금)',
  },
  '수': {
    category: '해산물/짠맛',
    examples: ['생선', '미역', '해조류', '조개'],
    taste: '짠맛',
    avoid: '단맛(토극수)',
  },
};
```

#### 방향 매핑
```typescript
const DIRECTION_BY_OHAENG = {
  '목': '동쪽',
  '화': '남쪽',
  '토': '중앙',
  '금': '서쪽',
  '수': '북쪽',
};
```

#### 시간대 매핑
```typescript
const TIME_BY_OHAENG = {
  '목': '오전 3-7시 (묘시, 인시)',
  '화': '오전 9-오후 1시 (사시, 오시)',
  '토': '계절 전환기, 오후 1-3시(미시), 저녁 7-9시(술시)',
  '금': '오후 3-7시 (신시, 유시)',
  '수': '오후 9시-새벽 1시 (해시, 자시)',
};
```

---

## 🔥 실제 적용 예시

### 사례 1: 김태현 (일간 갑목, 신약격, 용신 목/수)

**2026년 1월 30일 (병오년 경인월 갑자일)**

```typescript
// 계산 과정
일진 오행: '목' (갑자일 → 갑=목)
용신: ['목', '수']
용신 점수: { 목: 80, 수: 80, 화: 50, 토: 30, 금: 30 }
오늘 점수: 80 (목이 용신이므로 고점수)

// 최종 추천
{
  colors: {
    priority: 'high',
    primary: ['녹색', '청록색', '연두색'],  // 목 강화
    secondary: ['파란색', '검정'],         // 수 보조
    avoid: ['흰색', '금색'],               // 금(기신) 회피
  },
  foods: {
    priority: 'high',
    breakfast: '블루베리 + 그리스 요거트 + 녹즙',  // 목+수
    lunch: '연어 샐러드 (채소 많이)',               // 수+목
    snack: '수박, 포도, 키위',                      // 수+목
    drinks: '녹차, 페퍼민트차',                     // 목
    avoid: '견과류 과다(금 강화)',
  },
  workspace: {
    direction: '동쪽 창가',  // 목=동쪽
    items: '녹색 소품, 파란색 머그컵',
  },
  activities: {
    exercise: '러닝 5-6km (가볍게, 신약이므로 무리 금지)',
    hobby: '숲 산책, 식물 키우기',
    avoid: '격렬한 운동 (체력 소모)',
  },
  timeSlots: {
    best: '오전 3-7시 (목 기운 최고)',
    good: '오후 9시-새벽 1시 (수 기운)',
    avoid: '오후 3-7시 (금 기운, 기신)',
  }
}
```

---

### 사례 2: 박서연 (일간 정화, 신강격, 용신 토/금)

**2026년 1월 30일 (병오년 경인월 갑자일)**

```typescript
// 계산 과정
일진 오행: '목' (갑자일 → 갑=목)
용신: ['토', '금']
용신 점수: { 토: 80, 금: 80, 수: 50, 목: 30, 화: 30 }
오늘 점수: 30 (목이 기신이므로 저점수)

// 최종 추천
{
  colors: {
    priority: 'low',  // 오늘은 기신 날
    primary: ['노란색', '갈색', '베이지'],  // 토 강화
    secondary: ['흰색', '은색'],            // 금 보조
    avoid: ['녹색', '청록색'],              // 목(기신) 회피!
  },
  foods: {
    priority: 'medium',
    breakfast: '고구마 + 견과류',           // 토+금
    lunch: '현미밥 + 무나물 + 생강차',     // 토+금
    snack: '바나나, 곶감',                  // 토
    avoid: '샐러드, 신맛 과일(목 강화)',
  },
  workspace: {
    direction: '중앙 또는 서쪽',  // 토=중앙, 금=서쪽
    items: '노란색 소품, 흰색 머그컵',
  },
  activities: {
    exercise: '요가, 필라테스 (안정적인 운동)',
    hobby: '도자기, 정리정돈',
    avoid: '격렬한 유산소 (목 기운 강화)',
  },
  warning: '⚠️ 오늘은 기신 오행의 날입니다. 녹색 계열 회피, 채소 과다 섭취 자제'
}
```

---

## 📋 결론

### 활용 가능한 계산 요소 정리

| 요소 | 변동 주기 | 활용도 | 비고 |
|------|-----------|--------|------|
| **용신/기신** | 평생 고정 | ⭐⭐⭐⭐⭐ | 가장 중요! |
| **일진 오행** | 매일 변경 | ⭐⭐⭐⭐⭐ | 매일 다른 추천 |
| **오행 균형** | 평생 고정 | ⭐⭐⭐⭐ | 기본 체질 |
| **격국** | 평생 고정 | ⭐⭐⭐⭐ | 활동 강도 결정 |
| **십성** | 평생 고정 | ⭐⭐⭐ | 활동 종류 결정 |
| **대운** | 10년마다 | ⭐⭐⭐ | 장기 운세 |
| **세운** | 매년 변경 | ⭐⭐⭐ | 연간 운세 |
| **신살** | 평생 고정 | ⭐⭐ | 보조 참고 |
| **합충** | 평생 고정 | ⭐⭐ | 관계 조언 |

---

## 🚀 구현 우선순위

### Phase 1: 핵심 기능 (필수)
1. **용신/기신 계산** → 색상/음식 기본 매핑
2. **일진 계산** → 매일 다른 오행 적용
3. **오행별 추천 DB** → 색상/음식/방향/시간대

### Phase 2: 정교화
4. **점수 계산 알고리즘** → 용신+대운+세운 종합 점수
5. **격국 반영** → 신강/신약에 따른 활동 강도 조절
6. **십성 반영** → 활동 종류 개인화

### Phase 3: 고급 기능
7. **시간대별 세밀 조정** → 시진까지 계산
8. **신살 보너스** → 천을귀인 날 특별 조언
9. **합충 분석** → 관계 운세 조언

---

## 📊 데이터 흐름

```
사용자 출생 정보
  ↓
CompleteSajuData 계산
  ├─ 용신/기신 (yongSin) ⭐
  ├─ 오행 균형 (ohHaeng)
  ├─ 격국 (gyeokGuk)
  ├─ 십성 (sipSung)
  ├─ 대운 (daewoon)
  └─ 세운 (sewoon)
  ↓
오늘 날짜 입력
  ↓
일진 계산 (calculateDayPillar)
  ↓
오늘의 오행 도출
  ↓
용신 점수 매핑 (yongSinScore)
  ↓
추천 강도 결정 (high/medium/low)
  ↓
오행별 매핑 테이블 조회
  ↓
최종 추천 생성
  ├─ 색상 (primary, secondary, avoid)
  ├─ 음식 (breakfast, lunch, snack, avoid)
  ├─ 방향 (workspace direction)
  ├─ 시간대 (best/good/avoid)
  ├─ 활동 (exercise, hobby, avoid)
  └─ 경고 (기신 날 특별 주의사항)
```

---

## ✅ 체크리스트

### 구현 확인 사항
- [x] 사주 계산기 코드 확인
- [x] 용신/기신 계산 로직 확인
- [x] 오행별 속성 매핑 확인
- [ ] 색상 추천 로직 구현
- [ ] 음식 추천 로직 구현
- [ ] 방향/시간대 추천 로직 구현
- [ ] 일진 계산 API 구현
- [ ] 추천 점수 알고리즘 구현
- [ ] 테스트 케이스 작성

---

이 보고서를 기반으로 색상/음식/활동 추천 시스템을 구현할 수 있습니다!
