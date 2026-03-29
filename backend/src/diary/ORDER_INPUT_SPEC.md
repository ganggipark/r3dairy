# 주문 입력 표준 사양 (Order Input Specification)

## 개요
주문형 인쇄 제작 파이프라인의 입력 형식 및 검증 규칙을 정의합니다.

## OrderInput 타입 정의

```typescript
interface OrderInput {
  customerName: string;      // 필수
  ownerLabel?: string;        // 선택 (기본값: customerName)
  productTitle?: string;      // 선택 (기본값: "라이프 리듬 다이어리")
  calendarType: CalendarType; // 필수: "solar" | "lunar"
  gender: Gender;            // 필수: "male" | "female"
  birth: {                   // 필수
    year: number;            // 필수 (1900-현재)
    month: number;           // 필수 (1-12)
    day: number;             // 필수 (1-31)
    hour?: number;           // 선택 (0-23)
    minute?: number;         // 선택 (0-59)
  };
  startDate: string;         // 필수 (YYYY-MM-DD 형식)
  durationType: DurationType; // 필수: "1m" | "3m" | "6m" | "1y"
  renderMode?: RenderMode;   // 선택: "standard" | "large" (기본값: "standard")
}
```

## 필드 설명

### 필수 필드

#### `customerName` (string)
- **설명**: 주문 고객의 이름
- **제약**: 공백 제거 후 1자 이상
- **예시**: "김다이어리", "이연구", "Park Diary"

#### `calendarType` (CalendarType)
- **설명**: 달력 유형 (향후 계산 엔진 확장 대비)
- **허용값**: `"solar"` (양력), `"lunar"` (음력)
- **현재**: 메타데이터로만 저장, 향후 음력 계산 시 활용

#### `gender` (Gender)
- **설명**: 성별 정보 (향후 맞춤 콘텐츠 생성 대비)
- **허용값**: `"male"` (남성), `"female"` (여성)
- **현재**: 메타데이터로만 저장, 향후 성별 맞춤 콘텐츠 활용

#### `birth` (객체)
- **설명**: 출생 정보
- **필수 속성**:
  - `year`: 출생 연도 (1900 ~ 현재 연도)
  - `month`: 출생 월 (1-12)
  - `day`: 출생 일 (1-31)
- **선택 속성**:
  - `hour`: 출생 시간 (0-23, 24시간제)
  - `minute`: 출생 분 (0-59)

#### `startDate` (string)
- **설명**: 다이어리 시작 날짜
- **형식**: `"YYYY-MM-DD"`
- **예시**: `"2026-04-01"`

#### `durationType` (DurationType)
- **설명**: 다이어리 기간
- **허용값**:
  - `"1m"`: 1개월
  - `"3m"`: 3개월
  - `"6m"`: 6개월
  - `"1y"`: 1년

### 선택 필드

#### `ownerLabel` (string)
- **설명**: 표지에 표시될 소유자명
- **기본값**: `customerName` 값 사용
- **예시**: "김다이어리님의 전용 다이어리"
- **표시 위치**: 표지 중앙 소유자 섹션

#### `productTitle` (string)
- **설명**: 표지 메인 타이틀
- **기본값**: `"라이프 리듬 다이어리"`
- **예시**: "라이프 리듬 다이어리 - 프리미엄 에디션"
- **표시 위치**: 표지 상단 메인 타이틀

#### `renderMode` (RenderMode)
- **설명**: 렌더링 모드
- **허용값**: `"standard"` (기본), `"large"` (큰 글씨)
- **기본값**: `"standard"`
- **large 모드 특징**:
  - 글꼴 크기 증가 (10pt → 12pt)
  - 여백 증가 (10mm → 15mm)
  - 라인 간격 증가 (1.3 → 1.5)

## 검증 규칙

### 1. 필수 필드 검증
- 모든 필수 필드가 존재해야 함
- `customerName`은 공백 제거 후 1자 이상

### 2. 날짜 형식 검증
- `startDate`는 `YYYY-MM-DD` 형식 준수
- 유효한 날짜여야 함 (예: 2026-02-30은 불가)

### 3. 출생 정보 검증
- `year`: 1900 ≤ year ≤ 현재 연도
- `month`: 1 ≤ month ≤ 12
- `day`: 1 ≤ day ≤ 31
- `hour`: 0 ≤ hour ≤ 23 (제공 시)
- `minute`: 0 ≤ minute ≤ 59 (제공 시)

### 4. 열거형 검증
- `calendarType`: "solar" 또는 "lunar"만 허용
- `gender`: "male" 또는 "female"만 허용
- `durationType`: "1m", "3m", "6m", "1y"만 허용
- `renderMode`: "standard" 또는 "large"만 허용

## 오류 메시지

### 필수 필드 누락
```
"고객명(customerName)이 필요합니다"
"출생 정보(birth)가 필요합니다"
"출생 년월일(birth.year/month/day)이 필요합니다"
"시작 날짜(startDate)가 필요합니다"
"기간 타입(durationType)이 필요합니다"
```

### 형식 오류
```
"startDate는 YYYY-MM-DD 형식이어야 합니다"
"유효하지 않은 시작 날짜입니다"
```

### 범위 오류
```
"출생 연도가 유효하지 않습니다 (1900-현재)"
"출생 월이 유효하지 않습니다 (1-12)"
"출생 일이 유효하지 않습니다 (1-31)"
"기간 타입은 1m, 3m, 6m, 1y 중 하나여야 합니다"
```

## 파일명 생성 규칙

생성되는 PDF 파일명 형식:
```
YYYYMMDD_고객명_기간_모드.pdf
```

예시:
- `20260401_김다이어리_1m_standard.pdf`
- `20260401_이연구_3m_large.pdf`

파일명 처리 규칙:
- 특수문자는 언더스코어(_)로 변환
- 공백은 언더스코어(_)로 변환
- 한글 이름 유지 (최대 20자)
- 연속 언더스코어는 단일 언더스코어로 변환

## API 사용 예시

```typescript
import { buildOrderDiary, OrderInput } from './orderDiaryBuilder';

const order: OrderInput = {
  customerName: '김다이어리',
  ownerLabel: '김다이어리님의 전용 다이어리',
  productTitle: '라이프 리듬 다이어리 - 프리미엄',
  calendarType: 'solar',
  gender: 'female',
  birth: {
    year: 1990,
    month: 5,
    day: 15,
    hour: 14,
    minute: 30
  },
  startDate: '2026-04-01',
  durationType: '1m',
  renderMode: 'standard'
};

const result = await buildOrderDiary(order);

if (result.success) {
  console.log('PDF 생성 완료:', result.files.pdfPath);
  console.log('총 페이지:', result.orderSummary.totalPages);
} else {
  console.error('생성 실패:', result.error);
}
```

## 성공 응답 구조

```typescript
interface OrderBuildResult {
  success: true;
  orderSummary: {
    customerName: string;
    startDate: string;
    endDate: string;
    durationType: DurationType;
    totalDays: number;
    totalPages: number;
  };
  files: {
    pdfPath: string;
    htmlPath?: string;
  };
  metadata: {
    generatedAt: string;
    renderMode: RenderMode;
    calendarType: CalendarType;
  };
}
```

## 실패 응답 구조

```typescript
interface OrderBuildResult {
  success: false;
  orderSummary: { ... };  // 부분 정보
  files: {};              // 빈 객체
  metadata: { ... };
  error: string;          // 오류 메시지
}
```