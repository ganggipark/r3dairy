# 사주 계산 패키지 (Saju Calculator)

한국 전통 사주명리학 계산 라이브러리입니다.

## 주요 기능

- **사주팔자 계산**: 년주, 월주, 일주, 시주 계산
- **진태양시 보정**: 지역별 경도 기준 시간 보정
- **절기 계산**: 2024-2030년 정확한 절기 데이터 (한국천문연구원 기준)
- **음양력 변환**: 양력 ↔ 음력 변환 (윤달 지원)
- **오행 분석**: 오행 균형 분석
- **십성 분석**: 비겁, 식상, 재성, 관성, 인성
- **대운/세운 계산**: 10년 단위 대운 및 연간 세운
- **격국/용신 분석**: 신강/신약 판단 및 용신 선정

## 설치

```bash
npm install saju-calculator
# 또는
yarn add saju-calculator
```

## 사용법

### 기본 사주 계산

```typescript
import { calculateFourPillars, formatFourPillars } from 'saju-calculator';

const result = calculateFourPillars({
  year: 1990,
  month: 5,
  day: 15,
  hour: 14,
  minute: 30,
  isLunar: false,
  gender: 'male'
});

console.log(formatFourPillars(result));
// "경오년 신사월 기유일 신미시"
```

### 완전한 사주 분석

```typescript
import { calculateCompleteSajuData } from 'saju-calculator';

const data = calculateCompleteSajuData({
  year: 1990,
  month: 5,
  day: 15,
  hour: 14,
  minute: 30,
  gender: 'male',
  isLunar: false,
  useTrueSolarTime: true,  // 진태양시 보정 적용
  birthPlace: '서울'
});

console.log(data.fourPillars);      // 사주 팔자
console.log(data.ohHaeng);          // 오행 분석
console.log(data.sipSung);          // 십성 분석
console.log(data.gyeokGuk);         // 격국 분석
console.log(data.yongSin);          // 용신/기신
console.log(data.daewoon);          // 대운
console.log(data.currentYearSewoon); // 올해 세운
console.log(data.personality);       // 성격/적성
```

### 음력 변환

```typescript
import { lunarToSolar, solarToLunar } from 'saju-calculator';

// 음력 → 양력
const solarDate = lunarToSolar(1990, 4, 15, false); // 윤달 아님
console.log(solarDate); // Date 객체

// 양력 → 음력
const lunarDate = solarToLunar(new Date(1990, 4, 15));
console.log(lunarDate); // { year, month, day, isLeapMonth }
```

### 진태양시 보정

```typescript
import { applyTrueSolarTimeByCity, getTrueSolarTimeDescription } from 'saju-calculator';

// 서울 기준 진태양시 계산
const result = applyTrueSolarTimeByCity(14, 30, '서울');
console.log(result.adjustedHour);      // 13
console.log(result.adjustedMinute);    // 58
console.log(result.correctionMinutes); // -32.088

// 설명 텍스트
console.log(getTrueSolarTimeDescription('서울'));
// "서울(경도 126.98°)은 한국 표준시보다 약 32분 느립니다."
```

### 절기 계산

```typescript
import { getExactSolarMonth, getSolarTermByDate } from 'saju-calculator';

// 정확한 절기월 계산
const solarMonth = getExactSolarMonth(2026, 2, 4, 6, 0);
console.log(solarMonth); // 1 (인월)

// 특정 날짜의 절기 확인
const term = getSolarTermByDate(2026, 2, 4);
console.log(term?.term); // "입춘"
```

## 파일 구조

```
saju-calculator-package/
├── src/
│   ├── index.ts                  # 메인 Export
│   ├── types.ts                  # 타입 정의
│   ├── sajuCalculator.ts         # 기본 사주 계산
│   ├── completeSajuCalculator.ts # 완전한 사주 분석
│   ├── lunarCalendar.ts          # 음양력 변환
│   ├── trueSolarTimeCalculator.ts # 진태양시 계산
│   └── solarTermsCalculator.ts   # 절기 계산
├── package.json
├── tsconfig.json
└── README.md
```

## 검증 예시

```
1968년 1월 24일 19:00 양력 서울
→ 계산 결과: 정미 계축 계사 신유 ✅ 만세력 일치!
```

## 의존성

- `korean-lunar-calendar`: 음양력 변환

## 라이선스

MIT License

## 기여

버그 리포트 및 기능 제안은 GitHub Issues에 등록해주세요.
