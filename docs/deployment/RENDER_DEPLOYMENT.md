# R³ Diary System - Render 배포 가이드

## 목차
1. [Render란?](#render란)
2. [사전 준비](#사전-준비)
3. [Backend 배포 (Render)](#backend-배포-render)
4. [Frontend 배포 (Vercel)](#frontend-배포-vercel)
5. [배포 후 검증](#배포-후-검증)
6. [트러블슈팅](#트러블슈팅)

## Render란?

**Render**는 개발자 친화적인 클라우드 플랫폼으로, Docker 기반 애플리케이션을 쉽게 배포할 수 있습니다.

### 장점
- ✅ Docker 완벽 지원
- ✅ 무료 티어 제공 (750시간/월)
- ✅ 자동 SSL 인증서
- ✅ Git 연동 자동 배포
- ✅ `render.yaml`로 Infrastructure as Code

### 단점
- ⚠️ 무료 티어는 비활성 시 Spin Down (첫 요청 시 30초~1분 소요)
- ⚠️ 무료 티어는 매월 15일간 자동 정지

## 사전 준비

### 1. 계정 생성
- [Render](https://render.com) 가입
- GitHub 계정 연동

### 2. Supabase 설정 확인
사용자님은 이미 완료하셨습니다:
- ✅ Supabase 프로젝트 생성
- ✅ SQL 스키마 실행 (`backend/src/db/schema.sql`)

**Supabase 정보 확인**:
1. Supabase Dashboard → **Settings** → **API**
2. 필요한 값:
   - **Project URL**: `https://xxx.supabase.co`
   - **anon public key**: `sb_publishable_MmUagrOK0ptxcljT09izxg_kGQguOSn` (사용자님 키)

### 3. GitHub 저장소 푸시
```bash
# 로컬에서 GitHub에 푸시
git add .
git commit -m "Add Render deployment configuration"
git push origin main
```

## Backend 배포 (Render)

### Option 1: render.yaml 사용 (권장)

저장소 루트에 `render.yaml` 파일이 이미 있습니다. Render가 자동으로 인식합니다.

**1단계: Render Dashboard 접속**
1. https://render.com 로그인
2. **Dashboard** 클릭

**2단계: 새 서비스 생성**
1. **New** → **Blueprint** 클릭
2. GitHub 저장소 연결 (your-username/diary-PJ)
3. Render가 `render.yaml` 파일을 자동으로 감지

**3단계: 환경 변수 설정**
Render가 서비스를 생성한 후, 다음 환경 변수를 수동으로 추가해야 합니다:

1. **Dashboard** → **r3-diary-backend** 서비스 클릭
2. **Environment** 탭 클릭
3. 다음 변수 추가:

| Key | Value | 설명 |
|-----|-------|------|
| `SUPABASE_URL` | `https://xxx.supabase.co` | Supabase Project URL |
| `SUPABASE_KEY` | `sb_publishable_MmUagrOK0ptxcljT09izxg_kGQguOSn` | Supabase anon key |
| `CORS_ORIGINS` | `https://r3-diary.vercel.app` | Frontend URL (Vercel 배포 후 업데이트) |

**4단계: 배포 시작**
1. **Save Changes** 클릭
2. Render가 자동으로 Docker 이미지 빌드 및 배포 시작
3. 배포 로그 확인 (5-10분 소요)

**5단계: 배포 URL 확인**
- 배포 완료 후 **URL** 확인 (예: `https://r3-diary-backend.onrender.com`)
- 이 URL을 Frontend 환경 변수에 사용합니다

### Option 2: Dashboard에서 수동 생성

**1단계: 새 Web Service 생성**
1. **Dashboard** → **New** → **Web Service**
2. GitHub 저장소 선택 (diary-PJ)

**2단계: 설정**
- **Name**: `r3-diary-backend`
- **Region**: Singapore (가장 가까운 리전)
- **Branch**: `main`
- **Root Directory**: `backend` (선택 사항)
- **Environment**: `Docker`
- **Dockerfile Path**: `./backend/Dockerfile` (Root Directory 설정 안 한 경우)

**3단계: 인스턴스 타입**
- **Instance Type**: `Free` (무료 티어)

**4단계: 환경 변수**
위의 Option 1과 동일하게 설정

**5단계: 배포**
- **Create Web Service** 클릭
- 빌드 및 배포 대기 (5-10분)

### 배포 확인

배포 완료 후 다음을 확인하세요:

```bash
# 헬스체크
curl https://r3-diary-backend.onrender.com/health

# 응답 예시
{"status": "healthy"}

# API 문서 접속
https://r3-diary-backend.onrender.com/docs
```

## Frontend 배포 (Vercel)

### 1단계: Vercel 로그인
```bash
cd frontend
npx vercel login
```

### 2단계: 환경 변수 설정
```bash
# Backend API URL (Render에서 받은 URL)
npx vercel env add NEXT_PUBLIC_API_URL production
# 입력: https://r3-diary-backend.onrender.com

# Supabase URL
npx vercel env add NEXT_PUBLIC_SUPABASE_URL production
# 입력: https://xxx.supabase.co

# Supabase anon key
npx vercel env add NEXT_PUBLIC_SUPABASE_ANON_KEY production
# 입력: sb_publishable_MmUagrOK0ptxcljT09izxg_kGQguOSn
```

### 3단계: 프로덕션 배포
```bash
npx vercel --prod
```

배포 완료 후 URL 확인 (예: `https://r3-diary.vercel.app`)

### 4단계: CORS 설정 업데이트

Frontend URL이 확정되었으므로 Backend CORS를 업데이트합니다:

1. **Render Dashboard** → **r3-diary-backend** → **Environment**
2. `CORS_ORIGINS` 값을 실제 Vercel URL로 업데이트:
   ```
   https://r3-diary.vercel.app
   ```
3. **Save Changes** → 자동 재배포됨

## 배포 후 검증

### 1. Backend 검증
```bash
# 헬스체크
curl https://r3-diary-backend.onrender.com/health

# Swagger UI 접속
https://r3-diary-backend.onrender.com/docs
```

### 2. Frontend 검증
1. 브라우저에서 `https://r3-diary.vercel.app` 접속
2. 회원가입 테스트
3. 로그인 테스트
4. 프로필 생성 테스트
5. 오늘 페이지 조회
6. 기록 저장 테스트

### 3. 통합 테스트
**전체 플로우 확인**:
1. ✅ 회원가입 → 로그인
2. ✅ 프로필 입력 (출생 정보, 역할)
3. ✅ 오늘 페이지 콘텐츠 조회 (10개 블록)
4. ✅ 역할 변경 (학생 ↔ 직장인)
5. ✅ 사용자 기록 저장
6. ✅ PDF 다운로드 (**중요**: 첫 요청 시 Spin Up으로 30초 소요 가능)

## 트러블슈팅

### 1. Backend가 시작되지 않음

**증상**: "Service Unavailable" 또는 빌드 실패

**해결책**:
```bash
# Render 로그 확인
Dashboard → r3-diary-backend → Logs

# 일반적인 문제:
# 1. WeasyPrint 의존성 설치 실패
#    → Dockerfile에 시스템 패키지 확인
# 2. 환경 변수 누락
#    → SUPABASE_URL, SUPABASE_KEY 확인
# 3. 메모리 부족
#    → 무료 티어 제한 (512MB) 확인
```

### 2. 첫 요청이 매우 느림 (30초~1분)

**원인**: 무료 티어의 Spin Down 기능
- 15분간 요청이 없으면 자동으로 서비스 정지
- 다음 요청 시 다시 시작 (Cold Start)

**해결책**:
1. **업그레이드**: Starter 플랜 ($7/월) 사용 시 항상 활성화
2. **핑 서비스**: 5분마다 헬스체크 요청 (UptimeRobot 등)
   ```bash
   # 예: 매 5분마다 /health 호출
   curl https://r3-diary-backend.onrender.com/health
   ```

### 3. Frontend에서 API 호출 실패

**증상**: CORS 에러 또는 "Network Error"

**해결책**:
```bash
# 1. CORS_ORIGINS 확인
Render Dashboard → Environment → CORS_ORIGINS 값 확인

# 2. Backend URL 확인
Frontend .env.local:
NEXT_PUBLIC_API_URL=https://r3-diary-backend.onrender.com

# 3. 브라우저 콘솔에서 확인
console.log(process.env.NEXT_PUBLIC_API_URL)
```

### 4. PDF 생성 실패

**증상**: `/api/pdf/daily/{date}` 호출 시 500 에러

**해결책**:
```bash
# 1. WeasyPrint 의존성 확인
Render Logs에서 다음 패키지 설치 확인:
- libcairo2
- libpango-1.0-0
- libpangocairo-1.0-0
- libgdk-pixbuf2.0-0

# 2. 메모리 확인
무료 티어 512MB 제한 → PDF 생성 시 부족할 수 있음
해결: Starter 플랜 업그레이드
```

### 5. Supabase 연결 실패

**증상**: "Invalid API key" 또는 "Connection refused"

**해결책**:
```bash
# 1. SUPABASE_URL 형식 확인
https://xxx.supabase.co (https:// 필수)

# 2. SUPABASE_KEY 확인
Supabase Dashboard → Settings → API → anon public key

# 3. Supabase 프로젝트 상태 확인
Dashboard → Project가 활성화되어 있는지 확인 (일시 중단 아님)
```

## 자동 배포 설정

### GitHub Actions 연동

`.github/workflows/backend-ci.yml`이 이미 설정되어 있습니다:

```yaml
# main 브랜치에 푸시하면 자동으로:
1. Backend 테스트 실행
2. Docker 이미지 빌드 및 테스트
3. Render가 자동으로 새 이미지 배포
```

**설정 확인**:
1. GitHub 저장소 → **Settings** → **Actions** → **General**
2. "Allow all actions and reusable workflows" 선택

**Render 자동 배포 설정**:
1. Render Dashboard → **r3-diary-backend** → **Settings**
2. **Build & Deploy** 섹션
3. **Auto-Deploy**: `Yes` (기본값)
4. **Branch**: `main`

이제 `main` 브랜치에 푸시하면 자동으로 배포됩니다!

## 비용 안내

### 무료 티어
- **Render Backend**: 750시간/월 무료 (충분)
- **Vercel Frontend**: Hobby 플랜 무료
- **Supabase**: 500MB 데이터베이스 무료
- **총 비용**: $0/월 ✅

### 업그레이드 옵션 (선택)
- **Render Starter**: $7/월 (항상 활성화, Cold Start 없음)
- **Vercel Pro**: $20/월 (상용 프로젝트)
- **Supabase Pro**: $25/월 (8GB 데이터베이스)

## 다음 단계

배포가 완료되었습니다! 🎉

### 모니터링
- [ ] Render Dashboard에서 로그 확인
- [ ] Vercel Analytics 활성화
- [ ] Supabase 사용량 확인

### 개선 사항
- [ ] 커스텀 도메인 연결 (선택)
- [ ] Sentry 에러 트래킹 (선택)
- [ ] LogRocket 세션 리플레이 (선택)

### 유지보수
- [ ] 정기적으로 로그 확인
- [ ] Supabase 무료 티어 제한 모니터링 (500MB)
- [ ] Render 무료 티어 750시간 확인

## 참고 문서

- [Render 공식 문서](https://render.com/docs)
- [Vercel 배포 가이드](https://vercel.com/docs)
- [Supabase 공식 문서](https://supabase.com/docs)
- [환경 변수 가이드](./ENVIRONMENT_VARIABLES.md)
