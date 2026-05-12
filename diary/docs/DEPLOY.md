# Deployment Guide

새 PC에서 diary 시스템을 처음부터 설정하는 절차 (Windows 기준).

## 시스템 요구사항

| 항목 | 최소 |
|---|---|
| OS | Windows 10/11 (macOS/Linux는 GTK 대신 native lib) |
| Python | 3.11+ |
| Node.js | 18+ |
| RAM | 2GB+ |
| Disk | ~500MB (코드 + 폰트 + venv) + 캐시 |

Windows 추가 의존:
- **GTK3 Runtime** (WeasyPrint native lib)

## 셋업 절차

### 1. 필수 도구 설치 (관리자 PowerShell)

```powershell
# Python 3.11+ (확인)
python --version

# Node.js
winget install --id=OpenJS.NodeJS

# GTK3 Runtime (WeasyPrint 의존)
winget install --id=GNOME.GTK3 -e

# Git
winget install --id=Git.Git -e
```

설치 후 **새 PowerShell 창** 열어야 PATH 인식.

### 2. 저장소 가져오기

```powershell
git clone <repo-url>
cd diary-PJ
```

SSH 키 사용 시 GitHub 계정 매핑 확인.

### 3. saju-engine (Node.js)

```powershell
cd saju-engine
npm install
npm run build
node cli.js examples\sample_input.json | Select-Object -First 10
cd ..
```

마지막 명령에서 사주 JSON 출력되면 OK.

### 4. diary (Python)

```powershell
cd diary
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

`(.venv)` 프롬프트 확인 후 다음 단계.

### 5. 환경 변수

세션 한정:
```powershell
$env:DEEPINFRA_API_KEY = "실제 키"
```

영구 설정 (PowerShell):
```powershell
[Environment]::SetEnvironmentVariable("DEEPINFRA_API_KEY", "실제 키", "User")
```

### 6. 동작 확인

```powershell
# 단위 테스트 (~30초, 단 PDF 렌더 포함 시 ~10분)
pytest

# Hello World — 1일치 PDF
diary --year 1990 --month 5 --day 15 --hour 14 --gender male `
      --start 2026-05-15 --days 1 -o output\hello.pdf

start output\hello.pdf
```

PDF 정상 열림 + 한글 표시 + 표지 2 + 월구분 2 + 일별 2 = 6p 확인.

## Troubleshooting

| 증상 | 해결 |
|---|---|
| `diary: command not found` | venv 미활성. `.venv\Scripts\Activate.ps1` |
| `OSError: cannot load library 'libgobject'` | GTK3 미설치 또는 새 셸 미사용. winget 재실행 + 새 PowerShell |
| `node: command not found` | Node.js PATH 누락. `winget install OpenJS.NodeJS` + 새 셸 |
| `Pretendard not in PDF` | 폰트 파일 누락. `pytest tests/test_render.py::test_pretendard_font_files_present` |
| `LLM API failed: 401` | API 키 placeholder. `$env:DEEPINFRA_API_KEY.Substring(0,6)` 로 확인 |
| `LLM API failed: 429` | rate limit. `--concurrency 3` 로 낮추거나 `--max-retries 5` |
| `Set-ExecutionPolicy 거부` | `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` 한 번 |
| PDF가 너무 작음 (<10KB) | LLM 호출 모두 실패. 진행률 출력에서 errors 확인 |

## 업그레이드

```powershell
cd diary-PJ
git pull
cd saju-engine && npm install && npm run build && cd ..
cd diary && .venv\Scripts\Activate.ps1 && pip install -e ".[dev]" --upgrade
pytest
```

## 디렉토리 구조

```
diary-PJ/
├── saju-engine/              # TS 사주/기문 계산 엔진
│   ├── src/                  # TypeScript 소스
│   ├── dist/                 # tsc 빌드 산출물 (cli.js가 require)
│   ├── cli.js                # 사주 stdin/stdout JSON CLI
│   ├── qimen-cli.js          # 기문 stdin/stdout JSON CLI
│   └── examples/             # sample_input/output.json
│
└── diary/                    # Python 파이프라인
    ├── diary/                # 패키지
    │   ├── __init__.py
    │   ├── cli.py            # diary CLI 진입점
    │   ├── batch.py          # diary-batch CLI 진입점
    │   ├── pipeline.py       # 오케스트레이션 (cache + parallel)
    │   ├── content.py        # LLM 호출 + lucky_* 결정론
    │   ├── render.py         # WeasyPrint 호출
    │   ├── saju.py / qimen.py  # subprocess wrapper
    │   ├── models.py         # Pydantic 모델
    │   ├── retry.py          # 재시도 로직
    │   ├── prompts/          # daily.md (Jinja2 LLM 프롬프트)
    │   ├── templates/        # diary.html (Jinja2 PDF 템플릿)
    │   └── static/           # styles.css + fonts/Pretendard-*.woff2
    ├── samples/              # sample_customers.csv, generate_sample.py
    ├── tests/                # pytest 스위트
    ├── docs/                 # DEPLOY.md, PRINT_CHECKLIST.md
    ├── output/               # 생성 PDF (gitignored)
    ├── .cache/               # LLM 응답 캐시 per customer (gitignored)
    ├── pyproject.toml
    ├── README.md
    └── .gitattributes        # woff2 binary 명시
```
