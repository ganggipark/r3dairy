# R³ Diary System - 빠른 배포 가이드

이 문서는 **5단계로 배포를 완료**할 수 있도록 최소한의 명령어만 제공합니다.

## 사전 확인 ✅

사용자님이 이미 완료한 작업:
- ✅ Supabase 프로젝트 생성
- ✅ SQL 스키마 실행 (`schema.sql`)
- ✅ Supabase anon key 확인: `sb_publishable_MmUagrOK0ptxcljT09izxg_kGQguOSn`

## Step 1: GitHub에 코드 푸시

```bash
# 프로젝트 루트에서 실행
cd E:\project\diary-PJ

# Git 저장소 초기화 (아직 안 했다면)
git init

# 모든 파일 추가
git add .

# 커밋
git commit -m "R³ Diary System MVP - Ready for deployment"

# GitHub 저장소 생성 후 (https://github.com/new)
git remote add origin https://github.com/your-username/r3-diary.git
git branch -M main
git push -u origin main
```

## Step 2: Backend 배포 (Render)

### 2-1. Render 설정

1. https://render.com 접속 및 로그인
2. **New** → **Blueprint** 클릭
3. GitHub 저장소 연결: `your-username/r3-diary`
4. Render가 `render.yaml` 자동 감지

### 2-2. 환경 변수 설정

Dashboard → **r3-diary-backend** → **Environment** 탭에서 추가:

```bash
# Supabase 연결
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=sb_publishable_MmUagrOK0ptxcljT09izxg_kGQguOSn

# CORS (나중에 Vercel URL로 업데이트)
CORS_ORIGINS=https://r3-diary.vercel.app
```

### 2-3. 배포 시작

- **Save Changes** → 자동 빌드 시작
- 5-10분 대기
- 배포 완료 후 **URL 복사** (예: `https://r3-diary-backend.onrender.com`)

### 2-4. 검증

```bash
curl https://r3-diary-backend.onrender.com/health
# 응답: {"status": "healthy"}
```

## Step 3: Frontend 배포 (Vercel)

```bash
cd frontend

# Vercel 로그인
npx vercel login

# 환경 변수 설정
npx vercel env add NEXT_PUBLIC_API_URL production
# 입력: https://r3-diary-backend.onrender.com

npx vercel env add NEXT_PUBLIC_SUPABASE_URL production
# 입력: https://your-project.supabase.co

npx vercel env add NEXT_PUBLIC_SUPABASE_ANON_KEY production
# 입력: sb_publishable_MmUagrOK0ptxcljT09izxg_kGQguOSn

# 프로덕션 배포
npx vercel --prod
```

배포 완료 후 **URL 확인** (예: `https://r3-diary.vercel.app`)

## Step 4: CORS 업데이트

Frontend URL이 확정되었으므로 Backend CORS를 업데이트합니다:

1. Render Dashboard → **r3-diary-backend** → **Environment**
2. `CORS_ORIGINS` 값 수정:
   ```
   https://r3-diary.vercel.app
   ```
3. **Save Changes** → 자동 재배포

## Step 5: 배포 검증

### Backend 확인
```bash
# 헬스체크
curl https://r3-diary-backend.onrender.com/health

# API 문서
https://r3-diary-backend.onrender.com/docs
```

### Frontend 확인
1. https://r3-diary.vercel.app 접속
2. 회원가입 → 로그인
3. 프로필 입력 (출생 정보)
4. 오늘 페이지 조회
5. 기록 저장
6. PDF 다운로드

## 완료! 🎉

**배포된 서비스**:
- Frontend: `https://r3-diary.vercel.app`
- Backend: `https://r3-diary-backend.onrender.com`
- Database: Supabase (PostgreSQL + Auth)

**비용**: $0/월 (모두 무료 티어)

## 주의사항

### Render 무료 티어 제한
- ⚠️ **15분간 요청 없으면 Spin Down** (다음 요청 시 30초~1분 소요)
- 해결책: Starter 플랜 ($7/월) 또는 핑 서비스 사용

### Supabase 무료 티어 제한
- 500MB 데이터베이스
- 50,000 월간 활성 사용자
- 2GB 파일 스토리지

## 트러블슈팅

### Backend 시작 안 됨
```bash
# Render 로그 확인
Dashboard → r3-diary-backend → Logs
```

### Frontend에서 API 호출 실패
```bash
# CORS 확인
1. Render → CORS_ORIGINS 값 확인
2. Frontend → .env.local의 NEXT_PUBLIC_API_URL 확인
```

### PDF 생성 실패
- 원인: 메모리 부족 (무료 티어 512MB)
- 해결: Starter 플랜 업그레이드 또는 PDF 크기 최적화

## 다음 단계

### 커스텀 도메인 (선택)
- Vercel: Settings → Domains
- Render: Settings → Custom Domain

### 모니터링
- Render: Dashboard에서 로그 확인
- Vercel: Analytics 활성화
- Supabase: Usage 확인

### CI/CD 자동화
- GitHub Actions가 이미 설정되어 있음
- `main` 브랜치 푸시 시 자동 배포

## 참고 문서

- [상세 배포 가이드](./RENDER_DEPLOYMENT.md)
- [환경 변수 가이드](./ENVIRONMENT_VARIABLES.md)
- [트러블슈팅 전체 목록](./DEPLOYMENT_GUIDE.md#롤백-및-트러블슈팅)
