"""Deployment configurations for survey forms to different platforms."""

from __future__ import annotations

from typing import Dict, Any
import json

from ...skills.form_builder.models import FormConfiguration
from ...skills.form_builder.generators import FormGenerator


class SurveyDeploymentConfig:
    """Configuration for deploying surveys to different platforms."""

    @staticmethod
    def get_n8n_deployment_config(form: FormConfiguration) -> Dict[str, Any]:
        """
        Returns n8n workflow configuration with:
        - HTTP trigger (webhook)
        - Form field normalization
        - Database write node (if configured)
        - Response confirmation webhook

        Args:
            form: FormConfiguration to deploy

        Returns:
            n8n workflow JSON configuration
        """
        # Use existing FormGenerator for n8n workflow
        base_workflow = FormGenerator.to_n8n_workflow(form)

        # Add additional nodes for complete deployment
        enhanced_workflow = {
            **base_workflow,
            "nodes": [
                # 1. Webhook trigger
                {
                    "parameters": {
                        "httpMethod": "POST",
                        "path": f"survey/{form.id}",
                        "responseMode": "responseNode",
                        "options": {
                            "allowedOrigins": "*",
                        }
                    },
                    "name": "Webhook Survey Submit",
                    "type": "n8n-nodes-base.webhook",
                    "typeVersion": 1,
                    "position": [250, 300],
                    "webhookId": form.id,
                },

                # 2. Data normalization
                {
                    "parameters": {
                        "functionCode": _get_normalization_function(form),
                    },
                    "name": "Normalize Survey Data",
                    "type": "n8n-nodes-base.function",
                    "typeVersion": 1,
                    "position": [450, 300],
                },

                # 3. Database insert (Supabase)
                {
                    "parameters": {
                        "resource": "row",
                        "operation": "insert",
                        "tableId": "survey_responses",
                        "columns": {
                            "mappingMode": "defineBelow",
                            "value": {
                                "survey_id": f"={{'{form.id}'}}",
                                "response_data": "={{ $json.raw_response }}",
                                "normalized_data": "={{ $json.normalized }}",
                                "submitted_at": "={{ $now }}",
                                "ip_address": "={{ $json.headers['x-forwarded-for'] }}",
                                "source": "n8n"
                            }
                        }
                    },
                    "name": "Save to Supabase",
                    "type": "n8n-nodes-base.supabase",
                    "typeVersion": 1,
                    "position": [650, 300],
                    "credentials": {
                        "supabaseApi": {
                            "id": "1",
                            "name": "Supabase account"
                        }
                    }
                },

                # 4. Send confirmation email (optional)
                {
                    "parameters": {
                        "resource": "email",
                        "operation": "send",
                        "fromEmail": "noreply@r3diary.com",
                        "toEmail": "={{ $json.normalized.email }}",
                        "subject": "Thank you for completing the R³ Diary survey",
                        "emailType": "html",
                        "message": _get_confirmation_email_template(),
                    },
                    "name": "Send Confirmation Email",
                    "type": "n8n-nodes-base.emailSend",
                    "typeVersion": 2,
                    "position": [850, 200],
                },

                # 5. Response webhook
                {
                    "parameters": {
                        "respondWith": "json",
                        "responseBody": json.dumps({
                            "success": True,
                            "message": "Survey submitted successfully",
                            "survey_id": form.id,
                            "response_id": "={{ $json.id }}"
                        }),
                        "options": {
                            "responseCode": 200
                        }
                    },
                    "name": "Return Success Response",
                    "type": "n8n-nodes-base.respondToWebhook",
                    "typeVersion": 1,
                    "position": [850, 300],
                },

                # 6. Error handling
                {
                    "parameters": {
                        "respondWith": "json",
                        "responseBody": json.dumps({
                            "success": False,
                            "error": "={{ $json.error.message }}"
                        }),
                        "options": {
                            "responseCode": 400
                        }
                    },
                    "name": "Return Error Response",
                    "type": "n8n-nodes-base.respondToWebhook",
                    "typeVersion": 1,
                    "position": [850, 400],
                }
            ],
            "connections": {
                "Webhook Survey Submit": {
                    "main": [[{"node": "Normalize Survey Data", "type": "main", "index": 0}]]
                },
                "Normalize Survey Data": {
                    "main": [[{"node": "Save to Supabase", "type": "main", "index": 0}]]
                },
                "Save to Supabase": {
                    "main": [
                        [
                            {"node": "Send Confirmation Email", "type": "main", "index": 0},
                            {"node": "Return Success Response", "type": "main", "index": 0}
                        ]
                    ]
                }
            },
            "settings": {
                "executionOrder": "v1"
            },
            "staticData": None,
            "tags": ["survey", "r3diary", form.id],
        }

        return enhanced_workflow

    @staticmethod
    def get_google_forms_config(form: FormConfiguration) -> Dict[str, Any]:
        """
        Google Forms API configuration.

        Note: This returns the configuration structure. Actual Google Forms
        creation requires OAuth2 authentication and the Google Forms API.

        Args:
            form: FormConfiguration to deploy

        Returns:
            Google Forms API request configuration
        """
        # Use existing FormGenerator
        return FormGenerator.to_google_forms_config(form)

    @staticmethod
    def get_web_deployment_config(form: FormConfiguration) -> Dict[str, Any]:
        """
        Web form deployment with React/Next.js component configuration.

        Returns both HTML and React component code.

        Args:
            form: FormConfiguration to deploy

        Returns:
            Configuration with HTML, React code, and API endpoint info
        """
        return {
            "form_id": form.id,
            "name": form.name,
            "description": form.description,

            # HTML version
            "html": FormGenerator.to_html_form(form),

            # React component template
            "react_component": _generate_react_component(form),

            # API endpoint configuration
            "api": {
                "submit_endpoint": f"/api/surveys/{form.id}/submit",
                "method": "POST",
                "headers": {
                    "Content-Type": "application/json"
                },
                "example_payload": _get_example_payload(form)
            },

            # Styling suggestions
            "css_classes": {
                "form": "survey-form max-w-2xl mx-auto p-6",
                "section": "survey-section mb-8",
                "field": "survey-field mb-4",
                "label": "survey-label block text-sm font-medium mb-2",
                "input": "survey-input w-full px-3 py-2 border rounded-md",
                "button": "survey-submit bg-blue-600 text-white px-6 py-3 rounded-md hover:bg-blue-700"
            }
        }

    @staticmethod
    def get_deployment_instructions(form: FormConfiguration, target: str) -> str:
        """
        Get human-readable deployment instructions.

        Args:
            form: FormConfiguration to deploy
            target: "n8n", "google_forms", or "web"

        Returns:
            Markdown-formatted deployment instructions
        """
        if target == "n8n":
            return f"""
# Deploy Survey to n8n

## Steps:

1. **Import Workflow**
   - Open n8n dashboard
   - Click "Import from JSON"
   - Paste the workflow configuration
   - Save workflow as "Survey: {form.name}"

2. **Configure Supabase Connection**
   - Add Supabase credentials in n8n
   - Set SUPABASE_URL and SUPABASE_KEY
   - Test connection

3. **Activate Webhook**
   - Activate the workflow
   - Note the webhook URL: `https://your-n8n.com/webhook/survey/{form.id}`

4. **Test Submission**
   - Use curl or Postman to send a test POST request
   - Verify data appears in Supabase `survey_responses` table

## Webhook URL:
`POST https://your-n8n.com/webhook/survey/{form.id}`

## Example curl command:
```bash
curl -X POST https://your-n8n.com/webhook/survey/{form.id} \\
  -H "Content-Type: application/json" \\
  -d '{{"name": "Test User", "email": "test@example.com"}}'
```
"""

        elif target == "google_forms":
            return f"""
# Deploy Survey to Google Forms

## Prerequisites:
- Google account with Forms API enabled
- OAuth2 credentials configured

## Steps:

1. **Create Form via API**
   - Use the Google Forms API configuration provided
   - Send POST request to `https://forms.googleapis.com/v1/forms`
   - Use OAuth2 token for authentication

2. **Configure Response Destination**
   - Link form responses to a Google Sheet
   - Or set up webhook for real-time responses

3. **Share Form**
   - Get the public form URL
   - Embed in your website or share directly

## Note:
Google Forms has limitations on conditional logic and custom validation.
Consider using web form for full functionality.
"""

        elif target == "web":
            return f"""
# Deploy Survey as Web Form

## Steps:

1. **Create React Component**
   - Copy the React component code provided
   - Save as `components/Survey{form.id}.tsx`
   - Install dependencies: `npm install react-hook-form zod`

2. **Create API Endpoint**
   - Create `/api/surveys/{form.id}/submit` endpoint
   - Handle POST requests with survey data
   - Save to database

3. **Add Route**
   - Create page at `/surveys/{form.id}`
   - Import and render the survey component

4. **Test**
   - Run dev server: `npm run dev`
   - Navigate to `http://localhost:5000/surveys/{form.id}`
   - Submit test response

## API Endpoint Example (Next.js):
```typescript
// app/api/surveys/{form.id}/submit/route.ts
export async function POST(request: Request) {{
  const data = await request.json();
  // Validate and save to database
  return Response.json({{ success: true }});
}}
```
"""

        else:
            return f"Unknown target: {target}"


def _get_normalization_function(form: FormConfiguration) -> str:
    """Generate JavaScript function for n8n to normalize survey data."""
    return """
// Normalize survey response data
const rawResponse = items[0].json;
const normalized = {};

// Extract and standardize field values
for (const [key, value] of Object.entries(rawResponse)) {
    if (key.startsWith('p_')) {
        // Personality scores (Likert scale)
        if (!normalized.personality_scores) {
            normalized.personality_scores = {};
        }
        normalized.personality_scores[key] = parseInt(value);
    } else if (Array.isArray(value)) {
        // Multiple choice fields
        normalized[key] = value;
    } else {
        // Single value fields
        normalized[key] = value;
    }
}

// Add metadata
normalized.form_version = rawResponse.form_version || '1.0';
normalized.submitted_at = new Date().toISOString();

return [{
    json: {
        raw_response: rawResponse,
        normalized: normalized,
        headers: $input.headers
    }
}];
"""


def _get_confirmation_email_template() -> str:
    """Get HTML template for confirmation email."""
    return """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; }
        .content { padding: 30px 20px; background: #f9f9f9; }
        .footer { text-align: center; padding: 20px; color: #666; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Welcome to R³ Diary</h1>
        </div>
        <div class="content">
            <p>Thank you for completing your personal assessment!</p>
            <p>We're now creating your personalized diary experience based on your unique rhythm and preferences.</p>
            <p><strong>What happens next:</strong></p>
            <ul>
                <li>Your personalized daily insights are being prepared</li>
                <li>You'll receive your first diary page within 24 hours</li>
                <li>Access your diary anytime at <a href="https://r3diary.com">r3diary.com</a></li>
            </ul>
            <p>If you have any questions, reply to this email.</p>
        </div>
        <div class="footer">
            <p>&copy; 2026 R³ Diary. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
"""


def _generate_react_component(form: FormConfiguration) -> str:
    """Generate React component code for the survey."""
    return f"""
'use client';

import {{ useState }} from 'react';
import {{ useForm }} from 'react-hook-form';

interface SurveyData {{
  [key: string]: any;
}}

export default function Survey{form.id}() {{
  const {{ register, handleSubmit, watch, formState: {{ errors }} }} = useForm<SurveyData>();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState(false);

  const onSubmit = async (data: SurveyData) => {{
    setIsSubmitting(true);
    try {{
      const response = await fetch('/api/surveys/{form.id}/submit', {{
        method: 'POST',
        headers: {{
          'Content-Type': 'application/json',
        }},
        body: JSON.stringify(data),
      }});

      if (response.ok) {{
        setSubmitSuccess(true);
      }} else {{
        alert('Submission failed. Please try again.');
      }}
    }} catch (error) {{
      console.error('Submission error:', error);
      alert('An error occurred. Please try again.');
    }} finally {{
      setIsSubmitting(false);
    }}
  }};

  if (submitSuccess) {{
    return (
      <div className="max-w-2xl mx-auto p-6 text-center">
        <h2 className="text-2xl font-bold text-green-600 mb-4">Thank You!</h2>
        <p>Your survey has been submitted successfully.</p>
      </div>
    );
  }}

  return (
    <form onSubmit={{handleSubmit(onSubmit)}} className="max-w-2xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-2">{form.name}</h1>
      <p className="text-gray-600 mb-8">{form.description}</p>

      {{/* Fields will be rendered here based on form configuration */}}
      {{/* This is a template - implement field rendering based on FormConfiguration */}}

      <button
        type="submit"
        disabled={{isSubmitting}}
        className="bg-blue-600 text-white px-6 py-3 rounded-md hover:bg-blue-700 disabled:bg-gray-400"
      >
        {{isSubmitting ? 'Submitting...' : 'Submit Survey'}}
      </button>
    </form>
  );
}}
"""


def _get_example_payload(form: FormConfiguration) -> Dict[str, Any]:
    """Generate example API payload for the form."""
    payload = {}

    for section in form.sections:
        for field in section.fields:
            if field.field_type.value == "text":
                payload[field.id] = "Example text"
            elif field.field_type.value == "email":
                payload[field.id] = "user@example.com"
            elif field.field_type.value == "date":
                payload[field.id] = "2000-01-01"
            elif field.field_type.value == "single_choice":
                payload[field.id] = field.options[0] if field.options else "Option 1"
            elif field.field_type.value == "multiple_choice":
                payload[field.id] = field.options[:2] if field.options else ["Option 1", "Option 2"]
            elif field.field_type.value == "likert_scale":
                payload[field.id] = 3
            elif field.field_type.value == "long_text":
                payload[field.id] = "Example long text response"

    return payload
