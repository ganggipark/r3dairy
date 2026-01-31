# R³ 개인별 맞춤 다이어리 - 개발 로드맵

## 📋 프로젝트 개요

개인별 맞춤 설문을 통해 고객의 성향, 생년월일, 관심사를 수집하고,
이를 기반으로 완전히 개인화된 일간 다이어리를 생성하여
웹 앱, 모바일 앱, 인쇄 PDF 등 다양한 채널로 제공하는 시스템.

## 🎯 최종 목표

```
고객 설문 → 프로필 생성 → 개인화 콘텐츠 → 멀티 채널 배포
                                    ├─ 웹 앱
                                    ├─ 모바일 앱
                                    ├─ 인쇄 PDF
                                    └─ 이메일
```

## 👥 고객 세분화

### 1. 앱 전용 고객 (App-Only)
- **사용 방식**: 웹/모바일 앱에서만 접근
- **제공 서비스**:
  - 실시간 일간 리듬 확인
  - 앱에서 기록 작성
  - 월간/연간 분석 리포트

### 2. 앱 + 종이 다이어리 고객 (Hybrid)
- **사용 방식**: 앱 + 주간/월간 인쇄 다이어리
- **제공 서비스**:
  - 앱의 모든 기능
  - 매월 인쇄된 월간 다이어리 우편 배송
  - 종이 위의 손글씨 기록을 앱에 스캔 동기화

### 3. 종이 다이어리만 고객 (Paper-Only)
- **사용 방식**: 월간/연간 인쇄 다이어리만 사용
- **제공 서비스**:
  - 매월 맞춤형 인쇄 다이어리 우편 배송
  - QR코드를 통한 온라인 콘텐츠 접근 (선택)

## 🔧 필요한 기술 스택

### Backend
- **언어**: Python 3.11+
- **프레임워크**: FastAPI
- **데이터베이스**: PostgreSQL (Supabase)
- **작업 큐**: Celery + Redis

### Frontend
- **웹**: Next.js 14+ (이미 구축)
- **모바일**: React Native / Flutter (Phase 2)
- **인쇄**: WeasyPrint

### 통합 시스템
- **설문**: n8n + Google Forms
- **이메일**: Mailgun / SendGrid
- **파일 저장소**: AWS S3 / Azure Blob
- **자동화**: n8n Workflows

## 📦 필요한 에이전트 (Agents)

### 신규 생성
1. **Form Designer Agent**
   - 설문 폼 자동 생성
   - n8n 워크플로우 구축

2. **Data Processing Agent**
   - 설문 데이터 수집 및 정규화
   - 프로필 객체 생성

3. **Customer Manager Agent**
   - 고객 세분화 및 라우팅
   - 구독 관리

4. **PDF Generator Agent**
   - 인쇄용 PDF 생성
   - 레이아웃 최적화

5. **Email Service Agent**
   - PDF 및 알림 이메일 발송
   - 템플릿 관리

6. **Analytics Agent**
   - 사용 패턴 분석
   - 리포팅

### 기존 강화
- Personalization Engine Agent
- Content Assembly Engine
- Role Translation Layer

## 🔌 필요한 MCP 서버

### 신규 생성
1. **n8n-mcp**
   - n8n 워크플로우 자동화
   - 폼 생성, 데이터 수집

2. **file-storage-mcp**
   - S3 / Azure Blob 연동
   - 파일 업로드/다운로드

3. **email-service-mcp**
   - Mailgun / SendGrid
   - 이메일 템플릿

4. **google-forms-mcp**
   - Google Forms API
   - 응답 수집

### 기존 강화
- database-mcp (고객 데이터, 구독 정보)
- auth-mcp (고객 인증)

## 🎨 필요한 Skill

### 신규 생성
1. **form-builder**
   - 설문 폼 자동 설계
   - 조건부 질문 로직

2. **personalization-engine**
   - 프로필 → 콘텐츠 매핑
   - 개인화 알고리즘

3. **pdf-layout-optimizer**
   - 인쇄용 레이아웃
   - 페이지 분할, 타이포그래피

4. **email-template-designer**
   - HTML/CSS 이메일
   - 반응형 이메일

5. **customer-segmentation**
   - 고객 분류 로직
   - 라우팅 규칙

6. **data-validator**
   - 입력 데이터 검증
   - 필드 타입 확인

7. **content-quality-checker**
   - 콘텐츠 품질 검증
   - 글자 수, 의미

### 기존 활용
- korean-divination ✅
- saju-calculator ✅
- qimen-calculator ✅

## 📅 개발 타임라인

### Phase A: 핵심 설문 시스템 (1-2주)
**목표**: 설문 수집 파이프라인 구축

#### Week 1
- [ ] n8n-mcp 설계 및 생성
- [ ] form-builder Skill 개발
- [ ] 설문 폼 템플릿 작성

#### Week 2
- [ ] 설문 데이터 정규화 로직
- [ ] 프로필 생성 API
- [ ] 테스트 및 검증

### Phase B: 개인화 엔진 (3-4주)
**목표**: 프로필 기반 콘텐츠 생성

#### Week 3
- [ ] personalization-engine Skill 개발
- [ ] 프로필 → 콘텐츠 매핑 로직
- [ ] 역할 기반 번역 통합

#### Week 4
- [ ] 콘텐츠 생성 파이프라인
- [ ] 품질 검증 추가
- [ ] 성능 최적화

### Phase C: 멀티 채널 배포 (5-6주)
**목표**: 웹, 이메일, PDF 배포

#### Week 5
- [ ] pdf-layout-optimizer Skill 개발
- [ ] WeasyPrint 통합
- [ ] 인쇄용 템플릿

#### Week 6
- [ ] email-service-mcp 생성
- [ ] email-template-designer Skill
- [ ] 이메일 발송 파이프라인

### Phase D: 고객 관리 (7-8주)
**목표**: 고객 세분화 및 구독 관리

#### Week 7
- [ ] customer-segmentation Skill 개발
- [ ] 구독 타입 관리 DB
- [ ] 라우팅 로직

#### Week 8
- [ ] Analytics Agent 개발
- [ ] 대시보드 구축
- [ ] 사용 패턴 리포팅

## 🛠️ 기술 구성도

```
┌─────────────────────────────────────────────────────────────┐
│                     고객 입력 채널                             │
│  ┌──────────────┬──────────────┬──────────────┐             │
│  │  구글 폼      │  n8n 폼      │  웹 폼        │             │
│  └──────────────┴──────────────┴──────────────┘             │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  데이터 정규화 & 프로필                        │
│         (Data Processing Agent + data-validator)            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              개인화 엔진 (Personalization)                    │
│  ┌──────────────┬──────────────┬──────────────┐             │
│  │  리듬 분석     │  성향 분석     │  콘텐츠 생성 │             │
│  │  (사주/기문)   │  (프로필)      │  (AI)        │             │
│  └──────────────┴──────────────┴──────────────┘             │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  역할 기반 번역                               │
│         (Role Translation + customer-segmentation)          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  콘텐츠 배포 라우터                            │
│  ┌──────────────┬──────────────┬──────────────┐             │
│  │  웹 앱        │  이메일 PDF   │  대량 인쇄     │             │
│  │  (Next.js)   │  (Mailgun)   │  (인쇄소)     │             │
│  └──────────────┴──────────────┴──────────────┘             │
└─────────────────────────────────────────────────────────────┘
```

## 💾 데이터베이스 스키마 (추가)

### customers 테이블
```sql
CREATE TABLE customers (
    id UUID PRIMARY KEY,
    name VARCHAR(255),
    email VARCHAR(255),
    birth_date DATE,
    subscription_type ENUM('app_only', 'hybrid', 'paper_only'),
    profile_data JSONB,  -- 설문 응답
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### subscription_logs 테이블
```sql
CREATE TABLE subscription_logs (
    id UUID PRIMARY KEY,
    customer_id UUID REFERENCES customers,
    pdf_sent_date DATE,
    email_sent_date DATE,
    last_app_access DATE,
    status VARCHAR(50)
);
```

### generated_content 테이블
```sql
CREATE TABLE generated_content (
    id UUID PRIMARY KEY,
    customer_id UUID REFERENCES customers,
    content_date DATE,
    content_data JSONB,  -- 생성된 콘텐츠
    web_url VARCHAR(500),
    pdf_path VARCHAR(500),
    created_at TIMESTAMP
);
```

## 🚀 즉시 시작 항목

1. **n8n-mcp 설계 문서** 작성
2. **form-builder Skill** 스켈레톤 생성
3. **설문 폼** 템플릿 정의
4. **고객 DB 스키마** 확정
5. **이메일 템플릿** 설계

## 📊 성공 메트릭

- ✅ 설문 완료율 > 90%
- ✅ 프로필 생성 성공률 > 95%
- ✅ 콘텐츠 생성 시간 < 2초
- ✅ PDF 생성 시간 < 5초
- ✅ 이메일 발송 성공률 > 98%
- ✅ 고객 만족도 > 4.5/5.0
- ✅ 월간 활성 사용자 > 80%

## 📞 연락처 및 참고

- 프로젝트 리드: Claude Code
- 최종 승인: User
- 기술 리소스: E:\project, E:\project\sajuapp
- 문서: E:\project\diary-PJ\docs
