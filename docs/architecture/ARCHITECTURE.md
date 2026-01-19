# ARCHITECTURE - R³ Diary System

## 1. 목표
- 동일한 콘텐츠 데이터로 Web + Print(PDF) 동시 지원
- 내부 계산(전문용어)과 사용자 노출(일반 언어) 완전 분리
- 역할 기반 가변 콘텐츠는 번역 레이어에서만 수행

## 2. High-level Components
1) Input Layer
- Profile: birth info, role, preferences
- Daily Log: user entries (mood/energy/notes)

2) Rhythm Analysis Engine (internal)
- 출생/시간 기반 데이터로 "오늘의 흐름"을 산출 (내부 표현)
- 결과는 "리듬 신호" 형태로 Content Assembly에 전달

3) Content Assembly Engine
- 리듬 신호를 기반으로 구조화된 콘텐츠 블록 생성
- 출력은 DAILY_CONTENT_SCHEMA.json 구조를 준수

4) Role Translation Layer
- role에 따라 문장/예시/질문/행동 가이드를 변형
- 리듬(핵심 의미)을 바꾸지 않고 표현만 변형

5) Output Layer
- Web Renderer (React/Next 등)
- PDF Renderer (HTML→PDF 또는 ReportLab 등)

## 3. Data Flow
Profile + Preferences → Rhythm Analysis → Content Assembly → Role Translation → Render(Web/PDF)

## 4. Separation of Concerns
- internal_terms: internal only (never shown to user)
- user_copy: user-facing text only (no internal terms)
- Schema-first: 콘텐츠는 스키마가 기준, UI는 스키마를 렌더링

## 5. Daily Page Principle
- Left page: content-rich guidance (min 8 blocks, long-form explanation)
- Right page: writable space (minimal prompts)

## 6. Storage (suggested)
- users
- profiles
- daily_content (date, schema_json)
- daily_logs (user inputs)
- templates (role translation templates)

## 7. Testing
- Schema validation tests (JSON schema)
- Role translation regression tests (meaning invariance)
- Print layout tests (overflow, typography, pagination)
