# CLAUDE_CODE_SKILLS - Project Execution Rules

## 1. Non-negotiables
1) Schema-first: DAILY_CONTENT_SCHEMA.json을 기준으로 생성/렌더링
2) Left page richness: 좌측은 최소 8개 블록 + 설명 문단 포함
3) Length: 좌측 최소 400자, 권장 700~1200자
4) No jargon exposure: NLP/사주/기문 등 사용자 노출 금지
5) No copying: 외부 자료 문장 복제 금지 (완전 신규 작성)

## 2. Development approach
- Start with docs and schemas
- Build content generator stub (rule-based)
- Build role translation layer
- Build renderers (web + pdf)

## 3. Testing rules
- Validate schema for each daily content JSON
- Enforce minimum length for left page text fields (rhythm_description + others)
- Snapshot test for role translation (meaning preserved)

## 4. Commit hygiene (recommended)
- docs first commit
- generator commit
- renderer commit
- role translation commit
