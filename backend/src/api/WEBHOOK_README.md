# n8n Webhook Integration

## Overview

The n8n webhook integration allows external survey submissions from n8n workflows to be processed and stored in the diary system. The webhook endpoint handles survey response ingestion, profile creation, and transaction management.

## Endpoint

```
POST /api/webhooks/n8n/survey
```

## Features

1. **HMAC Signature Validation** (Optional)
   - Validates webhook authenticity using shared secret
   - Prevents unauthorized submissions
   - Configurable via `N8N_WEBHOOK_SECRET` environment variable

2. **Idempotency**
   - Prevents duplicate processing using `submission_id`
   - Safe to retry failed requests
   - Returns existing response for duplicate submissions

3. **Transaction Management**
   - Saves survey response first (guaranteed)
   - Creates customer profile second (best effort)
   - Partial failures handled gracefully

4. **Error Handling**
   - Clear 4xx/5xx responses
   - No partial records on failure
   - Detailed error messages

## Configuration

### Environment Variables

Add to `backend/.env`:

```bash
# Optional: Enable HMAC signature verification
# Generate with: python -c "import secrets; print(secrets.token_hex(32))"
N8N_WEBHOOK_SECRET=your-n8n-webhook-secret-here
```

If `N8N_WEBHOOK_SECRET` is not set, signature verification is disabled (useful for development).

### n8n Workflow Setup

1. **Add HTTP Request Node**
   - Method: POST
   - URL: `https://your-api.com/api/webhooks/n8n/survey`
   - Authentication: None (or use HMAC signature)

2. **Payload Structure**
   ```json
   {
     "survey_id": "survey_abc123",
     "submission_id": "n8n_{{ $json.execution_id }}_{{ $json.timestamp }}",
     "response_data": {
       "name": "{{ $json.name }}",
       "email": "{{ $json.email }}",
       "birth_date": "{{ $json.birth_date }}",
       "primary_role": "{{ $json.primary_role }}",
       ...
     },
     "metadata": {
       "n8n_workflow_id": "{{ $json.workflow_id }}",
       "n8n_execution_id": "{{ $json.execution_id }}"
     }
   }
   ```

3. **Optional: Add HMAC Signature**
   - Add Function node before HTTP Request
   - Code:
     ```javascript
     const crypto = require('crypto');
     const secret = 'your-n8n-webhook-secret-here';
     const payload = JSON.stringify($input.item.json);
     const signature = crypto.createHmac('sha256', secret)
       .update(payload)
       .digest('hex');
     return { signature };
     ```
   - Add header: `X-N8N-Signature: {{ $json.signature }}`

## Request/Response

### Request Schema

```typescript
{
  survey_id: string;           // Required: Survey configuration ID
  submission_id: string;       // Required: Unique submission ID (for idempotency)
  response_data: {             // Required: Survey field answers
    name: string;
    email: string;
    birth_date: string;        // ISO format YYYY-MM-DD
    gender: string;
    primary_role: string;
    // ... other survey fields
  };
  metadata?: {                 // Optional: Additional metadata
    n8n_workflow_id?: string;
    n8n_execution_id?: string;
    // ... custom fields
  };
}
```

### Response Schema

#### Success (200 OK)

```json
{
  "success": true,
  "message": "Survey submitted successfully",
  "response_id": "response_xyz789",
  "profile_id": "profile_abc123",
  "errors": null
}
```

#### Idempotent Duplicate (200 OK)

```json
{
  "success": true,
  "message": "Survey submission already processed (idempotent request)",
  "response_id": "response_existing_123",
  "profile_id": "profile_existing_456"
}
```

#### Profile Creation Failed (200 OK)

```json
{
  "success": true,
  "message": "Survey submitted, but profile creation failed",
  "response_id": "response_xyz789",
  "profile_id": null,
  "errors": ["Profile creation failed: Invalid birth date format"]
}
```

#### Missing Signature (401 Unauthorized)

```json
{
  "detail": "Missing X-N8N-Signature header. Webhook signature required."
}
```

#### Invalid Signature (401 Unauthorized)

```json
{
  "detail": "Invalid webhook signature. Signature verification failed."
}
```

#### Survey Not Found (404 Not Found)

```json
{
  "detail": "Survey not found: survey_invalid_123"
}
```

#### Invalid Payload (400 Bad Request)

```json
{
  "detail": "Invalid survey response data: Missing required field 'name'"
}
```

#### Server Error (500 Internal Server Error)

```json
{
  "detail": "Failed to process survey submission: Database connection failed"
}
```

## Testing

### Health Check

```bash
curl http://localhost:8000/webhooks/health
```

### Test Webhook (Without Signature)

```bash
curl -X POST http://localhost:8000/webhooks/n8n/survey \
  -H "Content-Type: application/json" \
  -d '{
    "survey_id": "survey_test_123",
    "submission_id": "test_submission_001",
    "response_data": {
      "name": "테스트 사용자",
      "email": "test@example.com",
      "birth_date": "1995-05-15",
      "gender": "남성",
      "primary_role": "학생"
    },
    "metadata": {
      "source": "manual_test"
    }
  }'
```

### Test Webhook (With Signature)

```bash
# Generate signature
SECRET="your-n8n-webhook-secret-here"
PAYLOAD='{"survey_id":"survey_test_123","submission_id":"test_002",...}'
SIGNATURE=$(echo -n "$PAYLOAD" | openssl dgst -sha256 -hmac "$SECRET" | cut -d' ' -f2)

# Send request
curl -X POST http://localhost:8000/webhooks/n8n/survey \
  -H "Content-Type: application/json" \
  -H "X-N8N-Signature: $SIGNATURE" \
  -d "$PAYLOAD"
```

### Run Unit Tests

```bash
cd backend
pytest tests/test_webhook.py -v
```

## Security Considerations

1. **HMAC Signature**
   - Always enable in production: `N8N_WEBHOOK_SECRET=<strong-random-secret>`
   - Keep secret secure (never commit to git)
   - Rotate periodically

2. **Rate Limiting**
   - Consider adding rate limiting middleware
   - Prevent abuse from compromised n8n instances

3. **Input Validation**
   - All inputs are validated via Pydantic models
   - SQL injection: Protected by Supabase parameterized queries
   - XSS: Not applicable (API only, no HTML rendering)

4. **Error Messages**
   - Detailed errors in development
   - Generic errors in production (avoid information leakage)

## Database Impact

### Tables Written

1. **survey_responses**
   - Inserts new response record
   - Triggers increment of `response_count` in `survey_configurations`

2. **profiles**
   - Upserts customer profile (creates or updates)

3. **survey_responses (metadata update)**
   - Updates `metadata.profile_id` after profile creation

### RLS Policies

- Service role key bypasses RLS (required for webhook processing)
- User-facing API endpoints use RLS for security

## Monitoring

### Metrics to Track

1. **Request Volume**
   - Total webhook requests per day
   - Success rate (200 OK vs errors)

2. **Error Rates**
   - 401 errors (signature failures)
   - 404 errors (invalid survey_id)
   - 500 errors (server failures)

3. **Processing Time**
   - Average response time
   - P95/P99 latency

4. **Profile Creation Rate**
   - Successful profile creation vs failures
   - Common failure reasons

### Logging

Add to application logs:
- Request timestamp
- Survey ID
- Submission ID
- Response ID (if created)
- Profile ID (if created)
- Error messages (if any)

## Troubleshooting

### Common Issues

**Issue**: 401 Unauthorized (signature mismatch)
- **Cause**: Secret mismatch between n8n and backend
- **Fix**: Ensure `N8N_WEBHOOK_SECRET` matches in both systems

**Issue**: 404 Survey Not Found
- **Cause**: Survey not created or deployed
- **Fix**: Create survey via `/api/surveys/create` and activate it

**Issue**: Profile creation always fails
- **Cause**: Missing required fields in `response_data`
- **Fix**: Check survey includes all required fields (name, birth_date, etc.)

**Issue**: Duplicate submissions not detected
- **Cause**: Different `submission_id` for same submission
- **Fix**: Ensure n8n generates consistent `submission_id` (e.g., based on form submission ID)

## Development

### Local Testing

```bash
# Start backend
cd backend
uvicorn src.main:app --reload --port 8000

# Test webhook
python verify_webhook.py

# Or use pytest
pytest tests/test_webhook.py -v
```

### Adding New Fields

1. Update `response_data` structure in n8n workflow
2. Update `_normalize_response_data()` in `surveys.py`
3. Update `SurveyResponseToProfile.convert()` if needed
4. Update tests

## References

- [Plan Document](.omc/plans/personalized-survey-system.md)
- [Survey API](./surveys.py)
- [Database Models](../config/survey_templates/database_models.py)
- [Supabase Operations](../db/supabase.py)
