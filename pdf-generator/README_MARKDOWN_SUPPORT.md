# Markdown Support for PDF Generation

PDF Generator now supports Markdown format as input.

## Features

1. **Markdown Parsing**: Converts Markdown daily content to dictionary format matching DAILY_CONTENT_SCHEMA
2. **Clean Text Extraction**: Removes markdown formatting (bold, italic, headers) for clean PDF output
3. **Emoji Support**: Preserves emojis in the parsed content
4. **Flexible Input**: Accepts both dictionary format and Markdown string format

## Usage

### Python API

```python
from generator import PDFGenerator

generator = PDFGenerator()

# From Markdown file
with open('backend/daily/2026-01-31_new_format.md', 'r', encoding='utf-8') as f:
    md_content = f.read()

pdf_path = generator.generate_daily_pdf(
    content=md_content,
    output_path="output/2026-01-31.pdf",
    role=None,
    is_markdown=True
)
```

### REST API

```bash
# Generate PDF from Markdown file
curl -H "Authorization: Bearer {token}" \
     "http://localhost:8000/api/pdf/daily/2026-01-31?use_markdown=true" \
     --output diary_2026-01-31.pdf

# Generate PDF from database (existing method)
curl -H "Authorization: Bearer {token}" \
     "http://localhost:8000/api/pdf/daily/2026-01-31?role=student" \
     --output diary_2026-01-31.pdf
```

## Markdown Format Requirements

The Markdown file should follow this structure:

```markdown
# 오늘의 안내

## 요약
Summary text here...

## 키워드
- 키워드1 • 키워드2 • 키워드3

## 리듬 해설
Rhythm description text...

## 집중/주의 포인트

### 집중
- Focus point 1
- Focus point 2

### 주의
- Caution point 1
- Caution point 2

## 행동 가이드

### 권장
- Do action 1
- Do action 2

### 지양
- Avoid action 1
- Avoid action 2

## 시간/방향

### 좋은 시간:
- **09:00~11:00**: Description
- **13:00~15:00**: Description

### 피할 시간:
- **23:30~00:30**: Description

### 좋은 방향:
- Direction text

### 피할 방향:
- Direction text

## 상태 전환 트리거

### 제스처:
- Gesture description

### 문구:
- Phrase text

### 방법:
- How-to description

## 의미 전환
Meaning shift text...

## 리듬 질문
- Question text
```

## Testing

### Test Markdown Parsing (No PDF generation)

```bash
cd pdf-generator
python test_markdown_parsing.py
```

This will:
- Parse the Markdown file to dictionary format
- Display parsed sections
- Save full JSON to `output/parsed_content.json`

### Test PDF Generation

**Prerequisites**: WeasyPrint must be properly installed with system libraries.

On Windows, WeasyPrint requires GTK+ libraries which are complex to install. Options:

1. **WSL2** (Recommended for Windows): Install Ubuntu on WSL2 and run Python there
2. **Docker**: Use containerized environment
3. **Linux/macOS**: Install system dependencies directly

See [WEASYPRINT_SETUP.md](WEASYPRINT_SETUP.md) for detailed installation instructions.

```bash
# If WeasyPrint is installed:
cd pdf-generator
python test_markdown_pdf.py
```

## File Locations

- **Markdown Files**: `backend/daily/{date}_new_format.md`
- **Output PDFs**: `pdf-generator/output/test_daily_{date}.pdf`
- **Parsed JSON**: `pdf-generator/output/parsed_content.json`

## Implementation Details

### Parser Logic (`generator.py`)

- `_parse_markdown_to_dict()`: Main parsing function
- `_save_buffer()`: Saves parsed sections to appropriate dictionary keys
- `_parse_bullet_list()`: Extracts bullet point lists
- `_clean_markdown()`: Removes markdown formatting

### API Endpoint (`backend/src/api/pdf.py`)

- New parameter: `use_markdown` (boolean)
- Loads from `backend/daily/{date}_new_format.md` when `use_markdown=true`
- Falls back to database generation when `use_markdown=false` (default)

### HTML Template (`templates/daily.html`)

No changes required - template already supports dictionary format.

## Known Limitations

1. **WeasyPrint Dependencies**: Requires system libraries (Cairo, Pango, GdkPixbuf) which are platform-specific
2. **Windows Support**: Native Windows PDF generation is challenging; WSL2 or Docker recommended
3. **Date Field**: Currently not extracted from Markdown (defaults to empty string)
4. **Extended Sections**: Additional lifestyle sections (건강/운동, 음식/영양, etc.) are not yet parsed

## Future Enhancements

- [ ] Extract date from Markdown filename
- [ ] Parse extended lifestyle sections (🏃 건강/운동, 🍜 음식/영양, etc.)
- [ ] Support for monthly content Markdown format
- [ ] Markdown validation against schema
- [ ] Auto-generate Markdown from database content
