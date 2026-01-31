# 색은식(五運六氣) 모듈 사용 가이드

## 개요

색은식(五運六氣) 계산 모듈은 한의학의 운기학설을 기반으로 일간 건강 리듬을 분석합니다.

### 핵심 개념

**五運(오운)**: 년/월/일의 천간(天干)을 기준으로 5가지 운(運) 결정
- 木運(목운): 성장과 확장의 에너지
- 火運(화운): 활동과 열정의 에너지
- 土運(토운): 안정과 정리의 에너지
- 金運(금운): 수확과 결단의 에너지
- 水運(수운): 휴식과 지혜의 에너지

**六氣(육기)**: 년/월의 지지(地支)를 기준으로 6가지 기(氣) 결정
- 厥陰風木(궐음풍목): 봄 기운, 바람
- 少陰君火(소음군화): 초여름 기운, 군화
- 少陽相火(소양상화): 한여름 기운, 상화
- 太陰濕土(태음습토): 장마 기운, 습기
- 陽明燥金(양명조금): 가을 기운, 건조
- 太陽寒水(태양한수): 겨울 기운, 한기

## 주요 함수

### 1. calculate_five_movements()

년/월/일의 오운 계산

```python
from datetime import date
from src.rhythm.saekeunshik import calculate_five_movements

# 오운 계산
result = calculate_five_movements(
    birth_year=1971,
    target_date=date(2026, 1, 31)
)

# 결과
{
    "year_movement": "土運",   # 년운
    "month_movement": "金運",  # 월운
    "day_movement": "水運",    # 일운
    "year_stem": "甲",         # 년 천간
    "month_stem": "乙",        # 월 천간
    "day_stem": "丙"           # 일 천간
}
```

### 2. calculate_six_qi()

사천/재천/주기 계산

```python
from src.rhythm.saekeunshik import calculate_six_qi

# 육기 계산
result = calculate_six_qi(
    birth_year=1971,
    target_date=date(2026, 1, 31)
)

# 결과
{
    "sicheon": "少陰君火",        # 사천 (상반기 주도 기운)
    "jaecheon": "陽明燥金",       # 재천 (하반기 주도 기운)
    "dominant_qi": "厥陰風木",    # 주기 (현재 월의 기본 기운)
    "year_branch": "子",          # 년 지지
    "month_branch": "寅",         # 월 지지
    "qi_phase": "상반기"          # 기운 단계
}
```

### 3. generate_health_signals()

오운육기 조합 기반 건강 신호 생성

```python
from src.rhythm.saekeunshik import (
    calculate_five_movements,
    calculate_six_qi,
    generate_health_signals
)

birth_year = 1971
target_date = date(2026, 1, 31)

# 오운/육기 계산
five_movements = calculate_five_movements(birth_year, target_date)
six_qi = calculate_six_qi(birth_year, target_date)

# 건강 신호 생성
health_signals = generate_health_signals(five_movements, six_qi, target_date)

# 결과
{
    "energy_balance": "조화",              # 에너지 균형 (조화/과잉/부족)
    "vulnerable_organs": ["신", "방광"],   # 취약 장부
    "favorable_foods": [                   # 권장 음식
        "검은콩",
        "짠맛 음식",
        "해조류",
        "따뜻한 차"
    ],
    "caution_activities": [                # 주의할 활동
        "외풍 주의",
        "신 부담 활동 자제"
    ],
    "recommended_rest_times": [            # 권장 휴식 시간
        "오전 9-11시",
        "오후 3-5시"
    ],
    "seasonal_nature": "바람",             # 계절 특성
    "season_context": "봄"                 # 계절 맥락
}
```

### 4. integrate_with_energy_json()

기존 energy.json에 색은식 데이터 통합

```python
from src.rhythm.saekeunshik import integrate_with_energy_json

# 기존 에너지 데이터
energy_data = {
    "사주": {...},
    "오행": {...},
    "에너지_수준": 4,
    "집중력": 3
}

# 색은식 데이터 통합
result = integrate_with_energy_json(
    energy_data=energy_data,
    birth_year=1971,
    target_date=date(2026, 1, 31)
)

# 결과: 기존 데이터 + saekeunshik 섹션 추가
{
    "사주": {...},
    "오행": {...},
    "에너지_수준": 4,
    "집중력": 3,
    "saekeunshik": {
        "five_movements": {...},
        "six_qi": {...},
        "health_signals": {...},
        "calculation_date": "2026-01-31"
    }
}
```

### 5. analyze_saekeunshik_summary()

색은식 종합 분석 요약

```python
from src.rhythm.saekeunshik import analyze_saekeunshik_summary

# 종합 요약
summary = analyze_saekeunshik_summary(
    birth_year=1971,
    target_date=date(2026, 1, 31)
)

# 결과
{
    "date": "2026-01-31",
    "five_movements_summary": "수운 (水運) - 휴식과 지혜의 에너지",
    "six_qi_summary": "궐음풍목 - 봄 기운, 바람 주의",
    "health_advice": "신, 방광 건강 관리, 바람 대응, 검은콩 등 섭취",
    "energy_balance": "조화",
    "detailed_data": {
        "five_movements": {...},
        "six_qi": {...},
        "health_signals": {...}
    }
}
```

## 실제 사용 예시

### 일간 리듬 분석 워크플로우

```python
from datetime import date
from src.rhythm.saekeunshik import (
    calculate_five_movements,
    calculate_six_qi,
    generate_health_signals,
    analyze_saekeunshik_summary
)

# 사용자 정보
birth_year = 1971
target_date = date(2026, 1, 31)

# 1단계: 오운 계산
five_movements = calculate_five_movements(birth_year, target_date)
print(f"일운: {five_movements['day_movement']}")
# 출력: 일운: 水運

# 2단계: 육기 계산
six_qi = calculate_six_qi(birth_year, target_date)
print(f"주기: {six_qi['dominant_qi']}")
# 출력: 주기: 厥陰風木

# 3단계: 건강 신호 생성
health = generate_health_signals(five_movements, six_qi, target_date)
print(f"취약 장부: {', '.join(health['vulnerable_organs'])}")
print(f"권장 음식: {', '.join(health['favorable_foods'][:3])}")
# 출력:
# 취약 장부: 신, 방광
# 권장 음식: 검은콩, 짠맛 음식, 해조류

# 4단계: 종합 요약
summary = analyze_saekeunshik_summary(birth_year, target_date)
print(summary['health_advice'])
# 출력: 신, 방광 건강 관리, 바람 대응, 검은콩 등 섭취
```

### 월간 배치 분석

```python
import calendar
from datetime import date
from src.rhythm.saekeunshik import analyze_saekeunshik_summary

# 2026년 1월 전체 분석
year = 2026
month = 1
birth_year = 1971

days_in_month = calendar.monthrange(year, month)[1]

monthly_report = []

for day in range(1, days_in_month + 1):
    target_date = date(year, month, day)
    summary = analyze_saekeunshik_summary(birth_year, target_date)

    monthly_report.append({
        "date": summary["date"],
        "movement": summary["five_movements_summary"],
        "qi": summary["six_qi_summary"],
        "balance": summary["energy_balance"]
    })

# 결과 출력
for report in monthly_report[:7]:  # 첫 주만 출력
    print(f"{report['date']}: {report['movement']}, {report['balance']}")
```

### API 응답 생성

```python
from fastapi import APIRouter
from datetime import date
from src.rhythm.saekeunshik import integrate_with_energy_json

router = APIRouter()

@router.get("/api/daily/{date}/saekeunshik")
async def get_daily_saekeunshik(
    date: str,
    birth_year: int
):
    """일간 색은식 분석 API"""
    target_date = date.fromisoformat(date)

    # 기존 에너지 데이터 로드 (예시)
    energy_data = load_energy_data(target_date)

    # 색은식 데이터 통합
    result = integrate_with_energy_json(
        energy_data=energy_data,
        birth_year=birth_year,
        target_date=target_date
    )

    return result
```

## 한의학 이론 배경

### 오운(五運)과 장부 관계

| 오운 | 장부 | 특성 |
|------|------|------|
| 木運 | 간, 담 | 성장, 확장, 분노 조절 |
| 火運 | 심, 소장 | 활동, 열정, 기쁨 표현 |
| 土運 | 비, 위 | 안정, 소화, 걱정 조절 |
| 金運 | 폐, 대장 | 수렴, 호흡, 슬픔 조절 |
| 水運 | 신, 방광 | 저장, 휴식, 두려움 조절 |

### 육기(六氣)와 계절/기후

| 육기 | 계절 | 기후 | 영향 |
|------|------|------|------|
| 厥陰風木 | 봄 | 바람 | 간 기능 활성화, 외풍 주의 |
| 少陰君火 | 초여름 | 더위 시작 | 심장 부담 증가 |
| 少陽相火 | 한여름 | 무더위 | 염증 주의, 수분 보충 |
| 太陰濕土 | 장마 | 습기 | 소화 기능 저하, 제습 필요 |
| 陽明燥金 | 가을 | 건조 | 호흡기 건조, 보습 필요 |
| 太陽寒水 | 겨울 | 추위 | 보온 필수, 에너지 저장 |

### 에너지 균형 판단 기준

**과잉(過剩)**:
- 상반기 + 火運/木運 조합
- 하반기 + 水運/金運 조합
→ 활동 과다, 휴식 필요

**부족(不足)**:
- 상반기 + 水運 조합
- 하반기 + 火運 조합
→ 에너지 부족, 보강 필요

**조화(調和)**:
- 위 두 경우 외
→ 균형 상태, 유지 필요

## 주의사항

### 내부 전문 용어 사용
이 모듈은 **내부 계산용**이며, 사주명리/한의학 전문 용어를 사용합니다.

⚠️ **사용자 노출 시 반드시 변환 필요**:
- "오운육기" → "에너지 리듬"
- "사천/재천" → "상반기/하반기 주도 흐름"
- "간, 담" → "해독 기능", "에너지 관리"

### Content Assembly Engine에서의 처리
```python
# 내부 표현 (이 모듈)
"vulnerable_organs": ["간", "담"]

# 사용자 표현 (변환 필요)
"건강_주의": "해독 기능과 에너지 관리에 신경 쓰세요"
```

### Role Translation Layer 통합
```python
# 역할별 번역 예시
student_version = translate_to_role(health_signals, role="student")
# "신, 방광" → "체력 관리", "충분한 수면"

worker_version = translate_to_role(health_signals, role="worker")
# "신, 방광" → "업무 피로 관리", "과로 주의"
```

## 성능 최적화

### 배치 처리
월간 또는 연간 데이터를 한번에 처리할 때는 사주 계산 결과를 재사용하세요.

```python
from src.rhythm.saju import calculate_saju
from src.rhythm.saekeunshik import generate_health_signals

# 사주 데이터는 한 번만 계산
saju_data = calculate_saju(birth_info, target_date)

# 여러 날짜에 재사용
for day in range(1, 32):
    target = date(2026, 1, day)
    five_movements = extract_from_saju(saju_data, target)
    six_qi = extract_from_saju(saju_data, target)
    health = generate_health_signals(five_movements, six_qi, target)
```

### 캐싱
동일한 출생년도/날짜 조합은 캐싱하여 재사용 가능합니다.

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def cached_saekeunshik(birth_year: int, target_date_str: str):
    target_date = date.fromisoformat(target_date_str)
    return analyze_saekeunshik_summary(birth_year, target_date)
```

## 테스트

### 단위 테스트
```bash
# 독립 테스트 (사주 계산 불필요)
pytest tests/test_saekeunshik_standalone.py -v

# 통합 테스트 (사주 엔진 필요)
pytest tests/test_saekeunshik.py -v
```

### 커버리지 확인
```bash
pytest tests/test_saekeunshik_standalone.py --cov=src.rhythm.saekeunshik
```

## 참고 문헌

1. **황제내경(黃帝內經)** - 운기학설의 기초
2. **동의보감(東醫寶鑑)** - 한의학 종합 이론서
3. **오운육기론** - 운기학설 전문 해설서

## 라이선스

MIT License - 한의학 이론은 공공 지식이며, 구현 코드는 MIT 라이선스를 따릅니다.
