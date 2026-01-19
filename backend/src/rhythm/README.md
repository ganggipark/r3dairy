# Rhythm Analysis Engine

출생 정보 기반 리듬 분석 엔진 - R³ 다이어리 시스템의 핵심 모듈

## 📋 개요

이 모듈은 사용자의 출생 정보를 기반으로 일간/월간/연간 리듬을 분석하고 신호를 생성합니다.

**⚠️ 중요**: 이 모듈의 출력은 **내부 전문 용어**를 사용합니다. 사용자에게 직접 노출하지 마세요! Content Assembly Engine에서 일반 언어로 변환됩니다.

## 📁 파일 구조

```
rhythm/
├── __init__.py       # 모듈 초기화
├── models.py         # 데이터 모델 (BirthInfo, RhythmSignal 등)
├── saju.py           # 사주명리 계산 (기존 로직 통합 지점)
├── signals.py        # 리듬 신호 생성 메인 로직
└── README.md         # 이 파일
```

## 🔧 사용 방법

### 1. 기본 사용법

```python
from datetime import date, time
from src.rhythm.models import BirthInfo, Gender
from src.rhythm.signals import create_daily_rhythm

# 출생 정보 생성
birth_info = BirthInfo(
    name="홍길동",
    birth_date=date(1990, 1, 15),
    birth_time=time(14, 30),
    gender=Gender.MALE,
    birth_place="서울"
)

# 일간 리듬 신호 생성
signal = create_daily_rhythm(birth_info, date.today())

print(f"에너지 레벨: {signal.energy_level}/5")
print(f"주요 테마: {signal.main_theme}")
print(f"유리한 시간: {signal.favorable_times}")
```

### 2. 월간/연간 리듬

```python
from src.rhythm.signals import create_monthly_rhythm, create_yearly_rhythm

# 월간 리듬
monthly_signal = create_monthly_rhythm(birth_info, 2026, 1)
print(f"월간 테마: {monthly_signal.main_theme}")

# 연간 리듬
yearly_signal = create_yearly_rhythm(birth_info, 2026)
print(f"연간 키워드: {yearly_signal.keywords}")
```

## 🔌 기존 사주명리 로직 통합

### 방법 1: 라이브러리/패키지 통합

기존에 사주명리 계산 라이브러리가 있다면:

```python
# saju.py 파일에서

from your_saju_library import SajuCalculator  # 기존 라이브러리 import

def calculate_saju(birth_info: BirthInfo, target_date: date) -> Dict[str, Any]:
    calculator = SajuCalculator()

    result = calculator.calculate(
        birth_date=birth_info.birth_date,
        birth_time=birth_info.birth_time,
        gender=birth_info.gender.value
    )

    # 결과를 Dict 형식으로 변환
    return {
        "사주": result.pillar_data,
        "오행": result.element_data,
        "십성": result.ten_gods_data,
        "특수신살": result.special_stars
    }
```

**requirements.txt에 추가:**
```
your-saju-library==x.x.x
```

### 방법 2: 직접 작성한 코드 통합

직접 작성한 사주명리 코드가 있다면:

1. 코드를 `saju.py`에 복사
2. `calculate_saju()` 함수에서 해당 코드 호출
3. 출력 형식을 Dict로 통일

```python
# saju.py 파일에서

# 기존 코드 복사
def my_existing_saju_calculation(birth_date, birth_time):
    # ... 기존 계산 로직 ...
    return calculation_result

def calculate_saju(birth_info: BirthInfo, target_date: date) -> Dict[str, Any]:
    # 기존 함수 호출
    result = my_existing_saju_calculation(
        birth_info.birth_date,
        birth_info.birth_time
    )

    # Dict 형식으로 변환
    return {
        "사주": result,
        # ... 기타 필드
    }
```

### 방법 3: 외부 API 통합

외부 사주명리 API를 사용하는 경우:

```python
# saju.py 파일에서

import requests
import os

def calculate_saju(birth_info: BirthInfo, target_date: date) -> Dict[str, Any]:
    api_url = os.getenv("SAJU_API_URL")
    api_key = os.getenv("SAJU_API_KEY")

    response = requests.post(api_url, json={
        "birth_date": birth_info.birth_date.isoformat(),
        "birth_time": birth_info.birth_time.isoformat(),
        "gender": birth_info.gender.value
    }, headers={
        "Authorization": f"Bearer {api_key}"
    })

    return response.json()
```

**.env에 추가:**
```
SAJU_API_URL=https://your-api.com/calculate
SAJU_API_KEY=your_api_key_here
```

## 📊 데이터 모델

### BirthInfo (입력)

사용자 출생 정보:
- `name`: 이름
- `birth_date`: 생년월일
- `birth_time`: 출생 시간
- `gender`: 성별 (male/female/other)
- `birth_place`: 출생지
- `birth_place_lat/lng`: 출생지 좌표 (옵션)

### RhythmSignal (출력)

일간 리듬 신호:
- `date`: 분석 날짜
- `saju_data`: 사주명리 계산 결과 (내부 용어)
- `energy_level`: 에너지 레벨 (1-5)
- `focus_capacity`: 집중력 (1-5)
- `favorable_times`: 유리한 시간대
- `main_theme`: 주요 테마
- `opportunities`: 기회 요소
- `challenges`: 도전 요소

## 🧪 테스트

```bash
# 전체 테스트 실행
pytest tests/test_rhythm.py -v

# 커버리지 확인
pytest tests/test_rhythm.py --cov=src/rhythm

# 특정 테스트만 실행
pytest tests/test_rhythm.py::TestRhythmAnalyzer -v
```

## ⚠️ 주의사항

### 1. 내부 용어 vs 사용자 용어

**이 모듈의 출력은 내부 전문 용어를 사용합니다:**

❌ **절대 금지** (사용자 UI 노출):
- 사주명리, 기문둔갑, 천간, 지지, 오행, 십성
- 대운, 세운, 월운, 일운
- 천을귀인, 역마, 공망, 도화

✅ **허용** (Content Assembly에서 변환 후):
- 오늘의 흐름, 리듬, 에너지
- 집중 시간, 주의 시간
- 기회, 도전, 정리, 휴식

### 2. 데이터 흐름

```
BirthInfo → Rhythm Analysis Engine → RhythmSignal (내부)
                                           ↓
                        Content Assembly Engine (변환)
                                           ↓
                             DailyContent (사용자 노출)
```

### 3. 정확도 개선

현재 `saju.py`의 계산 로직은 **간이 버전**입니다.

정확한 사주명리 계산을 위해:
1. 기존 검증된 라이브러리 통합
2. 전문가 검수
3. 다양한 케이스 테스트

## 📚 참고 자료

- [DAILY_CONTENT_SCHEMA.json](../../../docs/content/DAILY_CONTENT_SCHEMA.json) - 콘텐츠 스키마
- [TERMINOLOGY_POLICY.md](../../../docs/legal/TERMINOLOGY_POLICY.md) - 용어 정책
- [Phase 2 작업 계획](../../../docs/tasks/WORKPLAN.md#phase-2)

## 🔄 다음 단계: Phase 3

Rhythm Signal → Content Assembly Engine으로 넘어갑니다.

Content Assembly Engine에서:
- RhythmSignal을 받아서
- DAILY_CONTENT_SCHEMA.json 형식으로 변환
- 내부 용어를 사용자 친화적 언어로 번역
- 최소 400-600자의 풍부한 콘텐츠 생성

---

**Rhythm Analysis Engine v1.0.0**
