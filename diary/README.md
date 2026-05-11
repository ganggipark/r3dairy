# diary

사주 + 기문 기반 인쇄용 다이어리 생성 파이프라인.

## 빠른 사용

```bash
# 설치 (개발)
cd diary
python -m venv .venv
source .venv/Scripts/activate    # Windows Git Bash
pip install -e ".[dev]"

# 환경 변수
export DEEPINFRA_API_KEY="..."   # 또는 OPENAI_API_KEY, ANTHROPIC_API_KEY

# CLI 실행 (7일치)
diary --year 1990 --month 5 --day 15 --hour 14 --gender male \
      --start 2026-05-15 --days 7 --output output/diary.pdf

# 또는 python -m
python -m diary --year 1990 --month 5 --day 15 --hour 14 --gender male \
                --start 2026-05-15 --days 7
```

## 주요 옵션

| 옵션 | 설명 | 기본 |
|---|---|---|
| `--year/month/day/hour/minute` | 출생 정보 (필수) | — |
| `--gender male\|female` | 성별 (필수) | — |
| `--start YYYY-MM-DD` | 시작일 (필수) | — |
| `--days N` | 생성할 일수 | 7 |
| `--output PATH` | PDF 경로 | output/diary.pdf |
| `--provider deepinfra\|openai\|anthropic` | LLM 제공자 | deepinfra |
| `--model NAME` | 모델 override | provider 기본 |
| `--lunar` / `--leap-month` | 음력/윤월 | false |
| `--target-hour H` | 일간 기문 기준 시 | 12 |
| `--no-cache` | 캐시 끔 | (캐시 사용) |
| `--cache-dir DIR` | 캐시 위치 | .cache/content |
| `--fail-fast` | 첫 실패 시 종료 | (실패 격리) |
| `--quiet` | 진행률 숨김 | (표시) |

## 아키텍처

```
SajuInput (출생정보)
   │
   ├──▶ saju.py ─────▶ node cli.js ───────▶ CompleteSajuData
   │                                          (사주 25 필드)
   │
   └──▶ qimen.py ────▶ node qimen-cli.js ──▶ QimenResult
                                              (9궁 + best/avoid)
                                                    │
                                                    ▼
                              ┌─────────────────────────────────┐
                              │ content.py                       │
                              │   lucky_*    ← qimen (결정론)    │
                              │   narrative  ← LLM               │
                              │   (deepinfra / openai / anthropic)│
                              └────────────────┬────────────────┘
                                               ▼
                                       DailyContent (11 필드)
                                               │
                                               ▼  × N days
                              ┌─────────────────────────────────┐
                              │ pipeline.py                      │
                              │   파일 캐시 + 진행 콜백 + 격리   │
                              └────────────────┬────────────────┘
                                               ▼
                              ┌─────────────────────────────────┐
                              │ render.py                        │
                              │   WeasyPrint + Jinja2 + CSS      │
                              │   A5 portrait, 1일 = 2페이지     │
                              └────────────────┬────────────────┘
                                               ▼
                                              PDF
```

- **사주 계산** (TypeScript): `saju-engine/` — 변경 잠금 자산
- **Python 파이프라인** (`diary/`): subprocess로 saju/qimen 호출, Pydantic 검증, LLM 호출, PDF 조판
- **캐시 격리**: `customer_id = sha256(birth_info)[:12]` — 고객별 분리 디렉토리

## 출력

| 페이지 | 내용 |
|---|---|
| **좌측** | 날짜 / 요약 / 행운 정보 (색·방향·시간) / 집중·주의 / 추천·피할 / 마음챙김 |
| **우측** | 작은 날짜 / 격려문 / 28줄 글쓰기 공간 / 코너 힌트 |

## 진행 상태

- [x] M1: saju-engine CLI 통합
- [x] M2: Python 패키지 + subprocess wrapper
- [x] M3: LLM 콘텐츠 생성 (3 provider)
- [x] M3.2: qimen 통합 (lucky_* 결정론, narrative LLM)
- [x] M4: WeasyPrint PDF 양면 펼침
- [x] M5: 파이프라인 + 캐시 + 진행률
- [x] M6: CLI 진입점
- [ ] M7+: 표지·월구분·폰트 임베드·디지털 컴패니언
