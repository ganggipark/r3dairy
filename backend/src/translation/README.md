## Role Translation Layer

DailyContent를 사용자 역할에 맞게 표현 변환

## 📋 개요

Role Translation Layer는 동일한 DailyContent를 사용자의 역할(학생, 직장인, 프리랜서)에 맞게 표현을 변환하는 시스템입니다.

### 핵심 원칙

1. **의미 불변성(Semantic Preservation)**: 리듬의 본질적 의미는 유지
2. **표현 변형(Expression Transformation)**: 역할에 맞는 언어로 변환
3. **컨텍스트 적응(Context Adaptation)**: 역할별 관심사와 상황 반영

## 📁 파일 구조

```
translation/
├── __init__.py         # 모듈 초기화
├── models.py           # Role, RoleTemplate, TranslationContext
├── translator.py       # RoleTranslator (변환 엔진)
├── templates/          # 역할별 템플릿
│   ├── student.json
│   ├── office_worker.json
│   └── freelancer.json
└── README.md           # 이 파일
```

## 🔧 사용 방법

### 1. 기본 사용법

```python
from datetime import date, time
from src.rhythm.models import BirthInfo, Gender
from src.rhythm.signals import create_daily_rhythm
from src.content.assembly import create_daily_content
from src.translation import translate_content, Role

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

# 3. 중립 콘텐츠 생성 (사용자 노출)
neutral_content = create_daily_content(signal)

# 4. 역할별 변환
student_content = translate_content(neutral_content, Role.STUDENT)
worker_content = translate_content(neutral_content, Role.OFFICE_WORKER)
freelancer_content = translate_content(neutral_content, Role.FREELANCER)
```

### 2. RoleTranslator 직접 사용

```python
from src.translation.translator import RoleTranslator
from src.translation.models import Role

translator = RoleTranslator()

# 역할별 변환
student_content = translator.translate(neutral_content, Role.STUDENT)

# 의미 불변성 검증
is_valid, issues = translator.validate_semantic_preservation(
    neutral_content, student_content
)

if not is_valid:
    print("의미 불변성 검증 실패:", issues)
```

## 🎭 역할별 표현 변환

### 학생 (Student)

**특징**: 학습, 집중, 페이스 관리 강조

| 중립 표현 | 학생 표현 |
|---------|---------|
| 작업 완료 | 과제 마무리 |
| 중요한 결정 | 진로 결정 |
| 집중 시간 | 집중 학습 시간 |
| 관계 조율 | 친구 관계 |

**질문 예시**:
- "오늘 집중해서 공부할 과목은 무엇인가요?"
- "이번 주 목표를 달성하려면 어떤 준비가 필요한가요?"

### 직장인 (Office Worker)

**특징**: 업무, 관계, 결정, 보고 강조

| 중립 표현 | 직장인 표현 |
|---------|-----------|
| 작업 완료 | 업무 마무리 |
| 중요한 결정 | 업무 의사결정 |
| 집중 시간 | 집중 업무 시간 |
| 관계 조율 | 동료 관계 |

**질문 예시**:
- "오늘 가장 중요하게 처리할 업무는 무엇인가요?"
- "동료와의 협업에서 어떤 점을 개선하고 싶나요?"

### 프리랜서 (Freelancer)

**특징**: 결정, 계약, 창작, 체력 강조

| 중립 표현 | 프리랜서 표현 |
|---------|------------|
| 작업 완료 | 프로젝트 마감 |
| 중요한 결정 | 사업 의사결정 |
| 집중 시간 | 집중 작업 시간 |
| 관계 조율 | 클라이언트 관계 |

**질문 예시**:
- "오늘 마감해야 할 프로젝트는 무엇인가요?"
- "수익과 창작 사이의 균형을 어떻게 맞출까요?"

## 🔄 변환 프로세스

```
1. RoleTemplate 로드
   └─ templates/{role}.json 파일 읽기

2. 표현 매핑 적용
   └─ expressions 사전으로 텍스트 치환

3. 역할별 키워드 반영
   └─ action_keywords, avoid_keywords 활용

4. 질문 변환
   └─ question_templates 활용

5. 의미 불변성 검증
   └─ 날짜, 개수, 길이(±20%) 확인
```

## 📊 템플릿 구조

### student.json 예시

```json
{
  "role": "student",
  "expressions": {
    "작업 완료": "과제 마무리",
    "집중 시간": "집중 학습 시간"
  },
  "action_keywords": [
    "학습", "복습", "정리", "집중"
  ],
  "avoid_keywords": [
    "무리한 일정", "과도한 비교"
  ],
  "question_templates": [
    "오늘 집중해서 공부할 과목은 무엇인가요?"
  ],
  "example_sentences": {
    "focus": [
      "오늘은 수학 문제 풀이에 집중하기 좋은 날입니다"
    ]
  }
}
```

## 🔍 의미 불변성 검증

### 검증 항목

1. **날짜 동일성**: 원본과 번역본의 날짜가 같은지
2. **키워드 개수**: 키워드 개수가 유지되는지
3. **블록 개수**: Focus/Caution, Do/Avoid 개수 유지
4. **길이 보존**: 전체 텍스트 길이가 ±20% 이내인지
5. **필수 블록**: rhythm_description, meaning_shift, rhythm_question 존재

### 검증 예시

```python
translator = RoleTranslator()

original = neutral_content
translated = translator.translate(neutral_content, Role.STUDENT)

is_valid, issues = translator.validate_semantic_preservation(
    original, translated
)

if not is_valid:
    for issue in issues:
        print(f"❌ {issue}")
else:
    print("✅ 의미 불변성 검증 통과")
```

## 🧪 테스트

```bash
# 전체 테스트 실행
pytest tests/test_translation.py -v

# 의미 불변성 테스트만 실행
pytest tests/test_translation.py::TestSemanticPreservation -v

# 통합 테스트 (Rhythm → Content → Translation)
pytest tests/test_translation.py::TestIntegration -v

# 커버리지 확인
pytest tests/test_translation.py --cov=src/translation
```

## 🎯 설계 목표

### 달성된 목표

✅ **의미 불변성**: 리듬의 본질적 의미는 모든 역할에서 동일
✅ **표현 다양성**: 역할별로 다른 언어 사용 (학생 vs 직장인)
✅ **자동 변환**: 템플릿 기반 자동 변환
✅ **검증 시스템**: 의미 불변성 자동 검증
✅ **확장성**: 새 역할 추가 시 JSON 파일만 추가

### 향후 개선 방향

- [ ] AI 기반 동적 표현 생성 (GPT-4 활용)
- [ ] 사용자 피드백 기반 템플릿 최적화
- [ ] 역할별 예시 문장 라이브러리 확장
- [ ] 다국어 지원 (영어, 일본어 등)

## 📚 참고 자료

- [Content Assembly Engine](../content/README.md) - 이전 단계
- [DAILY_CONTENT_SCHEMA.json](../../../docs/content/DAILY_CONTENT_SCHEMA.json) - 콘텐츠 스키마
- [WORKPLAN.md](../../../docs/tasks/WORKPLAN.md) - Phase 4 작업 계획

## 🔄 다음 단계: Phase 5

**Backend API 구축** - RESTful API 엔드포인트 구현

Phase 5에서는:
- Supabase Auth 통합
- 프로필 CRUD API
- 일간/월간/연간 콘텐츠 조회 API (역할별 변환 포함)
- 사용자 기록 저장 API

Role Translation Layer가 완성되어, 이제 API에서 사용자 역할에 따라 다른 콘텐츠를 제공할 수 있습니다.

---

**Role Translation Layer v1.0.0**
