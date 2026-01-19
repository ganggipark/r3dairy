# R³ 다이어리 PDF Generator

WeasyPrint와 Jinja2를 사용한 HTML → PDF 변환 시스템

## 개요

R³ 다이어리 시스템의 일간/월간 콘텐츠를 인쇄물로 출력하기 위한 PDF 생성 엔진입니다.

## 기술 스택

- **PDF 생성**: WeasyPrint
- **템플릿 엔진**: Jinja2
- **스타일링**: CSS3 (인쇄 최적화)

## 프로젝트 구조

```
pdf-generator/
├── templates/           # HTML 템플릿
│   ├── daily.html      # 일간 PDF 템플릿 (10개 블록)
│   └── monthly.html    # 월간 PDF 템플릿 (플레이스홀더)
├── styles.css          # PDF 스타일시트 (인쇄 최적화)
├── generator.py        # PDF 생성 엔진
└── README.md           # 이 파일
```

## 설치

### 의존성 설치

PDF Generator는 Backend의 일부로 설치됩니다:

```bash
cd backend
pip install -r requirements.txt
```

**필수 패키지**:
- `weasyprint` - HTML → PDF 변환
- `jinja2` - 템플릿 렌더링

### WeasyPrint 시스템 의존성

WeasyPrint는 시스템 레벨 라이브러리가 필요합니다:

**Windows**:
- GTK+ for Windows 설치 필요
- 또는 WeasyPrint Windows 빌드 사용

**macOS**:
```bash
brew install cairo pango gdk-pixbuf libffi
```

**Linux (Ubuntu/Debian)**:
```bash
sudo apt-get install build-essential python3-dev python3-pip python3-setuptools python3-wheel python3-cffi libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info
```

## 사용 방법

### 1. Python 스크립트에서 직접 사용

```python
from generator import PDFGenerator

# PDF Generator 인스턴스 생성
generator = PDFGenerator()

# 일간 PDF 생성
daily_content = {
    "date": "2026-01-20",
    "summary": "오늘은 집중과 정리가 필요한 날입니다.",
    "keywords": ["집중", "정리", "완료"],
    "rhythm_description": "오늘의 리듬은 안정적입니다...",
    # ... (DAILY_CONTENT_SCHEMA에 맞는 나머지 필드)
}

pdf_path = generator.generate_daily_pdf(
    content=daily_content,
    output_path="output/2026-01-20.pdf",
    role="student"  # 선택사항
)
print(f"PDF 생성 완료: {pdf_path}")
```

### 2. Backend API를 통한 사용

Backend API 엔드포인트를 통해 PDF를 생성하고 다운로드:

```bash
# 일간 PDF 다운로드
curl -H "Authorization: Bearer {your_token}" \
     http://localhost:8000/api/pdf/daily/2026-01-20?role=student \
     --output diary_2026-01-20.pdf

# 월간 PDF 다운로드 (Phase 3 이후 지원)
curl -H "Authorization: Bearer {your_token}" \
     http://localhost:8000/api/pdf/monthly/2026/1?role=student \
     --output diary_2026-01.pdf
```

### 3. 테스트 실행

```bash
cd pdf-generator
python generator.py
```

샘플 PDF (`test_daily_full.pdf`)가 생성됩니다.

## 템플릿 구조

### 일간 템플릿 (daily.html)

**Jinja2 변수**:
- `content` - DailyContent 딕셔너리 (10개 블록)
  - `content.date` - 날짜
  - `content.summary` - 요약
  - `content.keywords` - 키워드 리스트
  - `content.rhythm_description` - 리듬 해설
  - `content.focus_caution` - 집중/주의 포인트
  - `content.action_guide` - 행동 가이드 (Do/Avoid)
  - `content.time_direction` - 시간/방향
  - `content.state_trigger` - 상태 전환 트리거
  - `content.meaning_shift` - 의미 전환
  - `content.rhythm_question` - 리듬 질문
- `role` - 역할 (student, office_worker, freelancer)
- `role_display` - 역할 한글 표시 (학생, 직장인, 프리랜서)
- `generated_at` - 생성 시각

### 월간 템플릿 (monthly.html)

**현재 상태**: 플레이스홀더
- Phase 3에서 MonthlyContent 구조가 정의되면 상세 구현 예정
- 예상 콘텐츠: 이번 달 테마, 우선순위, 주별 요약, 캘린더

## PDF 스타일 (styles.css)

### 페이지 설정
- **용지 크기**: A4
- **여백**: 상하 20mm, 좌우 15mm
- **페이지 번호**: 하단 중앙
- **헤더**: 상단 중앙에 "R³ 다이어리" (첫 페이지 제외)

### 주요 스타일 클래스

**레이아웃**:
- `.header` - 페이지 헤더 (제목, 날짜, 역할)
- `.summary-card` - 요약 카드 (회색 배경, 파란 좌측 테두리)
- `.content-block` - 콘텐츠 블록 (제목 + 본문)
- `.two-column` - 2열 레이아웃 (집중/주의, Do/Avoid)

**특수 블록**:
- `.focus-section` - 집중 포인트 (녹색 계열)
- `.caution-section` - 주의 포인트 (빨간색 계열)
- `.do-section` - 권장 행동 (녹색 계열)
- `.avoid-section` - 지양 행동 (빨간색 계열)
- `.trigger-box` - 트리거 박스 (노란색 계열)
- `.meaning-shift-block` - 의미 전환 (보라색 계열)
- `.question-block` - 질문 박스 (주황색 계열)

**페이지 브레이크**:
- `.page-break` - 페이지 브레이크 강제
- `.page-break-avoid` - 페이지 브레이크 금지 (블록 분할 방지)

### 인쇄 최적화
- 색상 보존 (`print-color-adjust: exact`)
- 페이지 브레이크 제어 (블록 단위 유지)
- 폰트: 맑은 고딕 (한글 가독성)
- 타이포그래피: 10pt (본문), 12pt (소제목)

## API 통합

Backend의 `src/api/pdf.py`가 PDF Generator를 호출합니다:

### 엔드포인트

#### GET /api/pdf/daily/{date}
일간 콘텐츠 PDF 생성 및 다운로드

**Query Parameters**:
- `role` (선택): student, office_worker, freelancer

**Response**: PDF 파일 (application/pdf)

#### GET /api/pdf/monthly/{year}/{month}
월간 콘텐츠 PDF 생성 및 다운로드 (Phase 3 이후 지원)

**Query Parameters**:
- `role` (선택): student, office_worker, freelancer

**Response**: PDF 파일 (application/pdf)

### 파일명 형식
- 일간: `R3_Diary_2026-01-20_student.pdf`
- 월간: `R3_Diary_2026_01_student.pdf`

## 개발 가이드

### 새 템플릿 추가

1. `templates/` 디렉토리에 HTML 파일 생성
2. Jinja2 변수 사용 (`{{ variable }}`, `{% for %}`)
3. `styles.css`의 클래스 활용
4. `generator.py`에 생성 메서드 추가

### 스타일 수정

`styles.css`를 수정하여 PDF 디자인 변경:
- 색상 변경
- 여백 조정
- 폰트 크기 변경
- 페이지 레이아웃 변경

**주의사항**:
- `@page` 규칙 사용 (WeasyPrint 지원)
- `page-break-inside: avoid` 사용 (블록 분할 방지)
- 인쇄용 색상 사용 (CMYK 고려)

### 테스트

```bash
# generator.py의 main() 함수 실행
python generator.py

# 생성된 PDF 확인
# test_daily_full.pdf
```

## 문제 해결

### WeasyPrint 설치 실패

**증상**: `pip install weasyprint` 실패

**해결**:
1. 시스템 의존성 설치 (위의 "설치" 섹션 참조)
2. Python 버전 확인 (3.7+ 필요)
3. 공식 문서 참조: https://doc.courtbouillon.org/weasyprint/

### PDF에 폰트가 깨짐

**증상**: 한글이 네모 박스로 표시됨

**해결**:
1. 시스템에 "맑은 고딕" 폰트 설치 확인
2. `styles.css`에서 폰트 패밀리 변경
3. 폰트 파일을 직접 지정 (CSS `@font-face`)

### PDF 레이아웃이 예상과 다름

**증상**: 요소가 겹치거나 잘림

**해결**:
1. `page-break-inside: avoid` 추가
2. 여백 조정 (`margin`, `padding`)
3. 브라우저에서 HTML 먼저 확인 (F12 개발자 도구)

### 페이지 번호가 표시되지 않음

**증상**: @page 규칙이 동작하지 않음

**해결**:
- WeasyPrint는 CSS Paged Media 모듈을 지원합니다
- `@page { @bottom-center { content: counter(page); } }`
- 첫 페이지 제외: `@page :first { @bottom-center { content: none; } }`

## 성능 최적화

### PDF 생성 속도 개선
- 템플릿 캐싱 (Jinja2 Environment)
- 스타일시트 재사용
- 임시 파일 정리

### 파일 크기 최적화
- 이미지 압축 (필요 시)
- CSS 최소화
- 불필요한 스타일 제거

## 향후 개선 사항

### Phase 3 이후
- [ ] MonthlyContent 구조 정의 후 월간 템플릿 상세 구현
- [ ] 월간 캘린더 렌더링
- [ ] 주별 요약 레이아웃

### 추가 기능
- [ ] 연간 PDF 생성 (YearlyContent)
- [ ] 사용자 프로필 정보 포함 옵션
- [ ] 사용자 기록 (로그) 포함 옵션
- [ ] PDF 워터마크 추가
- [ ] 다크 모드 스타일

## 참고 문서

- [WeasyPrint 공식 문서](https://doc.courtbouillon.org/weasyprint/)
- [Jinja2 공식 문서](https://jinja.palletsprojects.com/)
- [CSS Paged Media Module](https://www.w3.org/TR/css-page-3/)
- [Backend API 문서](../backend/src/api/README.md)
- [DAILY_CONTENT_SCHEMA](../docs/content/DAILY_CONTENT_SCHEMA.json)

## 라이선스

R³ Diary System의 일부로 동일한 라이선스 적용
