## Content Assembly Engine

RhythmSignal(내부 표현) → DailyContent(사용자 노출) 변환 엔진

## 📋 개요

Content Assembly Engine은 Rhythm Analysis Engine에서 생성된 리듬 신호를 사용자가 읽을 수 있는 콘텐츠로 변환합니다.

### 핵심 역할

1. **내부 용어 → 사용자 용어 변환**
   - ❌ 사주명리, 천간, 지지 → ✅ 흐름, 리듬, 에너지
2. **10개 블록 생성**
   - 요약, 키워드, 해설, 집중/주의, Do/Avoid, 시간/방향, 트리거, 의미전환, 질문
3. **최소 400-600자 콘텐츠 생성**
4. **설명형 문단 포함** (카드 전용 요약 금지)

## 📁 파일 구조

```
content/
├── __init__.py       # 모듈 초기화
├── models.py         # 데이터 모델 (DailyContent 등)
├── assembly.py       # 콘텐츠 조립 메인 로직
├── validator.py      # 스키마 검증 및 품질 체크
└── README.md         # 이 파일
```

## 🔧 사용 방법

### 1. 기본 사용법

```python
from datetime import date, time
from src.rhythm.models import BirthInfo, Gender
from src.rhythm.signals import create_daily_rhythm
from src.content.assembly import create_daily_content

# 1. 출생 정보
birth_info = BirthInfo(
    name="홍길동",
    birth_date=date(1990, 1, 15),
    birth_time=time(14, 30),
    gender=Gender.MALE,
    birth_place="서울"
)

# 2. 리듬 신호 생성 (내부 표현)
signal = create_daily_rhythm(birth_info, date.today())

# 3. 콘텐츠 생성 (사용자 노출)
content = create_daily_content(signal)

print(f"요약: {content.summary}")
print(f"키워드: {', '.join(content.keywords)}")
print(f"총 글자 수: {content.get_total_text_length()}")
```

### 2. 검증 및 품질 체크

```python
from src.content.validator import validate_content, get_quality_report

# 검증
is_valid, messages = validate_content(content)
if not is_valid:
    print("검증 실패:", messages)

# 품질 리포트
report = get_quality_report(content)
print(f"총 글자 수: {report['total_chars']}")
print(f"완성도: {report['completion_rate']:.1f}%")
print(f"개선 제안: {report['suggestions']}")
```

## 📊 데이터 변환 흐름

```
RhythmSignal (내부)              DailyContent (사용자)
├─ energy_level: 4      →      ├─ summary: "활기찬 에너지..."
├─ main_theme: "안정과 정리" →  ├─ keywords: ["안정", "정리"]
├─ saju_data: {...}     →      ├─ rhythm_description: "오늘의 리듬은..."
├─ favorable_times: ... →      ├─ time_direction: {...}
└─ opportunities: ...   →      └─ focus_caution: {...}
```

## 🚫 내부 용어 vs 사용자 용어

### 절대 금지 (사용자 노출 불가)

❌ **전문 용어**:
- 사주명리, 기문둔갑
- 천간, 지지, 오행, 십성
- 대운, 세운, 월운, 일운
- 천을귀인, 역마, 공망, 도화
- 甲乙丙丁... (한자 간지)

### 허용 (사용자 노출 가능)

✅ **일반 언어**:
- 흐름, 리듬, 에너지
- 집중 시간, 주의 시간
- 좋은 방향, 피할 방향
- 집중력, 관계운, 건강 리듬
- 의사결정, 휴식, 정리, 창작

### 변환 예시

```python
# 내부 표현 (RhythmSignal)
main_theme = "안정과 정리"
energy_level = 3
favorable_times = ["오전 9-11시(巳時)"]

# 사용자 표현 (DailyContent)
summary = "오늘은 안정적인 에너지가 있는 날입니다. 정리와 마무리에 집중하면 좋습니다."
keywords = ["안정", "정리", "마무리"]
time_direction.good_time = "오전 9-11시"
```

## 📏 길이 요구사항

### 최소 요구사항
- **좌측 페이지 전체**: 최소 400자, 목표 600-1200자
- **리듬 해설**: 최소 100자
- **의미 전환**: 최소 50자
- **키워드**: 2-5개

### 검증 방법

```python
# 1. 총 길이 계산
total_chars = content.get_total_text_length()

# 2. 요구사항 검증
is_valid, total, message = content.validate_length_requirements()
print(message)  # "길이 요구사항 충족: 850자"

# 3. 블록별 길이 분포
from src.content.validator import ContentValidator
validator = ContentValidator()
dist = validator.validate_length_distribution(content)
print(dist)
# {
#   "summary": 65,
#   "rhythm_description": 180,
#   "total": 850
# }
```

## 🧱 10개 콘텐츠 블록

### 1. 요약 (summary)
- 30-200자
- 오늘의 한 줄 요약

### 2. 키워드 (keywords)
- 2-5개
- 오늘의 핵심 키워드

### 3. 리듬 해설 (rhythm_description)
- 100-500자
- **설명형 문단 필수** (카드 요약 금지)

### 4. 집중/주의 포인트 (focus_caution)
- focus: 집중할 영역
- caution: 주의할 영역

### 5. 행동 가이드 (action_guide)
- do: 추천 행동
- avoid: 피할 행동

### 6. 시간/방향 (time_direction)
- good_time: 좋은 시간대
- avoid_time: 피할 시간대
- good_direction: 좋은 방향
- avoid_direction: 피할 방향

### 7. 상태 트리거 (state_trigger)
- gesture: 제스처/동작
- phrase: 문구/주문
- how_to: 사용 방법

### 8. 의미 전환 (meaning_shift)
- 50-300자
- 불안/충동을 긍정적으로 재해석

### 9. 리듬 질문 (rhythm_question)
- 20-150자
- 자기 성찰을 위한 질문

### 10. 길이 요구사항 (length_requirements)
- 메타데이터 (검증용)

## 🧪 테스트

```bash
# 전체 테스트 실행
pytest tests/test_content.py -v

# 통합 테스트 (Rhythm → Content)
pytest tests/test_content.py::TestIntegration -v

# 커버리지 확인
pytest tests/test_content.py --cov=src/content

# 특정 테스트만 실행
pytest tests/test_content.py::TestContentAssembler::test_assemble_daily_content -v
```

## 🔄 다음 단계: Phase 4

**Role Translation Layer** - 역할별 콘텐츠 변형

동일한 DailyContent를 역할에 따라 다르게 표현:
- **학생**: 학습/집중/페이스 관리 강조
- **직장인**: 업무/관계/결정/보고 강조
- **프리랜서**: 결정/계약/창작/체력 강조

Role Translation Layer에서:
- DailyContent의 핵심 의미는 유지
- 표현, 예시, 질문만 역할에 맞게 변형
- 의미 불변성 검증 테스트 필수

## 📚 참고 자료

- [DAILY_CONTENT_SCHEMA.json](../../../docs/content/DAILY_CONTENT_SCHEMA.json) - 콘텐츠 스키마
- [TERMINOLOGY_POLICY.md](../../../docs/legal/TERMINOLOGY_POLICY.md) - 용어 정책
- [Rhythm Analysis Engine](../rhythm/README.md) - 이전 단계
- [Phase 3 작업 계획](../../../docs/tasks/WORKPLAN.md#phase-3)

---

**Content Assembly Engine v1.0.0**
