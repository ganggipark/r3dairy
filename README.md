# R³ Diary System

**Rhythm → Response → Recode**

출생 정보 기반 리듬 분석과 사용자 기록을 결합한 개인 맞춤 다이어리 애플리케이션

## 프로젝트 개요

R³ 다이어리는 사용자의 출생 정보를 기반으로 매일의 흐름(리듬)을 분석하고, 이를 실용적인 가이드로 변환하여 제공하는 다이어리 시스템입니다. 웹앱과 인쇄(PDF) 출력을 동시에 지원합니다.

### R³ 시스템이란?

- **Rhythm**: 출생 데이터 기반으로 오늘의 흐름/리듬 분석
- **Response**: 자동 반응(불안, 충동, 미루기 등) 인지
- **Recode**: 언어/질문/기록으로 반응을 재설계

## 주요 기능

- ✅ 사용자 프로필 입력 (출생 정보, 역할, 선호사항)
- ✅ 오늘/이번 달/올해 화면
- ✅ 일간 페이지 렌더링 (좌측: 안내, 우측: 기록)
- ✅ 역할 기반 콘텐츠 변형 (학생/직장인/프리랜서)
- ✅ PDF 출력 (월간 + 일간 페이지)

## 기술 스택

### Backend
- **Python 3.11+** - 프로그래밍 언어
- **FastAPI** - 웹 프레임워크
- **Supabase** - 데이터베이스 (PostgreSQL + Auth)
- **WeasyPrint** - PDF 생성

### Frontend
- **Next.js 14+** - React 프레임워크 (App Router)
- **TypeScript** - 타입 안전성
- **Tailwind CSS** - 스타일링
- **shadcn/ui** - UI 컴포넌트

### DevOps
- **Vercel** - Frontend 배포
- **Railway/Render** - Backend 배포
- **GitHub Actions** - CI/CD

## 프로젝트 구조

```
diary-PJ/
├── docs/              # 문서
├── backend/           # Python FastAPI 백엔드
├── frontend/          # Next.js 프론트엔드
├── pdf-generator/     # PDF 생성 엔진
├── .gitignore
├── CLAUDE.md          # 개발 가이드
└── README.md          # 이 파일
```

## 시작하기

### 필수 요구사항

- **Python 3.11+**
- **Node.js 18+**
- **npm 또는 yarn**
- **Supabase 계정**

### Backend 설정

```bash
# 1. 가상환경 생성 및 활성화
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 2. 의존성 설치
pip install -r requirements.txt

# 3. 환경변수 설정
cp .env.example .env
# .env 파일을 열어 Supabase URL, Key 등을 입력하세요

# 4. 개발 서버 실행
uvicorn src.main:app --reload
```

Backend가 http://localhost:8000 에서 실행됩니다.

### Frontend 설정

```bash
# 1. 의존성 설치
cd frontend
npm install

# 2. 환경변수 설정
cp .env.example .env.local
# .env.local 파일을 열어 API URL 등을 입력하세요

# 3. 개발 서버 실행
npm run dev
```

Frontend가 http://localhost:3000 에서 실행됩니다.

### Supabase 설정

1. https://supabase.com 에서 프로젝트 생성
2. **Database → SQL Editor**에서 `backend/src/db/schema.sql` 실행
3. **Project Settings → API**에서 URL과 anon key 복사
4. `backend/.env`와 `frontend/.env.local`에 추가

## API 문서

Backend 서버 실행 후 http://localhost:8000/docs 에서 Swagger UI를 확인하세요.

## 개발 가이드

상세한 개발 가이드는 [CLAUDE.md](./CLAUDE.md)를 참조하세요.

- 기술 스택 상세 설명
- 프로젝트 구조 및 아키텍처
- API 엔드포인트 목록
- 테스트 실행 방법
- 빌드 및 배포
- 트러블슈팅

## 주요 문서

- [PRD](docs/prd/PRD.md) - 제품 요구사항
- [Architecture](docs/architecture/ARCHITECTURE.md) - 아키텍처 설계
- [Daily Content Schema](docs/content/DAILY_CONTENT_SCHEMA.json) - 콘텐츠 스키마
- [Terminology Policy](docs/legal/TERMINOLOGY_POLICY.md) - 용어 정책
- [Workplan](docs/tasks/WORKPLAN.md) - 작업 계획

## 테스트

### Backend 테스트
```bash
cd backend
pytest tests/ -v
```

### Frontend 테스트
```bash
cd frontend
npm test
```

## 배포

### Frontend (Vercel)
```bash
cd frontend
npm run build
vercel --prod
```

### Backend (Railway)
```bash
cd backend
railway up
```

## 라이센스

이 프로젝트는 비공개 프로젝트입니다.

## 연락처

문의사항이 있으시면 프로젝트 관리자에게 연락주세요.

---

**R³ Diary System v0.1.0** - Rhythm, Response, Recode
