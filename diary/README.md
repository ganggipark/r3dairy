# diary

사주 + 기문 기반 인쇄용 다이어리 생성 파이프라인.

## 빠른 사용

```bash
cd diary
python -m venv .venv
.venv\Scripts\Activate.ps1     # Windows PowerShell
pip install -e ".[dev]"

# 환경 변수
$env:DEEPINFRA_API_KEY = "..."    # 또는 OPENAI_API_KEY, ANTHROPIC_API_KEY

# 단일 고객 — 7일치
diary --year 1990 --month 5 --day 15 --hour 14 --gender male `
      --customer-name "홍길동" --start 2026-05-15 --days 7 `
      -o output\diary.pdf

# 다고객 일괄 — CSV
diary-batch --customers samples\sample_customers.csv `
            --start 2026-05-15 --days 365 `
            --output-dir output\batch `
            --summary-output output\run-summary.json `
            --continue-on-error
```

자세한 설정은 [docs/DEPLOY.md](docs/DEPLOY.md) 참조.

## 주요 옵션 (단일 CLI)

| 옵션 | 설명 | 기본 |
|---|---|---|
| `--year/month/day/hour/minute` | 출생 정보 (필수) | — |
| `--gender male\|female` | 성별 (필수) | — |
| `--start YYYY-MM-DD` | 시작일 (필수) | — |
| `--days N` | 일수 | 7 |
| `--output PATH` | PDF 경로 | output/diary.pdf |
| `--customer-name "이름"` | 표지에 표시 | — |
| `--subtitle "부제"` | 표지 부제 | — |
| `--no-cover` | 표지 제외 | (포함) |
| `--no-month-dividers` | 월 구분 제외 | (포함) |
| `--provider deepinfra\|openai\|anthropic` | LLM 제공자 | deepinfra |
| `--model NAME` | 모델 override | provider 기본 |
| `--lunar` / `--leap-month` | 음력/윤월 | false |
| `--target-hour H` | 일간 기문 기준 시 | 12 |
| `--concurrency N` | 병렬 워커 수 | 5 |
| `--max-retries N` | LLM 재시도 횟수 | 3 |
| `--no-cache` / `--cache-dir DIR` | 캐시 제어 | `.cache/content` |
| `--fail-fast` | 첫 실패 즉시 종료 | (실패 격리) |
| `--quiet` | 진행률 숨김 | (표시) |

## CSV 일괄 처리 (diary-batch)

**CSV 형식** (UTF-8):

| 컬럼 | 필수 | 비고 |
|---|---|---|
| customer_id | ✓ | 출력 파일명 prefix |
| name | ✓ | 표지에 표시 |
| year/month/day/hour | ✓ | 출생 정보 |
| gender | ✓ | male / female |
| minute | | 기본 0 |
| lunar | | true/false, 기본 false |
| leap_month | | true/false, 기본 false |
| birth_place | | 기본 "서울" |

샘플: [`samples/sample_customers.csv`](samples/sample_customers.csv).

**옵션** (diary 옵션과 대부분 동일, 차이점만):

| 옵션 | 설명 |
|---|---|
| `--customers PATH` | CSV 파일 (필수) |
| `--output-dir DIR` | 결과 PDF들 저장 디렉토리 |
| `--summary-output PATH.json` | 머신 가독 JSON 요약 |
| `--continue-on-error` | 1명 실패 시 다음 고객 진행 |

**출력 파일명**: `<output-dir>/<customer_id>_<safe_name>.pdf`
(`safe_name`은 영숫자/한글/underscore만; 그 외 문자는 `_`로 치환)

## 출력 페이지 구성

| 페이지 타입 | 좌 | 우 |
|---|---|---|
| **표지** | 제목 / 부제 / 기간 / 이름 | 사용법 안내문 |
| **월 구분** | 큰 월 번호 / 연도 | "이번 달의 다짐" 18줄 |
| **일별** | 날짜 / 요약 / 색·방향·시간 / 집중·주의 / 추천·피할 / 마음챙김 | 작은 날짜 / 격려문 / 28줄 작성 / 코너 힌트 |

## 모바일 컴패니언 (Web)

```bash
diary --year 1971 --month 11 --day 17 --hour 4 --gender male \
      --customer-name "박준수" --start 2026-05-15 --days 365 \
      -o output/park_junsoo.pdf \
      --web-output ../web-deploy/public/d

cd ../web-deploy && vercel deploy --prod
```

상세: [`../docs/DEPLOY_WEB.md`](../docs/DEPLOY_WEB.md)

## 인계/운영 문서

- [`docs/DEPLOY.md`](docs/DEPLOY.md) — 새 PC 셋업 가이드 (Windows 기준)
- [`docs/PRINT_CHECKLIST.md`](docs/PRINT_CHECKLIST.md) — 인쇄소 출고 전 검증 절차

## 개발

```bash
# 테스트
pytest

# 단일 테스트
pytest tests/test_pipeline.py -v
```

## 진행 상태

- [x] M1: saju-engine CLI 통합
- [x] M2: Python 패키지 + subprocess wrapper
- [x] M3: LLM 콘텐츠 생성 (3 provider)
- [x] M3.2: qimen 통합 (lucky_* 결정론, narrative LLM)
- [x] M4: WeasyPrint PDF 양면 펼침
- [x] M5: 파이프라인 + 캐시 + 진행률
- [x] M6: CLI 진입점
- [x] M7: 병렬 처리 (ThreadPoolExecutor)
- [x] M8: LLM retry + 백오프
- [x] M9: 표지 + 월 구분 페이지
- [x] M10: Pretendard 폰트 임베드
- [x] M11/M11.1: JSON 파싱 retry + 진행률 카운터 + auth fail-fast
- [x] M12: CSV 일괄 처리 (diary-batch)
- [x] M13: JSON 요약 출력 + RuntimeWarning 해소
- [x] M14: 운영 문서 (DEPLOY + PRINT_CHECKLIST)
- [ ] 후순위: Pretendard glyph coverage 검증, Retry jitter, FastAPI 디지털 컴패니언
