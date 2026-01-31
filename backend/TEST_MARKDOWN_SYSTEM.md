# Markdown System Test Suite

Comprehensive test script for the daily Markdown content generation system. Tests cover the complete pipeline from 색은식 calculation through NLP content generation to API endpoints.

## Overview

**File**: `test_markdown_system.py`

**Total Tests**: 18 test cases across 5 test classes

**Framework**: pytest

## Test Structure

### 1. TestSaekeunshik - 색은식 Calculation Verification (4 tests)

Tests that verify the core calculation logic for daily rhythm analysis.

#### Tests
- `test_five_movements_exist` - Verify five_movements (오행) calculation
- `test_six_qi_calculation` - Verify six_qi (육기) calculation
- `test_energy_integration_with_json` - Verify energy JSON structure
- `test_time_direction_integration` - Verify time/direction JSON structure

#### What It Tests
- Saju calculation module produces valid output
- Energy data includes all required fields (rhythm_label, intensity_level, focus_level, recovery_need, decision_level, social_level)
- Qimen data includes time windows and directions
- Lifestyle recommendations are complete

### 2. TestNLPContent - NLP Content Generation Quality (3 tests)

Tests that verify natural language generation meets quality standards.

#### Tests
- `test_character_count_minimum` - Verify minimum 400-600 characters requirement
- `test_no_technical_terms` - Verify no forbidden technical terms (사주, 천간, 지지, 오행, 십성, 대운, NLP, 알고리즘, etc.)
- `test_natural_language_quality` - Verify text is well-structured with paragraphs and sentences

#### Quality Requirements Tested
- **Character Count**: Minimum 400 characters (target 700-1200)
- **Forbidden Terms**: None of these should appear:
  - 사주, 천간, 지지, 오행, 십성, 대운, 세운, 월운
  - 기문둔갑, 납음, NLP, 알고리즘, 엔진, 계산 모듈
- **Structure**: Sentences should be clear, paragraphs should be logical
- **Readability**: Suitable for end-user consumption

### 3. TestMarkdownGeneration - Markdown Format Validation (4 tests)

Tests that verify Markdown output matches the required format and structure.

#### Tests
- `test_all_required_sections_present` - Verify all 10+ sections exist
- `test_emoji_rendering` - Verify emoji display in lifestyle categories
- `test_markdown_format_validity` - Verify valid Markdown syntax
- `test_desktop_example_structure_match` - Verify structure matches desktop layout

#### Sections Verified
1. `# 오늘의 안내` - Title
2. `## 요약` - Summary (2 sentences)
3. `## 키워드` - Keywords (8-10 items)
4. `## 리듬 해설` - Rhythm explanation (3+ paragraphs)
5. `## 집중/주의 포인트` - Focus/caution points
6. `## 행동 가이드` - Action guide (Do/Avoid)
7. `## 시간/방향` - Time windows and directions
8. `## 상태 전환 트리거` - State trigger (gesture, phrase, how-to)
9. `## 의미 전환` - Meaning shift
10. `## 리듬 질문` - Rhythm question
11. `---` - Divider
12. **10 Lifestyle Categories** with emojis:
    - 🏃 건강/운동
    - 🍜 음식/영양
    - 👔 패션/뷰티
    - 💰 쇼핑/금융
    - 🏠 생활 공간
    - ⏰ 일상 루틴
    - 📱 디지털 소통
    - 🎨 취미/창작
    - 🤝 관계/사회
    - ❄️ 계절/환경

### 4. TestAPIEndpoints - API Endpoint Testing (4 tests)

Tests that simulate API endpoint behavior and file generation.

#### Tests
- `test_markdown_file_generation` - Verify .md file is created with correct format
- `test_get_daily_markdown_endpoint_simulation` - Simulate GET /api/daily/{date}/markdown
- `test_get_daily_markdown_html_endpoint_simulation` - Simulate GET /api/daily/{date}/markdown-html
- `test_error_handling_missing_date` - Verify 404 handling for missing dates

#### Endpoints Simulated
```
GET /api/daily/{date}/markdown
- Input: target_date (YYYY-MM-DD format)
- Output: Markdown text (text/markdown)
- Error: 404 if file not found

GET /api/daily/{date}/markdown-html
- Input: target_date (YYYY-MM-DD format)
- Output: JSON {"html": "...", "date": "..."}
- Error: 404 if file not found
```

### 5. TestPipeline - Complete Pipeline Integration (3 tests)

Tests the entire content generation pipeline from birth data to Markdown output.

#### Tests
- `test_complete_generation_pipeline` - Full pipeline: Saju → Analysis → Assembly → Markdown
- `test_output_file_creation` - Verify output file is created successfully
- `test_content_quality_metrics` - Verify quality metrics across all sections

#### Pipeline Steps
1. **Saju Calculation**: `calculate_saju(birth_info)` → saju_result dict
2. **Daily Analysis**: `analyze_daily_fortune(birth_info, target_date)` → fortune dict
3. **Content Assembly**: `assemble_daily_content(date, saju_data, daily_rhythm)` → content dict
4. **Markdown Generation**: `DailyMarkdownGenerator.generate_markdown()` → markdown text
5. **File Output**: `generator.save_markdown()` → file path

## Test Data

### Sample Birth Profile (테스트 기본 사주)
Used throughout tests for consistency:

```python
BirthInfo(
    name="테스트 사용자",
    birth_date=date(1971, 11, 17),      # 1971년 11월 17일
    birth_time=time(4, 0),               # 04:00 (양력)
    gender=Gender.MALE,                  # 남자
    birth_place="서울",                  # 서울
    birth_place_lat=37.5665,
    birth_place_lng=126.9780
)
```

### Sample Energy Data (샘플 에너지 JSON)
Complete energy analysis data with:
- Rhythm type (활동적, 차분함, 균형 등)
- Energy levels (높음/중간/낮음)
- Keywords with scores (0.0-1.0)
- Flags (fatigue_risk, overpromise_risk, conflict_risk, etc.)
- Lifestyle recommendations (10 categories)

### Sample Time/Direction Data (샘플 시간/방향 JSON)
Complete Qimen analysis with:
- Good time windows (start/end times)
- Avoid time windows
- Good directions (North, South, East, West, combinations)
- Avoid directions

## Running Tests

### Run All Tests
```bash
cd backend
pytest test_markdown_system.py -v
```

### Run Specific Test Class
```bash
# Saekeunshik tests only
pytest test_markdown_system.py::TestSaekeunshik -v

# NLP content tests only
pytest test_markdown_system.py::TestNLPContent -v

# Markdown format tests only
pytest test_markdown_system.py::TestMarkdownGeneration -v

# API endpoint tests only
pytest test_markdown_system.py::TestAPIEndpoints -v

# Pipeline integration tests only
pytest test_markdown_system.py::TestPipeline -v
```

### Run Specific Test
```bash
pytest test_markdown_system.py::TestNLPContent::test_character_count_minimum -v
```

### Run with Coverage
```bash
pytest test_markdown_system.py --cov=src --cov-report=html
```

### Run with Detailed Output
```bash
pytest test_markdown_system.py -vv --tb=long
```

### Run and Stop on First Failure
```bash
pytest test_markdown_system.py -x
```

## Expected Output

### Success Example
```
============================= test session starts ==============================
platform win32 -- Python 3.10.10, pytest-9.0.2, pluggy-1.6.0
collected 18 items

test_markdown_system.py::TestSaekeunshik::test_five_movements_exist PASSED
test_markdown_system.py::TestSaekeunshik::test_six_qi_calculation PASSED
test_markdown_system.py::TestSaekeunshik::test_energy_integration_with_json PASSED
test_markdown_system.py::TestSaekeunshik::test_time_direction_integration PASSED
test_markdown_system.py::TestNLPContent::test_character_count_minimum PASSED
test_markdown_system.py::TestNLPContent::test_no_technical_terms PASSED
test_markdown_system.py::TestNLPContent::test_natural_language_quality PASSED
test_markdown_system.py::TestMarkdownGeneration::test_all_required_sections_present PASSED
test_markdown_system.py::TestMarkdownGeneration::test_emoji_rendering PASSED
test_markdown_system.py::TestMarkdownGeneration::test_markdown_format_validity PASSED
test_markdown_system.py::TestMarkdownGeneration::test_desktop_example_structure_match PASSED
test_markdown_system.py::TestAPIEndpoints::test_markdown_file_generation PASSED
test_markdown_system.py::TestAPIEndpoints::test_get_daily_markdown_endpoint_simulation PASSED
test_markdown_system.py::TestAPIEndpoints::test_get_daily_markdown_html_endpoint_simulation PASSED
test_markdown_system.py::TestAPIEndpoints::test_error_handling_missing_date PASSED
test_markdown_system.py::TestPipeline::test_complete_generation_pipeline PASSED
test_markdown_system.py::TestPipeline::test_output_file_creation PASSED
test_markdown_system.py::TestPipeline::test_content_quality_metrics PASSED

============================== 18 passed in 2.34s ==============================
```

## Key Assertions

### Character Count
- Minimum: 400 characters (required)
- Target: 700-1200 characters (goal)

### Forbidden Terms (Absolute)
```python
forbidden_terms = [
    "사주", "천간", "지지", "오행", "십성",
    "대운", "세운", "월운", "기문둔갑", "납음",
    "NLP", "알고리즘", "엔진", "계산 모듈"
]
```

### Required Sections (Markdown)
- Title: `# 오늘의 안내`
- 10+ subsections with `## ` headers
- At least one divider `---`

### Structure Requirements
- Summary: 2+ sentences
- Rhythm explanation: 3+ paragraphs
- Keywords: 8-10 items separated by bullet points
- Action guide: Both "권장" (do) and "지양" (avoid) sections
- Time/Direction: Good and avoid windows/directions

### File Output
- Format: `.md` file
- Encoding: UTF-8
- Naming: `{YYYY-MM-DD}.md` or `{YYYY-MM-DD}_new_format.md`
- Location: `backend/daily/` directory

## Troubleshooting

### Test Collection Fails
```bash
# Check Python path
python -m pytest test_markdown_system.py --collect-only

# Verify imports
python -c "from generate_daily_markdown import DailyMarkdownGenerator; print('OK')"
```

### Tests Timeout
- Increase pytest timeout: `pytest test_markdown_system.py --timeout=60`
- Check if large JSON files are being loaded

### Character Count Issues
- Verify sample JSON data has sufficient content
- Check if sections are being generated with minimum content
- Review `generate_rhythm_explanation()` output length

### Missing Sections
- Verify `generate_markdown()` calls all section methods
- Check section headers match exactly (case-sensitive)
- Ensure no sections are conditionally skipped

### Encoding Issues
- Ensure all files use UTF-8 encoding
- Check JSON files have `ensure_ascii=False`
- Verify emoji support in terminal

## Dependencies

```bash
pytest>=6.0
fastapi
pydantic
supabase>=2.0
markdown>=3.0
pathlib (built-in)
json (built-in)
datetime (built-in)
```

## File Structure

```
backend/
├── test_markdown_system.py          # This test suite
├── TEST_MARKDOWN_SYSTEM.md          # This documentation
├── generate_daily_markdown.py       # Markdown generator (tested)
├── generate_daily_content.py        # Content generator (supports tests)
├── src/
│   ├── rhythm/
│   │   ├── saju.py                  # Saju calculation (tested)
│   │   └── models.py
│   ├── content/
│   │   ├── assembly.py              # Content assembly (tested)
│   │   └── models.py
│   ├── api/
│   │   ├── daily.py                 # Daily API endpoints (simulated)
│   │   └── models.py
│   └── translation/
│       └── translator.py
├── daily/                           # Output directory for .md files
└── tests/                           # Existing tests
```

## Integration with CI/CD

### GitHub Actions Example
```yaml
name: Test Markdown System
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - run: pip install -r backend/requirements.txt
      - run: pytest backend/test_markdown_system.py -v --tb=short
```

## Performance Notes

- Complete pipeline test: ~2-5 seconds
- Individual section tests: <100ms each
- File I/O (temporary files): ~500ms
- JSON loading/dumping: <50ms

## Future Enhancements

- [ ] Add performance benchmark tests
- [ ] Add internationalization (i18n) tests for other languages
- [ ] Add accessibility tests for screen readers
- [ ] Add edge case tests (extreme energy levels, etc.)
- [ ] Add regression tests for specific user issues
- [ ] Add performance profiling
- [ ] Add snapshot testing for Markdown output

## References

- `CLAUDE.md` - Project guidelines (글자 수 요구사항, 용어 정책)
- `docs/content/DAILY_CONTENT_SCHEMA.json` - Content schema
- `docs/legal/TERMINOLOGY_POLICY.md` - Forbidden terms policy
- `generate_daily_markdown.py` - Markdown generator implementation
- `src/api/daily.py` - API endpoint implementation
