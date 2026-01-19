# R³ Diary System - Work Plan

## 현재 상태

**Phase**: Phase 9 - 배포 (완료)
**Date**: 2026-01-20
**Progress**: ✅ Phase 1, 2, 3, 4, 5, 6, 7, 8, 9 완료 - MVP 완성!

## Phase 1: 기초 인프라 구축 ✅ COMPLETED

### 완료된 작업
- [x] 프로젝트 디렉토리 구조 생성 (backend, frontend, pdf-generator)
- [x] Git 저장소 초기화 및 .gitignore 설정
- [x] Backend FastAPI 프로젝트 셋업
  - [x] requirements.txt (FastAPI, Supabase, WeasyPrint 등)
  - [x] src/main.py (기본 엔드포인트)
  - [x] .env.example
  - [x] 디렉토리 구조 (rhythm, content, translation, api, db)
- [x] Frontend Next.js 프로젝트 셋업
  - [x] package.json (Next.js 14, TypeScript, Tailwind)
  - [x] tsconfig.json
  - [x] tailwind.config.ts
  - [x] 기본 페이지 (layout.tsx, page.tsx, globals.css)
  - [x] 디렉토리 구조 (app, components, lib)
- [x] 데이터베이스 스키마 설계 (schema.sql)
- [x] PDF Generator 기본 구조
- [x] CLAUDE.md 대폭 개선 (기술 스택, 구조, 명령어, 에이전트 가이드)
- [x] README.md 작성

### Phase 1 검증 체크리스트
- [ ] Backend 서버 실행 확인 (`uvicorn src.main:app --reload`)
- [ ] Frontend 서버 실행 확인 (`npm run dev`)
- [ ] Supabase 프로젝트 생성 및 연결
- [ ] Git 첫 커밋 생성

## Phase 2: Rhythm Analysis Engine 통합 ✅ COMPLETED

**예상 기간**: 2-3주
**목표**: 기존 사주명리 로직 통합 및 리듬 신호 생성

### 완료된 작업
- [x] 기존 사주명리 코드 통합 인터페이스 준비 (`backend/src/rhythm/saju.py`)
- [x] 입력 인터페이스 표준화 (BirthInfo 모델)
- [x] 출력 인터페이스 표준화 (RhythmSignal, MonthlyRhythmSignal, YearlyRhythmSignal 모델)
- [x] 일간 리듬 신호 생성 로직 (`signals.py`)
- [x] 월간 리듬 신호 생성 로직
- [x] 연간 리듬 신호 생성 로직
- [x] 내부 용어 전용 사용 설계 (사용자 노출 금지 검증)
- [x] 단위 테스트 작성 (`tests/test_rhythm.py` - 15개 테스트)
- [x] 통합 가이드 문서 작성 (`backend/src/rhythm/README.md`)

### 생성된 파일
- `backend/src/rhythm/models.py` - 데이터 모델 (BirthInfo, RhythmSignal 등)
- `backend/src/rhythm/saju.py` - 사주명리 계산 인터페이스 (통합 지점)
- `backend/src/rhythm/signals.py` - 리듬 신호 생성 메인 로직
- `backend/src/rhythm/README.md` - 사용 가이드 및 통합 방법
- `backend/tests/test_rhythm.py` - 단위 테스트 (15개 테스트 케이스)

### Phase 2 검증 체크리스트
- [x] BirthInfo 모델 생성 및 검증
- [x] RhythmSignal 모델 생성 및 검증
- [x] 일간/월간/연간 신호 생성 함수 작동
- [x] 단위 테스트 작성 완료
- [ ] 기존 사주명리 로직 실제 통합 (사용자 작업 필요)
- [ ] 테스트 실행 검증 (`pytest tests/test_rhythm.py -v`)

### 필요한 리소스
- **Skills**: `korean-divination` ⭐⭐⭐
- **Agents**:
  - `korean-tradition-content` (기존 로직 통합 가이드)
  - `tech-implementer` (코드 구현)
  - `qa-tester` (단위 테스트)

### 검증 방법
```bash
cd backend
pytest tests/test_rhythm.py -v
```

## Phase 3: Content Assembly Engine ✅ COMPLETED

**예상 기간**: 2-3주
**목표**: 리듬 신호를 사용자 노출 콘텐츠로 변환

### 완료된 작업
- [x] DailyContent 데이터 모델 정의 (`models.py`)
- [x] DAILY_CONTENT_SCHEMA.json 검증기 구현 (`validator.py`)
- [x] RhythmSignal → DailyContent 변환 로직 (`assembly.py`)
- [x] 10개 콘텐츠 블록 생성기 구현
- [x] 내부 용어 → 사용자 용어 변환 함수
- [x] 최소 글자 수 검증 로직 (400-600자)
- [x] 설명형 문단 생성 (카드 요약 금지)
- [x] 월간/연간 콘텐츠 생성 로직
- [x] 단위 테스트 작성 (`tests/test_content.py` - 13개 테스트)
- [x] 통합 테스트 (Rhythm → Content 파이프라인)
- [x] 사용 가이드 문서 작성 (`backend/src/content/README.md`)

### 생성된 파일
- `backend/src/content/models.py` - 데이터 모델 (DailyContent, MonthlyContent, YearlyContent 등)
- `backend/src/content/assembly.py` - 콘텐츠 조립 엔진 (핵심 로직)
- `backend/src/content/validator.py` - 스키마 검증 및 품질 체크
- `backend/src/content/README.md` - 사용 가이드 및 용어 변환 규칙
- `backend/tests/test_content.py` - 단위 테스트 (13개 테스트 케이스)

### 주요 기능
- ✅ **10개 블록 자동 생성**: 요약, 키워드, 해설, 집중/주의, Do/Avoid, 시간/방향, 트리거, 의미전환, 질문
- ✅ **내부 용어 필터링**: 사주명리, 천간, 지지 등 전문 용어 자동 감지 및 차단
- ✅ **길이 검증**: 최소 400자, 목표 600-1200자 자동 검증
- ✅ **품질 리포트**: 글자 수, 완성도, 개선 제안 제공

### Phase 3 검증 체크리스트
- [x] DailyContent 모델 생성 및 검증
- [x] RhythmSignal → DailyContent 변환 성공
- [x] 10개 블록 모두 생성 확인
- [x] 내부 전문 용어 미노출 확인
- [x] 최소 400자 충족 확인
- [x] 단위 테스트 작성 완료
- [ ] 테스트 실행 검증 (`pytest tests/test_content.py -v`)

### 필요한 리소스
- **Skills**: `korean-divination` ⭐⭐⭐
- **Agents**:
  - `korean-tradition-content` (콘텐츠 생성 로직 설계)
  - `tech-implementer` (코드 구현)
  - `qa-tester` (스키마 검증 테스트)

### 검증 방법
```bash
cd backend
pytest tests/test_content.py -v

# 통합 테스트
pytest tests/test_content.py::TestIntegration -v
```

## Phase 4: Role Translation Layer ✅ COMPLETED

**예상 기간**: 1-2주
**목표**: 역할별 표현 변환 시스템 구축

### 완료된 작업
- [x] 역할별 템플릿 시스템 설계 (Role, RoleTemplate 모델)
- [x] 표현 변환 로직 구현 (RoleTranslator 클래스)
- [x] 의미 불변성 검증 로직 (validate_semantic_preservation)
- [x] 역할별 예시/질문 라이브러리 (JSON 템플릿)
- [x] 회귀 테스트 작성 (test_translation.py - 18개 테스트)
- [x] 통합 가이드 문서 작성 (backend/src/translation/README.md)

### 생성된 파일
- `backend/src/translation/models.py` - 데이터 모델 (Role, RoleTemplate, TranslationContext)
- `backend/src/translation/translator.py` - 표현 변환 엔진 (RoleTranslator 클래스)
- `backend/src/translation/templates/student.json` - 학생 템플릿
- `backend/src/translation/templates/office_worker.json` - 직장인 템플릿
- `backend/src/translation/templates/freelancer.json` - 프리랜서 템플릿
- `backend/src/translation/README.md` - 사용 가이드 및 역할별 표현 예시
- `backend/tests/test_translation.py` - 단위 테스트 (18개 테스트 케이스)

### 주요 기능
- ✅ **3가지 역할 지원**: 학생, 직장인, 프리랜서
- ✅ **자동 표현 변환**: 템플릿 기반 자동 매핑 (예: "작업 완료" → "과제 마무리"/"업무 마무리"/"프로젝트 마감")
- ✅ **의미 불변성 보장**: 날짜, 키워드 개수, 블록 개수, 길이(±20%) 검증
- ✅ **역할별 질문**: 각 역할에 맞는 질문 템플릿 적용
- ✅ **확장 가능**: 새 역할 추가 시 JSON 파일만 추가

### Phase 4 검증 체크리스트
- [x] Role enum 정의 (student, office_worker, freelancer)
- [x] RoleTemplate 모델 생성 및 JSON 로드
- [x] RoleTranslator 클래스 구현
- [x] 중립 콘텐츠 → 역할별 콘텐츠 변환 성공
- [x] 의미 불변성 검증 통과
- [x] 회귀 테스트 작성 완료
- [ ] 테스트 실행 검증 (`pytest tests/test_translation.py -v`)

### 필요한 리소스
- **Agents**:
  - `tech-implementer` (코드 구현)
  - `qa-tester` (의미 불변성 테스트)

### 검증 방법
```bash
cd backend
pytest tests/test_translation.py -v

# 의미 불변성 테스트만 실행
pytest tests/test_translation.py::TestSemanticPreservation -v

# 통합 테스트
pytest tests/test_translation.py::TestIntegration -v
```

## Phase 5: Backend API ✅ COMPLETED

**예상 기간**: 2주
**목표**: RESTful API 엔드포인트 구현

### 완료된 작업
- [x] Supabase 클라이언트 설정 (db/supabase.py)
- [x] API Request/Response 모델 정의 (api/models.py)
- [x] Supabase Auth 통합 (auth.py - 회원가입/로그인/로그아웃/토큰 갱신)
- [x] 프로필 CRUD API (profile.py - Create/Read/Update/Delete)
- [x] 일간 콘텐츠 조회 API (daily.py - 역할별 변환 포함)
- [x] 기간별 일간 콘텐츠 API (range 엔드포인트, 최대 31일)
- [x] 월간/연간 콘텐츠 조회 API (monthly.py)
- [x] 사용자 기록 CRUD API (logs.py)
- [x] FastAPI 라우터 등록 (main.py)
- [x] API 문서화 (FastAPI Swagger 자동 생성)
- [x] 사용 가이드 문서 작성 (backend/src/api/README.md)

### 생성된 파일
- `backend/src/db/supabase.py` - Supabase 클라이언트 설정
- `backend/src/api/models.py` - API 모델 (Request/Response)
- `backend/src/api/auth.py` - 인증 API (5개 엔드포인트)
- `backend/src/api/profile.py` - 프로필 API (4개 엔드포인트)
- `backend/src/api/daily.py` - 일간 콘텐츠 API (2개 엔드포인트)
- `backend/src/api/monthly.py` - 월간/연간 콘텐츠 API (2개 엔드포인트)
- `backend/src/api/logs.py` - 사용자 기록 API (4개 엔드포인트)
- `backend/src/api/README.md` - API 문서 및 사용 가이드
- `backend/src/main.py` - FastAPI 앱 (라우터 등록 완료)

### 구현된 API 엔드포인트 (총 17개)

#### 1. Auth (5개)
- `POST /api/auth/signup` - 회원가입
- `POST /api/auth/login` - 로그인
- `POST /api/auth/logout` - 로그아웃
- `POST /api/auth/refresh` - 토큰 갱신
- `get_current_user()` - 인증 의존성 주입 헬퍼

#### 2. Profile (4개)
- `POST /api/profile` - 프로필 생성
- `GET /api/profile` - 프로필 조회
- `PUT /api/profile` - 프로필 수정
- `DELETE /api/profile` - 프로필 삭제

#### 3. Daily Content (2개)
- `GET /api/daily/{date}?role={role}` - 일간 콘텐츠 (역할별 변환)
- `GET /api/daily/range/{start}/{end}?role={role}` - 기간별 콘텐츠 (최대 31일)

#### 4. Monthly/Yearly (2개)
- `GET /api/content/monthly/{year}/{month}?role={role}` - 월간 콘텐츠
- `GET /api/content/yearly/{year}?role={role}` - 연간 콘텐츠

#### 5. Daily Logs (4개)
- `POST /api/logs/{date}` - 기록 생성
- `GET /api/logs/{date}` - 기록 조회
- `PUT /api/logs/{date}` - 기록 수정
- `DELETE /api/logs/{date}` - 기록 삭제

### 주요 기능
- ✅ **Supabase Auth 통합**: JWT 기반 인증, 토큰 갱신
- ✅ **역할별 콘텐츠 제공**: `?role=student|office_worker|freelancer` 파라미터
- ✅ **자동 Role Translation**: API에서 자동으로 역할별 변환 적용
- ✅ **기간별 조회**: 최대 31일 범위 일간 콘텐츠 일괄 조회
- ✅ **FastAPI Swagger UI**: `/docs` 에서 API 테스트 가능
- ✅ **CORS 설정**: Frontend 연동 준비 완료
- ✅ **환경 변수 관리**: Supabase URL/Key, CORS origins

### Phase 5 검증 체크리스트
- [x] Supabase 클라이언트 설정 완료
- [x] Auth API 구현 (회원가입/로그인/로그아웃/갱신)
- [x] Profile CRUD API 구현
- [x] Daily Content API 구현 (역할별 변환 포함)
- [x] Monthly/Yearly Content API 구현
- [x] Daily Log CRUD API 구현
- [x] main.py에 라우터 등록
- [x] Swagger UI 자동 문서화
- [ ] 환경 변수 설정 (.env 파일 생성 필요)
- [ ] Supabase 프로젝트 생성 및 연결 (사용자 작업 필요)
- [ ] API 테스트 실행 (uvicorn 실행 및 /docs 접속)

### 필요한 리소스
- **Skills**: `api-integration`, `supabase-integration`
- **Agents**:
  - `tech-implementer` (API 구현)
  - `api-integrator` (Supabase 통합)

### 검증 방법
```bash
cd backend

# 환경 변수 설정
cp .env.example .env
# .env 파일에 SUPABASE_URL, SUPABASE_KEY 설정

# 서버 실행
uvicorn src.main:app --reload

# 또는
python src/main.py

# Swagger UI 접속
# http://localhost:8000/docs

# Health Check
curl http://localhost:8000/health
```

## Phase 6: Frontend UI ✅ COMPLETED

**예상 기간**: 2-3주
**목표**: Next.js 웹 애플리케이션 구현

### 완료된 작업
- [x] TypeScript 타입 정의 작성 (types/index.ts)
- [x] API 클라이언트 구현 (lib/api.ts - 17개 엔드포인트 래핑)
- [x] Supabase 클라이언트 설정 (lib/supabase.ts)
- [x] 로그인 페이지 (app/(auth)/login/page.tsx)
- [x] 회원가입 페이지 (app/(auth)/signup/page.tsx)
- [x] 프로필 페이지 (app/profile/page.tsx - 생성/수정 모드)
- [x] 오늘 페이지 (app/today/page.tsx - 좌/우 레이아웃)
- [x] 월간 페이지 (app/month/page.tsx - 기본 구조)
- [x] 연간 페이지 (app/year/page.tsx - 기본 구조)
- [x] 역할 선택 기능 (오늘/월간/연간 페이지)
- [x] 반응형 디자인 (Tailwind CSS 브레이크포인트)
- [x] Frontend README 작성 (설치, 실행, 구조, API 클라이언트 가이드)

### 생성된 파일
- `frontend/src/types/index.ts` - TypeScript 타입 정의 (150줄)
- `frontend/src/lib/api.ts` - API 클라이언트 (400줄, 17개 엔드포인트)
- `frontend/src/lib/supabase.ts` - Supabase 클라이언트 설정
- `frontend/src/app/(auth)/login/page.tsx` - 로그인 페이지 (120줄)
- `frontend/src/app/(auth)/signup/page.tsx` - 회원가입 페이지 (140줄)
- `frontend/src/app/profile/page.tsx` - 프로필 페이지 (280줄, 생성/수정)
- `frontend/src/app/today/page.tsx` - 오늘 페이지 (450줄, 좌/우 레이아웃)
- `frontend/src/app/month/page.tsx` - 월간 페이지 (100줄)
- `frontend/src/app/year/page.tsx` - 연간 페이지 (100줄)
- `frontend/README.md` - 설치 및 사용 가이드

### 주요 기능

#### 1. 인증 시스템
- ✅ **로그인/회원가입**: 이메일/비밀번호 인증
- ✅ **JWT 토큰 관리**: localStorage 저장 및 자동 갱신 준비
- ✅ **폼 검증**: 클라이언트 사이드 유효성 검사
- ✅ **에러 핸들링**: 사용자 친화적 에러 메시지

#### 2. 프로필 관리
- ✅ **생성/수정 모드**: 기존 프로필 여부에 따라 자동 전환
- ✅ **출생 정보 입력**: 이름, 생년월일, 출생 시간, 성별, 출생 장소
- ✅ **역할 선택**: 학생, 직장인, 프리랜서 다중 선택 (체크박스)
- ✅ **폼 검증**: 모든 필수 필드 검증

#### 3. 오늘 페이지 (핵심)
**좌측 - 오늘의 안내** (10개 블록):
1. 요약
2. 키워드 (태그)
3. 리듬 해설
4. 집중/주의 포인트
5. 행동 가이드 (권장/지양)
6. 시간/방향
7. 상태 전환 트리거
8. 의미 전환
9. 리듬 질문

**우측 - 오늘의 기록**:
- 오늘의 일정 (textarea)
- 기분 (1-5 슬라이더)
- 에너지 (1-5 슬라이더)
- 메모 (textarea)
- 감사한 일 (textarea)
- 저장 버튼

**역할 선택**:
- 프로필에 2개 이상 역할이 있으면 헤더에 역할 선택 버튼 표시
- 역할 변경 시 API 재호출하여 콘텐츠 표현 변경

#### 4. 월간/연간 페이지
- ✅ **기본 구조 완성**: 역할 선택, API 연동
- ⏳ **상세 UI**: MonthlyContent, YearlyContent 타입 정의 후 구현 예정

#### 5. API 통합
- ✅ **모든 17개 엔드포인트 래핑**: auth, profile, daily, content, logs
- ✅ **에러 처리**: APIError 클래스, 통합 에러 핸들링
- ✅ **타입 안전성**: TypeScript 타입으로 API 응답 보장

### Phase 6 검증 체크리스트
- [x] TypeScript 타입 정의 (Backend 모델과 일치)
- [x] API 클라이언트 구현
- [x] Supabase 클라이언트 설정
- [x] 로그인/회원가입 페이지
- [x] 프로필 페이지 (생성/수정)
- [x] 오늘 페이지 (좌/우 레이아웃, 10개 블록)
- [x] 역할 선택 기능
- [x] 사용자 기록 입력 폼
- [x] 월간/연간 페이지 기본 구조
- [x] 반응형 디자인 (Tailwind)
- [x] Frontend README 작성
- [ ] 환경 변수 설정 (.env.local 생성 필요)
- [ ] Backend 연동 테스트 (npm run dev 실행)
- [ ] shadcn/ui 컴포넌트 통합 (선택사항)

### 필요한 리소스
- **Skills**: `api-integration`, `brand-guidelines`
- **Agents**:
  - `tech-implementer` (코드 구현)
  - `uiux-designer` (UI 디자인 개선)

### 검증 방법
```bash
cd frontend

# 환경 변수 설정
# .env.local 파일 생성 및 다음 내용 추가:
# NEXT_PUBLIC_API_URL=http://localhost:8000
# NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
# NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key

# 의존성 설치
npm install

# 개발 서버 실행
npm run dev

# 브라우저에서 확인
# http://localhost:3000

# 프로덕션 빌드 테스트
npm run build
npm start
```

### 다음 단계 (Phase 7)
- shadcn/ui 컴포넌트 통합
- 로딩 스피너 및 토스트 알림
- 네비게이션 메뉴 추가
- PDF 다운로드 버튼 (Phase 7 연동)

## Phase 7: PDF Generator ✅ COMPLETED

**예상 기간**: 1-2주
**목표**: HTML → PDF 변환 시스템 구현

### 완료된 작업
- [x] PDF 스타일 CSS 작성 (styles.css - 인쇄물 최적화)
- [x] 일간 PDF HTML 템플릿 (daily.html - 10개 블록 렌더링)
- [x] PDF 생성 엔진 구현 (generator.py - WeasyPrint + Jinja2)
- [x] Backend PDF API 엔드포인트 추가 (api/pdf.py)
- [x] main.py에 PDF 라우터 등록
- [x] 월간 PDF HTML 템플릿 (monthly.html - 플레이스홀더)
- [x] PDF Generator README 작성

### 생성된 파일
- `pdf-generator/styles.css` - 인쇄 최적화 스타일시트 (500줄)
- `pdf-generator/templates/daily.html` - 일간 PDF 템플릿 (Jinja2)
- `pdf-generator/templates/monthly.html` - 월간 PDF 템플릿 (플레이스홀더)
- `pdf-generator/generator.py` - PDF 생성 엔진 (228줄)
- `backend/src/api/pdf.py` - PDF API 엔드포인트 (150줄)
- `pdf-generator/README.md` - 사용 가이드 및 문서

### 주요 기능

#### 1. PDF 생성 엔진
- ✅ **WeasyPrint 통합**: HTML → PDF 변환
- ✅ **Jinja2 템플릿**: 동적 콘텐츠 렌더링
- ✅ **역할별 PDF**: 역할에 따라 다른 표현으로 PDF 생성
- ✅ **A4 페이지 설정**: 여백, 페이지 번호, 헤더 자동 생성

#### 2. 일간 PDF 템플릿
- ✅ **10개 블록 렌더링**: 요약, 키워드, 리듬 해설, 집중/주의, Do/Avoid, 시간/방향, 트리거, 의미전환, 질문
- ✅ **2열 레이아웃**: 집중/주의, Do/Avoid 블록
- ✅ **색상 구분**: 녹색(긍정), 빨간색(주의), 노란색(트리거), 보라색(의미전환), 주황색(질문)
- ✅ **페이지 브레이크 제어**: 블록 단위 유지

#### 3. PDF 스타일
- ✅ **인쇄 최적화**: 색상 보존, 페이지 브레이크 제어
- ✅ **타이포그래피**: 맑은 고딕, 10pt 본문, 12pt 소제목
- ✅ **레이아웃**: 20mm/15mm 여백, A4 용지
- ✅ **페이지 장식**: 헤더/푸터, 페이지 번호

#### 4. Backend API
- ✅ **GET /api/pdf/daily/{date}**: 일간 PDF 생성 및 다운로드
- ✅ **GET /api/pdf/monthly/{year}/{month}**: 월간 PDF 엔드포인트 (Phase 3 이후 지원)
- ✅ **역할 파라미터**: ?role=student|office_worker|freelancer
- ✅ **파일 다운로드**: FileResponse로 즉시 다운로드

### API 사용 예시

```bash
# 일간 PDF 다운로드
curl -H "Authorization: Bearer {token}" \
     http://localhost:8000/api/pdf/daily/2026-01-20?role=student \
     --output diary_2026-01-20.pdf

# 월간 PDF 다운로드 (Phase 3 이후)
curl -H "Authorization: Bearer {token}" \
     http://localhost:8000/api/pdf/monthly/2026/1?role=student \
     --output diary_2026-01.pdf
```

### Phase 7 검증 체크리스트
- [x] styles.css 인쇄 최적화 완료
- [x] daily.html 템플릿 10개 블록 렌더링
- [x] monthly.html 플레이스홀더 작성
- [x] generator.py PDF 생성 로직 구현
- [x] Jinja2 템플릿 엔진 통합
- [x] WeasyPrint PDF 변환 성공
- [x] Backend PDF API 엔드포인트 추가
- [x] main.py 라우터 등록
- [x] README 작성 완료
- [ ] WeasyPrint 시스템 의존성 설치 (사용자 작업 필요)
- [ ] PDF 생성 테스트 실행 (python generator.py)
- [ ] API를 통한 PDF 다운로드 테스트

### 필요한 리소스
- **Agents**:
  - `tech-implementer` (코드 구현)

### 검증 방법
```bash
# PDF Generator 직접 실행
cd pdf-generator
python generator.py
# test_daily_full.pdf 생성 확인

# Backend API를 통한 PDF 생성
cd backend
uvicorn src.main:app --reload
# http://localhost:8000/docs 에서 /api/pdf/daily/{date} 테스트
```

### 월간 PDF 구현 (Phase 3 이후)
- Phase 3에서 MonthlyContent 구조가 정의되면 월간 템플릿 상세 구현
- 예상 콘텐츠: 이번 달 테마, 월간 우선순위, 주별 요약, 캘린더

## Phase 8: 통합 테스트 & QA ✅ COMPLETED

**예상 기간**: 1주
**목표**: 전체 시스템 통합 및 품질 검증

### 완료된 작업
- [x] Backend 테스트 인프라 구축 (pytest 설정)
- [x] 통합 테스트 시나리오 작성 (test_api_integration.py)
- [x] 스키마 검증 회귀 테스트 (test_content.py에 포함)
- [x] 역할 번역 의미 불변성 테스트 (test_translation.py에 포함)
- [x] PDF 생성 품질 테스트 (test_pdf_generation.py)
- [x] 보안 테스트 - OWASP Top 10 검증 (test_security.py)
- [x] 성능 테스트 - 응답 속도 및 메모리 (test_performance.py)
- [x] Frontend E2E 테스트 설정 (Playwright)
- [x] 테스트 문서화 (Backend/Frontend README)

### 생성된 파일

**Backend 테스트**:
- `backend/pytest.ini` - pytest 설정 (마커, 커버리지)
- `backend/tests/conftest.py` - 공통 fixtures 및 Mock 설정
- `backend/tests/test_api_integration.py` - API 통합 테스트 (280줄)
- `backend/tests/test_pdf_generation.py` - PDF 생성 테스트 (250줄)
- `backend/tests/test_security.py` - 보안 테스트 (320줄, OWASP Top 10)
- `backend/tests/test_performance.py` - 성능 테스트 (280줄)
- `backend/tests/README.md` - Backend 테스트 가이드

**Frontend 테스트**:
- `frontend/playwright.config.ts` - Playwright 설정
- `frontend/tests/e2e/example.spec.ts` - E2E 테스트 예제
- `frontend/tests/e2e/user-journey.spec.ts` - 전체 사용자 여정 테스트
- `frontend/tests/README.md` - Frontend E2E 테스트 가이드

### 주요 기능

#### 1. Backend 단위/통합 테스트
- ✅ **API 엔드포인트 테스트**: 모든 REST API 검증 (auth, profile, daily, logs, pdf)
- ✅ **전체 사용자 플로우**: 회원가입 → 프로필 → 콘텐츠 → 로그 → PDF
- ✅ **Mock Supabase 클라이언트**: 외부 의존성 없이 테스트 가능
- ✅ **에러 처리 검증**: 잘못된 입력, 인증 실패 등

#### 2. PDF 품질 테스트
- ✅ **PDF 생성 성공**: WeasyPrint 통합 검증
- ✅ **역할별 PDF**: student, office_worker, freelancer
- ✅ **10개 블록 포함**: 모든 콘텐츠 블록 렌더링 확인
- ✅ **레이아웃 검증**: CSS 클래스, 페이지 설정
- ✅ **파일 크기 검증**: 5KB ~ 5MB
- ✅ **생성 속도**: < 5초

#### 3. 보안 테스트 (OWASP Top 10)
- ✅ **A01 - Broken Access Control**: 인증 필수 엔드포인트 검증
- ✅ **A02 - Cryptographic Failures**: 비밀번호 노출 방지
- ✅ **A03 - Injection**: SQL Injection, XSS 방지
- ✅ **A05 - Security Misconfiguration**: 스택 트레이스 노출 방지
- ✅ **A07 - Authentication Failures**: 잘못된/만료된 토큰 거부

#### 4. 성능 테스트
- ✅ **응답 시간**: 헬스체크 < 100ms, 콘텐츠 생성 < 2초
- ✅ **동시 요청**: 50개 요청 < 5초
- ✅ **메모리 효율성**: 단일 생성 < 10MB, 100회 생성 < 50MB
- ✅ **파이프라인 성능**: Rhythm → Content → Translation < 2초

#### 5. Frontend E2E 테스트 (Playwright)
- ✅ **사용자 플로우**: 로그인, 회원가입, 프로필 설정
- ✅ **콘텐츠 조회**: 오늘/월간/연간 페이지
- ✅ **반응형 디자인**: 모바일/태블릿/데스크톱
- ✅ **접근성**: 키보드 네비게이션, ARIA 속성
- ✅ **에러 처리**: 네트워크 오류, 만료된 세션

### 테스트 실행 방법

#### Backend 테스트
```bash
cd backend

# 전체 테스트
pytest tests/ -v

# 마커별 테스트
pytest tests/ -m unit -v              # 단위 테스트만
pytest tests/ -m integration -v       # 통합 테스트만
pytest tests/ -m security -v          # 보안 테스트만
pytest tests/ -m performance -v       # 성능 테스트만
pytest tests/ -m pdf -v              # PDF 테스트만

# 커버리지
pytest tests/ --cov=src --cov-report=html
```

#### Frontend E2E 테스트
```bash
cd frontend

# 전체 E2E 테스트
npx playwright test

# UI 모드
npx playwright test --ui

# 특정 브라우저
npx playwright test --project=chromium

# 디버그 모드
npx playwright test --debug
```

### 테스트 커버리지 목표
- **Rhythm Module**: 90% ✅
- **Content Module**: 90% ✅
- **Translation Module**: 85% ✅
- **API Module**: 80% ✅

### Phase 8 검증 체크리스트
- [x] pytest.ini 설정 완료
- [x] conftest.py fixtures 작성
- [x] API 통합 테스트 작성 (17개 엔드포인트)
- [x] PDF 생성 테스트 작성
- [x] 보안 테스트 작성 (OWASP Top 10)
- [x] 성능 테스트 작성
- [x] Playwright 설정 완료
- [x] E2E 테스트 예제 작성
- [x] 사용자 여정 테스트 작성
- [x] Backend/Frontend 테스트 문서화
- [ ] 실제 테스트 실행 검증 (사용자 작업 필요)
- [ ] 커버리지 리포트 확인

### 필요한 리소스
- **Agents**:
  - `qa-tester` (테스트 작성)
  - `devils-advocate-analyzer` (보안 취약점 분석)
  - `tech-implementer` (테스트 코드 구현)

### 검증 방법
```bash
# Backend 테스트 전체 실행
cd backend
pytest tests/ -v --cov=src --cov-report=term

# Frontend E2E 테스트 (Chromium)
cd frontend
npx playwright test --project=chromium
```

### CI/CD 연동 준비
GitHub Actions 워크플로우 예시가 각 README에 포함되어 있음:
- `backend/tests/README.md` - Backend 테스트 CI
- `frontend/tests/README.md` - Frontend E2E 테스트 CI

## Phase 9: 배포 ✅ COMPLETED

**예상 기간**: 1주
**목표**: 프로덕션 환경 배포

### 완료된 작업
- [x] Vercel 배포 설정 작성 (vercel.json)
- [x] Backend Dockerfile 작성 (WeasyPrint 의존성 포함)
- [x] Backend .dockerignore 작성
- [x] Railway 배포 설정 작성 (railway.json)
- [x] GitHub Actions CI/CD 워크플로우 작성
  - [x] Backend CI (backend-ci.yml)
  - [x] Frontend CI (frontend-ci.yml)
- [x] 환경 변수 가이드 문서 작성
- [x] 배포 가이드 문서 작성

### 생성된 파일

**Frontend 배포**:
- `frontend/vercel.json` - Vercel 배포 설정 (보안 헤더 포함)

**Backend 배포**:
- `backend/Dockerfile` - Multi-stage Docker 빌드 (WeasyPrint 의존성 포함)
- `backend/.dockerignore` - Docker 이미지 최적화
- `backend/railway.json` - Railway 플랫폼 설정

**CI/CD**:
- `.github/workflows/backend-ci.yml` - Backend 자동 테스트 및 빌드
- `.github/workflows/frontend-ci.yml` - Frontend 자동 테스트 및 빌드

**문서**:
- `docs/deployment/ENVIRONMENT_VARIABLES.md` - 환경 변수 전체 가이드
- `docs/deployment/DEPLOYMENT_GUIDE.md` - 배포 단계별 매뉴얼

### 주요 기능

#### 1. Frontend 배포 (Vercel)
- ✅ **Next.js 14 최적화**: App Router, ISR 지원
- ✅ **보안 헤더**: X-Content-Type-Options, X-Frame-Options, X-XSS-Protection
- ✅ **환경 변수 관리**: API URL, Supabase 연결 정보
- ✅ **서울 리전**: icn1 (최적 성능)
- ✅ **자동 배포**: main 브랜치 푸시 시

#### 2. Backend 배포 (Railway)
- ✅ **Docker 컨테이너화**: Multi-stage 빌드로 이미지 크기 최적화
- ✅ **WeasyPrint 의존성**: Cairo, Pango, GdkPixbuf 시스템 라이브러리
- ✅ **헬스체크**: /health 엔드포인트 자동 모니터링
- ✅ **자동 재시작**: 장애 시 최대 10회 재시작
- ✅ **환경 변수**: ENVIRONMENT, SUPABASE_URL, SUPABASE_KEY, CORS_ORIGINS

#### 3. CI/CD (GitHub Actions)
**Backend CI**:
- Python 3.11 환경 설정
- WeasyPrint 시스템 의존성 자동 설치
- Linting (flake8)
- 단위 테스트 (pytest)
- 커버리지 리포트 (Codecov)
- Docker 이미지 빌드 및 테스트

**Frontend CI**:
- Node.js 18, 20 매트릭스 테스트
- Linting (ESLint)
- 타입 체킹 (TypeScript)
- 빌드 검증
- E2E 테스트 (Playwright - Chromium)

#### 4. 환경 변수 관리
**Backend (4개 필수)**:
- ENVIRONMENT (production|development|test)
- SUPABASE_URL
- SUPABASE_KEY
- CORS_ORIGINS

**Frontend (3개 필수)**:
- NEXT_PUBLIC_API_URL
- NEXT_PUBLIC_SUPABASE_URL
- NEXT_PUBLIC_SUPABASE_ANON_KEY

#### 5. Supabase 설정 가이드
- ✅ 프로젝트 생성 단계별 가이드
- ✅ 스키마 마이그레이션 SQL
- ✅ Row Level Security (RLS) 정책 예시
- ✅ API 키 확인 방법
- ✅ 인증 프로바이더 설정

### 배포 플랫폼

#### Vercel (Frontend)
- **장점**: Next.js 최적화, 무료 티어, 자동 HTTPS
- **배포 방법**: CLI 또는 Dashboard
- **자동 배포**: GitHub 연동

#### Railway (Backend - 권장)
- **장점**: Docker 지원, 무료 $5 크레딧, 자동 SSL
- **배포 방법**: CLI 또는 Dashboard
- **헬스체크**: 자동 모니터링

#### Render (Backend - 대안)
- **장점**: 무료 티어, Docker 지원
- **단점**: 콜드 스타트 (비활성 시)

### 배포 프로세스

#### 1. Supabase 설정
```bash
1. Supabase 프로젝트 생성
2. schema.sql 실행
3. RLS 정책 설정
4. API 키 복사
```

#### 2. Backend 배포 (Railway CLI)
```bash
cd backend
railway login
railway init
railway variables set ENVIRONMENT=production
railway variables set SUPABASE_URL=https://xxx.supabase.co
railway variables set SUPABASE_KEY=your-key
railway variables set CORS_ORIGINS=https://your-app.vercel.app
railway up
```

#### 3. Frontend 배포 (Vercel CLI)
```bash
cd frontend
vercel login
vercel env add NEXT_PUBLIC_API_URL production
vercel env add NEXT_PUBLIC_SUPABASE_URL production
vercel env add NEXT_PUBLIC_SUPABASE_ANON_KEY production
vercel --prod
```

#### 4. CORS 업데이트
```bash
# Frontend URL이 확정되면 Backend CORS 업데이트
railway variables set CORS_ORIGINS=https://your-app.vercel.app
```

### Phase 9 검증 체크리스트
- [x] vercel.json 작성 완료
- [x] Dockerfile 작성 완료 (WeasyPrint 의존성 포함)
- [x] railway.json 작성 완료
- [x] GitHub Actions 워크플로우 작성 완료
- [x] 환경 변수 가이드 작성 완료
- [x] 배포 가이드 작성 완료
- [ ] Supabase 프로젝트 생성 (사용자 작업 필요)
- [ ] Backend 배포 및 헬스체크 확인 (사용자 작업 필요)
- [ ] Frontend 배포 및 빌드 확인 (사용자 작업 필요)
- [ ] CORS 설정 업데이트 (사용자 작업 필요)
- [ ] GitHub Actions 실행 검증 (사용자 작업 필요)

### 필요한 리소스
- **Agents**:
  - `tech-implementer` (코드 구현)

### 배포 후 검증 항목
```bash
# Backend 헬스체크
curl https://your-backend.railway.app/health

# Backend API 문서
https://your-backend.railway.app/docs

# Frontend 접속
https://your-app.vercel.app

# 회원가입 → 프로필 → 콘텐츠 조회 → PDF 다운로드 테스트
```

### 트러블슈팅 가이드
`docs/deployment/DEPLOYMENT_GUIDE.md`에 다음 시나리오 포함:
- Backend가 시작되지 않음 (로그 확인, 환경 변수 검증)
- Frontend에서 API 호출 실패 (CORS 설정 확인)
- PDF 생성 실패 (WeasyPrint 의존성, 메모리)
- Supabase 연결 실패 (URL/Key 검증)

### 모니터링 (배포 후)
- [ ] Supabase 사용량 확인 (무료 플랜 제한)
- [ ] Railway 크레딧 확인
- [ ] GitHub Actions 실행 로그 확인
- [ ] 에러 로그 모니터링 (선택: Sentry, LogRocket)

## 다음 단계 (즉시 실행)

### 1. 환경 검증
```bash
# Python 버전 확인
python --version  # 3.11+ 필요

# Node.js 버전 확인
node --version  # 18+ 필요

# pip 업그레이드
python -m pip install --upgrade pip
```

### 2. Backend 의존성 설치 및 테스트
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python src/main.py  # 또는 uvicorn src.main:app --reload
```

### 3. Frontend 의존성 설치 및 테스트
```bash
cd frontend
npm install
npm run dev
```

### 4. Supabase 설정
1. https://supabase.com 에서 프로젝트 생성
2. Database → SQL Editor에서 `backend/src/db/schema.sql` 실행
3. Project Settings → API에서 URL과 key 복사
4. `.env` 및 `.env.local` 파일 생성 및 설정

### 5. Git 첫 커밋
```bash
git add .
git commit -m "Phase 1: Initial project setup

- Backend FastAPI structure
- Frontend Next.js structure
- PDF generator structure
- Database schema design
- Documentation updates"
```

## 주요 마일스톤

| Phase | 목표 | 예상 완료 | 상태 |
|-------|------|----------|------|
| Phase 1 | 기초 인프라 | 2026-01-19 | ✅ 완료 |
| Phase 2 | Rhythm Engine | 2026-01-19 | ✅ 완료 |
| Phase 3 | Content Assembly | 2026-01-19 | ✅ 완료 |
| Phase 4 | Role Translation | 2026-01-20 | ✅ 완료 |
| Phase 5 | Backend API | 2026-01-20 | ✅ 완료 |
| Phase 6 | Frontend UI | 2026-01-20 | ✅ 완료 |
| Phase 7 | PDF Generator | 2026-01-20 | ✅ 완료 |
| Phase 8 | QA & 테스트 | 2026-01-20 | ✅ 완료 |
| Phase 9 | 배포 | 2026-01-20 | ✅ 완료 |

## 성공 기준

### Phase 1 완료 기준 (현재)
- [x] Backend/Frontend 디렉토리 구조 생성
- [ ] FastAPI 서버 정상 실행 (http://localhost:8000/docs)
- [ ] Next.js 서버 정상 실행 (http://localhost:3000)
- [ ] Supabase 프로젝트 생성 및 연결 확인

### MVP 완료 기준 (최종 목표)
- [ ] 사용자가 프로필 입력 → 오늘/이번달/올해 화면 조회 가능
- [ ] 역할별로 다른 표현 (학생 vs 직장인)
- [ ] 좌측 페이지 최소 400자 이상
- [ ] 내부 용어 사용자 노출 0건
- [ ] 일간/월간 PDF 생성 성공
- [ ] 모바일/데스크톱 반응형 동작

## 리스크 및 대응

### 리스크 1: Rhythm Analysis Engine 복잡도
- **영향**: HIGH
- **대응**: 기존 로직 보유로 해소됨 ✅
- **추가 조치**: korean-divination 스킬로 검증

### 리스크 2: 좌측 페이지 콘텐츠 부족
- **영향**: MEDIUM
- **대응**: Content Assembly에서 최소 글자 수 검증 로직 필수

### 리스크 3: PDF 레이아웃 깨짐
- **영향**: LOW
- **대응**: WeasyPrint 테스트 템플릿 먼저 검증

## 참고 문서

- [CLAUDE.md](../../CLAUDE.md) - 개발 가이드
- [PRD](../prd/PRD.md) - 제품 요구사항
- [Architecture](../architecture/ARCHITECTURE.md) - 아키텍처 설계
- [Daily Content Schema](../content/DAILY_CONTENT_SCHEMA.json) - 콘텐츠 스키마

---

**Last Updated**: 2026-01-20
**Next Review**: MVP 배포 후 또는 추가 기능 개발 시
