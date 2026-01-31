# WORKPLAN - Execution Plan

## Project Status (2026-01-25)
- Backend: Render connected and verified
- MVP: 100% complete (see PROJECT_COMPLETION_REPORT.md)
- Remaining issues: left-page length, PDF Linux validation

## Improvement Work Instructions (priority order)

### 1) Left-page richness expansion (Medium)
Goal: Increase left-page text length from ~316 chars to 400-600+ chars while preserving schema and terminology rules.

Tasks:
1. Review content generation entry points:
   - backend/src/content/assembly.py
   - backend/src/content/models.py
2. Expand rhythm_description generation:
   - Add 2-4 more sentences with concrete guidance
   - Maintain user-safe language (no internal terminology)
   - Keep schema fields intact
3. Update length validation tests if needed:
   - backend/tests/test_content.py
   - backend/tests/integration/test_full_workflow.py
4. Run backend tests (scope: content + integration)
   - pytest tests/test_content.py -v
   - pytest tests/integration/test_full_workflow.py -v

Acceptance criteria:
- Left-page length consistently >= 400 chars
- Schema validation passes
- No internal terms in user-facing output

### 2) PDF generation validation on Linux (Low)
Goal: Verify WeasyPrint PDF generation in Linux environment and document results.

Tasks:
1. Provision Linux test environment (Render shell or local WSL2)
2. Install WeasyPrint dependencies per pdf-generator/WEASYPRINT_SETUP.md
3. Run PDF tests:
   - pytest tests/test_pdf_generation.py -v
4. Document results in backend/tests/PHASE8_TEST_REPORT.md or new report

Acceptance criteria:
- PDF tests pass on Linux
- Report includes environment + command outputs summary

### 3) Schema format cleanup (Optional)
Goal: Convert DAILY_CONTENT_SCHEMA.json to standard JSONSchema format (if required).

Tasks:
1. Review current schema usage in backend/src/content/validator.py
2. Convert to JSONSchema without breaking existing validation
3. Update tests that reference schema definitions

Acceptance criteria:
- Schema tests pass
- No changes to runtime validation behavior
