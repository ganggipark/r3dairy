# Survey System Deployment Checklist

## Prerequisites

- [ ] Supabase project set up
- [ ] n8n instance running (or account created)
- [ ] Environment variables configured
- [ ] Backend API server running

---

## Step 1: Database Setup

### Supabase Configuration

1. **Execute SQL Schema**
   ```bash
   # Copy schema from database_models.py
   # Paste into Supabase SQL Editor
   # Run to create tables
   ```

   Location: `backend/src/config/survey_templates/database_models.py`
   Look for: `SUPABASE_SCHEMA` constant

2. **Verify Tables Created**
   - [ ] `survey_configurations`
   - [ ] `survey_responses`
   - [ ] `survey_deployments`

3. **Check RLS Policies**
   - [ ] Public can view active surveys
   - [ ] Authenticated users can submit responses
   - [ ] Service role has full access

4. **Test Database Connection**
   ```python
   from backend.src.db.supabase import get_supabase_client

   supabase = get_supabase_client()
   result = supabase.table("survey_configurations").select("*").execute()
   print(result.data)  # Should return empty array
   ```

---

## Step 2: Create Initial Survey

### Via API

1. **Start Backend Server**
   ```bash
   cd backend
   uvicorn src.main:app --reload
   ```

2. **Create Survey**
   ```bash
   curl -X POST http://localhost:8000/api/surveys/create \
     -H "Content-Type: application/json" \
     -d '{
       "template": "default",
       "locale": "ko-KR"
     }'
   ```

3. **Save Survey ID**
   - Response will include `survey_id`
   - Save this for deployment

### Via Python

```python
from backend.src.config.survey_templates import (
    create_default_survey,
    apply_korean_localization
)

# Create and localize
english_survey = create_default_survey()
korean_survey = apply_korean_localization(english_survey)

# Survey ID
print(f"Survey ID: {korean_survey.id}")
```

---

## Step 3: Deploy to n8n

### Generate Workflow

1. **Get Deployment Config**
   ```bash
   curl http://localhost:8000/api/surveys/{survey_id}/deploy \
     -H "Content-Type: application/json" \
     -d '{"target": "n8n"}' \
     > n8n_workflow.json
   ```

2. **Import to n8n**
   - Open n8n dashboard
   - Click "Import from JSON"
   - Paste `n8n_workflow.json`
   - Save workflow as "R³ Diary Survey - {language}"

3. **Configure Supabase Node**
   - Add Supabase credentials in n8n:
     - URL: `https://your-project.supabase.co`
     - Key: `your-anon-key`
   - Test connection

4. **Activate Workflow**
   - Click "Active" toggle
   - Note webhook URL
   - Format: `https://your-n8n.com/webhook/survey/{survey_id}`

### Test n8n Webhook

```bash
curl -X POST https://your-n8n.com/webhook/survey/{survey_id} \
  -H "Content-Type: application/json" \
  -d @backend/src/config/survey_templates/examples.json
```

Check:
- [ ] Response: `{"success": true, ...}`
- [ ] Data in Supabase `survey_responses` table
- [ ] Email sent (if configured)

---

## Step 4: Deploy to Web (Next.js)

### Generate React Component

1. **Get Web Config**
   ```bash
   curl http://localhost:8000/api/surveys/{survey_id}/deploy \
     -H "Content-Type: application/json" \
     -d '{"target": "web"}' \
     > web_config.json
   ```

2. **Extract React Component**
   ```javascript
   const config = require('./web_config.json');
   console.log(config.react_component);
   ```

3. **Create Component File**
   ```bash
   # In frontend/src/components/
   touch Survey{survey_id}.tsx
   ```

   Paste the generated React component code

4. **Create API Route**
   ```bash
   # In frontend/src/app/api/surveys/[survey_id]/submit/
   touch route.ts
   ```

   ```typescript
   // route.ts
   import { NextRequest, NextResponse } from 'next/server';

   export async function POST(
     request: NextRequest,
     { params }: { params: { survey_id: string } }
   ) {
     const data = await request.json();

     // Forward to backend API
     const response = await fetch(`http://localhost:8000/api/surveys/submit`, {
       method: 'POST',
       headers: { 'Content-Type': 'application/json' },
       body: JSON.stringify({
         survey_id: params.survey_id,
         response_data: data,
         source: 'web'
       })
     });

     return NextResponse.json(await response.json());
   }
   ```

5. **Create Survey Page**
   ```bash
   # In frontend/src/app/surveys/[survey_id]/
   touch page.tsx
   ```

   ```typescript
   import Survey from '@/components/Survey{survey_id}';

   export default function SurveyPage() {
     return <Survey />;
   }
   ```

### Test Web Form

1. **Start Dev Server**
   ```bash
   cd frontend
   npm run dev
   ```

2. **Navigate**
   - Go to: `http://localhost:5000/surveys/{survey_id}`

3. **Submit Test**
   - Fill out form
   - Submit
   - Check response in database

---

## Step 5: Update API for Production

### Replace In-Memory Storage

**Current** (development):
```python
_survey_configs: Dict[str, SurveyConfiguration] = {}
```

**Production**:
```python
from ..db.supabase import get_supabase_client

@router.post("/create")
async def create_survey(request: CreateSurveyRequest):
    # ... create survey_config ...

    supabase = get_supabase_client()
    supabase.table("survey_configurations").insert(
        survey_config.dict()
    ).execute()

    return {...}
```

### Update All TODO Markers

Search for: `# TODO: Save to Supabase` in `backend/src/api/surveys.py`

Replace with actual Supabase calls:
- [ ] `create_survey()`
- [ ] `get_survey()`
- [ ] `list_surveys()`
- [ ] `update_survey_status()`
- [ ] `submit_survey_response()`
- [ ] `get_survey_responses()`

---

## Step 6: Testing

### End-to-End Test

1. **Create Survey**
   ```bash
   curl -X POST http://localhost:8000/api/surveys/create \
     -H "Content-Type: application/json" \
     -d '{"template": "default", "locale": "ko-KR"}'
   ```

2. **Deploy to n8n**
   ```bash
   curl -X POST http://localhost:8000/api/surveys/{survey_id}/deploy \
     -H "Content-Type: application/json" \
     -d '{"target": "n8n"}'
   ```

3. **Submit via n8n Webhook**
   ```bash
   curl -X POST https://your-n8n.com/webhook/survey/{survey_id} \
     -H "Content-Type: application/json" \
     -d '{
       "name": "테스트 사용자",
       "email": "test@example.com",
       "birth_date": "1990-01-01",
       "primary_role": "학생",
       ...
     }'
   ```

4. **Verify in Supabase**
   - Check `survey_responses` table
   - Verify normalized data

5. **Submit via Web Form**
   - Go to survey page
   - Fill form
   - Submit
   - Verify in database

6. **Get Summary**
   ```bash
   curl http://localhost:8000/api/surveys/{survey_id}/summary
   ```

---

## Step 7: Monitoring

### Set Up Monitoring

1. **n8n Workflow Monitoring**
   - Check execution history
   - Monitor for errors
   - Set up alerts

2. **Database Monitoring**
   - Monitor response count
   - Check for validation errors
   - Track submission rates

3. **API Monitoring**
   - Log API requests
   - Monitor response times
   - Track error rates

### Metrics to Track

- [ ] Total surveys created
- [ ] Total responses submitted
- [ ] Responses by source (n8n, web, api)
- [ ] Average completion time
- [ ] Completion rate
- [ ] Error rate

---

## Verification Checklist

### Database
- [ ] Tables created
- [ ] RLS policies working
- [ ] Triggers functioning
- [ ] Indexes created

### n8n
- [ ] Workflow imported
- [ ] Webhook active
- [ ] Supabase connection working
- [ ] Email notifications sending

### Web Form
- [ ] Component renders
- [ ] API endpoint working
- [ ] Form submission successful
- [ ] Data in database

### API
- [ ] All endpoints responding
- [ ] Validation working
- [ ] Error handling correct
- [ ] Response format correct

---

## Rollback Plan

If deployment fails:

1. **Database**
   ```sql
   DROP TABLE IF EXISTS survey_responses;
   DROP TABLE IF EXISTS survey_deployments;
   DROP TABLE IF EXISTS survey_configurations;
   ```

2. **n8n**
   - Deactivate workflow
   - Delete workflow

3. **Web**
   - Remove component
   - Remove API route
   - Remove page

---

## Production Checklist

Before going live:

- [ ] Environment variables set
- [ ] Database schema deployed
- [ ] RLS policies tested
- [ ] n8n webhook secured (rate limiting, auth)
- [ ] Web form validated (client + server side)
- [ ] Error handling comprehensive
- [ ] Monitoring set up
- [ ] Backup strategy in place
- [ ] Documentation updated
- [ ] Team trained

---

## Support

**Issues?**
- Check logs in n8n execution history
- Check Supabase logs
- Check API logs (`uvicorn` output)
- Review test cases in `test_survey_deployment.py`

**Questions?**
- See `README.md` for detailed documentation
- Review examples in `examples.json`
- Check deployment instructions in `deployment.py`

---

**Last Updated**: 2026-01-29
**Version**: 1.0
**Status**: Ready for Deployment
