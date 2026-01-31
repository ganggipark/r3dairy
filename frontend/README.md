# R³ 다이어리 Frontend

Next.js 14 (App Router) 기반 프론트엔드 애플리케이션

## 기술 스택

- **프레임워크**: Next.js 14+ (App Router)
- **언어**: TypeScript
- **스타일링**: Tailwind CSS
- **UI 컴포넌트**: shadcn/ui (예정)
- **인증**: Supabase Auth
- **상태 관리**: React Hooks (Context API 또는 Zustand 예정)

## 프로젝트 구조

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── (auth)/            # 인증 라우트 그룹
│   │   │   ├── login/         # 로그인 페이지
│   │   │   └── signup/        # 회원가입 페이지
│   │   ├── profile/           # 프로필 생성/수정
│   │   ├── today/             # 오늘 페이지 (좌/우 레이아웃)
│   │   ├── month/             # 월간 콘텐츠
│   │   ├── year/              # 연간 콘텐츠
│   │   ├── layout.tsx         # 루트 레이아웃
│   │   └── page.tsx           # 홈 페이지
│   ├── components/            # 재사용 가능한 컴포넌트
│   │   └── ui/               # shadcn/ui 컴포넌트 (예정)
│   ├── lib/                   # 유틸리티 및 클라이언트
│   │   ├── api.ts            # Backend API 클라이언트
│   │   ├── supabase.ts       # Supabase 클라이언트
│   │   └── utils.ts          # 헬퍼 함수
│   ├── types/                # TypeScript 타입 정의
│   │   └── index.ts          # 전역 타입
│   └── styles/               # 글로벌 스타일
├── public/                    # 정적 파일
├── package.json
├── tsconfig.json
├── tailwind.config.ts
└── next.config.js
```

## 설치 및 실행

### 1. 의존성 설치

```bash
cd frontend
npm install
```

### 2. 환경 변수 설정

`.env.local` 파일을 생성하고 다음 환경 변수를 설정하세요:

```env
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# Supabase
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
```

### 3. 개발 서버 실행

```bash
npm run dev
```

브라우저에서 http://localhost:5000 을 열어 애플리케이션을 확인하세요.

### 4. 프로덕션 빌드

```bash
npm run build
npm start
```

## 주요 페이지

### 인증 페이지

#### 로그인 (`/login`)
- 이메일/비밀번호 로그인
- JWT 토큰 localStorage 저장
- 로그인 성공 시 `/profile`로 이동

#### 회원가입 (`/signup`)
- 이름, 이메일, 비밀번호 입력
- 클라이언트 사이드 폼 검증
  - 이메일 형식 검증
  - 비밀번호 최소 8자
  - 비밀번호 확인 일치
- 회원가입 성공 시 `/profile`로 이동

### 프로필 페이지 (`/profile`)

**신규 사용자**: 프로필 생성 폼
**기존 사용자**: 프로필 수정 폼

입력 필드:
- 이름 *
- 생년월일 * (날짜 선택)
- 출생 시간 * (시간 선택)
- 성별 * (남성/여성)
- 출생 장소 * (텍스트)
- 역할 선택 * (다중 선택)
  - 학생
  - 직장인
  - 프리랜서
- 선호 사항 (선택사항)

저장 후 `/today`로 이동

### 오늘 페이지 (`/today`)

**좌우 레이아웃**:

**좌측 - 오늘의 안내** (Content Display):
1. 요약
2. 키워드 (태그)
3. 리듬 해설
4. 집중/주의 포인트
5. 행동 가이드 (권장/지양)
6. 시간/방향
7. 상태 전환 트리거
8. 의미 전환
9. 리듬 질문

**우측 - 오늘의 기록** (User Log):
- 오늘의 일정 (텍스트)
- 기분 (1-5 슬라이더)
- 에너지 (1-5 슬라이더)
- 메모 (텍스트)
- 감사한 일 (텍스트)
- 저장 버튼

**역할 선택 기능**:
- 사용자가 프로필에서 설정한 역할이 2개 이상인 경우 헤더에 역할 선택 버튼 표시
- 역할 선택 시 좌측 콘텐츠 표현이 변경됨 (API 호출)

### 월간 페이지 (`/month`)
- 현재 년/월의 월간 콘텐츠 표시
- 역할 선택 기능
- TODO: MonthlyContent 타입 정의 후 UI 구현

### 연간 페이지 (`/year`)
- 현재 년도의 연간 콘텐츠 표시
- 역할 선택 기능
- TODO: YearlyContent 타입 정의 후 UI 구현

## API 클라이언트 (`src/lib/api.ts`)

Backend API와 통신하기 위한 클라이언트

### 인증 API

```typescript
api.auth.signUp(data: SignUpRequest): Promise<AuthResponse>
api.auth.login(data: LoginRequest): Promise<AuthResponse>
api.auth.logout(token: string): Promise<SuccessResponse>
api.auth.refreshToken(refreshToken: string): Promise<AuthResponse>
```

### 프로필 API

```typescript
api.profile.create(token: string, data: ProfileCreate): Promise<Profile>
api.profile.get(token: string): Promise<Profile>
api.profile.update(token: string, data: ProfileUpdate): Promise<Profile>
api.profile.delete(token: string): Promise<SuccessResponse>
```

### 일간 콘텐츠 API

```typescript
api.daily.getContent(token: string, date: string, role?: Role): Promise<DailyContentResponse>
api.daily.getContentRange(token: string, startDate: string, endDate: string, role?: Role): Promise<DailyContentResponse[]>
```

### 월간/연간 콘텐츠 API

```typescript
api.content.getMonthly(token: string, year: number, month: number, role?: Role): Promise<MonthlyContentResponse>
api.content.getYearly(token: string, year: number, role?: Role): Promise<YearlyContentResponse>
```

### 기록 API

```typescript
api.logs.create(token: string, date: string, data: DailyLogCreate): Promise<DailyLog>
api.logs.get(token: string, date: string): Promise<DailyLog>
api.logs.update(token: string, date: string, data: DailyLogUpdate): Promise<DailyLog>
api.logs.delete(token: string, date: string): Promise<SuccessResponse>
```

## 타입 정의 (`src/types/index.ts`)

Backend의 Pydantic 모델과 동일한 TypeScript 타입:

- `Gender`, `Role` (Enums)
- `AuthResponse`, `SignUpRequest`, `LoginRequest`
- `Profile`, `ProfileCreate`, `ProfileUpdate`
- `DailyContent`, `DailyContentResponse`
- `DailyLog`, `DailyLogCreate`, `DailyLogUpdate`
- `MonthlyContentResponse`, `YearlyContentResponse`

## 인증 흐름

1. 사용자 회원가입 또는 로그인
2. JWT 토큰 (access_token, refresh_token)을 localStorage에 저장
3. API 요청 시 `Authorization: Bearer {access_token}` 헤더 포함
4. 토큰 만료 시 refresh_token으로 갱신
5. 로그아웃 시 localStorage에서 토큰 제거

## Supabase 통합

`src/lib/supabase.ts`:
- Supabase 클라이언트 싱글톤 인스턴스
- `getSession()` - 현재 세션 가져오기
- `getUser()` - 현재 사용자 정보 가져오기
- `signOut()` - 로그아웃

## 반응형 디자인

Tailwind CSS 브레이크포인트:
- `sm:` - 640px+
- `md:` - 768px+
- `lg:` - 1024px+
- `xl:` - 1280px+

오늘 페이지는 `lg:` 이상에서 좌우 2열 레이아웃, 그 이하는 1열 스택 레이아웃

## 개발 가이드라인

### 컴포넌트 작성
- Client Component: `'use client'` 지시어 사용
- Server Component: 기본값, 데이터 페칭에 유리
- 상태 관리가 필요한 경우 Client Component 사용

### 스타일링
- Tailwind CSS 유틸리티 클래스 우선 사용
- 복잡한 스타일은 컴포넌트 레벨 CSS 모듈 고려

### 에러 처리
- API 호출 시 try-catch 사용
- 사용자에게 친화적인 에러 메시지 표시
- 필요 시 로그인 페이지로 리다이렉트

### 타입 안전성
- 모든 API 응답에 대한 타입 정의
- `any` 타입 사용 최소화
- Props 인터페이스 명시

## 다음 단계

### Phase 6 완료 후 추가할 기능
- [ ] shadcn/ui 컴포넌트 통합
- [ ] 전역 상태 관리 (Context API 또는 Zustand)
- [ ] 로딩 스피너 컴포넌트
- [ ] 에러 바운더리
- [ ] 토스트 알림
- [ ] 다크 모드 (선택사항)

### Phase 7: PDF Generator 연동
- [ ] PDF 다운로드 버튼 추가 (오늘/월간 페이지)
- [ ] PDF 생성 API 호출
- [ ] 다운로드 진행 상태 표시

### Phase 8: QA & 최적화
- [ ] E2E 테스트 (Playwright)
- [ ] 접근성 (a11y) 개선
- [ ] 성능 최적화 (이미지, 번들 크기)
- [ ] SEO 최적화

## 문제 해결

### 환경 변수가 인식되지 않음
- `.env.local` 파일이 `frontend/` 루트에 있는지 확인
- 환경 변수는 `NEXT_PUBLIC_` 접두사 필요 (클라이언트 사이드)
- 서버 재시작 필요

### API 호출 실패
- Backend 서버가 실행 중인지 확인
- `NEXT_PUBLIC_API_URL`이 올바른지 확인
- CORS 설정 확인 (Backend에서 허용)

### Supabase 연결 실패
- Supabase 프로젝트 설정 확인
- URL과 Anon Key가 정확한지 확인

## 참고 문서

- [Next.js 공식 문서](https://nextjs.org/docs)
- [Tailwind CSS 공식 문서](https://tailwindcss.com/docs)
- [Supabase 공식 문서](https://supabase.com/docs)
- [TypeScript 공식 문서](https://www.typescriptlang.org/docs)
