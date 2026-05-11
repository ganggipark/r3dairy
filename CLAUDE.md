# diary-PJ — 사주 기반 인쇄용 다이어리 생성기

## 활성 개발: `diary-gen/`

2026-05 재구축됨. 활성 코드는 `diary-gen/`에 있음.

- **산출물:** 인쇄 가능 PDF (1인 1책)
- **고객 노출:** 인쇄된 책 본문만 (UI 없음)
- **입력:** 고객 1명의 사주 정보
- **처리:** 사주 계산 → 365일 일간 콘텐츠 → PDF 조판
- **빈도:** 고객당 1회 (실시간성 불필요)

## 디렉토리

| 경로 | 역할 |
|---|---|
| `diary-gen/` | Python 파이프라인 (활성) |
| `backend/saju-calculator/` | TS 사주 계산 엔진 (lib, subprocess 호출됨) |

## 사주 용어 정책

`saju_summary`, `sinsal_influence` 등 사주 내부 용어 7필드는 **내부 메타데이터로만 유지**.
고객에게 노출되는 인쇄 본문에는 **해석된 일상 언어만** 사용.

## 레거시 코드 복구

재구축 직전 상태가 다음으로 보존됨:

| 위치 | 내용 |
|---|---|
| 태그 `pre-rebuild-baseline` | 56c0757 anchor |
| 브랜치 `archive/pre-clean-restart` | 정리 직전 |
| 원격 `main` | 11커밋 풀 백업 |

조회: `git show pre-rebuild-baseline:<path>`
복구: `git checkout archive/pre-clean-restart -- <path>`

## 워크플로우

- **회담 형식:** STATE / GOAL / EXECUTE / VERIFY / NEXT
- **코드 분석:** graphify (`graphify --update` 후 path/explain 쿼리)
- **사주 계산:** TS lib via subprocess (JSON I/O)
- **콘텐츠 생성:** Anthropic Claude API
- **인쇄 PDF:** WeasyPrint + HTML/CSS 템플릿
- **스키마 검증:** jsonschema (강제) + Pydantic (모델)
