# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 개발 환경 설정 원칙 ⚠️
- **프론트엔드**: 무조건 localhost:5000에서만 개발
- **백엔드**: localhost:8000에서 개발
- **환경변수**: .env.local은 항상 localhost:8000을 가리켜야 함
- **배포**: 별도 명령이 있을 때까지 배포 관련 질문/진행 금지
- **목업 데이터 사용 금지**:
  - 프론트엔드에서 목업 데이터 절대 사용 금지
  - 실제 백엔드 API에서 사주 계산 결과만 사용
  - 테스트용 기본 사주: 1971년 11월 17일 04:00 양력 남자

## 프로젝트 개요

R³ 다이어리 시스템 - 개인별 맞춤 설문을 통해 수집한 정보와 출생 데이터 기반 리듬 분석을 결합한 완전히 개인화된 다이어리 애플리케이션. 웹 앱, 모바일 앱, 인쇄 PDF 등 다양한 채널을 동시 지원.

**R³ 시스템**: Rhythm → Response → Recode
- **Rhythm**: 출생 데이터 기반으로 오늘의 흐름/리듬 분석
- **Response**: 자동 반응(불안, 충동, 미루기 등) 인지
- **Recode**: 언어/질문/기록으로 반응을 재설계

## 최종 목표

고객 맞춤형 개인 다이어리 시스템 제공:
1. **설문 기반 프로필링**: Google Forms / n8n을 통한 개인 성향, 생년월일, 관심사 수집
2. **개인화된 콘텐츠**: 고객의 성향에 맞춘 일간 리듬 분석 및 조언 생성
3. **멀티 채널 제공**:
   - 🌐 **웹 앱**: 실시간 기록 및 조회
   - 📱 **모바일 앱**: 이동 중 접근
   - 📄 **인쇄 PDF**: 종이 다이어리로 제공
4. **사용자 세분화**:
   - 앱만 사용하는 고객
   - 앱 + 종이 다이어리 병행 고객
   - 종이 다이어리만 원하는 고객

## 핵심 아키텍처 원칙

### 1. 데이터 흐름 (Markdown-First 시스템)
```
프로필 + 설정
    ↓
Rhythm Analysis Engine (3가지 계산)
    ├─ 사주(八字) 계산
    ├─ 기문둔갑(奇門遁甲) 분석
    └─ 색은식(五運六氣) 계산
    ↓
Content Assembly Engine (JSON)
    ↓
Markdown Generator (사용자 노출 텍스트)
    ↓
Output Channels
    ├─ Web (Markdown 렌더링)
    ├─ PDF (HTML → PDF)
    └─ API (JSON + Markdown 모두 반환)
```

### 1-1. 새로운 Markdown 워크플로우
- **기본 단위**: Markdown 파일 (`.md`)
- **저장 위치**: `backend/daily/{YYYY-MM-DD}.md`
- **생성 순서**:
  1. 사주/기문/색은식 계산 (내부 데이터, 사용자 노출 금지)
  2. JSON 구조로 어셈블
  3. Markdown으로 변환 (사용자 친화적 형식)
  4. 역할별 번역 적용 (학생/직장인/프리랜서)
- **API 응답**: JSON과 Markdown 모두 반환

### 2. 관심사 분리
- **내부 용어(Internal Terms)**: 계산 모듈에서만 사용, 사용자에게 절대 노출 금지
- **사용자 문구(User Copy)**: 사용자 노출 텍스트 전용, 전문/기술 용어 사용 금지
- **스키마 우선(Schema-First)**: 콘텐츠는 `DAILY_CONTENT_SCHEMA.json`을 따르며, UI는 스키마를 렌더링

### 3. 역할 기반 가변 콘텐츠
동일한 리듬 분석이 사용자 역할에 따라 다른 표현으로 변환됨:
- **학생**: 학습/집중/페이스 관리 강조, 업무/계약 표현 최소화
- **직장인**: 업무/관계/결정/보고 강조
- **프리랜서/자영업**: 결정/계약/창작/체력 강조
- **공통**: 건강/관계/정리/감정 조절은 모든 역할에 존재

역할 번역은 Role Translation Layer에서만 수행되며, 리듬의 본질적 의미를 바꾸지 않고 표현만 변형함.

## 콘텐츠 구조 요구사항

### 일간 페이지 레이아웃 (매우 중요)
**좌측(오늘의 안내)** - 반드시 풍성해야 함:
- 최소 8개 이상의 독립 블록
- 최소 400~600자 (목표 700~1200자)
- 설명형 문단 반드시 포함, 요약 카드만 나열 금지
- 표준 10개 블록: 요약, 키워드, 리듬 해설, 집중/주의 포인트, 행동 가이드(Do/Avoid), 시간/방향, 상태 트리거, 의미 전환, 리듬 질문

**우측(사용자 기록)**:
- 사용자가 직접 쓰는 공간 우선 확보
- 최소한의 가이드만 제공 (질문 1~2개)

### 콘텐츠 스키마
주요 스키마: `docs/content/DAILY_CONTENT_SCHEMA.json`
- 모든 일간 콘텐츠는 이 스키마를 준수해야 함
- 길이 요구사항이 스키마에 내장됨
- 좌측 페이지는 "카드 전용 요약" 금지

## 법적/표현 정책

**매우 중요**: 사용자 노출 텍스트에서 전문 용어 절대 사용 금지
- UI에서 금지: NLP, 사주명리, 기문둔갑 등 전문/기술 용어
- 허용: 내부 계산 모듈에서만
- 참조: `docs/legal/TERMINOLOGY_POLICY.md`

## 주요 문서 파일

- `docs/prd/PRD.md` - 제품 요구사항, MVP 범위, R³ 시스템 정의
- `docs/architecture/ARCHITECTURE.md` - 상위 컴포넌트, 데이터 흐름, 스토리지
- `docs/architecture/docs/content/CONTENT_STRUCTURE.md` - 콘텐츠 구조, 블록 구성
- `docs/content/DAILY_CONTENT_SCHEMA.json` - 일간 콘텐츠 스키마 정의 (JSON 기본)
- `docs/content/MARKDOWN_FORMAT_SPEC.md` - Markdown 형식 스펙 (신규, 사용자 노출)
- `backend/README_CONTENT_GENERATION.md` - 콘텐츠 생성 파이프라인 완전 가이드
- `docs/tasks/WORKPLAN.md` - 현재 작업 계획

## 출력 채널

**웹 + 인쇄(PDF) 동시 지원**
- One Content, Multi Output 원칙
- 동일한 데이터 구조가 양쪽 채널 모두 지원
- 디자인은 화면과 인쇄 레이아웃 모두에서 작동해야 함
- 인쇄 시 넘침, 타이포그래피, 페이지네이션 테스트 필수

## MVP 범위

1. 사용자 프로필 입력 (출생 정보, 역할, 선호사항)
2. 오늘/이번 달/올해 화면
3. 일간 페이지 렌더링 (좌/우 레이아웃)
4. 역할 기반 문장 변형
5. PDF 출력 (월간 + 일간 페이지)

## 향후 확장

- 365일 전량 생성/저장
- 종교/단체 템플릿 모듈
- 기록 기반 리포트 (월간 회고/패턴)
- 프리미엄 인쇄 에디션

## 개발 가이드라인

### 콘텐츠 추가 시
- `DAILY_CONTENT_SCHEMA.json` 대비 검증 필수
- 좌측 페이지 최소 글자 수 충족 확인 (400~600자)
- 역할 번역은 translation layer에서만 적용
- 웹과 PDF 렌더링 모두 테스트

### 아키텍처 수정 시
- 내부 계산 vs 사용자 노출 텍스트 분리 유지
- 역할 번역은 전용 레이어에 격리
- 스키마 변경 시 양쪽 렌더러(웹 + PDF) 모두 업데이트 필요

### 테스트 요구사항
- 스키마 검증 테스트 (JSON 스키마 준수)
- 역할 번역 회귀 테스트 (의미 불변성 확인)
- 인쇄 레이아웃 테스트 (넘침, 타이포그래피, 페이지네이션)

---

## 기술 스택

### Backend
- **언어**: Python 3.11+
- **프레임워크**: FastAPI
- **데이터베이스**: Supabase (PostgreSQL + Auth)
- **PDF 생성**: WeasyPrint (HTML → PDF)
- **테스트**: pytest
- **의존성 관리**: pip + requirements.txt

### Frontend
- **프레임워크**: Next.js 14+ (App Router)
- **언어**: TypeScript 5+
- **스타일링**: Tailwind CSS
- **UI 컴포넌트**: shadcn/ui
- **상태관리**: React Context API (또는 Zustand)
- **HTTP 클라이언트**: fetch API
- **테스트**: Vitest + Playwright

### DevOps
- **Frontend 배포**: Vercel
- **Backend 배포**: Railway 또는 Render
- **버전관리**: Git + GitHub
- **CI/CD**: GitHub Actions
- **환경변수**: .env files

## 프로젝트 구조

### Backend 실제 구조 (2026-01-30 기준)

```
diary-PJ/
├── docs/                      # 문서
│   ├── prd/PRD.md
│   ├── architecture/ARCHITECTURE.md
│   ├── content/
│   │   ├── DAILY_CONTENT_SCHEMA.json
│   │   └── docs/content/ROLE_TRANSLATION.md
│   ├── legal/TERMINOLOGY_POLICY.md
│   └── tasks/WORKPLAN.md
│
├── backend/                   # Python FastAPI 백엔드
│   ├── saju-calculator/       # ⭐ TypeScript 사주 계산 모듈 (신규)
│   │   ├── src/
│   │   │   ├── completeSajuCalculator.ts  # 완전한 사주 계산
│   │   │   ├── qimenCalculator.ts         # 기문둔갑 계산
│   │   │   └── extended-types.ts          # 타입 정의
│   │   ├── package.json
│   │   └── tsconfig.json
│   ├── src/
│   │   ├── rhythm/           # Rhythm Analysis Engine
│   │   │   ├── __init__.py
│   │   │   ├── saju.py       # Python 사주명리 로직
│   │   │   ├── qimen.py      # 기문둔갑 계산
│   │   │   ├── extended_saju.py  # 확장 사주 분석
│   │   │   └── signals.py    # 리듬 신호 생성
│   │   ├── content/          # Content Assembly Engine
│   │   │   ├── __init__.py
│   │   │   ├── assembly.py   # 콘텐츠 조합
│   │   │   ├── validator.py  # 스키마 검증
│   │   │   ├── models.py     # 데이터 모델
│   │   │   ├── extended_content.py  # 확장 콘텐츠
│   │   │   └── expand_chars.py      # 문자 확장
│   │   ├── translation/      # Role Translation Layer
│   │   │   ├── __init__.py
│   │   │   ├── translator.py
│   │   │   ├── models.py     # 번역 모델
│   │   │   ├── templates/    # 역할별 템플릿
│   │   │   ├── translators/  # 번역기 모음
│   │   │   ├── validators/   # 검증기
│   │   │   ├── vocabulary/   # 용어집
│   │   │   └── tests/        # 번역 테스트
│   │   ├── api/              # API 엔드포인트
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── profile.py
│   │   │   ├── profiles.py   # ⭐ 프로필 관리 API (신규)
│   │   │   ├── daily.py
│   │   │   ├── monthly.py
│   │   │   ├── logs.py
│   │   │   ├── forms.py      # ⭐ 설문 폼 API (신규)
│   │   │   ├── surveys.py    # ⭐ 설문조사 API (신규)
│   │   │   └── pdf.py
│   │   ├── db/               # 데이터베이스
│   │   │   ├── __init__.py
│   │   │   ├── supabase.py
│   │   │   ├── schema.sql    # DB 스키마
│   │   │   └── migrations/
│   │   ├── skills/           # ⭐ 스킬 모듈 (신규)
│   │   │   ├── form_builder/
│   │   │   └── personalization_engine/
│   │   ├── config/           # ⭐ 설정 (신규)
│   │   │   └── survey_templates/
│   │   ├── data_processor/   # ⭐ 데이터 처리 (신규)
│   │   │   └── tests/
│   │   ├── utils/
│   │   └── main.py
│   ├── tests/
│   │   ├── test_rhythm.py
│   │   ├── test_content.py
│   │   ├── test_translation.py
│   │   ├── test_enhancement.py
│   │   └── integration/      # 통합 테스트
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/                  # Next.js 프론트엔드
│   ├── src/
│   │   ├── app/              # App Router
│   │   │   ├── (auth)/
│   │   │   │   ├── login/page.tsx
│   │   │   │   └── signup/page.tsx
│   │   │   ├── profile/page.tsx
│   │   │   ├── today/page.tsx
│   │   │   ├── month/page.tsx
│   │   │   └── year/page.tsx
│   │   ├── components/
│   │   │   ├── ui/           # shadcn/ui 컴포넌트
│   │   │   ├── DailyPage/
│   │   │   │   ├── LeftPanel.tsx
│   │   │   │   └── RightPanel.tsx
│   │   │   ├── MonthPage/
│   │   │   └── YearPage/
│   │   ├── lib/
│   │   │   ├── api.ts        # API 클라이언트
│   │   │   ├── supabase.ts
│   │   │   └── utils.ts
│   │   └── styles/
│   ├── public/
│   ├── package.json
│   ├── tsconfig.json
│   └── tailwind.config.ts
│
├── pdf-generator/             # PDF 생성
│   ├── templates/
│   │   ├── daily.html
│   │   └── monthly.html
│   ├── generator.py
│   └── styles.css
│
├── .gitignore
├── CLAUDE.md                  # 프로젝트 가이드 (이 파일)
└── README.md
```

## 개발 환경 설정

### Backend 설정
```bash
# Python 가상환경 생성
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt

# 환경변수 설정
cp .env.example .env
# .env 파일 편집 (Supabase URL, Key 등)

# 개발 서버 실행
uvicorn src.main:app --reload

# 테스트 실행
pytest tests/ -v
```

### Frontend 설정
```bash
# 의존성 설치
cd frontend
npm install

# 환경변수 설정
cp .env.example .env.local
# .env.local 편집 (API URL 등)

# 개발 서버 실행 (포트 5000)
npm run dev

# 테스트 실행
npm test
```

### Supabase 설정
1. https://supabase.com 에서 프로젝트 생성
2. Database → SQL Editor에서 스키마 실행
3. Project Settings → API에서 URL과 anon key 복사
4. backend/.env와 frontend/.env.local에 추가

## API 엔드포인트 목록

### Authentication
```
POST   /api/auth/signup       # 회원가입
POST   /api/auth/login        # 로그인
POST   /api/auth/logout       # 로그아웃
GET    /api/auth/me           # 현재 사용자 정보
```

### Profile (기본)
```
GET    /api/profile           # 프로필 조회
POST   /api/profile           # 프로필 생성
PUT    /api/profile           # 프로필 수정
```

### Profiles (확장) ⭐ 신규
```
GET    /api/profiles/{user_id}      # 특정 사용자 프로필 조회
PUT    /api/profiles/{user_id}      # 프로필 업데이트
DELETE /api/profiles/{user_id}      # 프로필 삭제
```

### Daily Content
```
GET    /api/daily/{date}              # 일간 콘텐츠 조회
GET    /api/daily/{date}/role/{role}  # 역할별 일간 콘텐츠
POST   /api/log/{date}                # 사용자 기록 저장
GET    /api/log/{date}                # 사용자 기록 조회
```

### Monthly Content
```
GET    /api/monthly/{year}/{month}    # 월간 콘텐츠 조회
```

### Yearly Content
```
GET    /api/yearly/{year}             # 연간 콘텐츠 조회
```

### Form & Survey ⭐ 신규
```
POST   /api/forms             # 설문 폼 생성
GET    /api/forms/{id}        # 설문 폼 조회
POST   /api/surveys           # 설문 응답 제출
GET    /api/surveys/{user_id} # 사용자 설문 응답 조회
```

### PDF Generation
```
GET    /api/pdf/daily/{date}          # 일간 PDF 생성
GET    /api/pdf/monthly/{year}/{month} # 월간 PDF 생성
```

### Health Check
```
GET    /health                        # 서버 상태 확인
```

## Rhythm Analysis Engine 가이드

### 기존 로직 통합 방법
1. 기존 사주명리 계산 코드를 `backend/src/rhythm/saju.py`에 배치
2. 입력 인터페이스 표준화:
   ```python
   def calculate_rhythm(birth_info: BirthInfo, target_date: date) -> RhythmSignal:
       """
       birth_info: name, birth_datetime, gender, birth_place
       target_date: 분석 대상 날짜
       return: RhythmSignal (내부 표현, 사용자 노출 금지)
       """
   ```
3. 출력은 `RhythmSignal` 객체로 통일
4. 내부 전문 용어는 이 레이어에서만 사용

### 내부 용어 vs 사용자 용어 예시

**절대 금지 (사용자 UI에 노출 불가)**:
- 사주명리, 기문둔갑, 천간, 지지, 오행, 십성
- NLP, 알고리즘, 엔진, 계산, 분석 모듈
- 천을귀인, 역마, 공망 등 전문 용어

**허용 (사용자 UI 노출 가능)**:
- 오늘의 흐름, 리듬, 에너지, 방향
- 집중 시간, 주의 시간, 좋은 방향
- 집중력, 관계운, 건강 리듬
- 의사결정, 휴식, 정리, 창작

**변환 예시**:
```
[내부] 천을귀인 방향: 북동, 시간: 오전 9-11시
[사용자] 집중하기 좋은 방향: 북동쪽, 시간: 오전 9-11시

[내부] 역마 작용, 이동운 강화
[사용자] 이동이나 변화가 자연스러운 날

[내부] 공망, 불안정성 증가
[사용자] 불안감이 생길 수 있는 시간대
```

## Claude Code 스킬 활용 가이드

### 필수 스킬
1. **korean-divination** ⭐⭐⭐
   - Phase 2, 3, 4에서 필수
   - 사주명리/기문둔갑 계산 로직 검증
   - 콘텐츠 생성 및 역할 번역 검증

2. **supabase-integration**
   - Phase 1, 5에서 필수
   - DB 스키마 설계 및 Auth 설정
   - RLS 정책 구성

3. **api-integration**
   - Phase 5, 6에서 필수
   - FastAPI 엔드포인트 구현
   - Frontend API 클라이언트 구현

### 권장 스킬
4. **brand-guidelines**
   - Phase 6에서 권장
   - UI/UX 일관성 유지

5. **seo-optimization**
   - 배포 후 최적화

## Claude Code 에이전트 활용 순서

### Phase 1: 기초 인프라 (1-2주)
- **app-analyst**: 전체 아키텍처 설계 검토
- **db-architect**: DB 스키마 상세 설계
- **tech-implementer**: 디렉토리 구조 및 초기 설정 파일 생성

### Phase 2: Rhythm Analysis Engine (2-3주)
- **korean-tradition-content** ⭐: 기존 로직 통합 가이드
- **tech-implementer**: 코드 구현
- **qa-tester**: 단위 테스트 작성

### Phase 3: Content Assembly Engine (2-3주)
- **korean-tradition-content** ⭐: 콘텐츠 생성 로직 설계
- **tech-implementer**: 스키마 검증 및 블록 생성 구현
- **qa-tester**: 스키마 검증 테스트

### Phase 4: Role Translation Layer (1-2주)
- **korean-tradition-content** ⭐: 역할별 템플릿 설계
- **tech-implementer**: 번역 로직 구현
- **qa-tester**: 의미 불변성 회귀 테스트

### Phase 5: Backend API (2주)
- **tech-implementer**: API 엔드포인트 구현
- **qa-tester**: API 테스트

### Phase 6: Frontend UI (2-3주)
- **uiux-designer**: UI 컴포넌트 설계
- **tech-implementer**: React 컴포넌트 구현

### Phase 7: PDF Generator (1-2주)
- **tech-implementer**: PDF 템플릿 및 생성 로직

### Phase 8: 통합 테스트 & QA (1주)
- **qa-tester**: E2E 테스트
- **devils-advocate-analyzer**: 배포 전 최종 검증

### Phase 9: 배포 (1주)
- **tech-implementer**: 배포 설정
- **seo-growth**: SEO 최적화

## 테스트 실행 방법

### Backend 테스트
```bash
cd backend

# 전체 테스트
pytest tests/ -v

# 특정 모듈 테스트
pytest tests/test_rhythm.py -v
pytest tests/test_content.py -v
pytest tests/test_translation.py -v

# 커버리지 확인
pytest --cov=src tests/
```

### Frontend 테스트
```bash
cd frontend

# 단위 테스트
npm test

# E2E 테스트
npm run test:e2e

# 타입 체크
npm run type-check
```

### 통합 테스트
```bash
# Backend 서버 실행 (터미널 1)
cd backend
uvicorn src.main:app --reload

# Frontend 서버 실행 (터미널 2, 포트 5000)
cd frontend
npm run dev

# E2E 테스트 실행 (터미널 3)
cd frontend
npm run test:e2e
```

## 빌드 및 배포

### Frontend 빌드 (Vercel)
```bash
cd frontend
npm run build
npm start  # 프로덕션 모드 로컬 테스트

# Vercel 배포
vercel --prod
```

### Backend 배포 (Railway/Render)
```bash
cd backend

# requirements.txt 최신화
pip freeze > requirements.txt

# Railway CLI 배포
railway up

# 또는 GitHub 연동으로 자동 배포
```

### 환경변수 설정
**Backend (.env)**:
```
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=xxx
DATABASE_URL=postgresql://xxx
SECRET_KEY=xxx
```

**Frontend (.env.local)**:
```
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=xxx
```

## 데이터베이스 스키마

### 주요 테이블
- **profiles**: 사용자 프로필 (출생 정보, 역할, 선호사항)
- **daily_rhythm_signals**: 내부 계산 결과 (사용자 노출 금지)
- **daily_content**: 사용자 노출 콘텐츠 (역할별)
- **daily_logs**: 사용자 기록 (일간)
- **role_templates**: 역할별 번역 템플릿

상세 스키마는 `backend/src/db/migrations/` 참조

## 트러블슈팅

### Backend 이슈
**문제**: uvicorn이 실행되지 않음
```bash
# 가상환경 활성화 확인
which python  # venv 경로여야 함

# uvicorn 재설치
pip install --upgrade uvicorn
```

**문제**: Supabase 연결 오류
```bash
# 환경변수 확인
cat .env

# Supabase URL/Key 유효성 확인
curl https://your-project.supabase.co/rest/v1/
```

### Frontend 이슈
**문제**: npm run dev 실패
```bash
# node_modules 삭제 후 재설치
rm -rf node_modules package-lock.json
npm install

# Node.js 버전 확인 (18+ 필요)
node -v
```

**문제**: Tailwind 스타일 적용 안됨
```bash
# tailwind.config.ts의 content 경로 확인
# postcss.config.js 존재 확인
```

## 성공 기준

### Phase 1 완료 기준
- [ ] Backend/Frontend 디렉토리 구조 생성
- [ ] FastAPI 서버 정상 실행 (http://localhost:8000/docs)
- [ ] Next.js 서버 정상 실행 (http://localhost:5000)
- [ ] Supabase 프로젝트 생성 및 연결 확인

### MVP 완료 기준
- [ ] 사용자가 프로필 입력 → 오늘/이번달/올해 화면 조회 가능
- [ ] 역할별로 다른 표현 (학생 vs 직장인)
- [ ] 좌측 페이지 최소 400자 이상
- [ ] 내부 용어 사용자 노출 0건
- [ ] 일간/월간 PDF 생성 성공
- [ ] 모바일/데스크톱 반응형 동작

## 최근 작업 이력

### 2026-01-30: 프로젝트 환경 전체 정리 및 포트 통일

#### 주요 변경사항
1. **포트 5000 완전 통일**
   - Backend CORS: `localhost:3000` → `localhost:5000` (main.py:24)
   - Playwright 테스트: 2곳 모두 `localhost:5000`으로 변경 (playwright.config.ts:37, 84)
   - Docker Compose: Frontend 포트 `3000:3000` → `5000:5000` (docker-compose.yml:24)
   - Docker CORS 환경변수: `localhost:5000`으로 통일 (docker-compose.yml:13)

2. **프로젝트 구조 문서화 개선**
   - Backend 실제 구조 반영 (saju-calculator, skills, config, data_processor 등 신규 모듈 추가)
   - API 엔드포인트 목록 업데이트 (forms, surveys, profiles API 추가)
   - 실제 파일 경로와 문서 일치 확인

3. **개발 환경 정책 강화**
   - 포트 3000 사용 절대 금지 명시
   - Docker, Playwright 등 모든 도구에서 5000 포트 통일
   - 환경 변수 설정 가이드 개선

#### 서버 실행 확인
- **프론트엔드**: http://localhost:5000 (Next.js dev server)
- **백엔드**: http://localhost:8000 (FastAPI uvicorn)
- **API 문서**: http://localhost:8000/docs

#### 주요 수정 파일
- `backend/src/main.py` - CORS 설정
- `frontend/playwright.config.ts` - 테스트 포트
- `docker-compose.yml` - 컨테이너 포트
- `CLAUDE.md` - 프로젝트 구조 및 API 문서

### 2026-01-29: 프론트엔드 포트 변경 (3000 → 5000)

#### 포트 변경 사항
1. **package.json 수정**
   - `"dev": "next dev"` → `"dev": "next dev -p 5000"` 변경
   - 모든 개발 서버 실행이 자동으로 포트 5000에서 시작됨

2. **CLAUDE.md 업데이트**
   - 프로젝트 가이드의 모든 localhost 참조를 5000으로 변경
   - 개발 환경 설정 원칙 섹션 업데이트

#### 서버 실행 확인
- **프론트엔드**: http://localhost:5000 (Next.js dev server)
- **백엔드**: http://localhost:8000 (FastAPI uvicorn)

### 2026-01-24: API 에러 처리 수정 및 로컬 개발 환경 설정

#### 문제 해결
1. **프론트엔드 API 에러 처리 개선** (`frontend/src/lib/api.ts:56-67`)
   - FastAPI 에러 응답 `detail` 필드 우선 처리
   - 결과: 백엔드의 구체적인 에러 메시지 정상 표시

2. **백엔드 API 검증** (Render 배포 서버)
   - 회원가입 API 테스트: ✅ 성공
   - 로그인 API 테스트: ✅ 성공
   - 프로필 생성 API 테스트: ✅ 성공

3. **로컬 개발 환경 정책**
   - `frontend/.env.local`을 `localhost:8000`으로 고정
   - CLAUDE.md에 "개발 환경 설정 원칙" 섹션 추가

#### 주의사항
- FastAPI 에러 응답은 항상 `detail` 필드 사용
- 로컬 개발은 무조건 localhost:5000 ↔ localhost:8000 사용

---

## 전체 워크플로우

### Phase 1: 설문 시스템 (Form Collection)
```
고객 입력 → 설문 수집 (Google Forms / n8n) → 데이터 정규화 → 프로필 생성
```
**필요 기술**: n8n MCP, Google Forms Integration, Data Validation

### Phase 2: 개인화 엔진 (Personalization Engine)
```
프로필 + 생년월일 → 리듬 분석 → 개인 맞춤 콘텐츠 생성 → 역할 기반 번역
```
**필요 기술**: Korean Divination (사주/기문 분석), AI 콘텐츠 생성, Role Translation

### Phase 3: 콘텐츠 배포 (Multi-Channel Distribution)
```
콘텐츠 DB → 웹 렌더링 → PDF 생성 → 메일 발송 / 다운로드
```
**필요 기술**: WeasyPrint, Email Service (Mailgun/SendGrid), Cloud Storage

### Phase 4: 사용자 관리 (Customer Segmentation)
```
고객 등록 → 사용 패턴 분류 → 맞춤 서비스 제공
  ├─ 앱 전용
  ├─ 앱 + 종이
  └─ 종이 전용
```

## 필요한 에이전트 (Agents)

### 필수 에이전트
1. **Form Designer Agent** (새로 생성)
   - 역할: 설문 폼 설계 및 구현
   - 도구: n8n, Google Forms
   - 담당: 고객 정보 수집 로직

2. **Data Processing Agent** (새로 생성)
   - 역할: 설문 데이터 정규화 및 프로필 생성
   - 도구: Python, Data Validation
   - 담당: 수집된 데이터 → 구조화된 프로필

3. **Personalization Engine Agent** (기존 강화)
   - 역할: 개인 맞춤 콘텐츠 생성
   - 도구: Korean Divination Skill, AI Content Gen
   - 담당: 프로필 → 개인화된 일간 리듬

4. **PDF Generator Agent** (기존 강화)
   - 역할: PDF 생성 및 최적화
   - 도구: WeasyPrint, Print Layout Engine
   - 담당: 콘텐츠 → 인쇄용 PDF

5. **Customer Manager Agent** (새로 생성)
   - 역할: 고객 세분화 및 서비스 라우팅
   - 도구: Customer DB, Service Router
   - 담당: 고객 유형별 서비스 제공

### 보조 에이전트
6. **Email Service Agent** (새로 생성)
   - 역할: PDF 및 알림 이메일 발송
   - 도구: Mailgun/SendGrid MCP
   - 담당: 이메일 배포

7. **Analytics Agent** (새로 생성)
   - 역할: 사용 패턴 분석 및 리포팅
   - 도구: Analytics DB, Visualization
   - 담당: 고객 인사이트 생성

## 필요한 MCP (Model Context Protocol) 서버

### 필수 MCP
1. **n8n-mcp** (새로 생성)
   - 목적: n8n 워크플로우 자동화
   - 기능: 폼 생성, 데이터 수집, 이메일 발송

2. **database-mcp** (기존 / 강화)
   - 목적: 고객 프로필, 콘텐츠, 사용 기록 관리
   - 기능: CRUD 작업, 쿼리, 트랜잭션

3. **file-storage-mcp** (새로 생성)
   - 목적: PDF, 이미지 등 파일 저장
   - 기능: S3 연동, 파일 업로드/다운로드

4. **email-service-mcp** (새로 생성)
   - 목적: Mailgun/SendGrid 통합
   - 기능: 이메일 발송, 템플릿 관리

5. **google-forms-mcp** (새로 생성)
   - 목적: Google Forms 연동
   - 기능: 폼 생성, 응답 수집, 데이터 추출

## 필요한 Skill (Claude Code 스킬)

### 필수 Skill
1. **korean-divination** ✅ (기존)
   - 사주명리, 기문둔갑 계산
   - 사용 시점: 리듬 분석 엔진

2. **form-builder** (새로 생성)
   - n8n/Google Forms 폼 설계
   - 자동 설문 생성 로직

3. **personalization-engine** (새로 생성)
   - 프로필 → 개인화 콘텐츠 매핑
   - 사용자 성향별 콘텐츠 변형

4. **pdf-layout-optimizer** (새로 생성)
   - 인쇄용 PDF 레이아웃 최적화
   - 페이지 네이션, 타이포그래피

5. **email-template-designer** (새로 생성)
   - 이메일 템플릿 설계
   - HTML/CSS 이메일 구성

6. **customer-segmentation** (새로 생성)
   - 고객 분류 로직
   - 앱/종이/혼합 고객 라우팅

### 보조 Skill
7. **data-validator** (새로 생성)
   - 입력 데이터 검증
   - 필드 타입, 범위 확인

8. **content-quality-checker** (새로 생성)
   - 생성된 콘텐츠 품질 검증
   - 글자 수, 의미 검증

## 필요한 기존 자산 활용

### E:\project 폴더
- 사주 계산 로직 ✅
- 기문둔갑 알고리즘 ✅
- 콘텐츠 번역 레이어 ✅
- PDF 생성 템플릿 ✅

### E:\project\sajuapp 폴더
- 사용자 인증 시스템 ✅
- 프로필 관리 로직 ✅
- 데이터베이스 스키마 ✅

## 개발 우선순위

### Phase A: 핵심 설문 시스템 (Week 1-2)
- [ ] n8n-mcp 생성
- [ ] form-builder Skill 생성
- [ ] 설문 데이터 수집 파이프라인

### Phase B: 개인화 엔진 (Week 3-4)
- [ ] personalization-engine Skill 생성
- [ ] 프로필 기반 콘텐츠 생성
- [ ] 역할 기반 번역 적용

### Phase C: 멀티 채널 배포 (Week 5-6)
- [ ] pdf-layout-optimizer Skill 생성
- [ ] 웹 렌더링 최적화
- [ ] PDF 생성 파이프라인

### Phase D: 고객 관리 (Week 7-8)
- [ ] customer-segmentation Skill 생성
- [ ] email-service-mcp 생성
- [ ] 이메일 배포 자동화

## 참고 문서

- [PRD](docs/prd/PRD.md) - 제품 요구사항
- [Architecture](docs/architecture/ARCHITECTURE.md) - 아키텍처 설계
- [Daily Content Schema](docs/content/DAILY_CONTENT_SCHEMA.json) - 콘텐츠 스키마
- [Terminology Policy](docs/legal/TERMINOLOGY_POLICY.md) - 용어 정책
- [Workplan](docs/tasks/WORKPLAN.md) - 현재 작업 계획
