## Backend API

RESTful API 엔드포인트 구현

## 📋 개요

R³ Diary System의 Backend API는 FastAPI 기반으로 구축되었으며, Supabase Auth 및 PostgreSQL 데이터베이스를 사용합니다.

### 핵심 기능

1. **인증** (Auth): 회원가입, 로그인, 토큰 갱신
2. **프로필** (Profile): 출생 정보 및 역할 관리
3. **일간 콘텐츠** (Daily): 역할별 일간 리듬 분석 콘텐츠 제공
4. **월간/연간 콘텐츠** (Monthly/Yearly): 기간별 리듬 분석
5. **사용자 기록** (Logs): 일간 사용자 기록 CRUD

## 📁 파일 구조

```
api/
├── __init__.py         # 모듈 초기화
├── models.py           # API Request/Response 모델
├── auth.py             # 인증 API
├── profile.py          # 프로필 API
├── daily.py            # 일간 콘텐츠 API
├── monthly.py          # 월간/연간 콘텐츠 API
├── logs.py             # 사용자 기록 API
└── README.md           # 이 파일
```

## 🔐 인증 (Authentication)

### POST /api/auth/signup
회원가입

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "password123",
  "name": "홍길동"
}
```

**Response**:
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "user_id": "uuid",
  "email": "user@example.com"
}
```

### POST /api/auth/login
로그인

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response**: 회원가입과 동일

### POST /api/auth/logout
로그아웃

**Response**:
```json
{
  "success": true,
  "message": "로그아웃되었습니다."
}
```

### POST /api/auth/refresh
토큰 갱신

**Request Body**:
```json
{
  "refresh_token": "eyJ..."
}
```

**Response**: 회원가입과 동일

## 👤 프로필 (Profile)

**인증 필요**: 모든 엔드포인트에 `Authorization: Bearer {access_token}` 헤더 필요

### POST /api/profile
프로필 생성

**Request Body**:
```json
{
  "name": "홍길동",
  "birth_date": "1990-01-15",
  "birth_time": "14:30:00",
  "gender": "male",
  "birth_place": "서울",
  "roles": ["student"],
  "preferences": {
    "interests": ["수학", "과학"]
  }
}
```

**Response**:
```json
{
  "id": "uuid",
  "name": "홍길동",
  "birth_date": "1990-01-15",
  "birth_time": "14:30:00",
  "gender": "male",
  "birth_place": "서울",
  "roles": ["student"],
  "preferences": {...},
  "created_at": "2026-01-20T...",
  "updated_at": "2026-01-20T..."
}
```

### GET /api/profile
프로필 조회

**Response**: 프로필 생성과 동일

### PUT /api/profile
프로필 수정 (모든 필드 optional)

**Request Body**:
```json
{
  "roles": ["student", "office_worker"]
}
```

**Response**: 수정된 프로필

### DELETE /api/profile
프로필 삭제

**Response**:
```json
{
  "success": true,
  "message": "프로필이 삭제되었습니다."
}
```

## 📅 일간 콘텐츠 (Daily Content)

**인증 필요**: Authorization 헤더 필수

### GET /api/daily/{date}?role={role}
일간 콘텐츠 조회 (역할별 변환)

**Parameters**:
- `date`: 날짜 (YYYY-MM-DD)
- `role`: (optional) student | office_worker | freelancer

**Example**:
```
GET /api/daily/2026-01-20?role=student
```

**Response**:
```json
{
  "date": "2026-01-20",
  "role": "student",
  "content": {
    "summary": "오늘은 과제 마무리에 집중하기 좋은 날입니다...",
    "keywords": ["집중", "학습", "정리"],
    "rhythm_description": "...",
    "focus_caution": {...},
    "action_guide": {...},
    "time_direction": {...},
    "state_trigger": {...},
    "meaning_shift": "...",
    "rhythm_question": "오늘 집중해서 공부할 과목은 무엇인가요?"
  }
}
```

### GET /api/daily/range/{start_date}/{end_date}?role={role}
기간별 일간 콘텐츠 조회 (최대 31일)

**Example**:
```
GET /api/daily/range/2026-01-01/2026-01-31?role=office_worker
```

**Response**:
```json
[
  {
    "date": "2026-01-01",
    "role": "office_worker",
    "content": {...}
  },
  ...
]
```

## 📆 월간/연간 콘텐츠 (Monthly/Yearly)

**인증 필요**: Authorization 헤더 필수

### GET /api/content/monthly/{year}/{month}?role={role}
월간 콘텐츠 조회

**Example**:
```
GET /api/content/monthly/2026/1?role=freelancer
```

**Response**:
```json
{
  "year": 2026,
  "month": 1,
  "role": "freelancer",
  "content": {
    "month_theme": "...",
    "energy_pattern": [...],
    "key_dates": [...]
  }
}
```

### GET /api/content/yearly/{year}?role={role}
연간 콘텐츠 조회

**Example**:
```
GET /api/content/yearly/2026?role=student
```

**Response**:
```json
{
  "year": 2026,
  "role": "student",
  "content": {
    "year_theme": "...",
    "monthly_signals": [...]
  }
}
```

## 📝 사용자 기록 (Daily Logs)

**인증 필요**: Authorization 헤더 필수

### POST /api/logs/{date}
일간 기록 생성

**Request Body**:
```json
{
  "schedule": "오전 10시: 수업\n오후 2시: 스터디",
  "todos": ["수학 과제", "영어 단어 암기"],
  "mood": 4,
  "energy": 3,
  "notes": "오늘은 집중이 잘 되는 날이었다.",
  "gratitude": "친구의 도움에 감사한다."
}
```

**Response**:
```json
{
  "id": "uuid",
  "profile_id": "uuid",
  "date": "2026-01-20",
  "schedule": "...",
  "todos": [...],
  "mood": 4,
  "energy": 3,
  "notes": "...",
  "gratitude": "...",
  "created_at": "...",
  "updated_at": "..."
}
```

### GET /api/logs/{date}
일간 기록 조회

**Response**: 기록 생성과 동일

### PUT /api/logs/{date}
일간 기록 수정 (모든 필드 optional)

**Request Body**:
```json
{
  "mood": 5,
  "energy": 4
}
```

**Response**: 수정된 기록

### DELETE /api/logs/{date}
일간 기록 삭제

**Response**:
```json
{
  "success": true,
  "message": "기록이 삭제되었습니다."
}
```

## 🔧 환경 변수 설정

`.env` 파일 생성:

```bash
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key

# CORS
CORS_ORIGINS=http://localhost:5000

# Environment
ENVIRONMENT=development
```

## 🚀 서버 실행

```bash
cd backend

# 가상환경 활성화 (선택)
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 서버 실행
uvicorn src.main:app --reload

# 또는
python src/main.py
```

서버 시작 후:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 📊 API 문서

FastAPI는 자동으로 API 문서를 생성합니다:

- **Interactive Swagger UI**: `/docs` - API를 직접 테스트할 수 있음
- **ReDoc**: `/redoc` - 읽기 전용 문서

## 🎯 API 흐름 예시

### 1. 회원가입 및 프로필 생성

```bash
# 1. 회원가입
POST /api/auth/signup
{
  "email": "student@example.com",
  "password": "password123",
  "name": "학생"
}

# 2. 프로필 생성
POST /api/profile
Authorization: Bearer {access_token}
{
  "name": "학생",
  "birth_date": "2000-01-01",
  "birth_time": "14:00:00",
  "gender": "male",
  "birth_place": "서울",
  "roles": ["student"]
}
```

### 2. 일간 콘텐츠 조회

```bash
# 학생용 일간 콘텐츠
GET /api/daily/2026-01-20?role=student
Authorization: Bearer {access_token}

# 응답: "과제 마무리", "집중 학습 시간" 등 학생용 표현
```

### 3. 사용자 기록 저장

```bash
# 오늘의 기록 저장
POST /api/logs/2026-01-20
Authorization: Bearer {access_token}
{
  "schedule": "오전: 수학 공부",
  "mood": 4,
  "energy": 3,
  "notes": "집중이 잘 되었다."
}
```

## 🔒 보안

- **인증**: Supabase Auth (JWT)
- **RLS**: Row Level Security (사용자별 데이터 격리)
- **CORS**: 허용된 origin만 접근 가능
- **환경 변수**: 민감한 정보는 .env 파일로 관리

## 🧪 테스트

```bash
# API 테스트 (TODO: Phase 8에서 구현 예정)
pytest tests/test_api.py -v
```

## 📚 참고 자료

- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [Supabase Python 문서](https://supabase.com/docs/reference/python)
- [Phase 4: Role Translation Layer](../translation/README.md)
- [Phase 3: Content Assembly Engine](../content/README.md)

## 🔄 다음 단계: Phase 6

**Frontend UI 구축** - Next.js 웹 애플리케이션

Phase 6에서는:
- Next.js API 클라이언트 구현
- 로그인/회원가입 페이지
- 프로필 입력 폼
- 오늘/이번 달/올해 페이지 UI
- 역할 선택 및 실시간 콘텐츠 변환

---

**Backend API v1.0.0**
