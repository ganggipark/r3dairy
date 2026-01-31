# ARCHITECTURE - R³ Diary System

## 1. 목표
- 동일한 콘텐츠 데이터로 Web + Print(PDF) 동시 지원
- 내부 계산(전문용어)과 사용자 노출(일반 언어) 완전 분리
- 역할 기반 가변 콘텐츠는 번역 레이어에서만 수행
- **Markdown-First**: 사용자 노출 콘텐츠는 Markdown 우선, JSON은 API 폴백

## 2. High-level Components

### 2.1 Input Layer
- **Profile**: birth info, role, preferences, birth place
- **Daily Log**: user entries (mood, energy, notes)
- **User Preferences**: role (student/employee/freelancer), language, format

### 2.2 Rhythm Analysis Engine (3가지 계산, 내부)

```
┌─────────────────────────────────────────────────────┐
│     Rhythm Analysis Engine (내부, 전문 용어)         │
│  사용자에게 절대 노출 금지                            │
└─────────────────────────────────────────────────────┘
  ├─ Saju (사주, 八字) Calculator
  │   ├─ Input: Birth year/month/day/hour/gender
  │   ├─ Process: Heavenly Stems, Earthly Branches, Ten Stems
  │   └─ Output: SajuData (내부 표현)
  │
  ├─ Qimen (기문둔갑, 奇門遁甲) Analyzer
  │   ├─ Input: Target date/time, SajuData
  │   ├─ Process: 9 Palaces, 8 Gates, 9 Stars
  │   └─ Output: QimenData (내부 표현)
  │
  └─ Saekeunshik (색은식, 五運六氣) Calculator
      ├─ Input: Target date
      ├─ Process: Five Movements, Six Qi (Sicheon/Jaecheon)
      └─ Output: SaekeunshikData (내부 표현)
```

**내부 용어 (절대 금지)**:
- 천간(Heavenly Stems), 지지(Earthly Branches)
- 십성(Ten Stems), 오행(Five Elements)
- NLP, 알고리즘, 계산 용어

### 2.3 Content Assembly Engine
- **Input**: SajuData + QimenData + SaekeunshikData + Profile
- **Process**: 리듬 신호를 구조화된 JSON 블록으로 변환
- **Output**: JSON (DAILY_CONTENT_SCHEMA.json 준수)
- **중요**: 여전히 내부 데이터 (사용자 노출 금지)

### 2.4 Markdown Generation Layer (신규, 사용자 노출)

```
┌──────────────────────────────────────────────────────┐
│  Markdown Generator                                  │
│  JSON → 사용자 친화적 Markdown (일반 언어)            │
│  저장 위치: backend/daily/{YYYY-MM-DD}.md            │
└──────────────────────────────────────────────────────┘
```

- **Input**: JSON (from Content Assembly)
- **Process**:
  1. JSON 필드 → Markdown 섹션 매핑
  2. 내부 용어 → 일반 언어 변환
  3. 역할별 번역 적용
  4. 파일 저장
- **Output**: Markdown (.md 파일)
- **특징**:
  - 사용자가 읽기 쉬운 형식
  - 구조화된 섹션 (제목, 리스트, 블록 인용)
  - 이모지 포함 (제한적)
  - 길이 요구사항 준수 (최소 400자)

### 2.5 Role Translation Layer
- **Input**: JSON 또는 Markdown
- **Process**: role(student/employee/freelancer)에 따라 표현 변형
- **Output**: 역할별 JSON/Markdown
- **원칙**: 핵심 의미는 변경하지 않고 표현만 변형

### 2.6 Output Layer

```
              ┌─────────────────────────────────┐
              │  Multiple Output Channels       │
              └─────────────────────────────────┘
                    ↙                    ↘
        ┌──────────────────┐      ┌──────────────────┐
        │   Web/App        │      │    PDF Diary     │
        │ (Markdown Render)│      │ (HTML → PDF)     │
        │                  │      │                  │
        │ • Real-time      │      │ • Printable      │
        │ • Interactive    │      │ • Archivable     │
        └──────────────────┘      └──────────────────┘
```

- **Web Renderer**: Markdown → HTML (React/Next.js)
- **PDF Renderer**: Markdown/HTML → PDF (WeasyPrint)
- **API Response**: JSON + Markdown (모두 제공)

## 3. Data Flow (Markdown-First)

```
┌──────────────┐
│ User Profile │ (birth date, role, preferences)
└──────┬───────┘
       │
       ↓
┌──────────────────────────────────┐
│ Rhythm Analysis (3가지 계산)      │
│ • Saju (사주)                    │
│ • Qimen (기문둔갑)               │
│ • Saekeunshik (색은식)           │
│                                  │
│ ⚠️ 내부 용어만 사용 (절대 노출 금지) │
└──────────┬───────────────────────┘
           │
           ↓
┌──────────────────────────────────┐
│ Content Assembly (JSON)           │
│ • Structured blocks               │
│ • DAILY_CONTENT_SCHEMA 준수       │
│                                  │
│ ⚠️ 여전히 내부 데이터            │
└──────────┬───────────────────────┘
           │
           ↓ (★ NEW)
┌──────────────────────────────────┐
│ Markdown Generation              │
│ • JSON → Markdown 변환            │
│ • 일반 언어로 변환                │
│ • 파일 저장 (backend/daily/)      │
│                                  │
│ ✅ 사용자 노출 OK                 │
└──────────┬───────────────────────┘
           │
           ├──→ Role Translation
           │    (학생/직장인/프리랜서)
           │
           ↓
┌──────────────────────────────────┐
│ API Response                      │
│ {                                │
│   "markdown": "# 2026년...",      │
│   "json": {...},                 │
│   "role": "employee",            │
│   "date": "2026-01-31"           │
│ }                                │
└──────────┬───────────────────────┘
           │
           ├──────┬──────┬──────┐
           ↓      ↓      ↓      ↓
        [Web]  [App]  [PDF] [API]
```

## 4. Separation of Concerns (데이터 격리)

| 레이어 | 포함 내용 | 사용자 노출 | 파일 | 예시 |
|--------|---------|-----------|------|------|
| **Rhythm Analysis** | 천간, 지지, 십성 등 | ❌ 금지 | saju.py | 甲子日, 陽明燥金 |
| **Content Assembly** | 구조화된 블록 | ❌ 금지 | assembly.py | JSON 필드 |
| **Markdown Gen** | 일반 언어 | ✅ OK | daily.py | 오늘의 흐름, 집중 |
| **Role Translation** | 역할별 문구 | ✅ OK | translator.py | 학생: 학습, 직장인: 업무 |
| **Output** | 최종 결과물 | ✅ OK | daily.md | Markdown + JSON |

## 5. Daily Page Principle

### Left Page (오늘의 안내) - 콘텐츠 풍부
- 최소 10개 섹션
- 최소 400-600자 (목표: 700-1200자)
- 설명형 문단 필수 (요약 카드 금지)
- Markdown 헤더, 리스트, 블록 인용 사용

### Right Page (사용자 기록) - 쓰기 공간
- 사용자 직접 입력 공간
- 최소한의 질문 (1-2개)
- 라이프스타일 팁 최소화

## 6. Storage & API

### Database Tables
```
profiles              # 사용자 프로필
  ├─ id
  ├─ birth_date
  ├─ birth_time
  ├─ gender
  ├─ role (student/employee/freelancer)
  └─ preferences

daily_content        # JSON 저장 (DB)
  ├─ date
  ├─ user_id
  ├─ json_data (DAILY_CONTENT_SCHEMA)
  └─ created_at

daily_logs           # 사용자 기록
  ├─ date
  ├─ user_id
  ├─ mood
  ├─ energy
  └─ notes
```

### File Storage
```
backend/daily/
├── 2026-01-31.md
├── 2026-02-01.md
└── 2026-02-02.md
```

### API Endpoints
```
GET  /api/daily/{date}              # JSON 응답
GET  /api/daily/{date}/markdown     # Markdown 응답
GET  /api/daily/{date}?role=role    # 역할별 응답
POST /api/daily/{date}/log          # 사용자 기록 저장
```

## 7. Testing Strategy

### Unit Tests
- ✅ Rhythm calculation (사주/기문/색은식)
- ✅ JSON schema validation
- ✅ Markdown generation
- ✅ Role translation (의미 불변성)

### Integration Tests
- ✅ End-to-end content generation
- ✅ API response validation
- ✅ File I/O (Markdown 저장/로드)

### Quality Tests
- ✅ Minimum character length validation
- ✅ No internal terms in Markdown
- ✅ Role-specific terminology check
- ✅ Print layout (PDF overflow, pagination)

## 8. Key Features

### Markdown-First Benefits
1. **Human Readable**: 코드로 보지 않고도 읽을 수 있음
2. **Version Control**: Git에서 diff 추적 가능
3. **Multi-Format**: Markdown → HTML, PDF, Text 변환 용이
4. **API Flexibility**: JSON과 Markdown 동시 제공

### Architecture Advantages
1. **Separation**: 내부 계산과 사용자 노출 완전 분리
2. **Reusability**: 동일 JSON으로 Web/PDF/API 모두 지원
3. **Maintainability**: 역할 번역은 한 곳에서만 수행
4. **Scalability**: 계산 결과를 캐싱하여 성능 최적화 가능

## 9. Performance Considerations

### Caching
- **Saju**: 생일별 캐시 (변경 없음)
- **Daily**: API 응답 캐시 (1시간)
- **Markdown**: 파일 시스템 캐시

### Optimization
- 계산 결과 사전 저장 (배치)
- CDN을 통한 정적 파일 제공
- API 응답 압축 (gzip)

---

## 참고 문서

- `docs/content/DAILY_CONTENT_SCHEMA.json` - JSON 스키마
- `docs/content/MARKDOWN_FORMAT_SPEC.md` - Markdown 형식 (신규)
- `backend/README_CONTENT_GENERATION.md` - 생성 파이프라인 (신규)
- `docs/legal/TERMINOLOGY_POLICY.md` - 용어 정책
- `CLAUDE.md` - 프로젝트 가이드
