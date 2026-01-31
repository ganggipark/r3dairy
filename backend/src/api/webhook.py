"""API endpoints for n8n webhook integration."""

from __future__ import annotations

import hashlib
import hmac
import uuid
from typing import Dict, Any, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Request, Header
from pydantic import BaseModel, Field
import os

from ..config.survey_templates.database_models import (
    SurveyResponse,
    SurveySource,
)
from ..db.supabase import (
    get_survey_config,
    save_survey_response,
    save_customer_profile,
    get_supabase_service,
)
from ..data_processor.survey_to_profile import SurveyResponseToProfile

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


# ============================================================================
# Request/Response Models
# ============================================================================

class N8nWebhookPayload(BaseModel):
    """n8n webhook payload for survey submission."""
    survey_id: str = Field(..., description="Survey ID from n8n workflow")
    submission_id: str = Field(..., description="Unique submission ID for idempotency")
    response_data: Dict[str, Any] = Field(..., description="Survey field answers")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata from n8n")


class WebhookResponse(BaseModel):
    """Response for webhook endpoint."""
    success: bool
    message: str
    response_id: Optional[str] = None
    profile_id: Optional[str] = None
    errors: Optional[list] = None


# ============================================================================
# Helper Functions
# ============================================================================

def verify_hmac_signature(payload: bytes, signature: str, secret: str) -> bool:
    """
    Verify HMAC signature from n8n webhook.

    Args:
        payload: Raw request body bytes
        signature: HMAC signature from header
        secret: Shared secret key

    Returns:
        True if signature is valid, False otherwise
    """
    if not signature or not secret:
        return False

    # Compute HMAC-SHA256
    expected_signature = hmac.new(
        secret.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()

    # Compare signatures (constant-time comparison to prevent timing attacks)
    return hmac.compare_digest(expected_signature, signature)


async def check_idempotency(submission_id: str, survey_id: str) -> Optional[dict]:
    """
    Check if submission_id has already been processed.

    Args:
        submission_id: Unique submission ID
        survey_id: Survey ID

    Returns:
        Existing response dict if found, None otherwise
    """
    client = get_supabase_service()

    # Query for existing response with this submission_id
    result = client.table("survey_responses").select("*").eq(
        "survey_id", survey_id
    ).eq(
        "metadata->>submission_id", submission_id
    ).execute()

    if result.data and len(result.data) > 0:
        return result.data[0]

    return None


def _normalize_response_data(response_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize survey response data to standard format.

    This is a simplified version that delegates to the main normalization
    function from surveys.py for consistency.

    Args:
        response_data: Raw survey response

    Returns:
        Normalized data structure
    """
    from ..api.surveys import _normalize_response_data as normalize
    return normalize(response_data)


# ============================================================================
# Webhook Endpoints
# ============================================================================

@router.post("/n8n/survey", response_model=WebhookResponse)
async def n8n_survey_webhook(
    request: Request,
    payload: N8nWebhookPayload,
    x_n8n_signature: Optional[str] = Header(None, alias="X-N8N-Signature")
):
    """
    Webhook endpoint for n8n survey submissions.

    This endpoint:
    1. Validates HMAC signature (if N8N_WEBHOOK_SECRET is configured)
    2. Checks idempotency using submission_id
    3. Saves survey response to Supabase
    4. Converts response to CustomerProfile
    5. Saves profile to Supabase
    6. Returns success/failure response

    Args:
        request: FastAPI Request object
        payload: N8nWebhookPayload with survey data
        x_n8n_signature: Optional HMAC signature header

    Returns:
        WebhookResponse with success status and IDs

    Raises:
        HTTPException: 401 if signature invalid, 400 if data invalid, 500 if processing fails
    """
    errors = []

    # Step 1: Validate HMAC signature (if configured)
    webhook_secret = os.getenv("N8N_WEBHOOK_SECRET")
    if webhook_secret:
        # Get raw request body for signature verification
        body = await request.body()

        if not x_n8n_signature:
            raise HTTPException(
                status_code=401,
                detail="Missing X-N8N-Signature header. Webhook signature required."
            )

        if not verify_hmac_signature(body, x_n8n_signature, webhook_secret):
            raise HTTPException(
                status_code=401,
                detail="Invalid webhook signature. Signature verification failed."
            )

    # Step 2: Check if survey exists
    survey_config = await get_survey_config(payload.survey_id)
    if not survey_config:
        raise HTTPException(
            status_code=404,
            detail=f"Survey not found: {payload.survey_id}"
        )

    # Step 3: Check idempotency
    existing_response = await check_idempotency(payload.submission_id, payload.survey_id)
    if existing_response:
        # Already processed - return success with existing IDs
        return WebhookResponse(
            success=True,
            message="Survey submission already processed (idempotent request)",
            response_id=existing_response["id"],
            profile_id=existing_response.get("metadata", {}).get("profile_id")
        )

    # Step 4: Normalize response data
    try:
        normalized_data = _normalize_response_data(payload.response_data)
    except Exception as e:
        errors.append(f"Normalization error: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid survey response data: {str(e)}"
        )

    # Step 5: Transaction - save response and create profile
    response_id = str(uuid.uuid4())
    profile_id = None
    profile_created = False

    try:
        # Step 5a: Save survey response
        ip_address = request.client.host if request.client else None

        # Include submission_id in metadata for idempotency
        metadata = payload.metadata.copy()
        metadata["submission_id"] = payload.submission_id
        metadata["n8n_timestamp"] = datetime.utcnow().isoformat()

        survey_response = SurveyResponse(
            id=response_id,
            survey_id=payload.survey_id,
            response_data=payload.response_data,
            normalized_data=normalized_data,
            ip_address=ip_address,
            source=SurveySource.N8N,
            user_id=None,  # n8n submissions are anonymous
            metadata=metadata,
        )

        saved_response = await save_survey_response(survey_response.dict())

        # Step 5b: Convert to CustomerProfile
        try:
            customer_profile = SurveyResponseToProfile.convert(normalized_data)

            # Save profile to Supabase
            saved_profile = await save_customer_profile(customer_profile.dict())
            profile_created = True
            profile_id = saved_profile.get("id")

            # Update response metadata with profile_id for linkage
            client = get_supabase_service()
            metadata["profile_id"] = profile_id
            client.table("survey_responses").update({
                "metadata": metadata
            }).eq("id", response_id).execute()

        except ValueError as e:
            # Profile creation failed - log error but don't fail the request
            # The survey response is already saved
            errors.append(f"Profile creation failed: {str(e)}")
            profile_created = False

        except Exception as e:
            errors.append(f"Unexpected error creating profile: {str(e)}")
            profile_created = False

        # Return success
        return WebhookResponse(
            success=True,
            message="Survey submitted successfully" if profile_created else "Survey submitted, but profile creation failed",
            response_id=response_id,
            profile_id=profile_id,
            errors=errors if errors else None
        )

    except Exception as e:
        # Transaction failed - rollback if possible
        # Note: Supabase doesn't support manual transactions via PostgREST
        # So we rely on atomic operations and error handling

        raise HTTPException(
            status_code=500,
            detail=f"Failed to process survey submission: {str(e)}"
        )


@router.get("/health")
async def webhook_health():
    """Health check for webhook endpoints."""
    webhook_secret_configured = bool(os.getenv("N8N_WEBHOOK_SECRET"))

    return {
        "status": "healthy",
        "webhook_secret_configured": webhook_secret_configured,
        "signature_verification": "enabled" if webhook_secret_configured else "disabled"
    }
