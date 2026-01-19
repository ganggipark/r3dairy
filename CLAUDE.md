# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 개요

R³ 다이어리 시스템 - 출생 정보 기반 리듬 분석과 사용자 기록을 결합한 개인 맞춤 다이어리 애플리케이션. 웹과 인쇄(PDF) 출력을 동시 지원.

**R³ 시스템**: Rhythm → Response → Recode
- **Rhythm**: 출생 데이터 기반으로 오늘의 흐름/리듬 분석
- **Response**: 자동 반응(불안, 충동, 미루기 등) 인지
- **Recode**: 언어/질문/기록으로 반응을 재설계

## 핵심 아키텍처 원칙

### 1. 데이터 흐름
```
프로필 + 설정 → Rhythm Analysis Engine(내부) →
Content Assembly Engine → Role Translation Layer →
출력(Web/PDF Renderer)
```

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
- `docs/content/DAILY_CONTENT_SCHEMA.json` - 일간 콘텐츠 스키마 정의
- `docs/tasks/WORKPLAN.md` - 현재 작업 계획 (초기 단계에서는 비어있을 수 있음)

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

```
diary-PJ/
├── docs/                      # 문서 (현재 존재)
│   ├── prd/PRD.md
│   ├── architecture/ARCHITECTURE.md
│   ├── content/
│   │   ├── DAILY_CONTENT_SCHEMA.json
│   │   └── ROLE_TRANSLATION.md
│   ├── legal/TERMINOLOGY_POLICY.md
│   └── tasks/WORKPLAN.md
│
├── backend/                   # Python FastAPI 백엔드
│   ├── src/
│   │   ├── rhythm/           # Rhythm Analysis Engine
│   │   │   ├── __init__.py
│   │   │   ├── saju.py       # 기존 사주명리 로직 통합
│   │   │   ├── qimen.py      # 기문둔갑 계산
│   │   │   └── signals.py    # 리듬 신호 생성
│   │   ├── content/          # Content Assembly Engine
│   │   │   ├── __init__.py
│   │   │   ├── assembly.py   # 콘텐츠 조합
│   │   │   └── validator.py  # 스키마 검증
│   │   ├── translation/      # Role Translation Layer
│   │   │   ├── __init__.py
│   │   │   ├── translator.py
│   │   │   └── templates/    # 역할별 템플릿
│   │   │       ├── student.json
│   │   │       ├── office_worker.json
│   │   │       └── freelancer.json
│   │   ├── api/              # API 엔드포인트
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── profile.py
│   │   │   ├── daily.py
│   │   │   ├── monthly.py
│   │   │   └── pdf.py
│   │   ├── db/               # 데이터베이스
│   │   │   ├── models.py
│   │   │   ├── supabase.py
│   │   │   └── migrations/
│   │   ├── utils/
│   │   └── main.py
│   ├── tests/
│   │   ├── test_rhythm.py
│   │   ├── test_content.py
│   │   └── test_translation.py
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

# 개발 서버 실행
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

### Profile
```
GET    /api/profile           # 프로필 조회
POST   /api/profile           # 프로필 생성
PUT    /api/profile           # 프로필 수정
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

# Frontend 서버 실행 (터미널 2)
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
- [ ] Next.js 서버 정상 실행 (http://localhost:3000)
- [ ] Supabase 프로젝트 생성 및 연결 확인

### MVP 완료 기준
- [ ] 사용자가 프로필 입력 → 오늘/이번달/올해 화면 조회 가능
- [ ] 역할별로 다른 표현 (학생 vs 직장인)
- [ ] 좌측 페이지 최소 400자 이상
- [ ] 내부 용어 사용자 노출 0건
- [ ] 일간/월간 PDF 생성 성공
- [ ] 모바일/데스크톱 반응형 동작

## 참고 문서

- [PRD](docs/prd/PRD.md) - 제품 요구사항
- [Architecture](docs/architecture/ARCHITECTURE.md) - 아키텍처 설계
- [Daily Content Schema](docs/content/DAILY_CONTENT_SCHEMA.json) - 콘텐츠 스키마
- [Terminology Policy](docs/legal/TERMINOLOGY_POLICY.md) - 용어 정책
- [Workplan](docs/tasks/WORKPLAN.md) - 현재 작업 계획
