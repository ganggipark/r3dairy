# diary-PJ

사주 기반 1인 1책 인쇄용 다이어리 생성기.

**현 상태:** 2026-05 nuclear clean restart 완료. **빈 상태에서 새로 시작.**
**유일 보존 자산:** `saju-engine/` (TS 사주 계산 엔진)

## 제품 본질

- **산출물:** 인쇄 가능 PDF (1인 1책)
- **고객 노출:** 인쇄된 책 본문만 (UI 없음)
- **입력:** 고객 1명의 사주 정보
- **처리:** 사주 계산 → 365일 콘텐츠 생성 → PDF 조판
- **빈도:** 고객당 1회 (실시간성 불필요)

## 현 디렉토리

| 경로 | 역할 |
|---|---|
| `saju-engine/` | TS 사주 계산 엔진 (검증됨, 유일 보존) |

그 외 모든 것은 새로 작성.

## 사주 용어 정책

`saju_summary`, `sinsal_influence` 등 사주 내부 용어 7필드는 **내부 메타데이터로만**.
고객 노출 인쇄 본문은 **해석된 일상 언어만**.

## 레거시 복구

다음 ref들에 옛 코드 모두 보존됨:

| ref | 가리키는 위치 |
|---|---|
| 태그 `pre-rebuild-baseline` | 56c0757 (rebuild 직전 11커밋) |
| 브랜치 `archive/pre-clean-restart` | ea1daf3 (정리 직전) |
| 커밋 `85df407` | diary-gen 골격 (보존 자산 5개 포함) |
| 원격 `main` | 11커밋 풀 백업 |

조회: `git show pre-rebuild-baseline:<path>`
복구: `git checkout 85df407 -- diary-gen/<path>` (필요한 자산만)

## 워크플로우

- **회담 형식:** STATE / GOAL / EXECUTE / VERIFY / NEXT
- **코드 분석:** graphify (`graphify --update` 후 path/explain)
- **사주 계산:** TS lib via subprocess (JSON I/O)
- **콘텐츠 생성:** Anthropic Claude API
- **인쇄 PDF:** WeasyPrint (예정)
- **스키마 검증:** jsonschema + Pydantic (예정)

## 다음 마일스톤

1. saju-engine CLI 인터페이스 분석 (입력/출력 JSON 스키마 확인)
2. 새 Python 파이프라인 패키지 설계 (이름/구조 신규 결정)
3. 사주 계산 → 7일치 PDF MVP

이전에 작성됐던 diary-gen 골격은 참고용으로 `85df407` 커밋에 보존됨.
실제 구현은 이 마일스톤들에서 신규 결정.
