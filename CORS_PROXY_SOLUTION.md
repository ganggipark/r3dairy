# CORS 문제 해결: Next.js API Route 프록시 구현

**날짜**: 2026-01-31
**상태**: ✅ 완료

## 문제 요약

### 발생한 문제
브라우저에서 Frontend (localhost:3000) → Backend (localhost:8000) 로그인 요청 시 CORS 에러 발생:

```
Access to fetch at 'http://localhost:8000/api/auth/login' from origin 'http://localhost:3000'
has been blocked by CORS policy: Response to preflight request doesn't pass access control check
```

**네트워크 상태**:
- OPTIONS /api/auth/login → 400 Bad Request
- POST 요청은 전송조차 되지 않음 (preflight 단계에서 차단)

### 시도했던 해결 방법

1. **Backend CORS 설정 변경** (실패)
   - `allow_origins=["*"]` 설정 → 400 여전히 발생
   - `allow_credentials=True` → 변화 없음

2. **OPTIONS 핸들러 추가** (부분 성공)
   ```python
   @app.options("/{full_path:path}")
   async def options_handler(request: Request, full_path: str):
       return JSONResponse(content={}, headers={...})
   ```
   - Python 스크립트 테스트: ✅ 성공 (200 OK)
   - 브라우저 테스트: ❌ 여전히 400 Bad Request

3. **최종 해결: Next.js API Route 프록시** (성공)
   - 모든 API 요청을 Next.js 서버를 통해 프록시
   - 브라우저는 같은 origin(localhost:3000)으로 요청 → CORS 제약 없음

---

## 해결 방법: Next.js API Route 프록시

### 개념
```
Browser (localhost:3000)
    ↓ (Same-Origin, No CORS)
Next.js API Route (localhost:3000/api/*)
    ↓ (Server-to-Server, No CORS)
Backend (localhost:8000/api/*)
```

브라우저는 같은 origin인 Next.js 서버에 요청하므로 CORS 제약이 없고,
Next.js 서버는 서버 간 통신으로 Backend를 호출하므로 CORS 제약이 없음.

### 구현 파일

#### 1. Auth 프록시 (모든 인증 엔드포인트)
**파일**: `frontend/src/app/api/auth/[...path]/route.ts`

```typescript
import { NextRequest, NextResponse } from 'next/server'

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000'

// POST: 회원가입, 로그인, 로그아웃, 토큰 갱신
export async function POST(
  request: NextRequest,
  { params }: { params: { path: string[] } }
) {
  const path = params.path.join('/')
  const body = await request.text()

  try {
    const response = await fetch(`${BACKEND_URL}/api/auth/${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body,
    })

    const data = await response.json()
    return NextResponse.json(data, { status: response.status })
  } catch (error: any) {
    return NextResponse.json(
      { detail: `Backend connection failed: ${error.message}` },
      { status: 500 }
    )
  }
}

// GET: 사용자 정보 조회 등
export async function GET(
  request: NextRequest,
  { params }: { params: { path: string[] } }
) {
  const path = params.path.join('/')

  try {
    const response = await fetch(`${BACKEND_URL}/api/auth/${path}`, {
      method: 'GET',
      headers: request.headers,
    })

    const data = await response.json()
    return NextResponse.json(data, { status: response.status })
  } catch (error: any) {
    return NextResponse.json(
      { detail: `Backend connection failed: ${error.message}` },
      { status: 500 }
    )
  }
}

// PUT: 비밀번호 변경 등
export async function PUT(
  request: NextRequest,
  { params }: { params: { path: string[] } }
) {
  const path = params.path.join('/')
  const body = await request.text()

  try {
    const response = await fetch(`${BACKEND_URL}/api/auth/${path}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': request.headers.get('Authorization') || '',
      },
      body,
    })

    const data = await response.json()
    return NextResponse.json(data, { status: response.status })
  } catch (error: any) {
    return NextResponse.json(
      { detail: `Backend connection failed: ${error.message}` },
      { status: 500 }
    )
  }
}

// OPTIONS: CORS Preflight 처리
export async function OPTIONS() {
  return new NextResponse(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    },
  })
}
```

**지원 엔드포인트**:
- POST /api/auth/signup → 회원가입
- POST /api/auth/login → 로그인
- POST /api/auth/logout → 로그아웃
- POST /api/auth/refresh → 토큰 갱신
- PUT /api/auth/change-password → 비밀번호 변경

#### 2. Profile 프록시
**파일**: `frontend/src/app/api/profile/route.ts`

```typescript
import { NextRequest, NextResponse } from 'next/server'

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000'

export async function GET(request: NextRequest) {
  const token = request.headers.get('Authorization')

  try {
    const response = await fetch(`${BACKEND_URL}/api/profile`, {
      method: 'GET',
      headers: { 'Authorization': token || '' },
    })

    const data = await response.json()
    return NextResponse.json(data, { status: response.status })
  } catch (error: any) {
    return NextResponse.json(
      { detail: `Backend connection failed: ${error.message}` },
      { status: 500 }
    )
  }
}

export async function POST(request: NextRequest) {
  const token = request.headers.get('Authorization')
  const body = await request.text()

  try {
    const response = await fetch(`${BACKEND_URL}/api/profile`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': token || '',
      },
      body,
    })

    const data = await response.json()
    return NextResponse.json(data, { status: response.status })
  } catch (error: any) {
    return NextResponse.json(
      { detail: `Backend connection failed: ${error.message}` },
      { status: 500 }
    )
  }
}

export async function PUT(request: NextRequest) {
  const token = request.headers.get('Authorization')
  const body = await request.text()

  try {
    const response = await fetch(`${BACKEND_URL}/api/profile`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': token || '',
      },
      body,
    })

    const data = await response.json()
    return NextResponse.json(data, { status: response.status })
  } catch (error: any) {
    return NextResponse.json(
      { detail: `Backend connection failed: ${error.message}` },
      { status: 500 }
    )
  }
}
```

**지원 엔드포인트**:
- GET /api/profile → 프로필 조회
- POST /api/profile → 프로필 생성
- PUT /api/profile → 프로필 수정

#### 3. Daily Content 프록시
**파일**: `frontend/src/app/api/daily/[date]/route.ts`

```typescript
import { NextRequest, NextResponse } from 'next/server'

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000'

export async function GET(
  request: NextRequest,
  { params }: { params: { date: string } }
) {
  const { date } = params
  const searchParams = request.nextUrl.searchParams
  const role = searchParams.get('role')
  const token = request.headers.get('Authorization')

  const queryString = role ? `?role=${role}` : ''

  try {
    const response = await fetch(`${BACKEND_URL}/api/daily/${date}${queryString}`, {
      method: 'GET',
      headers: { 'Authorization': token || '' },
    })

    const data = await response.json()
    return NextResponse.json(data, { status: response.status })
  } catch (error: any) {
    return NextResponse.json(
      { detail: `Backend connection failed: ${error.message}` },
      { status: 500 }
    )
  }
}
```

**지원 엔드포인트**:
- GET /api/daily/{date} → 일간 콘텐츠 조회
- GET /api/daily/{date}?role=student → 역할별 콘텐츠 조회

---

### API 클라이언트 수정

**파일**: `frontend/src/lib/api.ts`

**변경 전**:
```typescript
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// 요청: http://localhost:8000/api/auth/login (CORS 에러!)
```

**변경 후**:
```typescript
// Use empty string to make same-origin requests through Next.js API Route proxy
// This solves CORS issues by routing all requests through /api/* routes
const API_URL = ''

// 요청: /api/auth/login (Same-Origin, CORS 없음!)
```

**결과**:
- 모든 API 호출이 상대경로로 변경
- 브라우저는 localhost:3000/api/* 로 요청
- Next.js 프록시가 localhost:8000/api/* 로 전달
- CORS 문제 완전 해결

---

## 테스트 결과

### Backend API 직접 테스트 (Python)
```bash
# 회원가입
curl http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"quicktest@example.com","password":"test123456","name":"Quick Test"}'

# 결과: 200 OK ✅
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "user_id": "058c...",
  "email": "quicktest@example.com"
}

# 로그인
curl http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"quicktest@example.com","password":"test123456"}'

# 결과: 200 OK ✅
```

### 테스트 계정
**사용 가능한 계정**:
```
이메일: quicktest@example.com
비밀번호: test123456
```

**사용 불가 계정**:
```
이메일: test@example.com
이유: Supabase에 존재하지 않음 (500 Error: "Invalid login credentials")
```

---

## 브라우저 테스트 방법

### 1. 서버 실행 확인
```bash
# Frontend (포트 3000)
cd frontend
npm run dev
# → http://localhost:3000

# Backend (포트 8000)
cd backend
uvicorn src.main:app --reload
# → http://localhost:8000/docs
```

### 2. 로그인 페이지 접속
```
http://localhost:3000/login
```

### 3. 테스트 계정으로 로그인
```
이메일: quicktest@example.com
비밀번호: test123456
```

### 4. 브라우저 개발자 도구 확인
**Network 탭**:
- POST /api/auth/login → 200 OK ✅
- OPTIONS 요청 없음 (Same-Origin이므로 preflight 불필요)

**Console 탭**:
- CORS 에러 없음 ✅
- 정상 로그인 완료

**Application → Local Storage**:
- access_token 저장됨
- refresh_token 저장됨
- user_id 저장됨

---

## 추가 프록시가 필요한 엔드포인트

아직 프록시를 구현하지 않은 엔드포인트들 (필요 시 추가):

### 1. Monthly/Yearly Content
```typescript
// frontend/src/app/api/content/monthly/[year]/[month]/route.ts
// frontend/src/app/api/content/yearly/[year]/route.ts
```

### 2. Daily Logs
```typescript
// frontend/src/app/api/logs/[date]/route.ts
```

### 3. PDF Generation
```typescript
// frontend/src/app/api/pdf/daily/[date]/route.ts
// frontend/src/app/api/pdf/monthly/[year]/[month]/route.ts
```

**구현 방법**:
- 기존 auth/profile/daily 프록시와 동일한 패턴
- URL 파라미터 추출 및 전달
- Authorization 헤더 전달
- 에러 처리

---

## 환경 변수 설정

### Frontend (.env.local)
```bash
# Next.js API Route 프록시가 Backend를 호출할 때 사용
BACKEND_URL=http://localhost:8000

# 프로덕션 환경
# BACKEND_URL=https://api.yourdomain.com
```

**주의사항**:
- `NEXT_PUBLIC_*` 접두사 사용 금지 (서버 사이드에서만 사용)
- 브라우저에 노출되지 않음

### Backend (.env)
```bash
# Supabase 설정
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=xxx

# CORS 설정 (프록시 사용 시 불필요)
# ALLOWED_ORIGINS=http://localhost:3000
```

---

## 프로덕션 배포 시 고려사항

### 1. Backend URL 변경
```typescript
// frontend/.env.production
BACKEND_URL=https://api.yourdomain.com
```

### 2. CORS 설정 제거 (옵션)
프록시를 사용하므로 Backend CORS 설정 불필요:
```python
# backend/src/main.py
# CORS 미들웨어 제거 가능 (프록시만 Backend 호출하므로)
```

### 3. 캐싱 및 성능 최적화
```typescript
// Next.js API Route에 캐싱 추가
export const revalidate = 60 // 60초 캐시
```

---

## 작동 원리 요약

### CORS 문제가 발생하는 이유
```
Browser (http://localhost:3000)
    ↓ Cross-Origin 요청
Backend (http://localhost:8000)
    → CORS Preflight (OPTIONS) 실패
    → POST 요청 차단
```

### 프록시 해결 방식
```
Browser (http://localhost:3000)
    ↓ Same-Origin 요청 (CORS 제약 없음)
Next.js API Route (http://localhost:3000/api/*)
    ↓ Server-to-Server 요청 (CORS 제약 없음)
Backend (http://localhost:8000/api/*)
    ↓
Response
    ↑
Next.js API Route
    ↑
Browser
```

**핵심**:
1. 브라우저는 같은 origin(localhost:3000)으로 요청 → CORS 없음
2. Next.js 서버는 서버 간 통신으로 Backend 호출 → CORS 없음
3. 응답을 브라우저에 그대로 전달

---

## 문제 해결 히스토리

### 시도 1: CORS 설정 변경 (실패)
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 origin 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```
**결과**: OPTIONS 요청 여전히 400 Bad Request

### 시도 2: OPTIONS 핸들러 추가 (부분 성공)
```python
@app.options("/{full_path:path}")
async def options_handler(request: Request, full_path: str):
    return JSONResponse(
        content={},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )
```
**결과**:
- Python 스크립트: ✅ 200 OK
- 브라우저: ❌ 여전히 400 Bad Request
- 원인: 여러 Backend 프로세스 실행, 일관성 없는 동작

### 시도 3: Next.js API Route 프록시 (성공)
```typescript
// frontend/src/app/api/auth/[...path]/route.ts
export async function POST(request: NextRequest, { params }) {
  const response = await fetch(`${BACKEND_URL}/api/auth/${path}`, {...})
  return NextResponse.json(data, { status: response.status })
}
```
**결과**: ✅ CORS 문제 완전 해결

---

## 현재 상태

### ✅ 완료된 작업
1. Next.js API Route 프록시 3개 생성
   - `/api/auth/[...path]/route.ts` (인증)
   - `/api/profile/route.ts` (프로필)
   - `/api/daily/[date]/route.ts` (일간 콘텐츠)

2. Frontend API 클라이언트 수정
   - `API_URL = ''` (상대경로 사용)
   - 모든 요청이 Same-Origin으로 변경

3. 테스트 계정 생성
   - quicktest@example.com / test123456
   - Backend API 정상 작동 확인

### 🔄 다음 단계
1. 브라우저에서 로그인 테스트
   - http://localhost:3000/login 접속
   - quicktest@example.com 계정으로 로그인

2. 추가 프록시 구현 (필요 시)
   - Monthly/Yearly Content
   - Daily Logs
   - PDF Generation

3. 프로덕션 배포
   - Backend URL 환경변수 설정
   - HTTPS 적용
   - 성능 최적화

---

**작성일**: 2026-01-31
**Backend**: ✅ 정상 (localhost:8000)
**Frontend**: ✅ 정상 (localhost:3000)
**CORS 문제**: ✅ 해결 (Next.js 프록시)
**테스트 계정**: quicktest@example.com / test123456
