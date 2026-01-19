# R³ Diary System - Backend 테스트 가이드

## 목차

1. [개요](#개요)
2. [테스트 구조](#테스트-구조)
3. [설치 및 설정](#설치-및-설정)
4. [테스트 실행](#테스트-실행)
5. [테스트 종류](#테스트-종류)
6. [커버리지](#커버리지)
7. [CI/CD 연동](#cicd-연동)
8. [트러블슈팅](#트러블슈팅)

## 개요

R³ Diary System Backend의 테스트 스위트는 다음을 포함합니다:
- **단위 테스트**: Rhythm, Content, Translation 모듈
- **통합 테스트**: API 엔드포인트, 전체 플로우
- **보안 테스트**: OWASP Top 10 검증
- **성능 테스트**: 응답 시간, 메모리 사용량
- **PDF 테스트**: PDF 생성 및 품질 검증

## 테스트 구조

```
backend/tests/
├── __init__.py
├── conftest.py                  # 공통 fixtures 및 설정
├── test_rhythm.py               # Rhythm Analysis Engine 테스트
├── test_content.py              # Content Assembly Engine 테스트
├── test_translation.py          # Role Translation Layer 테스트
├── test_api_integration.py      # API 통합 테스트
├── test_pdf_generation.py       # PDF 생성 테스트
├── test_security.py             # 보안 테스트 (OWASP Top 10)
├── test_performance.py          # 성능 테스트
└── README.md                    # 이 파일
```

## 설치 및 설정

### 의존성 설치

```bash
cd backend
pip install -r requirements.txt
```

**주요 테스트 패키지**:
- `pytest==7.4.4` - 테스트 프레임워크
- `pytest-cov==4.1.0` - 커버리지 측정
- `pytest-asyncio==0.23.3` - 비동기 테스트
- `httpx==0.26.0` - FastAPI 테스트 클라이언트

### 환경변수 설정

테스트용 환경변수는 `conftest.py`에서 자동 설정됩니다:

```python
os.environ["ENVIRONMENT"] = "test"
os.environ["SUPABASE_URL"] = "https://test.supabase.co"
os.environ["SUPABASE_KEY"] = "test-key"
```

## 테스트 실행

### 전체 테스트 실행

```bash
pytest tests/ -v
```

### 특정 파일 테스트

```bash
# Rhythm 테스트만
pytest tests/test_rhythm.py -v

# Content 테스트만
pytest tests/test_content.py -v

# API 테스트만
pytest tests/test_api_integration.py -v
```

### 마커별 테스트

```bash
# 단위 테스트만
pytest tests/ -m unit -v

# 통합 테스트만
pytest tests/ -m integration -v

# 보안 테스트만
pytest tests/ -m security -v

# 성능 테스트만
pytest tests/ -m performance -v

# PDF 테스트만
pytest tests/ -m pdf -v

# 빠른 테스트만 (느린 테스트 제외)
pytest tests/ -m "not slow" -v
```

### 특정 클래스 또는 메서드 테스트

```bash
# 특정 클래스
pytest tests/test_rhythm.py::TestRhythmAnalyzer -v

# 특정 테스트 메서드
pytest tests/test_rhythm.py::TestRhythmAnalyzer::test_generate_daily_signal -v
```

## 테스트 종류

### 1. 단위 테스트 (`@pytest.mark.unit`)

**Rhythm Analysis Engine** (`test_rhythm.py`):
- BirthInfo 모델 검증
- RhythmSignal 생성 및 검증
- 사주 계산 로직 테스트
- 일간/월간/연간 리듬 신호 생성

**Content Assembly Engine** (`test_content.py`):
- DailyContent 모델 검증
- 리듬 신호 → 콘텐츠 변환
- 내부 용어 노출 방지 검증
- 최소 길이 요구사항 충족 확인

**Role Translation Layer** (`test_translation.py`):
- 역할별 표현 변환
- 의미 불변성 검증
- 템플릿 시스템 테스트

### 2. 통합 테스트 (`@pytest.mark.integration`)

**API Integration** (`test_api_integration.py`):
- 헬스체크 엔드포인트
- 인증 API (signup, login)
- 프로필 API (CRUD)
- 일간/월간 콘텐츠 API
- 로그 API
- PDF API
- 전체 사용자 플로우

### 3. 보안 테스트 (`@pytest.mark.security`)

**OWASP Top 10 검증** (`test_security.py`):
- ✅ A01:2021 – Broken Access Control
- ✅ A02:2021 – Cryptographic Failures
- ✅ A03:2021 – Injection
- ✅ A05:2021 – Security Misconfiguration
- ✅ A07:2021 – Identification and Authentication Failures

**검증 항목**:
- 보호된 엔드포인트 인증 필수
- SQL Injection 방지
- XSS 방지
- 비밀번호 노출 방지
- 내부 용어 노출 방지
- 스택 트레이스 노출 방지

### 4. 성능 테스트 (`@pytest.mark.performance`)

**Response Time** (`test_performance.py`):
- 헬스체크: < 100ms
- 리듬 신호 생성: < 1초
- 콘텐츠 조립: < 0.5초
- 역할 번역: < 0.3초
- 전체 파이프라인: < 2초

**Concurrency**:
- 동시 요청 50개: < 5초

**Memory**:
- 단일 콘텐츠 생성: < 10MB
- 100회 생성: < 50MB (메모리 누수 없음)

### 5. PDF 테스트 (`@pytest.mark.pdf`)

**PDF Generation** (`test_pdf_generation.py`):
- WeasyPrint 통합 검증
- 일간 PDF 생성
- 역할별 PDF 생성
- 10개 블록 포함 확인
- 레이아웃 검증
- 파일 크기 검증 (5KB ~ 5MB)
- 생성 속도 검증 (< 5초)

## 커버리지

### 커버리지 측정

```bash
# HTML 리포트 생성
pytest tests/ --cov=src --cov-report=html

# 터미널 출력
pytest tests/ --cov=src --cov-report=term

# 특정 모듈만
pytest tests/ --cov=src/rhythm --cov-report=html
```

### 커버리지 목표

- **Rhythm Module**: 90% 이상
- **Content Module**: 90% 이상
- **Translation Module**: 85% 이상
- **API Module**: 80% 이상

### 커버리지 리포트 확인

```bash
# HTML 리포트 열기
open htmlcov/index.html  # macOS
start htmlcov/index.html  # Windows
```

## CI/CD 연동

### GitHub Actions 예시

```yaml
# .github/workflows/backend-tests.yml
name: Backend Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python 3.11
      uses: actions/setup-python@v4
      with:
        python-version: 3.11

    - name: Install dependencies
      run: |
        cd backend
        pip install -r requirements.txt

    - name: Run tests
      run: |
        cd backend
        pytest tests/ -v -m "not slow" --cov=src --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: backend/coverage.xml
        flags: backend
```

### 로컬 CI 시뮬레이션

```bash
# CI 환경 변수 설정
export CI=true

# CI 모드로 테스트 실행
pytest tests/ -v -m "not slow" --cov=src --cov-report=term
```

## 트러블슈팅

### WeasyPrint 설치 실패

**증상**: `pip install weasyprint` 실패

**해결**:

**Windows**:
```bash
# GTK+ for Windows 설치 필요
# 또는 WeasyPrint Windows 빌드 사용
```

**macOS**:
```bash
brew install cairo pango gdk-pixbuf libffi
pip install weasyprint
```

**Linux (Ubuntu/Debian)**:
```bash
sudo apt-get install build-essential python3-dev \
    libcairo2 libpango-1.0-0 libgdk-pixbuf2.0-0
pip install weasyprint
```

### PDF 테스트 스킵

**증상**: PDF 테스트가 스킵됨

**해결**:
```bash
# WeasyPrint 설치 확인
python -c "import weasyprint; print(weasyprint.__version__)"

# PDF 테스트 강제 실행
pytest tests/test_pdf_generation.py -v
```

### Mock Supabase 관련 오류

**증상**: API 테스트에서 Supabase 관련 에러

**해결**:
- `conftest.py`의 `mock_supabase_client` fixture 확인
- 실제 Supabase 연결이 필요한 경우 `.env` 설정

### 성능 테스트 실패

**증상**: 성능 테스트 타임아웃

**해결**:
```bash
# 느린 테스트 제외
pytest tests/ -m "not slow" -v

# 타임아웃 증가
pytest tests/test_performance.py -v --timeout=60
```

## 테스트 베스트 프랙티스

1. **테스트 격리**: 각 테스트는 독립적으로 실행 가능해야 함
2. **Mock 사용**: 외부 의존성은 Mock으로 대체
3. **의미있는 이름**: 테스트 이름은 무엇을 검증하는지 명확히
4. **Arrange-Act-Assert 패턴**: 준비-실행-검증 구조 유지
5. **커버리지 유지**: 새 코드 작성 시 테스트도 함께 작성

## 참고 자료

- [Pytest 공식 문서](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [WeasyPrint 문서](https://doc.courtbouillon.org/weasyprint/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
