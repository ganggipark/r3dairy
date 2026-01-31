# R³ Diary System - 배포 체크리스트

## 📋 사용자님이 해야 할 작업

### ✅ 1단계: Supabase 정보 확인

**필요한 정보**:
1. **Project URL** 확인하기
   - Supabase Dashboard → **Settings** → **API**
   - **Project URL** 복사 (예: `https://xxxxx.supabase.co`)

2. **anon public key** 확인 (이미 있음)
   - ✅ `sb_publishable_MmUagrOK0ptxcljT09izxg_kGQguOSn`

3. **Row Level Security (RLS) 정책 확인**
   - Supabase Dashboard → **Database** → **Tables**
   - 각 테이블에 RLS가 활성화되어 있는지 확인
   - 아래 SQL을 실행했는지 확인:

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

**확인 완료하면**: ✅ Project URL을 기록해 두세요!

---

### ✅ 2단계: GitHub에 코드 푸시

```bash
# 프로젝트 루트에서 실행
cd E:\project\diary-PJ

# 현재 상태 확인
git status

# 모든 파일 추가
git add .

# 커밋
git commit -m "R³ Diary System MVP - Ready for deployment

- Phase 1-9 완료
- Backend: FastAPI + Supabase + WeasyPrint
- Frontend: Next.js + Tailwind
- Deployment: Render + Vercel 설정 완료"

# 원격 저장소 설정 (아직 안 했다면)
git remote add origin https://github.com/ganggipark/r3dairy.git

# 푸시
git branch -M main
git push -u origin main
```

**확인**: https://github.com/ganggipark/r3dairy 에서 코드가 올라갔는지 확인

---

### ✅ 3단계: Render에서 Backend 배포

#### 3-1. Render 회원가입
1. https://render.com 접속
2. **Sign Up** (GitHub 계정으로 로그인 권장)

#### 3-2. 새 서비스 생성
1. **Dashboard** → **New** → **Blueprint** 클릭
2. **Connect GitHub** → 저장소 선택: `ganggipark/r3dairy`
3. Render가 `render.yaml` 파일을 자동으로 감지
4. **Apply** 클릭

#### 3-3. 환경 변수 설정
Blueprint 생성 후, 서비스가 자동으로 생성됩니다:

1. **Dashboard** → **r3-diary-backend** 클릭
2. **Environment** 탭 클릭
3. 다음 환경 변수 추가:

| Key | Value | 어디서 가져오나요? |
|-----|-------|-------------------|
| `SUPABASE_URL` | `https://xxxxx.supabase.co` | Supabase Dashboard → Settings → API → Project URL |
| `SUPABASE_KEY` | `sb_publishable_MmUagrOK0ptxcljT09izxg_kGQguOSn` | 이미 있음 (anon public key) |
| `CORS_ORIGINS` | `http://localhost:5000` | 일단 로컬로 설정 (Vercel 배포 후 업데이트) |

4. **Save Changes** 클릭

#### 3-4. 배포 대기
- 자동으로 빌드 시작 (5-10분 소요)
- **Logs** 탭에서 진행 상황 확인
- 빌드 완료 후 **Service URL** 확인 (예: `https://r3-diary-backend.onrender.com`)

#### 3-5. 배포 확인
```bash
# 헬스체크 (30초~1분 대기 후 시도)
curl https://r3-diary-backend.onrender.com/health

# 응답 예시
{"status":"healthy"}
```

**중요**: 첫 요청은 Spin Up으로 30초~1분 소요됩니다!

**Backend URL 기록**: `_____________________`

---

### ✅ 4단계: Frontend 배포 (Vercel)

#### 4-1. Vercel 설치 및 로그인
```bash
# Vercel CLI 설치 (이미 설치되어 있을 수 있음)
npm install -g vercel

# 프론트엔드 디렉토리로 이동
cd E:\project\diary-PJ\frontend

# Vercel 로그인
npx vercel login
```

#### 4-2. 환경 변수 설정
```bash
# Backend API URL (Render에서 받은 URL)
npx vercel env add NEXT_PUBLIC_API_URL production
# 입력: https://r3-diary-backend.onrender.com

# Supabase URL (1단계에서 확인한 Project URL)
npx vercel env add NEXT_PUBLIC_SUPABASE_URL production
# 입력: https://xxxxx.supabase.co

# Supabase anon key
npx vercel env add NEXT_PUBLIC_SUPABASE_ANON_KEY production
# 입력: sb_publishable_MmUagrOK0ptxcljT09izxg_kGQguOSn
```

#### 4-3. 프로덕션 배포
```bash
# 배포 시작
npx vercel --prod

# 질문에 답변:
# - Set up and deploy? Y
# - Which scope? (본인 계정 선택)
# - Link to existing project? N
# - Project name? r3-diary (또는 원하는 이름)
# - In which directory? ./ (현재 디렉토리)
# - Override settings? N
```

배포 완료 후 **Vercel URL** 확인 (예: `https://r3-diary.vercel.app`)

**Frontend URL 기록**: `_____________________`

---

### ✅ 5단계: CORS 업데이트

Frontend URL이 확정되었으므로 Backend CORS를 업데이트합니다:

1. **Render Dashboard** → **r3-diary-backend** → **Environment** 탭
2. `CORS_ORIGINS` 값 수정:
   - 기존: `http://localhost:5000`
   - 변경: `https://r3-diary.vercel.app,http://localhost:5000` (로컬 개발도 유지)
3. **Save Changes** → 자동 재배포 (1-2분 소요)

---

### ✅ 6단계: 전체 테스트

#### Backend 테스트
```bash
# 헬스체크
curl https://r3-diary-backend.onrender.com/health

# API 문서 확인
https://r3-diary-backend.onrender.com/docs
```

#### Frontend 테스트
1. **브라우저에서 Frontend 접속**
   - URL: `https://r3-diary.vercel.app`

2. **회원가입 테스트**
   - 이메일: `test@example.com`
   - 비밀번호: `Test1234!`

3. **로그인 테스트**
   - 위에서 만든 계정으로 로그인

4. **프로필 생성**
   - 이름: 테스트 사용자
   - 생년월일: 1990-01-01
   - 출생 시간: 12:00
   - 성별: 남/여
   - 출생 장소: 서울
   - 역할: 학생, 직장인 등 선택

5. **오늘 페이지 조회**
   - 10개 콘텐츠 블록이 표시되는지 확인
   - 역할 변경 버튼 클릭 (여러 역할 선택한 경우)

6. **기록 저장**
   - 오늘의 일정 입력
   - 기분/에너지 슬라이더 조정
   - 저장 버튼 클릭

7. **PDF 다운로드** (중요!)
   - 오늘 페이지 상단의 "PDF 다운로드" 버튼 클릭
   - 첫 요청은 30초~1분 소요 (Render Spin Up)
   - PDF 파일이 다운로드되는지 확인

#### 문제 발생 시
- Backend 로그: Render Dashboard → Logs
- Frontend 로그: Vercel Dashboard → Deployments → Logs
- 브라우저 콘솔: F12 → Console 탭

---

## 📊 현재 상태 요약

### ✅ 완료된 작업
- [x] Phase 1-9 개발 완료
- [x] GitHub 레포지토리 생성 (`ganggipark/r3dairy`)
- [x] Supabase 프로젝트 생성 및 SQL 실행
- [x] Supabase anon key 확인
- [x] Render 배포 설정 파일 작성 (`render.yaml`)
- [x] Vercel 배포 설정 파일 작성 (`vercel.json`)

### ⏳ 진행 중인 작업
- [ ] 1단계: Supabase Project URL 확인
- [ ] 2단계: GitHub에 코드 푸시
- [ ] 3단계: Render Backend 배포
- [ ] 4단계: Vercel Frontend 배포
- [ ] 5단계: CORS 업데이트
- [ ] 6단계: 전체 테스트

---

## 🚨 예상 문제 및 해결책

### 문제 1: Render 첫 요청이 매우 느림
**원인**: 무료 티어 Spin Down (15분간 요청 없으면 정지)
**해결**:
- 기다리면 됨 (30초~1분)
- 또는 Starter 플랜 ($7/월) 업그레이드

### 문제 2: Frontend에서 API 호출 실패 (CORS 에러)
**원인**: CORS_ORIGINS 설정 누락
**해결**:
```bash
# Render Dashboard → Environment → CORS_ORIGINS 확인
# 값: https://r3-diary.vercel.app,http://localhost:5000
```

### 문제 3: PDF 생성 실패
**원인**: 메모리 부족 (무료 티어 512MB)
**해결**:
- Starter 플랜 업그레이드
- 또는 PDF 생성 시간을 늘림 (타임아웃 조정)

### 문제 4: Supabase 연결 실패
**원인**: SUPABASE_URL 또는 SUPABASE_KEY 오류
**해결**:
```bash
# Supabase Dashboard → Settings → API
# Project URL: https://로 시작하는지 확인
# anon public key: 정확히 복사했는지 확인
```

---

## 💰 비용 안내

### 현재 설정 (무료)
- **Render Backend**: 750시간/월 무료
- **Vercel Frontend**: Hobby 플랜 무료
- **Supabase Database**: 500MB 무료
- **총 비용**: **$0/월** ✅

### 업그레이드 옵션 (선택)
- **Render Starter**: $7/월 (Cold Start 없음)
- **Vercel Pro**: $20/월 (상용 서비스)
- **Supabase Pro**: $25/월 (8GB DB)

---

## 📞 도움이 필요하면?

각 단계별로 문제가 발생하면 다음 정보와 함께 알려주세요:
1. 어떤 단계에서 문제가 발생했나요? (1-6단계)
2. 에러 메시지가 있나요?
3. 어떤 작업을 하려고 했나요?

**참고 문서**:
- [빠른 시작 가이드](./QUICKSTART.md)
- [Render 상세 가이드](./RENDER_DEPLOYMENT.md)
- [환경 변수 가이드](./ENVIRONMENT_VARIABLES.md)
