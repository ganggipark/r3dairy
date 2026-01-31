# R³ 다이어리 시스템 - 배포 가이드

## 배포 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                      사용자 브라우저                          │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        │ HTTPS
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                  Vercel (Frontend)                           │
│                  - Next.js 14 App                            │
│                  - Static Assets                             │
│                  - Edge Functions                            │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        │ API Calls (HTTPS)
                        ▼
┌─────────────────────────────────────────────────────────────┐
│            Railway/Render (Backend)                          │
│            - FastAPI Application                             │
│            - Python 3.10+                                    │
│            - WeasyPrint (PDF Generation)                     │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        │ PostgreSQL + Auth
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                  Supabase (Database)                         │
│                  - PostgreSQL 15                             │
│                  - Authentication                            │
│                  - Row Level Security                        │
└─────────────────────────────────────────────────────────────┘
```

## 배포 체크리스트

### 사전 준비

- [ ] GitHub 저장소 생성 및 코드 푸시
- [ ] Supabase 프로젝트 생성
- [ ] Vercel 계정 생성
- [ ] Railway 또는 Render 계정 생성

### Backend 배포 (Railway/Render)

- [ ] Railway/Render 프로젝트 생성
- [ ] 환경 변수 설정
  - [ ] `SUPABASE_URL`
  - [ ] `SUPABASE_KEY`
  - [ ] `CORS_ORIGINS`
  - [ ] `ENVIRONMENT=production`
- [ ] `requirements.txt` 확인
- [ ] 시스템 라이브러리 설정 (WeasyPrint 의존성)
- [ ] 헬스체크 엔드포인트 확인 (`/health`)
- [ ] API 문서 접근 확인 (`/docs`)
- [ ] 도메인 확인 (예: `https://r3-diary-api.railway.app`)

### Frontend 배포 (Vercel)

- [ ] Vercel 프로젝트 생성
- [ ] GitHub 저장소 연결
- [ ] 환경 변수 설정
  - [ ] `NEXT_PUBLIC_SUPABASE_URL`
  - [ ] `NEXT_PUBLIC_SUPABASE_ANON_KEY`
  - [ ] `NEXT_PUBLIC_API_URL` (Backend URL)
- [ ] 빌드 설정 확인
  - Root Directory: `frontend`
  - Build Command: `npm run build`
  - Output Directory: `.next`
- [ ] 프로덕션 빌드 테스트
- [ ] 도메인 확인 (예: `https://r3-diary.vercel.app`)

### Database 설정 (Supabase)

- [ ] 프로덕션 프로젝트 생성
- [ ] 데이터베이스 스키마 마이그레이션
- [ ] Row Level Security (RLS) 정책 적용
- [ ] API 키 확인 (anon key, service_role key)
- [ ] 인증 설정 (이메일, OAuth 등)

### CI/CD 파이프라인

- [ ] GitHub Actions 워크플로우 작성
- [ ] 자동 테스트 실행
- [ ] 자동 배포 설정
- [ ] 배포 알림 설정 (선택)

### 최종 검증

- [ ] Frontend 접속 테스트
- [ ] Backend API 호출 테스트
- [ ] 회원가입/로그인 테스트
- [ ] 프로필 생성 테스트
- [ ] 일간 콘텐츠 조회 테스트
- [ ] 역할별 변환 테스트
- [ ] PDF 생성 테스트
- [ ] 모바일 반응형 테스트

---

## 1. Backend 배포 (Railway)

### Railway 배포 설정

**railway.json** (또는 **railway.toml**):

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn src.main:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### 시스템 라이브러리 설정 (WeasyPrint)

**Aptfile** (Railway에서 시스템 패키지 설치):

```
libcairo2
libpango-1.0-0
libpangocairo-1.0-0
libgdk-pixbuf2.0-0
libffi-dev
shared-mime-info
fonts-nanum
fonts-nanum-coding
```

### 환경 변수 설정

Railway 대시보드에서 다음 환경 변수 추가:

```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-role-key
CORS_ORIGINS=https://r3-diary.vercel.app
ENVIRONMENT=production
PORT=8000
```

### 배포 명령어

```bash
# Railway CLI 설치
npm install -g @railway/cli

# Railway 로그인
railway login

# 프로젝트 초기화
railway init

# 환경 변수 설정
railway variables set SUPABASE_URL=https://...
railway variables set SUPABASE_KEY=...
railway variables set CORS_ORIGINS=https://...

# 배포
railway up
```

### 헬스체크

```bash
curl https://your-backend.railway.app/health
```

예상 응답:
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "environment": "production"
}
```

---

## 2. Frontend 배포 (Vercel)

### Vercel 프로젝트 설정

1. Vercel 대시보드에서 "New Project" 클릭
2. GitHub 저장소 연결
3. Framework Preset: **Next.js** 선택
4. Root Directory: **`frontend`** 설정
5. Build Command: `npm run build`
6. Output Directory: `.next`

### 환경 변수 설정

Vercel 대시보드 → Settings → Environment Variables:

```bash
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
```

### 배포 명령어 (Vercel CLI)

```bash
# Vercel CLI 설치
npm install -g vercel

# 프로젝트 디렉토리에서 실행
cd frontend

# 로그인
vercel login

# 배포
vercel --prod
```

### 도메인 설정 (선택)

Vercel 대시보드 → Settings → Domains에서 커스텀 도메인 추가 가능:
- `r3-diary.com`
- `www.r3-diary.com`

---

## 3. Supabase 프로덕션 설정

### 프로젝트 생성

1. [Supabase Dashboard](https://app.supabase.com/) 접속
2. "New Project" 클릭
3. Organization 선택
4. Project Name: `r3-diary-prod`
5. Database Password: 강력한 비밀번호 설정
6. Region: 한국과 가까운 리전 선택 (예: Singapore, Tokyo)

### 데이터베이스 마이그레이션

**SQL Editor**에서 다음 스키마 실행:

```sql
-- profiles 테이블
CREATE TABLE profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id),
    name VARCHAR(100) NOT NULL,
    birth_date DATE NOT NULL,
    birth_time TIME NOT NULL,
    gender VARCHAR(10) NOT NULL,
    birth_place VARCHAR(200) NOT NULL,
    roles JSONB NOT NULL DEFAULT '[]',
    preferences JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- daily_logs 테이블
CREATE TABLE daily_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    schedule TEXT,
    todos JSONB,
    mood INTEGER CHECK (mood >= 1 AND mood <= 5),
    energy INTEGER CHECK (energy >= 1 AND energy <= 5),
    notes TEXT,
    gratitude TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(profile_id, date)
);

-- Row Level Security (RLS) 활성화
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE daily_logs ENABLE ROW LEVEL SECURITY;

-- RLS 정책: 본인만 조회/수정 가능
CREATE POLICY "Users can view own profile"
    ON profiles FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY "Users can update own profile"
    ON profiles FOR UPDATE
    USING (auth.uid() = id);

CREATE POLICY "Users can insert own profile"
    ON profiles FOR INSERT
    WITH CHECK (auth.uid() = id);

CREATE POLICY "Users can manage own logs"
    ON daily_logs FOR ALL
    USING (auth.uid() = profile_id);

-- 인덱스 추가
CREATE INDEX idx_daily_logs_profile_date ON daily_logs(profile_id, date);
CREATE INDEX idx_profiles_id ON profiles(id);
```

### Authentication 설정

Supabase Dashboard → Authentication → Settings:

1. **Email Auth**: Enabled
2. **Confirm Email**: Enabled (권장)
3. **Email Templates**: 한국어로 커스터마이징 (선택)

### API 키 확인

Supabase Dashboard → Settings → API:

- `SUPABASE_URL`: `https://xxxxx.supabase.co`
- `anon` key: Frontend에서 사용 (NEXT_PUBLIC_SUPABASE_ANON_KEY)
- `service_role` key: Backend에서 사용 (SUPABASE_KEY) - **절대 노출 금지**

---

## 4. CI/CD 파이프라인 (GitHub Actions)

### `.github/workflows/backend-deploy.yml`

```yaml
name: Backend Deploy

on:
  push:
    branches:
      - main
    paths:
      - 'backend/**'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt

      - name: Run tests
        run: |
          cd backend
          pytest tests/ -v

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Deploy to Railway
        run: |
          npm install -g @railway/cli
          railway up --service backend
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
```

### `.github/workflows/frontend-deploy.yml`

```yaml
name: Frontend Deploy

on:
  push:
    branches:
      - main
    paths:
      - 'frontend/**'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install dependencies
        run: |
          cd frontend
          npm ci

      - name: Build
        run: |
          cd frontend
          npm run build
        env:
          NEXT_PUBLIC_SUPABASE_URL: ${{ secrets.NEXT_PUBLIC_SUPABASE_URL }}
          NEXT_PUBLIC_SUPABASE_ANON_KEY: ${{ secrets.NEXT_PUBLIC_SUPABASE_ANON_KEY }}
          NEXT_PUBLIC_API_URL: ${{ secrets.NEXT_PUBLIC_API_URL }}

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          working-directory: ./frontend
```

---

## 5. 환경 변수 관리

### GitHub Secrets 설정

GitHub Repository → Settings → Secrets and variables → Actions:

**Backend**:
- `RAILWAY_TOKEN`: Railway API token
- `SUPABASE_URL`: Supabase 프로젝트 URL
- `SUPABASE_KEY`: Supabase service_role key

**Frontend**:
- `VERCEL_TOKEN`: Vercel API token
- `VERCEL_ORG_ID`: Vercel Organization ID
- `VERCEL_PROJECT_ID`: Vercel Project ID
- `NEXT_PUBLIC_SUPABASE_URL`: Supabase URL (public)
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`: Supabase anon key (public)
- `NEXT_PUBLIC_API_URL`: Backend API URL

---

## 6. 모니터링 & 로깅

### Railway 모니터링

Railway Dashboard에서 자동으로 제공:
- CPU/Memory 사용량
- Request logs
- Deployment history

### Vercel 분석

Vercel Dashboard에서 제공:
- Web Analytics
- Real User Monitoring (Core Web Vitals)
- Function logs

### Supabase 모니터링

Supabase Dashboard → Reports:
- API requests
- Database performance
- Auth activity

---

## 7. 배포 후 검증

### 배포 체크리스트

```bash
# 1. Backend Health Check
curl https://your-backend.railway.app/health

# 2. Backend API 문서 확인
open https://your-backend.railway.app/docs

# 3. Frontend 접속
open https://r3-diary.vercel.app

# 4. 회원가입 테스트
# 브라우저에서 회원가입 → 이메일 인증

# 5. 프로필 생성
# 생년월일, 시간, 성별, 출생지 입력

# 6. 일간 콘텐츠 조회
# "오늘" 페이지 접속 → 콘텐츠 표시 확인

# 7. 역할별 변환
# 역할 선택 (학생/직장인/프리랜서) → 표현 차이 확인

# 8. PDF 다운로드 (Linux 환경에서만)
curl -H "Authorization: Bearer {token}" \
     https://your-backend.railway.app/api/pdf/daily/2026-01-21 \
     --output test.pdf
```

---

## 8. 문제 해결

### Backend 배포 실패

**증상**: `ModuleNotFoundError` 또는 의존성 오류

**해결**:
```bash
# requirements.txt 확인
cd backend
pip freeze > requirements.txt

# Railway에서 재배포
railway up
```

### WeasyPrint 오류 (PDF 생성 실패)

**증상**: `OSError: cannot load library 'libgobject-2.0-0'`

**해결**:
- `Aptfile`에 시스템 라이브러리 추가 확인
- Railway는 자동으로 Aptfile 인식
- Render는 `render.yaml`에서 설정 필요

### Frontend 빌드 오류

**증상**: `Error: Environment variables not found`

**해결**:
```bash
# Vercel 환경 변수 확인
vercel env ls

# 환경 변수 추가
vercel env add NEXT_PUBLIC_SUPABASE_URL
```

### CORS 오류

**증상**: `Access-Control-Allow-Origin` 오류

**해결**:
```python
# backend/src/main.py
origins = [
    "https://r3-diary.vercel.app",
    "https://your-custom-domain.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 9. 프로덕션 최적화

### Backend 최적화

1. **Connection Pooling**: Supabase 연결 풀 설정
2. **Caching**: Redis 추가 (선택)
3. **Rate Limiting**: API 호출 제한
4. **Logging**: Structured logging (JSON)

### Frontend 최적화

1. **Image Optimization**: Next.js Image 컴포넌트 사용
2. **Code Splitting**: Dynamic imports
3. **CDN**: Vercel Edge Network (자동)
4. **SEO**: Meta tags, sitemap, robots.txt

---

## 배포 완료!

프로덕션 URL:
- **Frontend**: `https://r3-diary.vercel.app`
- **Backend**: `https://r3-diary-api.railway.app`
- **API Docs**: `https://r3-diary-api.railway.app/docs`

다음 단계:
1. 사용자 피드백 수집
2. 성능 모니터링
3. 버그 수정 및 개선
4. 새로운 기능 추가

---

**배포 가이드 버전**: 1.0
**작성일**: 2026-01-21
**R³ 다이어리 시스템**: MVP 배포 완료
