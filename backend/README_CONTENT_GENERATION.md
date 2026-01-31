# 일간 콘텐츠 생성 파이프라인 완전 가이드

> 사주, 기문둔갑, 색은식 세 가지 계산 시스템을 통합한 개인화 콘텐츠 자동 생성

## 목차

1. [시스템 개요](#시스템-개요)
2. [아키텍처](#아키텍처)
3. [세 가지 계산 시스템](#세-가지-계산-시스템)
4. [콘텐츠 생성 흐름](#콘텐츠-생성-흐름)
5. [CLI 명령어](#cli-명령어)
6. [API 엔드포인트](#api-엔드포인트)
7. [출력 형식](#출력-형식)
8. [문제 해결](#문제-해결)

---

## 시스템 개요

### 핵심 원칙

R³ 다이어리 시스템은 **세 가지 한동양 계산 시스템**을 통합하여 완전히 개인화된 콘텐츠를 생성합니다.

```
사용자 프로필 (생년월일, 시간, 역할, 선호도)
    ↓
[사주 계산] + [기문둔갑] + [색은식]
    ↓
내부 리듬 신호 (전문 용어, 사용자 노출 금지)
    ↓
콘텐츠 어셈블 (JSON 구조화)
    ↓
Markdown 변환 (사용자 친화적 언어)
    ↓
역할 번역 (학생/직장인/프리랜서별 표현)
    ↓
최종 출력 (Markdown + JSON)
```

### 데이터 격리 원칙

**절대 지켜야 할 규칙:**

| 레이어 | 포함 내용 | 사용자 노출 |
|--------|---------|-----------|
| **계산 모듈** (사주/기문/색은식) | 천간, 지지, 십성, 오행 등 전문 용어 | ❌ 금지 |
| **내부 데이터** (Rhythm Signal) | 계산 결과 구조화 데이터 | ❌ 금지 |
| **JSON 스키마** (DAILY_CONTENT_SCHEMA) | 구조화된 콘텐츠 블록 | ⚠️ 제한 |
| **Markdown 출력** | 일반 사용자 언어로 변환 | ✅ 노출 OK |
| **API 응답** | JSON + Markdown 모두 제공 | ✅ 노출 OK |

---

## 아키텍처

### 디렉토리 구조

```
backend/
├── src/
│   ├── rhythm/                      # Rhythm Analysis Engine
│   │   ├── saju.py                  # 사주 계산 (八字)
│   │   ├── qimen.py                 # 기문둔갑 (奇門遁甲)
│   │   ├── saekeunshik.py           # 색은식 (五運六氣)
│   │   ├── models.py                # 계산 데이터 모델
│   │   └── __init__.py
│   │
│   ├── content/                     # Content Assembly Engine
│   │   ├── assembly.py              # JSON 콘텐츠 조합
│   │   ├── validator.py             # 스키마 검증
│   │   ├── models.py                # 콘텐츠 데이터 모델
│   │   └── __init__.py
│   │
│   ├── translation/                 # Role Translation Layer
│   │   ├── translator.py            # 역할별 번역
│   │   ├── models.py                # 번역 데이터 모델
│   │   └── __init__.py
│   │
│   ├── api/
│   │   ├── daily.py                 # Daily 엔드포인트
│   │   └── README.md                # API 문서
│   │
│   └── main.py                      # FastAPI 애플리케이션
│
├── generate_daily_content.py        # 일회용 생성 스크립트
├── generate_daily_simple.py         # 간단한 생성 도구
├── README_CONTENT_GENERATION.md     # 이 파일
└── requirements.txt
```

### 모듈 역할

| 모듈 | 역할 | 입력 | 출력 |
|------|------|------|------|
| **rhythm/saju.py** | 사주 계산 | BirthInfo (생년월일, 시간) | SajuData (내부 표현) |
| **rhythm/qimen.py** | 기문둔갑 분석 | SajuData + TargetDate | QimenData (내부 표현) |
| **rhythm/saekeunshik.py** | 색은식 계산 | TargetDate + Sicheon | SaekeunshikData (내부 표현) |
| **content/assembly.py** | 콘텐츠 조합 | SajuData + QimenData + 기타 | JSON (스키마 준수) |
| **translation/translator.py** | 역할 번역 | JSON + UserRole | JSON (역할별 변형) |
| **api/daily.py** | API 엔드포인트 | HTTP 요청 | JSON + Markdown |

---

## 세 가지 계산 시스템

### 1. 사주 계산 (八字, Saju)

**목적**: 출생 시간 기반 운명의 틀 분석

**주요 요소**:
- **천간 (天干)**: 10개 순환 (甲乙丙丁戊己庚辛壬癸)
- **지지 (地支)**: 12개 순환 (子丑寅卯辰巳午未申酉戌亥)
- **오행 (五行)**: 목화토금수 (木火土金水)
- **십성 (十神)**: 비겹, 정관, 편관 등 10가지 관계
- **대운 (大運)**: 10년 단위 주기
- **세운 (歲運)**: 연도별 변화

**파일**: `backend/src/rhythm/saju.py`

```python
from src.rhythm.saju import calculate_saju

# 예: 1971년 11월 17일 04:00 양력 남자
saju_data = calculate_saju(
    year=1971, month=11, day=17,
    hour=4, minute=0,
    gender='M', calendar_type='gregorian'
)

# 출력 (내부 표현, 사용자 노출 금지):
# {
#   'heavenly_stems': ['甲', '甲', '己', '甲'],
#   'earthly_branches': ['子', '子', '酉', '寅'],
#   'five_elements': ['木', '木', '金', '木'],
#   'ten_stems': [...],
#   'major_luck': {...},
#   'annual_luck': {...}
# }
```

### 2. 기문둔갑 (奇門遁甲, Qimen)

**목적**: 특정 날짜/시간의 전술적 흐름 분석

**주요 요소**:
- **9궁 (九宮)**: 3x3 그리드 (坎離震兌乾坤艮巽中)
- **8문 (八門)**: 행동 방식 (開休生傷杜景死)
- **9성 (九星)**: 에너지 (天輔天芮天衝天輔天禽天心天柱天任天英)
- **5행 (五行)**: 목화토금수
- **12지지 (十二支)**: 방향 및 시간

**파일**: `backend/src/rhythm/qimen.py`

```python
from src.rhythm.qimen import analyze_qimen
from datetime import date, time

# 예: 2026-01-31 오전 9시
qimen_data = analyze_qimen(
    target_date=date(2026, 1, 31),
    target_time=time(9, 0),
    saju_data=saju_data  # 사주 데이터 참조
)

# 출력 (내부 표현, 사용자 노출 금지):
# {
#   'palace_grid': [[...], [...], [...]],
#   'gate': '開',
#   'star': '天心',
#   'element': '木',
#   'direction': '東',
#   'analysis': {...}
# }
```

### 3. 색은식 (五運六氣, Saekeunshik)

**목적**: 계절/절기별 자연 에너지 흐름 분석

**주요 요소**:
- **오운 (五運)**: 5가지 에너지 흐름 (木火土金水)
  - 천간 기반 계산
  - 년/월/일 에너지 레벨

- **육기 (六氣)**: 6가지 기후 에너지 (風熱濕火燥寒)
  - 지지 기반 계산
  - 사천/재천 (상반기/하반기)
  - 주기 (1년 6단계)

**파일**: `backend/src/rhythm/saekeunshik.py`

```python
from src.rhythm.saekeunshik import calculate_saekeunshik
from datetime import date

# 예: 2026-01-31
saekeunshik_data = calculate_saekeunshik(
    target_date=date(2026, 1, 31)
)

# 출력 (내부 표현, 사용자 노출 금지):
# {
#   'five_movements': {
#     'year_movement': '土運',
#     'month_movement': '木運',
#     'day_movement': '水運'
#   },
#   'six_qi': {
#     'sicheon': '少陽相火',     # 상반기
#     'jaecheon': '厥陰風木',    # 하반기
#     'main_qi': '厥陰風木'      # 현재
#   },
#   'seasonal_phase': 'spring'
# }
```

---

## 콘텐츠 생성 흐름

### 단계별 프로세스

#### Step 1: 프로필 로드

```python
# 사용자 정보 조회
profile = {
    'user_id': 'user123',
    'birth_year': 1971,
    'birth_month': 11,
    'birth_day': 17,
    'birth_hour': 4,
    'birth_minute': 0,
    'birth_place': 'Seoul',
    'gender': 'M',
    'role': 'employee',  # 직장인
    'calendar_type': 'gregorian'
}
```

#### Step 2: 세 가지 계산 수행

```python
from src.rhythm.saju import calculate_saju
from src.rhythm.qimen import analyze_qimen
from src.rhythm.saekeunshik import calculate_saekeunshik
from datetime import date

target_date = date(2026, 1, 31)

# 1. 사주 (생일 기반, 한 번만 계산)
saju = calculate_saju(
    year=profile['birth_year'],
    month=profile['birth_month'],
    day=profile['birth_day'],
    hour=profile['birth_hour'],
    minute=profile['birth_minute'],
    gender=profile['gender'],
    calendar_type=profile['calendar_type']
)

# 2. 기문 (매일 계산)
qimen = analyze_qimen(
    target_date=target_date,
    target_time=time(0, 0),  # 자정 기준
    saju_data=saju
)

# 3. 색은식 (매일 계산)
saekeunshik = calculate_saekeunshik(target_date=target_date)
```

#### Step 3: 콘텐츠 어셈블 (JSON)

```python
from src.content.assembly import assemble_daily_content

content_json = assemble_daily_content(
    date=target_date,
    saju_data=saju,
    qimen_data=qimen,
    saekeunshik_data=saekeunshik,
    profile=profile
)

# 출력: DAILY_CONTENT_SCHEMA.json 준수하는 JSON
# {
#   'date': '2026-01-31',
#   'summary': '오늘은 집중력이 강한...',
#   'keywords': ['집중', '결정', '관계'],
#   'rhythm_description': '...',
#   'focus_caution': {...},
#   ... (18개 필드)
# }
```

#### Step 4: Markdown 변환

```python
from src.api.daily import convert_json_to_markdown

markdown_text = convert_json_to_markdown(
    content_json=content_json,
    role=profile['role']  # 직장인 용어로 변환
)

# 출력:
# # 2026년 1월 31일 | 오늘의 흐름
#
# ## 오늘의 요약
# 오늘은 집중력이 강한 날입니다...
#
# ## 핵심 키워드
# - 집중  - 결정  - 관계
#
# ... (마크다운 형식)
```

#### Step 5: 파일 저장 및 응답

```python
# 파일 저장
markdown_file = f"backend/daily/{target_date}.md"
with open(markdown_file, 'w', encoding='utf-8') as f:
    f.write(markdown_text)

# API 응답 (JSON + Markdown 모두 제공)
response = {
    'date': '2026-01-31',
    'markdown': markdown_text,
    'json': content_json,
    'role': 'employee',
    'status': 'generated'
}
```

---

## CLI 명령어

### 1. FastAPI 서버 실행

```bash
# 개발 서버 시작 (포트 8000)
cd backend
python -m uvicorn src.main:app --reload

# 또는 간단히
uvicorn src.main:app --reload
```

**확인**: http://localhost:8000/docs (API 문서)

### 2. 일간 콘텐츠 생성 (일회용)

```bash
cd backend

# 특정 날짜 생성
python generate_daily_content.py 2026-01-31

# 또는 간단한 버전
python generate_daily_simple.py 2026-01-31

# 출력:
# ✅ 생성 완료: 2026-01-31.md
# 📁 저장 위치: backend/daily/2026-01-31.md
```

### 3. 콘텐츠 검증

```bash
# JSON 스키마 검증
python -c "
from src.content.validator import validate_daily_content
import json

with open('daily/2026-01-31.json') as f:
    content = json.load(f)

result = validate_daily_content(content)
print(result['valid'])  # True/False
"

# Markdown 길이 확인
python -c "
with open('daily/2026-01-31.md') as f:
    content = f.read()

# 좌측 페이지 글자 수 확인
print(f'총 글자 수: {len(content)}')
"
```

### 4. 계산 결과 확인

```bash
# 사주 계산 테스트
python -c "
from src.rhythm.saju import calculate_saju
result = calculate_saju(1971, 11, 17, 4, 0, 'M', 'gregorian')
import json
print(json.dumps(result, indent=2, ensure_ascii=False))
"

# 기문둔갑 분석
python -c "
from src.rhythm.qimen import analyze_qimen
from src.rhythm.saju import calculate_saju
from datetime import date

saju = calculate_saju(1971, 11, 17, 4, 0, 'M', 'gregorian')
result = analyze_qimen(date(2026, 1, 31), saju)
import json
print(json.dumps(result, indent=2, ensure_ascii=False))
"

# 색은식 계산
python -c "
from src.rhythm.saekeunshik import calculate_saekeunshik
from datetime import date

result = calculate_saekeunshik(date(2026, 1, 31))
import json
print(json.dumps(result, indent=2, ensure_ascii=False))
"
```

---

## API 엔드포인트

### 1. Markdown 조회 (새로운 엔드포인트)

```bash
GET /api/daily/{date}/markdown
Authorization: Bearer {access_token}

# 예:
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/daily/2026-01-31/markdown

# 응답 (text/markdown):
# # 2026년 1월 31일 | 오늘의 흐름
#
# ## 오늘의 요약
# ...
```

**응답 헤더**: `Content-Type: text/markdown`

**상태 코드**:
- `200 OK` - 성공
- `404 Not Found` - 콘텐츠 없음
- `401 Unauthorized` - 인증 실패

### 2. JSON 조회 (기존 엔드포인트)

```bash
GET /api/daily/{date}
Authorization: Bearer {access_token}

# 예:
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/daily/2026-01-31

# 응답 (application/json):
# {
#   "date": "2026-01-31",
#   "summary": "...",
#   "keywords": [...],
#   ... (20개 필드)
# }
```

### 3. 역할별 콘텐츠 조회

```bash
GET /api/daily/{date}?role=employee
Authorization: Bearer {access_token}

# 지원하는 역할:
# - student (학생)
# - employee (직장인)
# - freelancer (프리랜서)
# - entrepreneur (자영업자)

# 각 역할별로 문구가 자동 변환됨
```

---

## 출력 형식

### Markdown 형식 (사용자 노출)

```markdown
# 2026년 1월 31일 | 오늘의 흐름

## 오늘의 요약
오늘은 집중력이 강한 날입니다. 중요한 결정이나 어려운 업무를 진행하기에 좋은 에너지입니다.

## 핵심 키워드
- 집중
- 결정
- 관계운

## 리듬 해설
[설명형 문단 200자 이상]
오늘의 흐름은...

## 집중할 포인트
- 중요한 회의나 협상에 집중하기
- 결정을 미루지 말고 행동하기

## 주의해야 할 점
- 충동적인 표현 자제하기
- 관계에서 섬세함 필요

## 오늘의 행동 가이드

### 해야 할 것 (DO)
- 새로운 프로젝트 시작
- 상급자와의 소통
- 업무 성과 정리

### 피해야 할 것 (AVOID)
- 중요한 결정 미루기
- 무리한 약속
- 과도한 야근

## 시간대별 가이드
- **좋은 시간**: 09:00 - 11:00, 14:00 - 16:00
- **피해야 할 시간**: 18:00 - 20:00
- **좋은 방향**: 동쪽, 북동쪽
- **피해야 할 방향**: 서쪽, 남서쪽

## 건강과 운동
**추천 활동**: 야외 산책, 밸런스 운동
**건강 팁**: 충분한 수분 섭취, 규칙적인 스트레칭

## 식사와 영양
**음식 성향**: 가벼운, 상큼한
**추천 식재료**: 채소, 흰살 생선, 견과류
**피해야 할 음식**: 자극적인 음식, 과도한 자극

... (더 많은 섹션)
```

### JSON 형식 (API 응답, 내부 사용)

```json
{
  "date": "2026-01-31",
  "summary": "오늘은 집중력이 강한 날입니다...",
  "keywords": ["집중", "결정", "관계운"],
  "rhythm_description": "설명형 문단 200자 이상...",
  "focus_caution": {
    "focus": ["중요한 회의나 협상에 집중하기", "결정을 미루지 말고 행동하기"],
    "caution": ["충동적인 표현 자제하기", "관계에서 섬세함 필요"]
  },
  "action_guide": {
    "do": ["새로운 프로젝트 시작", "상급자와의 소통", "업무 성과 정리"],
    "avoid": ["중요한 결정 미루기", "무리한 약속", "과도한 야근"]
  },
  "time_direction": {
    "good_time": "09:00 - 11:00, 14:00 - 16:00",
    "avoid_time": "18:00 - 20:00",
    "good_direction": "동쪽, 북동쪽",
    "avoid_direction": "서쪽, 남서쪽",
    "notes": "오전 시간대에 중요한 업무 처리 추천"
  },
  ... (더 많은 필드, DAILY_CONTENT_SCHEMA.json 참조)
}
```

---

## 문제 해결

### 문제 1: Markdown 파일이 생성되지 않음

**증상**: API 호출 시 404 Not Found

**원인**:
- 파일 저장 경로 오류
- 권한 문제
- 콘텐츠 생성 실패

**해결**:

```bash
# 1. 디렉토리 확인
ls -la backend/daily/

# 2. 권한 확인
chmod 755 backend/daily/

# 3. 수동 생성 시도
python generate_daily_simple.py 2026-01-31

# 4. 로그 확인
tail -50 backend/logs/app.log
```

### 문제 2: 콘텐츠 글자 수 부족

**증상**: "좌측 페이지는 최소 400자 이상이어야 합니다" 경고

**원인**:
- 리듬 해설 또는 의미 전환 문단 부족
- AI 생성 텍스트 길이 미달

**해결**:

```python
# assembly.py의 _ensure_minimum_content_length() 함수 확인
from src.content.assembly import _ensure_minimum_content_length

# 각 필드의 최소 길이 요구사항:
# - rhythm_description: 200자 이상
# - meaning_shift: 80자 이상
# - 좌측 페이지 전체: 400~600자 (목표: 700~1200자)

# 부족한 경우, 자동으로 설명 확장
content = _ensure_minimum_content_length(content, daily_rhythm)
```

### 문제 3: 역할 번역이 제대로 작동하지 않음

**증상**: 모든 역할에서 동일한 표현 사용

**원인**:
- 번역 템플릿 로드 실패
- 역할 지정 오류

**해결**:

```bash
# 1. 번역 템플릿 확인
ls -la backend/src/translation/templates/

# 2. 지원되는 역할 확인
python -c "
from src.translation.translator import Role
for role in Role:
    print(f'- {role.value}')
"

# 3. 강제 번역 테스트
python -c "
from src.translation.translator import translate_daily_content, Role
import json

with open('daily/2026-01-31.json') as f:
    content = json.load(f)

# 각 역할별 번역 시도
for role in ['student', 'employee', 'freelancer']:
    translated = translate_daily_content(content, Role(role))
    print(f'{role}: OK')
"
```

### 문제 4: 계산 값이 비정상적임

**증상**: 사주 천간/지지가 올바르지 않음

**원인**:
- 음력/양력 변환 오류
- 시간대 설정 오류 (특히 자정 전후)
- 입춘 기준 연도 계산 오류

**해결**:

```bash
# 1. 사주 계산 검증 (기준: 1971-11-17 04:00 남자)
python -c "
from src.rhythm.saju import calculate_saju
result = calculate_saju(1971, 11, 17, 4, 0, 'M', 'gregorian')

# 기대값:
# heavenly_stems: ['甲', '甲', '己', '甲']
# earthly_branches: ['子', '子', '酉', '寅']

print(result['heavenly_stems'])
print(result['earthly_branches'])
"

# 2. 외부 사주 계산기와 비교
# https://www.saju.or.kr (한국 사주 정보)

# 3. 계산 함수의 주석 확인
# backend/src/rhythm/saju.py의 주석 참조
```

### 문제 5: API 응답이 너무 느림

**증상**: `/api/daily/{date}` 호출 시 5초 이상 대기

**원인**:
- 세 가지 계산 (사주, 기문, 색은식) 동시 수행
- 콘텐츠 어셈블리 시간
- 데이터베이스 쿼리

**해결**:

```python
# 1. 캐싱 활성화 (API 레이어)
# backend/src/api/daily.py의 _markdown_cache 사용

# 2. 백그라운드 작업 (Celery 도입)
# 미리 계산 후 저장

# 3. 계산 최적화
# 사주는 캐시 가능 (생일이 변경되지 않음)
# 기문, 색은식은 일일 계산 필요

# 구현 예:
from functools import lru_cache

@lru_cache(maxsize=10000)
def calculate_saju_cached(year, month, day, hour, minute, gender):
    """캐시된 사주 계산"""
    from src.rhythm.saju import calculate_saju
    return calculate_saju(year, month, day, hour, minute, gender, 'gregorian')
```

---

## 다음 단계

### 단기 (1-2주)
- [ ] 모든 엔드포인트에 Markdown 지원 추가
- [ ] 캐싱 메커니즘 구현
- [ ] 엣지 케이스 테스트

### 중기 (2-4주)
- [ ] 월간/연간 콘텐츠 생성 파이프라인
- [ ] 사용자 기록(로그) 연동
- [ ] PDF 렌더링 최적화

### 장기 (1-3개월)
- [ ] 365일 전량 미리 생성 (배치 작업)
- [ ] 개인 생성 통계 및 리포트
- [ ] 템플릿 기반 다국어 지원

---

## 참고 문서

- `docs/content/DAILY_CONTENT_SCHEMA.json` - 콘텐츠 스키마 정의
- `docs/content/MARKDOWN_FORMAT_SPEC.md` - Markdown 형식 스펙
- `docs/architecture/ARCHITECTURE.md` - 전체 아키텍처
- `docs/legal/TERMINOLOGY_POLICY.md` - 용어 정책
- `backend/src/api/README.md` - API 완전 문서

---

**마지막 업데이트**: 2026-01-31
**작성자**: R³ Development Team
