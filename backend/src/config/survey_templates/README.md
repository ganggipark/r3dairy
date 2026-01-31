# Survey Templates - R³ Diary Customer Onboarding

This module provides comprehensive survey form templates for collecting customer data during onboarding.

## Overview

The survey system supports:
- **Multiple templates**: Default, Quick Profile, Student, Office Worker
- **Localization**: English and Korean (ko-KR)
- **Multi-platform deployment**: n8n, Google Forms, Web
- **Response normalization**: Standardized data format
- **Database integration**: Supabase PostgreSQL

## Directory Structure

```
survey_templates/
├── __init__.py                 # Module exports
├── default_survey.py           # Main survey templates
├── korean_customization.py     # Korean localization
├── deployment.py               # Platform deployment configs
├── database_models.py          # Pydantic models + SQL schema
├── examples.json               # Example responses
└── README.md                   # This file
```

## Quick Start

### 1. Create a Survey

```python
from src.config.survey_templates import create_default_survey

# Create default English survey
survey = create_default_survey()
print(f"Survey ID: {survey.id}")
print(f"Sections: {len(survey.sections)}")
```

### 2. Create a Localized Survey

```python
from src.config.survey_templates import (
    get_survey_by_template,
    apply_korean_localization
)

# Get template and localize
english_survey = get_survey_by_template("default")
korean_survey = apply_korean_localization(english_survey)
```

### 3. Deploy to n8n

```python
from src.config.survey_templates import SurveyDeploymentConfig

# Generate n8n workflow
survey = create_default_survey()
workflow = SurveyDeploymentConfig.get_n8n_deployment_config(survey)

# Get deployment instructions
instructions = SurveyDeploymentConfig.get_deployment_instructions(
    survey,
    "n8n"
)
print(instructions)
```

### 4. Deploy to Web

```python
# Generate React component and API config
web_config = SurveyDeploymentConfig.get_web_deployment_config(survey)

print(web_config["react_component"])  # React code
print(web_config["api"]["submit_endpoint"])  # API endpoint
```

## Survey Templates

### Default Survey (Comprehensive)

**Purpose**: Complete customer onboarding
**Estimated Time**: 5 minutes
**Sections**: 7

1. **Basic Information**
   - Name, Email, Birth Date, Gender

2. **Role Selection**
   - Student, Office Worker, Freelancer, Parent, Other

3. **Personality Assessment** (8 questions)
   - Extroversion, Conscientiousness, Openness, Agreeableness
   - Emotional Stability, Focus, Creativity, Logic vs. Emotion

4. **Interests & Preferences**
   - Topics (multiple choice, max 5)
   - Communication tone preference

5. **Diary Format Preference**
   - App only, Hybrid (app + print), Paper only

6. **Paper Delivery Details** (conditional)
   - Paper size, Delivery frequency, Address
   - Only shown if NOT "App only"

7. **Communication Preferences**
   - Email frequency
   - Privacy, Marketing, Research consents

### Quick Profile Survey

**Purpose**: Fast onboarding
**Estimated Time**: 2 minutes
**Sections**: 3

Minimal version with only essentials:
- Basic info, Brief personality (3 questions), Format preference

### Student Survey

**Purpose**: Student-specific onboarding
**Sections**: 3

Focuses on:
- Education level, Learning style, Study preferences
- Academic goals

### Office Worker Survey

**Purpose**: Professional onboarding
**Sections**: 3

Focuses on:
- Industry, Work environment, Productivity patterns
- Professional priorities

## Korean Localization

All templates support Korean translation via `apply_korean_localization()`.

**Features**:
- Section titles and descriptions
- Field labels and placeholders
- All option lists (gender, role, interests, etc.)
- Personality question statements

**Example**:

```python
english = get_survey_by_template("default")
korean = apply_korean_localization(english)

# Basic Info section
# English: "Basic Information"
# Korean: "기본 정보"

# Gender options
# English: ["Male", "Female", "Other", "Prefer not to say"]
# Korean: ["남성", "여성", "기타", "답변 안 함"]
```

## Deployment Targets

### n8n Workflow

**Includes**:
- HTTP Webhook trigger
- Data normalization function
- Supabase database insert
- Email confirmation (optional)
- Response webhook

**Usage**:

```python
workflow = SurveyDeploymentConfig.get_n8n_deployment_config(survey)

# Import JSON into n8n
# Activate workflow
# Webhook URL: https://your-n8n.com/webhook/survey/{survey.id}
```

### Google Forms

**Includes**:
- Form metadata (title, description)
- Question items with validation
- Response destination

**Note**: Google Forms has limitations on conditional logic.

### Web Form

**Includes**:
- HTML form template
- React component code
- API endpoint configuration
- Example payload

**Usage**:

```python
web_config = SurveyDeploymentConfig.get_web_deployment_config(survey)

# Create React component
with open(f"components/Survey{survey.id}.tsx", "w") as f:
    f.write(web_config["react_component"])

# Create API endpoint
# POST /api/surveys/{survey.id}/submit
```

## Response Normalization

All survey responses are normalized to a standard format:

```python
{
    "profile": {
        "name": str,
        "email": str,
        "birth_date": str,
        "gender": "male" | "female" | "other" | "not_specified",
        "role": "student" | "office_worker" | "freelancer" | "parent" | "other"
    },
    "personality": {
        "extroversion": int,        # 1-5
        "structured": int,           # 1-5
        "openness": int,             # 1-5
        "empathy": int,              # 1-5
        "calm": int,                 # 1-5
        "focus": int,                # 1-5
        "creative": int,             # 1-5
        "logical": int               # 1-5
    },
    "interests": {
        "topics": List[str],
        "tone_preference": str
    },
    "format": {
        "diary_type": "app_only" | "hybrid" | "paper_only",
        "paper_size": str,           # if applicable
        "delivery_frequency": str,   # if applicable
        "delivery_address": str      # if applicable
    },
    "communication": {
        "email_frequency": str,
        "consents": {
            "privacy": bool,
            "marketing": bool,
            "research": bool
        }
    },
    "metadata": {
        "submitted_at": str,
        "form_version": str,
        "locale": str,
        "source": str
    }
}
```

## Database Schema

### Tables

**survey_configurations**
- Stores survey templates
- Fields: id, name, description, form_json, status, deployed_to, response_count

**survey_responses**
- Stores individual submissions
- Fields: id, survey_id, response_data, normalized_data, submitted_at, ip_address, source, user_id

**survey_deployments**
- Tracks deployments to platforms
- Fields: survey_id, target, deployed_at, deployment_config, webhook_url, status

### SQL Schema

The complete SQL schema is available in `database_models.py`:

```python
from src.config.survey_templates.database_models import SUPABASE_SCHEMA

# Execute in Supabase SQL Editor
```

## API Endpoints

### Create Survey

```http
POST /api/surveys/create
Content-Type: application/json

{
  "template": "default",
  "locale": "ko-KR"
}
```

### Get Survey

```http
GET /api/surveys/{survey_id}
```

### Deploy Survey

```http
POST /api/surveys/{survey_id}/deploy
Content-Type: application/json

{
  "target": "n8n"
}
```

### Submit Response

```http
POST /api/surveys/submit
Content-Type: application/json

{
  "survey_id": "survey_abc123",
  "response_data": {
    "name": "김학생",
    "email": "student@example.com",
    ...
  },
  "source": "web"
}
```

### Get Responses

```http
GET /api/surveys/{survey_id}/responses?limit=100&offset=0
```

### Get Summary

```http
GET /api/surveys/{survey_id}/summary
```

## Testing

Run tests with pytest:

```bash
cd backend
pytest tests/test_survey_deployment.py -v
```

**Test Coverage**:
- Survey creation from templates
- Korean localization
- Deployment config generation
- Response normalization
- Example validation

## Example Responses

See `examples.json` for complete example responses:

- `example_student` - Student response (Korean)
- `example_office_worker` - Office worker response
- `example_freelancer` - Freelancer response
- `example_parent` - Parent response
- `example_minimal` - Minimal required fields
- `normalized_example_student` - Normalized format
- `validation_test_cases` - Edge cases for testing

## Deployment Workflow

### Complete Deployment Process

1. **Create Survey**
   ```python
   survey = create_default_survey()
   korean_survey = apply_korean_localization(survey)
   ```

2. **Save to Database**
   ```python
   # Via API endpoint
   POST /api/surveys/create
   ```

3. **Deploy to Platform**
   ```python
   # Generate deployment config
   workflow = SurveyDeploymentConfig.get_n8n_deployment_config(korean_survey)

   # Deploy via API
   POST /api/surveys/{survey_id}/deploy
   ```

4. **Activate**
   - n8n: Import workflow, activate
   - Web: Deploy React component
   - Google Forms: Create via API

5. **Test**
   ```bash
   curl -X POST https://your-n8n.com/webhook/survey/{survey_id} \
     -H "Content-Type: application/json" \
     -d @examples/example_student.json
   ```

6. **Monitor**
   ```http
   GET /api/surveys/{survey_id}/summary
   ```

## Conditional Logic

The survey supports conditional sections and fields.

**Example**: Paper details section only shows if diary preference is NOT "App only"

```python
# In default_survey.py
builder.add_conditional_logic(
    "paper_details",
    {
        "show_if": {
            "field_id": "diary_preference",
            "operator": "not_equals",
            "value": "App only (web/mobile)"
        }
    }
)
```

## Validation

Response validation includes:
- Required field checks
- Email format validation
- Date format validation
- Likert scale range (1-5)
- Multiple choice max selections
- Conditional field requirements

## Extending the System

### Add New Template

```python
# In default_survey.py

def create_my_custom_survey() -> FormConfiguration:
    """Create custom survey."""
    return (
        FormBuilder("My Custom Survey", "Description")
        .add_section("section1", "Title")
        .add_field("section1", "field1", "Label", FieldType.TEXT)
        .build()
    )

# Register in get_survey_by_template()
```

### Add New Localization

```python
# In korean_customization.py or new file

JAPANESE_SETTINGS = {
    "locale": "ja-JP",
    "gender_options": ["男性", "女性", "その他", "回答しない"],
    ...
}

def apply_japanese_localization(form: FormConfiguration) -> FormConfiguration:
    # Implementation
    pass
```

### Add New Deployment Target

```python
# In deployment.py

@staticmethod
def get_typeform_deployment_config(form: FormConfiguration) -> Dict:
    """Typeform deployment configuration."""
    # Implementation
    pass
```

## Troubleshooting

### Issue: Survey not found

**Cause**: Survey ID doesn't exist in database
**Solution**: Check survey creation, verify ID

### Issue: Conditional logic not working

**Cause**: Field ID mismatch
**Solution**: Ensure exact field ID in conditional logic

### Issue: Korean text not displaying

**Cause**: Character encoding issue
**Solution**: Ensure UTF-8 encoding in all files

### Issue: n8n workflow fails

**Cause**: Missing Supabase credentials
**Solution**: Configure Supabase connection in n8n

## Next Steps

After Phase A Week 1 completion:

1. **Deploy to production**
   - Create survey in Supabase
   - Deploy n8n workflow
   - Test end-to-end submission

2. **Data normalization module** (Phase A Week 2)
   - Profile creation from survey responses
   - Validation and enrichment

3. **User research** (Phase A Week 3)
   - Collect real survey responses
   - Analyze patterns
   - Refine templates

## Support

For questions or issues:
- Check existing tests in `test_survey_deployment.py`
- Review example responses in `examples.json`
- See API documentation at `/docs` (FastAPI auto-docs)

---

**Version**: 1.0
**Last Updated**: 2026-01-29
**Status**: Phase A Week 1 - Ready for Deployment
