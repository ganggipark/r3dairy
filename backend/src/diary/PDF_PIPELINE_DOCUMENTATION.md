# PDF Generation Pipeline Documentation

## 개요
이 문서는 다이어리 시스템의 공식 PDF 변환 파이프라인을 설명합니다.

## 선택된 솔루션: Python + ReportLab

### 선택 이유
1. **Pure Python**: 외부 라이브러리 의존성 없음 (GTK, wkhtmltopdf 등 불필요)
2. **크로스 플랫폼**: Windows, Linux, Mac 모두 지원
3. **안정성**: 상용 수준의 PDF 생성 라이브러리
4. **한글 지원**: 유니코드 완벽 지원

### 기각된 대안
- **WeasyPrint**: GTK 라이브러리 필요 (Windows에서 설치 복잡)
- **Puppeteer**: Node.js 의존성, 큰 용량
- **wkhtmltopdf**: 별도 바이너리 설치 필요

## 아키텍처

```
TypeScript (데이터 생성)
    ↓
JSON 파일 저장
    ↓
Python ReportLab (PDF 변환)
    ↓
PDF 파일 출력
```

## 주요 컴포넌트

### 1. TypeScript 렌더러
- **파일**: `periodDiaryPdfRenderer.ts`, `dailyDiaryPdfRenderer.ts`
- **역할**: 
  - 다이어리 데이터 구조화
  - HTML 템플릿 생성 (백업용)
  - JSON 데이터 저장
  - Python converter 호출

### 2. Python PDF Converter
- **파일**: `simplePdfConverter.py`
- **역할**:
  - JSON 데이터 읽기
  - ReportLab으로 PDF 생성
  - 커맨드라인 인터페이스 제공

## 설치 방법

### 필수 의존성
```bash
# Python 패키지 설치
pip install reportlab

# TypeScript 의존성 (이미 설치됨)
npm install
```

## 사용 방법

### 1. 일간 다이어리 PDF 생성

#### TypeScript에서:
```typescript
import { buildDailyDiaryPayload } from './dailyDiaryBuilder';
import { DailyDiaryPdfRenderer } from './dailyDiaryPdfRenderer';

// 데이터 생성
const payload = await buildDailyDiaryPayload({
  date: '2026-03-28',
  birth: { year: 1971, month: 11, day: 17, hour: 4 }
});

// PDF 생성
const renderer = new DailyDiaryPdfRenderer();
const result = await renderer.renderPdf({ payload });
console.log(`PDF 생성: ${result.outputPath}`);
```

#### Python 직접 실행:
```bash
# 일간 PDF 생성
python simplePdfConverter.py --convert-daily test_daily.json --output daily.pdf
```

### 2. 기간별 다이어리 PDF 생성

#### TypeScript에서:
```typescript
import { buildPeriodDiary } from './periodDiaryGenerator';
import { renderPeriodDiaryPdf } from './periodDiaryPdfRenderer';

// 기간 데이터 생성
const period = await buildPeriodDiary({
  startDate: '2026-03-01',
  durationType: '1m',
  birth: { year: 1971, month: 11, day: 17, hour: 4 }
});

// PDF 생성
const result = await renderPeriodDiaryPdf({ period });
console.log(`PDF 생성: ${result.outputPath}, 페이지 수: ${result.pageCount}`);
```

#### Python 직접 실행:
```bash
# 기간 PDF 생성
python simplePdfConverter.py --convert-period test_period.json --output period.pdf
```

## 파일 구조

```
backend/src/diary/
├── periodDiaryGenerator.ts      # 기간 데이터 생성
├── periodDiaryPdfRenderer.ts    # 기간 PDF 렌더러
├── dailyDiaryBuilder.ts         # 일간 데이터 생성
├── dailyDiaryPdfRenderer.ts     # 일간 PDF 렌더러
├── simplePdfConverter.py        # Python PDF 변환기
├── types.ts                     # 타입 정의
└── test_output/                 # 테스트 출력 디렉토리
    ├── *.json                   # JSON 데이터
    ├── *.html                   # HTML 백업
    └── *.pdf                    # 생성된 PDF
```

## 테스트

### 통합 테스트 실행
```bash
# TypeScript 테스트 (PDF 생성 포함)
cd backend/src/diary
npx ts-node test_periodDiaryPdfRenderer.ts

# Python 단독 테스트
python simplePdfConverter.py
```

### 생성된 파일 확인
```bash
# PDF 파일 목록
ls test_output/*.pdf

# 파일 크기 확인
ls -lh test_output/*.pdf
```

## PDF 내용 구조

### 일간 PDF
- 날짜 헤더
- 요약
- 키워드
- 리듬 해설
- 집중/주의 포인트
- 행동 가이드
- 시간/방향
- 오늘의 질문

### 기간 PDF
- **표지**: 제목, 기간, 총 일수
- **일간 페이지**: 각 날짜별 다이어리
- **페이지 구분**: 자동 페이지 나눔

## 성능

### 예상 처리 시간
- 1개월 (31일): ~3초
- 3개월 (91일): ~9초
- 6개월 (183일): ~18초
- 1년 (365일): ~37초

### 파일 크기
- 일간 PDF: ~3KB
- 1개월 PDF: ~15KB
- 1년 PDF: ~180KB

## 트러블슈팅

### 문제: Python not found
```bash
# Python 설치 확인
python --version

# Python 경로 확인
which python
```

### 문제: reportlab not installed
```bash
# reportlab 설치
pip install reportlab
```

### 문제: 한글 깨짐
- UTF-8 인코딩 확인
- JSON 파일 저장 시 `ensure_ascii=False` 사용

## 향후 개선사항

1. **폰트 지원**: 사용자 정의 한글 폰트 추가
2. **템플릿 시스템**: 다양한 디자인 템플릿 지원
3. **배치 처리**: 여러 사용자의 PDF 동시 생성
4. **이미지 지원**: 차트, 그래프 삽입
5. **암호화**: PDF 암호 보호 기능

## 유지보수

### 로그 확인
```bash
# TypeScript 로그
grep "PeriodDiaryPdfRenderer" *.log

# Python 에러 로그
python simplePdfConverter.py 2> error.log
```

### 버전 업데이트
```bash
# ReportLab 업데이트
pip install --upgrade reportlab

# 버전 확인
pip show reportlab
```

## 연락처
문제 발생 시 이슈를 생성하거나 담당자에게 연락하세요.

---

마지막 업데이트: 2026-03-28
문서 버전: 1.0.0