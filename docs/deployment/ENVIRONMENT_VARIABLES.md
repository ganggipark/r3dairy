# R³ Diary System - 환경 변수 가이드

## 목차
1. [Backend 환경 변수](#backend-환경-변수)
2. [Frontend 환경 변수](#frontend-환경-변수)
3. [Supabase 설정](#supabase-설정)
4. [배포 플랫폼별 설정](#배포-플랫폼별-설정)

## Backend 환경 변수

### 필수 환경 변수

```bash
# Application
ENVIRONMENT=production                    # development | test | production
PORT=8000                                # 포트 번호 (Railway/Render는 자동 설정)

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key  # 선택사항 (관리 작업용)

# CORS
CORS_ORIGINS=https://your-frontend.vercel.app,https://custom-domain.com
```

### 선택적 환경 변수

```bash
# Logging
LOG_LEVEL=INFO                           # DEBUG | INFO | WARNING | ERROR

# PDF Generator
PDF_OUTPUT_DIR=/tmp/pdfs                 # PDF 임시 저장 경로

# Rate Limiting (구현 시)
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60
```

## Frontend 환경 변수

### 필수 환경 변수

```bash
# Backend API
NEXT_PUBLIC_API_URL=https://your-backend.railway.app

# Supabase
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-supabase-anon-key
```

### 선택적 환경 변수

```bash
# Analytics (구현 시)
NEXT_PUBLIC_GA_ID=G-XXXXXXXXXX           # Google Analytics
NEXT_PUBLIC_SENTRY_DSN=https://...       # Sentry 에러 트래킹
```

## Supabase 설정

### 1. Supabase 프로젝트 생성
1. https://supabase.com 접속
2. "New Project" 클릭
3. 프로젝트 이름 입력 (예: r3-diary-prod)
4. 강력한 데이터베이스 비밀번호 설정
5. Region 선택 (권장: Northeast Asia (Seoul))

### 2. 데이터베이스 스키마 설정
```sql
-- backend/src/db/schema.sql 내용 실행
-- Database → SQL Editor → New Query에서 실행
```

### 3. API 키 확인
- **Settings** → **API** 메뉴
- **Project URL**: `SUPABASE_URL`로 사용
- **anon public**: `SUPABASE_KEY` 및 `NEXT_PUBLIC_SUPABASE_ANON_KEY`로 사용
- **service_role** (선택): `SUPABASE_SERVICE_ROLE_KEY`로 사용

### 4. 인증 설정
- **Authentication** → **Providers**
- Email 인증 활성화
- OAuth 프로바이더 설정 (선택)

### 5. RLS (Row Level Security) 활성화
```sql
-- profiles 테이블 예시
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own profile"
ON profiles FOR SELECT
USING (auth.uid() = id);

CREATE POLICY "Users can update own profile"
ON profiles FOR UPDATE
USING (auth.uid() = id);
```

## 배포 플랫폼별 설정

### Vercel (Frontend)

#### CLI 배포
```bash
cd frontend

# Vercel 로그인
npx vercel login

# 환경 변수 설정
npx vercel env add NEXT_PUBLIC_API_URL
npx vercel env add NEXT_PUBLIC_SUPABASE_URL
npx vercel env add NEXT_PUBLIC_SUPABASE_ANON_KEY

# 배포
npx vercel --prod
```

#### 대시보드 설정
1. https://vercel.com 로그인
2. **New Project** → GitHub 저장소 선택
3. **Environment Variables** 추가:
   - `NEXT_PUBLIC_API_URL`
   - `NEXT_PUBLIC_SUPABASE_URL`
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY`
4. **Deploy** 클릭

### Railway (Backend - 권장)

#### CLI 배포
```bash
cd backend

# Railway 로그인
railway login

# 새 프로젝트 생성
railway init

# 환경 변수 설정
railway variables set ENVIRONMENT=production
railway variables set SUPABASE_URL=https://your-project.supabase.co
railway variables set SUPABASE_KEY=your-key
railway variables set CORS_ORIGINS=https://your-frontend.vercel.app

# 배포
railway up
```

#### 대시보드 설정
1. https://railway.app 로그인
2. **New Project** → **Deploy from GitHub repo**
3. 저장소 선택 및 `backend` 디렉토리 지정
4. **Variables** 탭에서 환경 변수 추가
5. **Deployments** 탭에서 배포 확인

### Render (Backend - 대안)

#### 대시보드 설정
1. https://render.com 로그인
2. **New** → **Web Service**
3. GitHub 저장소 연결
4. 설정:
   - **Name**: r3-diary-backend
   - **Environment**: Docker
   - **Dockerfile Path**: backend/Dockerfile
   - **Environment Variables** 추가 (위의 필수 변수)
5. **Create Web Service** 클릭

## 환경 변수 체크리스트

### 로컬 개발
- [ ] `backend/.env` 파일 생성
- [ ] `frontend/.env.local` 파일 생성
- [ ] Supabase 개발 프로젝트 생성
- [ ] 환경 변수 모두 설정 확인

### 프로덕션 배포
- [ ] Supabase 프로덕션 프로젝트 생성
- [ ] Supabase 스키마 마이그레이션 완료
- [ ] Vercel 환경 변수 설정 (3개)
- [ ] Railway/Render 환경 변수 설정 (4개 이상)
- [ ] CORS_ORIGINS에 프로덕션 도메인 추가
- [ ] Backend 헬스체크 확인 (`/health`)
- [ ] Frontend 빌드 및 배포 성공

### 보안 체크리스트
- [ ] Service Role Key는 Backend에만 설정 (Frontend 금지)
- [ ] 환경 변수 파일을 Git에 커밋하지 않음 (.gitignore 확인)
- [ ] 프로덕션 비밀번호는 충분히 강력함 (20자 이상)
- [ ] CORS_ORIGINS는 필요한 도메인만 포함
- [ ] Supabase RLS 정책 활성화됨

## 트러블슈팅

### Backend가 Supabase에 연결 실패
```bash
# 환경 변수 확인
echo $SUPABASE_URL
echo $SUPABASE_KEY

# URL 형식 확인 (https://로 시작해야 함)
# 키가 올바른지 Supabase 대시보드에서 재확인
```

### Frontend에서 Backend API 호출 실패
```bash
# NEXT_PUBLIC_API_URL 확인
# 브라우저 콘솔에서 확인
console.log(process.env.NEXT_PUBLIC_API_URL)

# CORS 설정 확인
# Backend의 CORS_ORIGINS에 Frontend 도메인 추가되어 있는지 확인
```

### Railway/Render 빌드 실패
```bash
# Dockerfile 경로 확인
# Railway: Root 디렉토리 설정이 backend인지 확인
# Render: Dockerfile Path가 backend/Dockerfile인지 확인

# 환경 변수 누락 확인
# 필수 환경 변수가 모두 설정되어 있는지 확인
```

### PDF 생성 실패 (WeasyPrint)
```bash
# 시스템 의존성 확인
# Dockerfile에 cairo, pango 등이 설치되어 있는지 확인

# 메모리 부족 시
# Railway/Render 플랜 업그레이드 필요 (최소 512MB RAM)
```

## 참고 문서
- [Supabase 공식 문서](https://supabase.com/docs)
- [Vercel 환경 변수](https://vercel.com/docs/concepts/projects/environment-variables)
- [Railway 문서](https://docs.railway.app/)
- [Render 문서](https://render.com/docs)
