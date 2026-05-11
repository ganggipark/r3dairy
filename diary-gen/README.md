# diary-gen

사주 기반 1인 1책 인쇄용 다이어리 생성 파이프라인.

## 제품 본질

- **산출물:** 인쇄 가능한 PDF 1책 (고객 1명당)
- **고객 노출:** 인쇄된 책 본문 텍스트만 (UI/웹 없음)
- **입력:** 고객 1명의 사주 정보
- **처리:** 사주 계산 → 365일 일간 콘텐츠 생성 → PDF 조판
- **빈도:** 고객당 1회 생성 (실시간성 불필요)

## 아키텍처

```
customer.json
    ↓
[saju] subprocess → backend/saju-calculator/ (TS, Node.js)
    ↓
[content] Anthropic Claude → 365일치 일간 콘텐츠 (schema.json 강제 검증)
    ↓
[render] Jinja2 → WeasyPrint → PDF 1책
    ↓
out/diary.pdf
```

## 실행

```bash
python -m diary_gen samples/sample_customer.json --output out/diary.pdf
```

## 핵심 의존성

- **saju-engine** (`../backend/saju-calculator/`): TS 사주 계산 엔진 (subprocess 호출)
- **WeasyPrint**: PDF 조판
- **Anthropic Claude**: 콘텐츠 생성
- **Pydantic + jsonschema**: 스키마 강제 검증

## 개발 상태

MVP 단계 — 사주 계산 → 7일치 PDF 경로 검증 중.
