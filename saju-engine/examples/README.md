# saju-engine examples

`cli.js`의 입출력 계약(contract) 문서.

## 파일

- `sample_input.json` — `SajuCalculationInput` 입력 예시
- `sample_output.json` — `CompleteSajuData` 출력 (cli.js를 위 입력으로 호출한 결과)

## 재생성

```bash
cd saju-engine
cat examples/sample_input.json | node cli.js > examples/sample_output.json
```

## 입력 스펙

| 필드 | 타입 | 필수 | 기본 | 설명 |
|---|---|---|---|---|
| year | number | ✓ | — | 출생연도 (4자리) |
| month | number | ✓ | — | 출생월 (1-12) |
| day | number | ✓ | — | 출생일 (1-31) |
| hour | number | ✓ | — | 출생시 (0-23) |
| minute | number | | 0 | 출생분 (0-59) |
| gender | "male" \| "female" | ✓ | — | 성별 |
| isLunar | boolean | | false | 음력 여부 |
| isLeapMonth | boolean | | false | 윤월 여부 |
| useTrueSolarTime | boolean | | true | 진태양시 보정 |
| birthPlace | string | | "서울" | 출생지 |

## 출력 스키마 (요약)

`sample_output.json`이 단일 진실 소스(SoT). 주요 섹션 키만 발췌:

| 섹션 | 주요 키 |
|---|---|
| `fourPillars.{year,month,day,time}` | `gan`, `ji`, `ganJi`, `ganOhHaeng`, `jiOhHaeng` |
| `fullSajuString` | `"경오 신사 경진 계미"` 형식 |
| `ohHaeng` | `dominant`, `weak`, `balance` |
| `sipSung` | `dominant`, `weak`, `balance`, `detail` |
| `gyeokGuk` | `dayMaster`, `dayMasterOhHaeng`, `strength`, `gyeokGukType`, `description`, `season`, `monthBranch`, `strengthDetail` |
| `yongSin` | `yongSin`, `giSin`, `huiSin`, `yongSinReason`, `giSinReason`, `yongSinScore` |
| `daewoon` | `startAge`, `direction`, `list[]`, `current`, `currentAge`, `bestPeriod`, `worstPeriod` |
| `currentYearSewoon` / `nextYearSewoon` | `year`, `age`, `gan`, `ji`, `ganJi`, `ohHaeng`, `animal`, `score` |
| `sinsal` | `gilSin`, `hyungSin`, `hasCheonEulGuiIn`, `hasMunChangGuiIn`, `hasYeokMaSal`, `hasDoHwaSal`, `hasYangInSal`, `hasGeopSal` |
| `personality` | `dayMasterTraits`, `dominantSipsung`, `careerAptitude`, `relationshipStyle` |
| `relations` | (객체) |

루트 메타: `version`, `calculatedAt`, `isComplete`, `birthInfo`.
루트 별칭(alias) 키: `year`, `month`, `day`, `time`, `ohHaengBalance`, `sipSungBalance`, `fullSaju`, `tenGods`, `fiveElements` — `fourPillars`/`ohHaeng`/`sipSung` 등의 평탄화 복제. M2에서는 **구조화된 키(`fourPillars`, `ohHaeng`)를 우선 사용**.

총 루트 키: 25.

## Python subprocess 호출 (M2 reference)

```python
import json, subprocess
from pathlib import Path

SAJU_ENGINE = Path(__file__).parent.parent / "saju-engine"

def calculate_saju(birth_info: dict) -> dict:
    result = subprocess.run(
        ["node", "cli.js"],
        cwd=str(SAJU_ENGINE),
        input=json.dumps(birth_info),
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)
```
