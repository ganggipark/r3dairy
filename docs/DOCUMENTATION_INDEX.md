# R³ 다이어리 시스템 - 문서 가이드 (Documentation Index)

> 모든 문서를 체계적으로 구성한 네비게이션 가이드

---

## 빠른 시작 (Quick Start)

### 개발자: "코드를 어떻게 짜야 하나?"
1. `CLAUDE.md` 읽기 (프로젝트 개요, 5분)
2. `docs/architecture/ARCHITECTURE.md` 읽기 (데이터 흐름, 10분)
3. `backend/README_CONTENT_GENERATION.md` 읽기 (구현 가이드, 15분)
4. 코드 작성 시작

### 콘텐츠 생성자: "마크다운을 어떻게 쓰나?"
1. `docs/content/MARKDOWN_FORMAT_SPEC.md` 읽기 (10분)
2. "완전 예제" 섹션 참고
3. 체크리스트 확인 후 작성

### 기획자: "전체 구조를 빠르게 이해하고 싶다"
1. `CLAUDE.md` 의 "프로젝트 개요" 섹션
2. `docs/architecture/ARCHITECTURE.md` 의 다이어그램
3. `backend/README_CONTENT_GENERATION.md` 의 "시스템 개요"

---

## 전체 문서 맵

```
E:\project\diary-PJ\
│
├── 📄 CLAUDE.md
│   └─ 프로젝트 전체 가이드 (개발 환경, 아키텍처, 기술 스택)
│
├── 📄 DOCUMENTATION_UPDATE_SUMMARY.md (신규)
│   └─ 이 버전에서 추가/변경된 문서 요약
│
├── 📄 README.md
│   └─ 프로젝트 개요 및 설치 가이드
│
├── 📁 docs/
│   ├── 📄 DOCUMENTATION_INDEX.md (이 파일)
│   │   └─ 모든 문서의 네비게이션 가이드
│   │
│   ├── 📁 architecture/
│   │   ├── 📄 ARCHITECTURE.md (수정됨)
│   │   │   ├─ High-level Components (6가지 계층)
│   │   │   ├─ Data Flow (Markdown-First)
│   │   │   ├─ Separation of Concerns (데이터 격리)
│   │   │   └─ Performance Considerations
│   │   │
│   │   └── 📁 docs/content/
│   │       └── 📄 CONTENT_STRUCTURE.md
│   │           └─ 콘텐츠 구조 및 블록 구성
│   │
│   ├── 📁 content/
│   │   ├── 📄 DAILY_CONTENT_SCHEMA.json
│   │   │   └─ JSON 스키마 정의 (20개 필드)
│   │   │
│   │   └── 📄 MARKDOWN_FORMAT_SPEC.md (신규)
│   │       ├─ Markdown 형식 완전 스펙
│   │       ├─ 10개 필수 섹션
│   │       ├─ 라이프스타일 블록 10가지
│   │       ├─ 포맷팅 규칙
│   │       ├─ 이모지 가이드
│   │       └─ 완전 예제 + 체크리스트
│   │
│   ├── 📁 legal/
│   │   ├── 📄 TERMINOLOGY_POLICY.md
│   │   │   └─ 금지 용어 vs 허용 용어 정책
│   │   │
│   │   └── 📄 docs/design/
│   │       └── 📄 DAILY_PAGE_LAYOUT.md
│   │           └─ 좌측(안내)/우측(기록) 페이지 레이아웃
│   │
│   ├── 📁 prd/
│   │   └── 📄 PRD.md
│   │       └─ 제품 요구사항 및 MVP 범위
│   │
│   ├── 📁 tasks/
│   │   └── 📄 WORKPLAN.md
│   │       └─ 현재 작업 계획 및 진행 상황
│   │
│   └── 📁 reports/
│       ├── 📄 SAJU_CALCULATION_ANALYSIS.md
│       │   └─ 사주 계산 검증 보고서
│       │
│       └── 📄 TECHNICAL_ARCHITECTURE.md
│           └─ 기술 아키텍처 상세
│
├── 📁 backend/
│   ├── 📄 README_CONTENT_GENERATION.md (신규)
│   │   ├─ 시스템 개요
│   │   ├─ 아키텍처 (6가지 모듈)
│   │   ├─ 세 가지 계산 시스템 (사주/기문/색은식)
│   │   ├─ 콘텐츠 생성 흐름 (Step 1-5)
│   │   ├─ CLI 명령어 (4가지)
│   │   ├─ API 엔드포인트 (3가지)
│   │   ├─ 출력 형식 (Markdown/JSON)
│   │   └─ 문제 해결 (5가지 시나리오)
│   │
│   ├── 📁 src/
│   │   ├── 📁 rhythm/
│   │   │   ├── 📄 README.md
│   │   │   ├── 📄 saju.py (사주 계산)
│   │   │   ├── 📄 qimen.py (기문둔갑)
│   │   │   └── 📄 saekeunshik.py (색은식)
│   │   │
│   │   ├── 📁 content/
│   │   │   ├── 📄 README.md
│   │   │   ├── 📄 assembly.py (콘텐츠 어셈블)
│   │   │   └── 📄 validator.py (스키마 검증)
│   │   │
│   │   ├── 📁 translation/
│   │   │   ├── 📄 README.md
│   │   │   └── 📄 translator.py (역할 번역)
│   │   │
│   │   └── 📁 api/
│   │       ├── 📄 README.md
│   │       └── 📄 daily.py (Daily 엔드포인트)
│   │
│   ├── 📄 generate_daily_content.py
│   │   └─ 일회용 콘텐츠 생성 스크립트
│   │
│   ├── 📁 daily/
│   │   ├── 📄 2026-01-31.md
│   │   └── 📄 2026-02-01.md
│   │
│   └── 📄 requirements.txt
│       └─ Python 의존성
│
├── 📁 frontend/
│   ├── 📄 README.md
│   │   └─ 프론트엔드 설치 및 실행
│   │
│   ├── 📁 src/
│   │   ├── 📁 app/
│   │   │   ├── 📄 page.tsx (홈)
│   │   │   ├── 📄 today/page.tsx (일간)
│   │   │   └── 📄 month/page.tsx (월간)
│   │   │
│   │   ├── 📁 components/
│   │   │   ├── 📄 DailyPage/
│   │   │   │   ├── 📄 LeftPanel.tsx (오늘의 안내)
│   │   │   │   └── 📄 RightPanel.tsx (사용자 기록)
│   │   │   │
│   │   │   └── 📁 ui/
│   │   │       └── shadcn/ui 컴포넌트
│   │   │
│   │   └── 📁 lib/
│   │       ├── 📄 api.ts (API 클라이언트)
│   │       └── 📄 markdown.ts (Markdown 파싱)
│   │
│   └── 📄 package.json
│       └─ JavaScript 의존성
│
└── 📁 pdf-generator/
    ├── 📄 generator.py
    ├── 📁 templates/
    │   ├── 📄 daily.html
    │   └── 📄 monthly.html
    └── 📄 WEASYPRINT_SETUP.md
```

---

## 문서별 상세 가이드

### 1. CLAUDE.md (프로젝트 가이드)

**위치**: `E:\project\diary-PJ\CLAUDE.md`

**읽는 시간**: 10-15분

**대상**: 모든 개발자 (필수 읽기)

**주요 내용**:
- 프로젝트 개요 (R³ 시스템)
- 개발 환경 설정 (포트 5000)
- 핵심 아키텍처 원칙
- 콘텐츠 구조 요구사항
- 법적/표현 정책
- 기술 스택
- API 엔드포인트 목록
- 개발 가이드라인

**찾는 방법**:
- "프로젝트 개요" → R³ 시스템 이해
- "핵심 아키텍처 원칙" → 데이터 흐름
- "API 엔드포인트 목록" → 구현할 엔드포인트
- "트러블슈팅" → 문제 해결

---

### 2. docs/architecture/ARCHITECTURE.md (시스템 설계)

**위치**: `E:\project\diary-PJ\docs\architecture\ARCHITECTURE.md`

**읽는 시간**: 15-20분

**대상**: 아키텍트, 시니어 개발자

**주요 내용**:
- High-level Components (6가지 계층)
- 3가지 계산 시스템 개요 (사주/기문/색은식)
- **Markdown Generation Layer** (신규)
- Separation of Concerns (데이터 격리)
- Daily Page Principle
- Storage & API
- Testing Strategy
- Performance Considerations

**다이어그램**:
- Rhythm Analysis Engine 구조도
- Data Flow (Markdown-First)
- Output Layer 구조

**찾는 방법**:
- "High-level Components" → 6가지 계층 이해
- "Data Flow" → 전체 흐름도
- "Separation of Concerns" → 데이터 격리 규칙
- "Testing Strategy" → 테스트 항목

---

### 3. backend/README_CONTENT_GENERATION.md (구현 가이드)

**위치**: `E:\project\diary-PJ\backend\README_CONTENT_GENERATION.md`

**읽는 시간**: 20-30분 (순차), 5분 (참고 검색)

**대상**: Python 백엔드 개발자

**주요 내용**:
1. **시스템 개요** (데이터 격리 원칙)
2. **아키텍처** (디렉토리 구조, 모듈 역할)
3. **세 가지 계산 시스템** (사주/기문/색은식 완전 가이드)
   - 각각 20+ 라인의 코드 예제
   - 입력/출력 설명
4. **콘텐츠 생성 흐름** (Step 1-5)
   - 프로필 로드
   - 세 가지 계산 수행
   - JSON 어셈블
   - Markdown 변환
   - 파일 저장
5. **CLI 명령어** (서버 실행, 콘텐츠 생성, 검증)
6. **API 엔드포인트** (3가지 새 엔드포인트)
7. **출력 형식** (Markdown 샘플, JSON 샘플)
8. **문제 해결** (5가지 시나리오)

**코드 예제**: 30+ 블록

**찾는 방법**:
- CLI 명령어 → "CLI 명령어" 섹션 5
- API 구현 → "API 엔드포인트" 섹션 6
- 계산 로직 → "세 가지 계산 시스템" 섹션 3
- 문제 해결 → "문제 해결" 섹션 8

---

### 4. docs/content/MARKDOWN_FORMAT_SPEC.md (Markdown 스펙)

**위치**: `E:\project\diary-PJ\docs\content\MARKDOWN_FORMAT_SPEC.md`

**읽는 시간**: 20분 (순차), 2-5분 (참고 검색)

**대상**: 콘텐츠 생성자, Markdown 렌더링 개발자

**주요 내용**:
1. **개요** (파일 목적, 사용자 대상, 용어 정책)
2. **파일 구조** (파일명, 인코딩, 크기)
3. **헤더 구조** (파일 시작 형식, 레벨별 제목)
4. **섹션 구성** (필수 10개 + 선택 10개)
   - 각 섹션별 예제
   - 최소 글자 수 요구사항
   - 리스트 형식
5. **포맷팅 규칙** (리스트, 강조, 구분선, 인용, 테이블, 링크)
6. **이모지 가이드** (허용/금지, 사용 규칙)
7. **완전 예제** (전체 Markdown 샘플, 2,000자)
8. **작성 팁** (DO/DON'T)
9. **렌더링 환경** (웹, PDF, 모바일)
10. **검증 체크리스트** (20항목)

**테이블**: 15+ 테이블

**찾는 방법**:
- 섹션 구성 → "섹션 구성" 섹션 4
- 포맷팅 → "포맷팅 규칙" 섹션 5
- 이모지 → "이모지 가이드" 섹션 6
- 예제 → "완전 예제" 섹션 7
- 검증 → "검증 체크리스트" 섹션 10

---

### 5. docs/content/DAILY_CONTENT_SCHEMA.json (JSON 스키마)

**위치**: `E:\project\diary-PJ\docs/content/DAILY_CONTENT_SCHEMA.json`

**읽는 시간**: 5-10분

**대상**: JSON 구조 이해 필요한 개발자

**주요 내용**:
- 20개 JSON 필드 정의
- 각 필드의 타입, 최소 길이, 요구 항목
- JSON Schema Draft-07 준수

**필드 예시**:
- `summary`: 30자 이상
- `keywords`: 배열 (3-10개)
- `rhythm_description`: 200자 이상
- `focus_caution`: 객체 (focus + caution)
- `daily_health_sports`: 객체 (추천/팁/웰니스)
- ... (총 20개)

**찾는 방법**:
- 필드 목록 → JSON 파일 직접 열기
- 필드별 요구사항 → "properties" 섹션 검색

---

### 6. docs/legal/TERMINOLOGY_POLICY.md (용어 정책)

**위치**: `E:\project\diary-PJ\docs/legal/TERMINOLOGY_POLICY.md`

**읽는 시간**: 5분

**대상**: 모든 콘텐츠 생성자, 개발자

**주요 내용**:
- 금지 용어 (사주명리, 기문둔갑, 색은식, NLP 등)
- 허용 용어 (오늘의 흐름, 리듬, 에너지 등)
- 변환 예시

**찾는 방법**:
- "이 용어를 써도 되나?" → 정책 문서 검색

---

### 7. docs/tasks/WORKPLAN.md (작업 계획)

**위치**: `E:\project\diary-PJ\docs/tasks/WORKPLAN.md`

**읽는 시간**: 5분

**대상**: 프로젝트 매니저, 팀 리더

**주요 내용**:
- 현재 진행 상황
- 다음 작업 항목
- 일정표

**찾는 방법**:
- "다음에 뭘 해야 하나?" → WORKPLAN.md 확인

---

## 사용자 역할별 읽기 경로

### 1. 신입 개발자 (전체 이해 필요)

**소요 시간**: 1-2시간

**읽기 순서**:
1. `CLAUDE.md` (15분) - 프로젝트 개요
2. `docs/architecture/ARCHITECTURE.md` (20분) - 전체 아키텍처
3. `backend/README_CONTENT_GENERATION.md` (25분) - 구현 이해
4. `docs/content/MARKDOWN_FORMAT_SPEC.md` (15분) - 출력 형식
5. `docs/legal/TERMINOLOGY_POLICY.md` (5분) - 용어 정책

**학습 목표**:
- R³ 시스템의 전체 흐름 이해
- 데이터 격리 원칙 이해
- 구현할 모듈 파악
- 콘텐츠 생성 요구사항 이해

---

### 2. 백엔드 개발자 (구현 담당)

**소요 시간**: 2-3시간 (세부 구현 포함)

**읽기 순서**:
1. `CLAUDE.md` (5분) - 개발 환경 설정
2. `docs/architecture/ARCHITECTURE.md` (15분) - 데이터 흐름
3. `backend/README_CONTENT_GENERATION.md` (전체, 30분) - 상세 가이드
   - 특히 섹션 3, 4, 5, 6 집중
4. `docs/content/DAILY_CONTENT_SCHEMA.json` (5분) - 스키마 확인

**구현 체크리스트**:
- [ ] 3가지 계산 모듈 이해 (사주/기문/색은식)
- [ ] JSON 어셈블리 로직 이해
- [ ] Markdown 생성 로직 구현
- [ ] 역할 번역 적용
- [ ] API 엔드포인트 구현
- [ ] 오류 처리 및 로깅

---

### 3. 프론트엔드 개발자 (렌더링 담당)

**소요 시간**: 1시간

**읽기 순서**:
1. `CLAUDE.md` - 개발 환경 설정 (프론트엔드 부분만)
2. `docs/content/MARKDOWN_FORMAT_SPEC.md` (20분) - Markdown 형식
3. `backend/README_CONTENT_GENERATION.md` - "API 엔드포인트" 섹션
4. `docs/content/DAILY_CONTENT_SCHEMA.json` (5분) - JSON 필드 이해

**구현 체크리스트**:
- [ ] API 호출 로직
- [ ] Markdown → HTML 렌더링
- [ ] 좌측/우측 페이지 레이아웃
- [ ] 반응형 디자인
- [ ] PDF 출력

---

### 4. 콘텐츠 생성자 (마크다운 작성)

**소요 시간**: 30분

**읽기 순서**:
1. `docs/content/MARKDOWN_FORMAT_SPEC.md` (20분)
   - 특히 "섹션 구성" + "완전 예제"
2. `docs/legal/TERMINOLOGY_POLICY.md` (5분)
3. "검증 체크리스트" 확인 (5분)

**작성 체크리스트**:
- [ ] 파일명: {YYYY-MM-DD}.md
- [ ] 인코딩: UTF-8, LF
- [ ] 섹션: 최소 10개
- [ ] 글자 수: 최소 400자
- [ ] 이모지: 20개 이하
- [ ] 전문용어: 0개
- [ ] 길이 요구사항 준수

---

### 5. QA/테스터 (검증 담당)

**소요 시간**: 45분

**읽기 순서**:
1. `backend/README_CONTENT_GENERATION.md` - "문제 해결" 섹션
2. `docs/content/MARKDOWN_FORMAT_SPEC.md` - "검증 체크리스트"
3. 각 계산 시스템의 기준값 확인

**테스트 항목**:
- [ ] JSON 스키마 검증
- [ ] Markdown 형식 검증
- [ ] 문자 길이 확인
- [ ] 전문용어 검사
- [ ] 역할별 번역 검증
- [ ] PDF 렌더링 테스트

---

### 6. 프로젝트 리더/아키텍트 (전체 감독)

**소요 시간**: 30분

**읽기 순서**:
1. `DOCUMENTATION_UPDATE_SUMMARY.md` (5분)
2. `docs/architecture/ARCHITECTURE.md` - 다이어그램만 (5분)
3. `backend/README_CONTENT_GENERATION.md` - "시스템 개요" (10분)
4. `docs/tasks/WORKPLAN.md` (5분)

**감독 항목**:
- [ ] 전체 아키텍처 일관성
- [ ] 데이터 격리 준수
- [ ] 성능 목표 달성
- [ ] 팀별 작업 진행

---

## 문서 버전 관리

### 현재 버전: 1.0 (2026-01-31)

**주요 추가사항**:
1. `backend/README_CONTENT_GENERATION.md` (신규)
   - 일간 콘텐츠 생성 파이프라인 완전 가이드
   - 시스템 개요부터 문제 해결까지

2. `docs/content/MARKDOWN_FORMAT_SPEC.md` (신규)
   - 사용자 노출 Markdown 형식 완전 스펙
   - 10개 필수 섹션 + 선택 라이프스타일 블록

3. `docs/architecture/ARCHITECTURE.md` (수정)
   - Markdown Generation Layer 추가
   - 데이터 흐름 다이어그램 개선
   - Separation of Concerns 테이블 추가

4. `CLAUDE.md` (수정)
   - 데이터 흐름 섹션 확장
   - 신규 문서 참조 추가

### 예상 다음 버전: 1.1

**계획 추가사항**:
- [ ] 월간/연간 콘텐츠 생성 가이드
- [ ] 배치 작업 설정 가이드
- [ ] 성능 최적화 전략
- [ ] 다국어 지원 가이드
- [ ] 실제 구현 예제 (코드)

---

## 자주 찾는 것들 (FAQ Index)

### "포트 몇 번을 써야 하나?"
→ `CLAUDE.md` - "개발 환경 설정 원칙"

### "어떻게 CLI 명령을 실행하나?"
→ `backend/README_CONTENT_GENERATION.md` - "CLI 명령어" 섹션

### "API 엔드포인트는 뭐가 있나?"
→ `backend/README_CONTENT_GENERATION.md` - "API 엔드포인트" 섹션
또는 `CLAUDE.md` - "API 엔드포인트 목록"

### "마크다운 파일 예제가 있나?"
→ `docs/content/MARKDOWN_FORMAT_SPEC.md` - "완전 예제" 섹션

### "이 용어를 써도 되나?"
→ `docs/legal/TERMINOLOGY_POLICY.md`

### "전체 구조를 시각화해줄래?"
→ `docs/architecture/ARCHITECTURE.md` - 다이어그램 섹션들

### "문제 해결 방법은?"
→ `backend/README_CONTENT_GENERATION.md` - "문제 해결" 섹션

### "다음에 뭘 해야 하나?"
→ `docs/tasks/WORKPLAN.md`

---

## 문서 최적화 팁

### 효율적인 검색

**IDE에서**: Ctrl+Shift+F (전체 검색)
```
검색어: "Markdown" 또는 "사주" 등
결과 필터링 후 해당 문서 열기
```

**GitHub에서**: 상단 검색창 사용
```
path:docs keyword 또는
path:backend keyword
```

**로컬에서**: 터미널 grep
```bash
grep -r "Markdown" docs/ backend/
grep -r "API 엔드포인트" CLAUDE.md
```

### 즐겨찾기 추천

1. **문제 해결**: `backend/README_CONTENT_GENERATION.md` 섹션 8
2. **Markdown 예제**: `docs/content/MARKDOWN_FORMAT_SPEC.md` 섹션 7
3. **용어 정책**: `docs/legal/TERMINOLOGY_POLICY.md`
4. **아키텍처**: `docs/architecture/ARCHITECTURE.md` 섹션 2-4

---

## 피드백 및 개선

### 문서 버그 제보

문제점 발견 시:
1. 어느 문서인지 (파일 경로)
2. 어느 섹션인지
3. 문제가 뭔지 (부정확한 정보, 오타, 등)

### 문서 개선 제안

개선 아이디어:
1. 추가되어야 할 내용
2. 더 명확해야 할 부분
3. 추가 예제 필요 부분

---

## 참고: 파일 절대 경로

모든 경로는 Windows 기준 절대 경로입니다:

```
E:\project\diary-PJ\
├── CLAUDE.md
├── DOCUMENTATION_UPDATE_SUMMARY.md
├── README.md
├── docs\
│   ├── DOCUMENTATION_INDEX.md
│   ├── architecture\ARCHITECTURE.md
│   ├── content\
│   │   ├── DAILY_CONTENT_SCHEMA.json
│   │   └── MARKDOWN_FORMAT_SPEC.md
│   ├── legal\TERMINOLOGY_POLICY.md
│   ├── prd\PRD.md
│   ├── tasks\WORKPLAN.md
│   └── reports\
├── backend\
│   ├── README_CONTENT_GENERATION.md
│   ├── src\
│   │   ├── rhythm\
│   │   ├── content\
│   │   ├── translation\
│   │   └── api\
│   ├── daily\
│   ├── generate_daily_content.py
│   └── requirements.txt
└── frontend\
```

---

**문서화 완료일**: 2026-01-31
**현재 버전**: 1.0
**다음 검토**: 2026-02-28
**담당**: Technical Documentation Team
