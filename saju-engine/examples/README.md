# saju-engine examples

`cli.js` (사주) + `qimen-cli.js` (기문) 입출력 계약 문서.

## 파일

- `sample_input.json` / `sample_output.json` — 사주 (cli.js)
- `sample_qimen_input.json` / `sample_qimen_output.json` — 기문 (qimen-cli.js)

## 재생성

```bash
cd saju-engine
cat examples/sample_input.json | node cli.js > examples/sample_output.json
cat examples/sample_qimen_input.json | node qimen-cli.js > examples/sample_qimen_output.json
```

## 사주 입력 스펙

`{year, month, day, hour, minute?, gender, isLunar?, isLeapMonth?, useTrueSolarTime?, birthPlace?}`

자세한 출력 스키마는 `sample_output.json`을 단일 진실 소스로 사용.
주요 루트 키: `version`, `calculatedAt`, `isComplete`, `birthInfo`, `fourPillars`,
`fullSajuString`, `ohHaeng`, `sipSung`, `gyeokGuk`, `yongSin`, `daewoon`,
`currentYearSewoon`, `nextYearSewoon`, `sinsal`, `relations`, `personality` (+ 별칭).

## 기문 입력 스펙

`{birthDate: ISO8601, targetDate: ISO8601, targetHour?: 0-23}`

기본 `targetHour=12` (오시) — 그날의 대표 기문 스냅샷.

기문 출력 키: `hourStart`, `hourEnd`, `hourBranch`, `palaces[9]`,
`bestPalace`, `avoidPalace`, `overallQuality` ('excellent'|'good'|'neutral'|'bad'),
`userGuidance`. 각 palace: `palaceNum`, `directionKo`/`directionEn`,
`gate`, `star`, `deity`, `earthlyPlateGan`, `heavenlyPlateGan`, `qualityScore`.

## Python subprocess 패턴

```python
from diary import SajuInput, calculate_saju, calculate_qimen
from datetime import datetime, date

saju = calculate_saju(SajuInput(year=1990, month=5, day=15, hour=14, gender="male"))
qimen = calculate_qimen(datetime(1990, 5, 15, 14, 0), date(2026, 5, 15), target_hour=12)
```
