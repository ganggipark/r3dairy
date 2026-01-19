# R³ Diary System - 배포 가이드

## 목차
1. [개요](#개요)
2. [사전 준비](#사전-준비)
3. [Supabase 설정](#supabase-설정)
4. [Backend 배포 (Railway)](#backend-배포-railway)
5. [Frontend 배포 (Vercel)](#frontend-배포-vercel)
6. [CI/CD 설정](#cicd-설정)
7. [배포 후 검증](#배포-후-검증)
8. [롤백 및 트러블슈팅](#롤백-및-트러블슈팅)

## 개요

R³ Diary System의 프로덕션 배포는 다음과 같이 구성됩니다:
- **Frontend**: Vercel (Next.js 앱)
- **Backend**: Railway 또는 Render (FastAPI + Docker)
- **Database**: Supabase (PostgreSQL + Auth)
- **CI/CD**: GitHub Actions

## 사전 준비

### 1. 계정 생성
- [x] GitHub 계정 (코드 저장소)
- [ ] Supabase 계정 (https://supabase.com)
- [ ] Vercel 계정 (https://vercel.com)
- [ ] Railway 계정 (https://railway.app) 또는 Render (https://render.com)

### 2. 도구 설치
```bash
# Vercel CLI
npm install -g vercel

# Railway CLI (선택)
npm install -g @railway/cli

# Git (이미 설치되어 있어야 함)
git --version
```

### 3. 코드 저장소 준비
```bash
# GitHub에 저장소 생성
# https://github.com/new

# 로컬 저장소 연결
cd /path/to/diary-PJ
git init
git remote add origin https://github.com/your-username/r3-diary.git
git add .
git commit -m "Initial commit - R³ Diary System MVP"
git push -u origin main
```

## Supabase 설정

### 1. 프로젝트 생성
1. https://supabase.com 로그인
2. **New Project** 클릭
3. 설정:
   - **Name**: r3-diary-production
   - **Database Password**: 강력한 비밀번호 (20자 이상)
   - **Region**: Northeast Asia (Seoul) - 권장
4. **Create new project** 클릭 (1-2분 소요)

### 2. 데이터베이스 스키마 마이그레이션
```sql
-- Dashboard → Database → SQL Editor → New Query

-- backend/src/db/schema.sql 내용 복사 후 실행
-- 또는 파일 업로드

RUN
```

### 3. Row Level Security (RLS) 설정
```sql
-- profiles 테이블
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own profile"
ON profiles FOR SELECT
USING (auth.uid() = id);

CREATE POLICY "Users can update own profile"
ON profiles FOR UPDATE
USING (auth.uid() = id);

-- daily_content 테이블
ALTER TABLE daily_content ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own content"
ON daily_content FOR SELECT
USING (auth.uid() = profile_id);

-- daily_logs 테이블
ALTER TABLE daily_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage own logs"
ON daily_logs FOR ALL
USING (auth.uid() = profile_id);
```

### 4. API 키 확인
**Settings** → **API** 메뉴에서 다음 정보 복사:
- **Project URL**: `https://xxx.supabase.co`
- **anon public**: `eyJhbGci...`

이 정보는 환경 변수로 사용됩니다.

## Backend 배포 (Railway)

### Option 1: Railway CLI

```bash
cd backend

# Railway 로그인
railway login

# 새 프로젝트 생성
railway init

# 환경 변수 설정
railway variables set ENVIRONMENT=production
railway variables set SUPABASE_URL=https://your-project.supabase.co
railway variables set SUPABASE_KEY=your-anon-key
railway variables set CORS_ORIGINS=https://your-frontend.vercel.app

# 배포
railway up

# 배포 URL 확인
railway status
# 예: https://r3-diary-backend-production.up.railway.app
```

### Option 2: Railway 대시보드

1. https://railway.app 로그인
2. **New Project** 클릭
3. **Deploy from GitHub repo** 선택
4. 저장소 선택 (your-username/r3-diary)
5. **Configure**:
   - **Root Directory**: `backend`
   - **Builder**: Dockerfile
6. **Variables** 탭으로 이동하여 환경 변수 추가:
   ```
   ENVIRONMENT=production
   SUPABASE_URL=https://xxx.supabase.co
   SUPABASE_KEY=eyJhbGci...
   CORS_ORIGINS=https://your-app.vercel.app
   ```
7. **Deploy** 클릭
8. 배포 완료 후 **Settings** → **Domains**에서 URL 확인

### Backend 배포 검증
```bash
# 헬스체크
curl https://your-backend.railway.app/health

# API 문서
https://your-backend.railway.app/docs
```

## Frontend 배포 (Vercel)

### Option 1: Vercel CLI

```bash
cd frontend

# Vercel 로그인
vercel login

# 환경 변수 설정
vercel env add NEXT_PUBLIC_API_URL production
# 입력: https://your-backend.railway.app

vercel env add NEXT_PUBLIC_SUPABASE_URL production
# 입력: https://xxx.supabase.co

vercel env add NEXT_PUBLIC_SUPABASE_ANON_KEY production
# 입력: eyJhbGci...

# 프로덕션 배포
vercel --prod

# 배포 URL 확인 (자동 출력됨)
# 예: https://r3-diary.vercel.app
```

### Option 2: Vercel 대시보드

1. https://vercel.com 로그인
2. **Add New** → **Project**
3. GitHub 저장소 import (your-username/r3-diary)
4. **Configure Project**:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
5. **Environment Variables** 추가:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend.railway.app
   NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
   NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGci...
   ```
6. **Deploy** 클릭
7. 배포 완료 후 **Visit** 버튼으로 확인

### Frontend 배포 검증
1. 브라우저에서 `https://your-app.vercel.app` 접속
2. 회원가입 페이지 작동 확인
3. 로그인 후 프로필 페이지 작동 확인

## CORS 설정 업데이트

Frontend 배포 후 Backend의 CORS 설정 업데이트 필요:

```bash
# Railway에서 환경 변수 업데이트
railway variables set CORS_ORIGINS=https://your-app.vercel.app

# 또는 대시보드에서 Variables → Edit
```

배포 자동 재시작됨.

## CI/CD 설정

### GitHub Actions 활성화

1. GitHub 저장소 → **Settings** → **Secrets and variables** → **Actions**
2. **New repository secret** 클릭하여 다음 추가:
   ```
   CODECOV_TOKEN=your-codecov-token (선택사항)
   ```
3. `.github/workflows/` 디렉토리에 워크플로우 파일 확인:
   - `backend-ci.yml` - Backend 테스트 및 빌드
   - `frontend-ci.yml` - Frontend 테스트 및 빌드

### 자동 배포 설정

**Vercel** (Frontend):
- GitHub 연동 시 자동 설정됨
- `main` 브랜치 푸시 → 자동 배포

**Railway** (Backend):
- Dashboard → Settings → **GitHub Repo** 연결
- `main` 브랜치 푸시 → 자동 배포
- **Watch Paths**: `backend/**`로 설정 (Backend 변경 시만 재배포)

## 배포 후 검증

### 체크리스트
- [ ] Backend 헬스체크 성공 (`/health`)
- [ ] Backend API 문서 접근 가능 (`/docs`)
- [ ] Frontend 홈페이지 로드 성공
- [ ] 회원가입 플로우 작동
- [ ] 로그인 플로우 작동
- [ ] 프로필 생성 작동
- [ ] 일간 콘텐츠 조회 작동
- [ ] 사용자 기록 저장 작동
- [ ] PDF 다운로드 작동
- [ ] 모바일 반응형 확인

### 성능 확인
```bash
# Backend 응답 시간
curl -w "@curl-format.txt" -o /dev/null -s https://your-backend.railway.app/health

# Frontend Lighthouse 점수
# Chrome DevTools → Lighthouse 실행
```

### 에러 모니터링 (선택)
- **Sentry** 연동 (Frontend/Backend 에러 트래킹)
- **LogRocket** 연동 (사용자 세션 리플레이)

## 롤백 및 트러블슈팅

### Vercel 롤백
```bash
# 이전 배포 목록 확인
vercel ls

# 특정 배포로 롤백
vercel rollback [deployment-url]
```

또는 대시보드에서:
1. **Deployments** 탭
2. 이전 배포 선택 → **Promote to Production**

### Railway 롤백
1. Dashboard → **Deployments** 탭
2. 이전 배포 선택 → **Rollback**

### 일반적인 문제

#### 1. Backend가 시작되지 않음
```bash
# 로그 확인
railway logs

# 환경 변수 확인
railway variables

# Dockerfile 빌드 확인
docker build -t test-backend backend/
docker run -p 8000:8000 test-backend
```

#### 2. Frontend에서 API 호출 실패
- NEXT_PUBLIC_API_URL 확인
- CORS_ORIGINS에 Frontend 도메인 추가 확인
- 브라우저 콘솔에서 에러 메시지 확인

#### 3. PDF 생성 실패
- WeasyPrint 시스템 의존성 확인 (Dockerfile)
- 메모리 부족 시 플랜 업그레이드 필요

#### 4. Supabase 연결 실패
- SUPABASE_URL 형식 확인 (`https://`로 시작)
- SUPABASE_KEY 올바른지 확인
- Supabase 프로젝트 상태 확인 (일시 중단되지 않았는지)

## 모니터링 및 유지보수

### 정기 체크 항목
- [ ] Supabase 사용량 확인 (무료 플랜 제한)
- [ ] Railway/Render 크레딧 확인
- [ ] 에러 로그 확인
- [ ] 성능 메트릭 확인

### 업데이트 배포
```bash
# 코드 변경 후
git add .
git commit -m "Feature: Add new functionality"
git push origin main

# GitHub Actions 자동 실행
# Vercel/Railway 자동 배포
```

## 참고 문서
- [환경 변수 가이드](./ENVIRONMENT_VARIABLES.md)
- [Supabase 공식 문서](https://supabase.com/docs)
- [Vercel 배포 가이드](https://vercel.com/docs)
- [Railway 문서](https://docs.railway.app/)
