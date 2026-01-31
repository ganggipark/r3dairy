# Daily Markdown Generation

## Overview

`generate_daily_markdown.py` script generates "오늘의 안내" (Today's Guide) Markdown files from JSON rhythm analysis data.

## Requirements

- Python 3.7+
- Input files:
  - `output/today_energy_simple.json` - Energy and lifestyle recommendations
  - `output/today_time_direction_simple.json` - Time windows and directions (Qimen analysis)

## Usage

### Basic Usage

```bash
cd backend
python generate_daily_markdown.py
```

This will:
1. Load JSON files from `backend/output/` directory
2. Generate Markdown file at `backend/daily/{YYYY-MM-DD}.md`
3. Display character count statistics

### Custom File Paths

```bash
python generate_daily_markdown.py path/to/energy.json path/to/time_direction.json
```

## Output Structure

The generated Markdown follows this exact structure:

```markdown
# 오늘의 안내

## 요약
(2 sentences: rhythm + key point)

## 키워드
(8-10 keywords from JSON scores)

## 리듬 해설
(3 paragraphs, 250+ chars)

## 집중/주의 포인트
### 집중
(2-3 focus points)
### 주의
(2-3 attention points)

## 행동 가이드
### 권장
(3-5 recommended actions)
### 지양
(3-5 actions to avoid)

## 시간/방향
### 좋은 시간:
### 피할 시간:
### 좋은 방향:
### 피할 방향:

## 상태 전환 트리거
### 제스처:
### 문구:
### 방법:

## 의미 전환
(Reframing paragraph)

## 리듬 질문
(Context-appropriate question)

---

## 🏃 건강/운동
## 🍜 음식/영양
## 👔 패션/뷰티
## 💰 쇼핑/금융
## 🏠 생활 공간
## ⏰ 일상 루틴
## 📱 디지털 소통
## 🎨 취미/창작
## 🤝 관계/사회
## ❄️ 계절/환경
```

## Content Requirements

### Character Count
- **Minimum**: 400 characters (left page requirement)
- **Target**: 700-1200 characters
- The script will display a warning if content is below 400 chars

### Language Guidelines
- ✅ Natural, conversational Korean
- ✅ User-friendly terminology (흐름, 리듬, 에너지)
- ❌ Technical terms (사주명리, 기문둔갑, NLP)
- ❌ Professional jargon (천간, 지지, 오행)

## Input JSON Schema

### today_energy_simple.json

```json
{
  "energy": {
    "rhythm_label": "차분",
    "intensity_level": "낮음",
    "focus_level": "높음",
    "decision_level": "보통",
    "social_level": "낮음",
    "recovery_need": "높음"
  },
  "flags": {
    "fatigue_risk": true,
    "overpromise_risk": false,
    "conflict_risk": false,
    "spending_risk": false,
    "mistake_risk": false
  },
  "keywords": {
    "scores": {
      "휴식": 0.9,
      "집중": 0.85,
      ...
    }
  },
  "lifestyle": {
    "reco": {
      "health": {
        "do": ["가벼운 산책"],
        "avoid": ["격한 운동"],
        "tip": "편안한 운동으로..."
      },
      ...
    }
  }
}
```

### today_time_direction_simple.json

```json
{
  "qimen": {
    "good_windows": [
      {
        "start": "09:00",
        "end": "11:00",
        "reason_plain": "집중이 잘 붙는 구간"
      }
    ],
    "avoid_windows": [...],
    "good_directions": ["북동", "남서"],
    "avoid_directions": []
  }
}
```

## Example Output

See `backend/daily/2026-01-31_new_format.md` for a complete example.

## Features

### Content Generation Logic

1. **Summary**: Combines rhythm label, intensity, and key flags
2. **Keywords**: Top 8-10 keywords sorted by score (threshold: 0.3+)
3. **Rhythm Explanation**: 3 paragraphs covering:
   - Overall flow and energy levels
   - Decision-making and social aspects
   - Recovery needs
4. **Focus/Attention**: Derived from energy levels and flags
5. **Action Guide**: Context-aware recommendations
6. **Time/Direction**: Qimen analysis data
7. **State Triggers**: Adaptive to rhythm type
8. **Meaning Shift**: Reframes the day's purpose
9. **Rhythm Question**: Prompts self-reflection
10. **Lifestyle Sections**: 10 categories with emoji headers

### Adaptive Content

The script intelligently adapts content based on:

- **Recovery Need High** → Rest-focused messaging
- **Intensity High** → Action-oriented guidance
- **Focus High** → Concentration tasks
- **Social Low** → Minimal interaction advice
- **Flags** → Specific warnings (fatigue, overpromise, etc.)

## Verification

After generation, check:

1. ✅ Character count >= 400 (shown in output)
2. ✅ All 10 lifestyle sections present
3. ✅ No technical terms in user-facing text
4. ✅ Structure matches desktop example
5. ✅ File saved to `backend/daily/{date}.md`

## Troubleshooting

### FileNotFoundError
```
[ERROR] 에러: 파일을 찾을 수 없습니다: ...
```
**Solution**: Ensure JSON files exist in `backend/output/` directory

### Character Count Warning
```
[WARN] 좌측 페이지 최소 글자 수 충족 (400+ 자)
```
**Action**: Review content generation logic for specific energy/flags combination

### Unicode Encoding Error
**Fixed**: All console output uses ASCII-safe markers (`[OK]`, `[ERROR]`)

## Integration

This script is part of the content pipeline:

```
Rhythm Analysis Engine → JSON Output → generate_daily_markdown.py → Markdown File → Frontend/PDF
```

## Related Files

- `backend/output/today_energy_simple.json` - Input energy data
- `backend/output/today_time_direction_simple.json` - Input time/direction data
- `backend/daily/2026-01-31_new_format.md` - Example output
- `docs/content/DAILY_CONTENT_SCHEMA.json` - Content schema definition
- `CLAUDE.md` - Project guidelines

## Future Enhancements

- [ ] Role-based translation (student/worker/freelancer)
- [ ] Season-aware content variations
- [ ] Multi-language support
- [ ] Validation against DAILY_CONTENT_SCHEMA.json
