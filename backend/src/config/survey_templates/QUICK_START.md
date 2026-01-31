# Quick Start Guide - Survey Template System

## 1. Create Your First Survey (30 seconds)

```python
from src.config.survey_templates import create_default_survey

# Create the survey
survey = create_default_survey()

print(f"Survey ID: {survey.id}")
print(f"Survey Name: {survey.name}")
print(f"Total Fields: {len(survey.get_all_fields())}")
```

**Output:**
```
Survey ID: form_abc123...
Survey Name: R³ Diary - Personal Assessment Survey
Total Fields: 23
```

---

## 2. Get Survey in Korean (15 seconds)

```python
from src.config.survey_templates import (
    get_survey_by_template,
    apply_korean_localization
)

# Get default template
english = get_survey_by_template("default")

# Apply Korean translation
korean = apply_korean_localization(english)

print(f"Survey Name: {korean.name}")
# Output: R³ 다이어리 - 개인 평가 설문
```

---

## 3. Deploy to n8n (5 minutes)

```python
from src.config.survey_templates import (
    create_default_survey,
    SurveyDeploymentConfig
)

# Create survey
survey = create_default_survey()

# Generate n8n workflow
workflow = SurveyDeploymentConfig.get_n8n_deployment_config(survey)

# Save to file
import json
with open("n8n_workflow.json", "w") as f:
    json.dump(workflow, f, indent=2)

print("Workflow saved! Import to n8n.")
```

**Next steps:**
1. Open n8n dashboard
2. Click "Import from JSON"
3. Upload `n8n_workflow.json`
4. Activate workflow
5. Test with: `curl -X POST <webhook_url> -d @examples.json`

---

## 4. Create API Endpoint (3 minutes)

```python
# In your FastAPI app
from fastapi import FastAPI
from src.api.surveys import router

app = FastAPI()
app.include_router(router)

# Start server
# uvicorn main:app --reload
```

**Test the API:**
```bash
# Create a survey
curl -X POST http://localhost:8000/api/surveys/create \
  -H "Content-Type: application/json" \
  -d '{"template": "default", "locale": "ko-KR"}'

# Get survey
curl http://localhost:8000/api/surveys/{survey_id}

# Submit response
curl -X POST http://localhost:8000/api/surveys/submit \
  -H "Content-Type: application/json" \
  -d '{
    "survey_id": "survey_123",
    "response_data": {
      "name": "김테스트",
      "email": "test@example.com",
      "birth_date": "1990-01-01",
      "primary_role": "학생"
    }
  }'
```

---

## 5. Use Example Data (1 minute)

```python
import json

# Load examples
with open("src/config/survey_templates/examples.json", encoding="utf-8") as f:
    examples = json.load(f)

# Get student example
student_response = examples["example_student"]

# Use for testing
print(student_response["name"])  # 김학생
print(student_response["email"]) # student@example.com
```

---

## 6. Create Custom Template (10 minutes)

```python
from src.skills.form_builder import FormBuilder, FieldType

def create_my_survey():
    return (
        FormBuilder("My Survey", "Custom survey for my use case")
        .add_section("basics", "Basic Info")
        .add_field("basics", "name", "Your Name", FieldType.TEXT)
        .add_field("basics", "email", "Your Email", FieldType.EMAIL)
        .add_section("preferences", "Preferences")
        .add_field("preferences", "choice", "Pick one",
                   FieldType.SINGLE_CHOICE,
                   options=["Option A", "Option B"])
        .build()
    )

survey = create_my_survey()
```

---

## 7. Test Everything (2 minutes)

```bash
# Run all tests
cd backend
pytest tests/test_survey_deployment.py -v

# Should see: 32 passed
```

---

## Common Use Cases

### Use Case 1: Quick Onboarding
```python
# For users who want fast onboarding
quick_survey = get_survey_by_template("quick_profile")
# 3 sections, ~2 minutes to complete
```

### Use Case 2: Student-Specific Survey
```python
# For student-focused apps
student_survey = get_survey_by_template("student")
# Includes education level, learning style, study preferences
```

### Use Case 3: Professional Survey
```python
# For B2B or professional tools
office_survey = get_survey_by_template("office_worker")
# Includes industry, work environment, productivity patterns
```

### Use Case 4: Multilingual Survey
```python
# Create both English and Korean versions
from src.config.survey_templates import (
    create_default_survey,
    apply_korean_localization
)

english_survey = create_default_survey()
korean_survey = apply_korean_localization(english_survey)

# Deploy both
n8n_en = SurveyDeploymentConfig.get_n8n_deployment_config(english_survey)
n8n_ko = SurveyDeploymentConfig.get_n8n_deployment_config(korean_survey)
```

---

## Deployment Shortcuts

### Deploy All Platforms at Once

```python
from src.config.survey_templates import (
    create_default_survey,
    apply_korean_localization,
    SurveyDeploymentConfig
)

# Create Korean survey
survey = apply_korean_localization(create_default_survey())

# Deploy to all platforms
configs = {
    "n8n": SurveyDeploymentConfig.get_n8n_deployment_config(survey),
    "web": SurveyDeploymentConfig.get_web_deployment_config(survey),
    "google_forms": SurveyDeploymentConfig.get_google_forms_config(survey),
}

# Save all configs
import json
for platform, config in configs.items():
    with open(f"deploy_{platform}.json", "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
```

---

## Troubleshooting

### Problem: Import Error
```python
# Make sure you're in the backend directory
cd backend

# Try:
from src.config.survey_templates import create_default_survey
```

### Problem: Encoding Error
```python
# Always use UTF-8 encoding
with open("examples.json", encoding="utf-8") as f:
    data = json.load(f)
```

### Problem: Tests Failing
```bash
# Make sure all dependencies are installed
pip install -r requirements.txt

# Run tests with verbose output
pytest tests/test_survey_deployment.py -v
```

---

## Next Steps

1. **Week 2: Deploy to Production**
   - Set up Supabase database
   - Deploy n8n workflow
   - Create web form in Next.js

2. **Week 3: Collect Data**
   - Start collecting survey responses
   - Analyze patterns
   - Refine templates

3. **Week 4: Create Profiles**
   - Build profile creation from survey data
   - Integrate with rhythm analysis
   - Generate first personalized content

---

## Resources

- **Full Documentation**: `README.md`
- **Deployment Guide**: `DEPLOYMENT_CHECKLIST.md`
- **Example Data**: `examples.json`
- **Test Suite**: `../../../tests/test_survey_deployment.py`
- **API Reference**: FastAPI docs at `/docs` (when server running)

---

**Ready to start!** 🚀

Choose your path:
- **Fast Track**: Use `default` template → Deploy to n8n → Start collecting data
- **Custom Track**: Create custom template → Test locally → Deploy when ready
- **Learning Track**: Read full README → Run tests → Experiment with examples

**Estimated Time to First Deployment**: 15-30 minutes
