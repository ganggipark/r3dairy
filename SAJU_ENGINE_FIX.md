# 사주 엔진 경로 수정

**날짜**: 2026-02-02
**상태**: ✅ 수정 완료

## 문제

브라우저에서 일간 콘텐츠 생성 시 사주 계산 오류 발생:

```
일간 콘텐츠 생성 중 오류가 발생했습니다:
사주 계산 중 오류 발생: 사주 계산 실패:

(node:10580) [MODULE_TYPELESS_PACKAGE_JSON] Warning:
Module type of file:///E:/project/diary-PJ/backend/saju-engine/cli.js is not specified

Error: Cannot find module 'E:\project\diary-PJ\backend\saju-engine\dist\index.js'
```

## 근본 원인

1. **경로 불일치**: Python 코드가 `saju-engine`을 참조하지만, 실제로는 `saju-calculator`에 빌드된 파일이 있음
2. **빌드 누락**: `saju-engine/dist` 폴더가 생성되지 않음
3. **중복 디렉토리**: `backend/saju-engine`과 `backend/saju-calculator` 두 개 존재

## 해결 방법

### 1. Python 코드 경로 수정

**파일**: `backend/src/rhythm/saju.py:39`

**변경 전**:
```python
# Node.js CLI 경로 (정확한 saju-engine 사용)
current_dir = Path(__file__).parent.parent.parent  # backend/
cli_path = current_dir / "saju-engine" / "cli.js"
```

**변경 후**:
```python
# Node.js CLI 경로 (saju-calculator 사용)
current_dir = Path(__file__).parent.parent.parent  # backend/
cli_path = current_dir / "saju-calculator" / "cli.js"
```

### 2. saju-calculator 디렉토리 확인

```bash
$ cd E:\project\diary-PJ\backend\saju-calculator
$ ls -la
total 121
drwxr-xr-x 1 PC2412 197121     0  1월 31 04:53 ./
drwxr-xr-x 1 PC2412 197121     0  1월 31 23:30 ../
-rwxr-xr-x 1 PC2412 197121  1815  1월 30 04:51 cli.js*
drwxr-xr-x 1 PC2412 197121     0  1월 31 04:12 dist/  ← 빌드 파일 존재 ✅
drwxr-xr-x 1 PC2412 197121     0  1월 21 13:03 node_modules/
-rw-r--r-- 1 PC2412 197121  1223  1월 31 04:53 package.json
drwxr-xr-x 1 PC2412 197121     0  1월 31 12:43 src/
```

### 3. Backend 서버 재시작

```bash
# 기존 프로세스 종료
powershell.exe -Command "Get-Process python | Stop-Process -Force"

# 새로 시작
cd E:\project\diary-PJ\backend
python -m uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
```

## 디렉토리 구조

```
backend/
├── saju-calculator/          ✅ 사용 중 (dist 폴더 있음)
│   ├── cli.js
│   ├── dist/
│   │   ├── index.js
│   │   ├── completeSajuCalculator.js
│   │   └── ...
│   ├── src/
│   ├── package.json
│   └── tsconfig.json
│
├── saju-engine/              ❌ 사용 안함 (dist 폴더 없음)
│   ├── cli.js
│   ├── src/
│   ├── package.json (type: module 추가됨)
│   └── tsconfig.json (module: ESNext 변경됨)
│
└── src/
    └── rhythm/
        └── saju.py          ✅ saju-calculator 사용으로 수정
```

## 테스트 방법

### 1. Backend API 직접 테스트
```bash
# 사주 계산 API 호출
curl -X POST http://localhost:8000/api/rhythm/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "birth_date": "1971-11-17",
    "birth_time": "04:00",
    "gender": "male",
    "birth_place": "서울"
  }'
```

### 2. 브라우저 테스트
```
1. http://localhost:3000/login 접속
2. quicktest@example.com / test123456 로그인
3. /today 페이지 접속
4. 일간 콘텐츠 생성 확인
```

## 예상 결과

### ✅ 성공 시
```json
{
  "year_pillar": { "cheongan": "辛", "jiji": "亥" },
  "month_pillar": { "cheongan": "己", "jiji": "亥" },
  "day_pillar": { "cheongan": "戊", "jiji": "申" },
  "hour_pillar": { "cheongan": "甲", "jiji": "寅" },
  "body_strength": "중화",
  "용신": "木",
  ...
}
```

### ❌ 실패 시
```json
{
  "error": "사주 계산 실패: Cannot find module 'E:\\project\\diary-PJ\\backend\\saju-engine\\dist\\index.js'"
}
```

**원인**: 경로가 여전히 `saju-engine`을 참조
**해결**: `backend/src/rhythm/saju.py:39` 확인

## 향후 작업

### 1. saju-engine 정리 (선택)
```bash
# saju-engine 디렉토리 제거 (saju-calculator 사용 확정 후)
cd E:\project\diary-PJ\backend
rm -rf saju-engine/
```

### 2. package.json 통합 (선택)
`saju-calculator`의 설정을 표준화:
```json
{
  "type": "module",
  "module": "ESNext",
  ...
}
```

### 3. 문서 업데이트
- `backend/README.md`: saju-calculator 사용 명시
- `docs/architecture/ARCHITECTURE.md`: 사주 계산 모듈 경로 업데이트

## Git 커밋

```bash
git add backend/src/rhythm/saju.py
git commit -m "fix: 사주 계산 모듈 경로 수정 (saju-engine → saju-calculator)

- backend/src/rhythm/saju.py에서 cli_path 변경
- saju-calculator/dist 폴더 사용 (빌드 파일 존재)
- saju-engine은 dist 폴더 없어서 에러 발생

문제:
  Cannot find module 'saju-engine/dist/index.js'

해결:
  saju-calculator/dist/index.js 사용

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

## 확인 사항

- [x] `backend/src/rhythm/saju.py` 경로 수정
- [x] `backend/saju-calculator/dist` 존재 확인
- [ ] Backend 서버 재시작
- [ ] 사주 계산 API 테스트
- [ ] 브라우저에서 일간 콘텐츠 생성 테스트

---

**작성일**: 2026-02-02
**수정 파일**: `backend/src/rhythm/saju.py`
**변경 내용**: `saju-engine` → `saju-calculator`
**다음 작업**: Backend 서버 재시작 및 테스트
