# Daily Content API Endpoints

## Overview

The Daily Content API provides three endpoints for accessing daily content in different formats:

1. **Markdown format** - Raw markdown text
2. **HTML format** - Converted markdown with styling classes
3. **JSON format** - Structured data with 색은식 analysis

## Endpoints

### 1. GET /api/daily/{date}/markdown

Returns the daily content as raw markdown text.

**Parameters:**
- `date`: Date in YYYY-MM-DD format (path parameter)
- `Authorization`: Bearer token (header, required)

**Response:**
- Content-Type: `text/markdown; charset=utf-8`
- Body: Raw markdown text

**Example:**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/daily/2026-01-31/markdown
```

**Response:**
```markdown
# 오늘의 안내

## 요약
오늘은 **차분한 리듬**의 날입니다...
```

**Caching:**
- Cached for 1 hour (3600 seconds)
- Cache key: `md_{date}`

**Error Responses:**
- 401: Unauthorized (missing or invalid token)
- 404: Date not found (no markdown file exists)
- 500: Server error

---

### 2. GET /api/daily/{date}/markdown-html

Converts markdown to HTML with Tailwind CSS classes for frontend rendering.

**Parameters:**
- `date`: Date in YYYY-MM-DD format (path parameter)
- `Authorization`: Bearer token (header, required)

**Response:**
- Content-Type: `application/json`
- Body: JSON object with `html` and `date` fields

**Example:**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/daily/2026-01-31/markdown-html
```

**Response:**
```json
{
  "html": "<h1 class=\"text-3xl font-bold mb-4\">오늘의 안내</h1>...",
  "date": "2026-01-31"
}
```

**Styling Classes:**
- `<h1>`: `text-3xl font-bold mb-4`
- `<h2>`: `text-2xl font-semibold mb-3 mt-6`
- `<h3>`: `text-xl font-medium mb-2 mt-4`
- `<ul>`: `list-disc list-inside mb-4 space-y-1`
- `<ol>`: `list-decimal list-inside mb-4 space-y-1`
- `<p>`: `mb-3 leading-relaxed`
- `<hr>`: `my-6 border-gray-300`

**Caching:**
- Cached for 1 hour (3600 seconds)
- Cache key: `html_{date}`

**Error Responses:**
- 401: Unauthorized
- 404: Date not found
- 500: Server error or markdown library not installed

**Dependencies:**
```bash
pip install markdown
```

Markdown extensions used:
- `extra`: Tables, fenced code blocks, etc.
- `nl2br`: Newline to `<br>` conversion
- `sane_lists`: Better list handling

---

### 3. GET /api/daily/{date}

Returns structured JSON data including 색은식 analysis (existing endpoint, enhanced).

**Parameters:**
- `date`: Date in YYYY-MM-DD format (path parameter)
- `role`: Optional role filter (query parameter: `student`, `office_worker`, `freelancer`)
- `Authorization`: Bearer token (header, required)

**Response:**
- Content-Type: `application/json`
- Body: DailyContentResponse model

**Example:**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/daily/2026-01-31?role=student"
```

**Response:**
```json
{
  "date": "2026-01-31",
  "role": "student",
  "content": {
    "summary": "...",
    "keywords": [...],
    "rhythm_analysis": "...",
    ...
  }
}
```

**Features:**
- User profile-based 사주 calculation
- Role-based content translation
- Includes 색은식 data if available
- Backward compatible with existing clients

**Error Responses:**
- 401: Unauthorized
- 404: Profile not found
- 500: Content generation error

---

## File Structure

Markdown files are stored in: `backend/daily/`

**File naming conventions:**
1. `{YYYY-MM-DD}_new_format.md` (preferred)
2. `{YYYY-MM-DD}.md` (fallback)

**Example:**
```
backend/daily/
├── 2026-01-31_new_format.md
├── 2026-01-31.json
└── COMPARISON_REPORT.md
```

---

## Caching Strategy

### In-Memory Cache
- Simple dictionary-based cache
- Timeout: 1 hour (3600 seconds)
- Keys: `md_{date}` for markdown, `html_{date}` for HTML

### Cache Invalidation
- Automatic after 1 hour
- Manual: Restart server

### Future Improvements
- Redis cache for production
- Cache warming for upcoming dates
- Cache invalidation API endpoint

---

## Testing

### Using FastAPI Docs
1. Start server: `uvicorn src.main:app --reload`
2. Open: http://localhost:8000/docs
3. Authenticate with Bearer token
4. Test endpoints interactively

### Using Test Script
```bash
cd backend
python test_daily_endpoints.py
```

### Using cURL
```bash
# Get markdown
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/daily/2026-01-31/markdown

# Get HTML
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/daily/2026-01-31/markdown-html

# Get JSON
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/daily/2026-01-31
```

---

## Implementation Notes

### Error Handling
- All endpoints validate authentication first
- 404 returned if markdown file doesn't exist
- 500 returned for unexpected errors
- Detailed error messages in response

### Performance
- Markdown → HTML conversion is fast (~1ms)
- File I/O is the bottleneck (~10ms)
- Caching reduces repeated file reads

### Security
- All endpoints require authentication
- User context validated via Supabase
- No file path traversal vulnerabilities

### Compatibility
- Python 3.11+
- FastAPI 0.100+
- markdown 3.5+
- Pydantic V2

---

## Frontend Integration

### React/Next.js Example

```typescript
// Fetch markdown
const markdown = await fetch(`/api/daily/${date}/markdown`, {
  headers: { Authorization: `Bearer ${token}` }
});
const mdText = await markdown.text();

// Fetch HTML
const htmlResponse = await fetch(`/api/daily/${date}/markdown-html`, {
  headers: { Authorization: `Bearer ${token}` }
});
const { html, date } = await htmlResponse.json();

// Render HTML
<div
  className="daily-content"
  dangerouslySetInnerHTML={{ __html: html }}
/>

// Fetch JSON
const jsonResponse = await fetch(`/api/daily/${date}?role=student`, {
  headers: { Authorization: `Bearer ${token}` }
});
const { content } = await jsonResponse.json();
```

### Tailwind CSS Setup
The HTML endpoint includes Tailwind classes, so ensure your frontend has Tailwind configured:

```javascript
// tailwind.config.js
module.exports = {
  content: [
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

---

## Troubleshooting

### "markdown library not installed"
```bash
pip install markdown
```

### "404: Date not found"
- Ensure markdown file exists in `backend/daily/`
- Check file naming: `YYYY-MM-DD_new_format.md` or `YYYY-MM-DD.md`

### "401: Unauthorized"
- Check Bearer token is valid
- Token may have expired, re-login

### HTML styling not working
- Verify Tailwind CSS is configured in frontend
- Check class names match your Tailwind config

---

## Future Enhancements

1. **Content Generation API**
   - Auto-generate markdown for missing dates
   - Queue-based generation for date ranges

2. **Advanced Caching**
   - Redis integration
   - Cache warming for next 7 days
   - Distributed cache for multi-instance deployments

3. **Content Versioning**
   - Track markdown file changes
   - Serve different versions based on user preference

4. **Export Features**
   - PDF generation from markdown
   - EPUB export for e-readers
   - Print-optimized HTML

5. **Search & Filter**
   - Full-text search across all dates
   - Keyword filtering
   - Mood/energy filtering

---

## Version History

- **v1.0.0** (2026-01-31): Initial implementation
  - Added `/markdown` endpoint
  - Added `/markdown-html` endpoint
  - Enhanced existing JSON endpoint
  - Implemented 1-hour caching
