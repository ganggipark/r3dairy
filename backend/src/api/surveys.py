"""API endpoints for survey management and submission."""

from __future__ import annotations

import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Request, Query
from pydantic import BaseModel, Field

from ..config.survey_templates import (
    create_default_survey,
    get_survey_by_template,
    apply_korean_localization,
    SurveyDeploymentConfig,
)
from ..config.survey_templates.database_models import (
    SurveyConfiguration,
    SurveyResponse,
    SurveyResponseCreate,
    SurveyResponseSummary,
    SurveyDeployment,
    SurveyStatus,
    SurveySource,
)
from ..skills.form_builder.models import FormConfiguration
from ..skills.form_builder.generators import FormGenerator
from ..db.supabase import (
    get_supabase_client,
    save_survey_config,
    get_survey_config,
    list_survey_configs,
    update_survey_status as db_update_survey_status,
    update_survey_deployment,
    save_survey_response,
    list_survey_responses,
    get_survey_response_summary,
    save_customer_profile,
)
from ..data_processor.survey_to_profile import SurveyResponseToProfile

router = APIRouter(prefix="/surveys", tags=["surveys"])


# ============================================================================
# Request/Response Models
# ============================================================================

class CreateSurveyRequest(BaseModel):
    """Request to create a new survey from template."""
    template: str = Field(
        ...,
        description="Template name: 'default', 'quick_profile', 'student', 'office_worker'"
    )
    locale: Optional[str] = Field(
        None,
        description="Locale for localization (e.g., 'ko-KR')"
    )
    name_override: Optional[str] = None
    description_override: Optional[str] = None


class DeployRequest(BaseModel):
    """Request to deploy survey to a platform."""
    target: str = Field(
        ...,
        description="Deployment target: 'json', 'n8n', 'html', 'google_forms', 'web', 'markdown'"
    )


class SubmitSurveyRequest(BaseModel):
    """Request to submit a survey response."""
    survey_id: str
    response_data: Dict[str, Any]
    source: SurveySource = SurveySource.WEB
    user_id: Optional[str] = None


# ============================================================================
# Survey Configuration Endpoints
# ============================================================================

@router.post("/create", response_model=Dict[str, Any])
async def create_survey(request: CreateSurveyRequest):
    """
    Create a new survey from a template.

    Args:
        request: CreateSurveyRequest with template name and optional overrides

    Returns:
        Survey configuration with ID
    """
    try:
        # Get survey from template
        form = get_survey_by_template(request.template)

        # Apply localization if requested
        if request.locale == "ko-KR":
            form = apply_korean_localization(form)

        # Apply overrides
        if request.name_override:
            form.name = request.name_override
        if request.description_override:
            form.description = request.description_override

        # Convert FormConfiguration to SurveyConfiguration
        survey_config = SurveyConfiguration(
            id=form.id,
            name=form.name,
            description=form.description,
            form_json=FormGenerator.to_json(form),
            status=SurveyStatus.DRAFT,
            metadata={
                "template": request.template,
                "locale": request.locale or "en-US",
            }
        )

        # Save to Supabase
        saved_config = await save_survey_config(survey_config.dict())

        return {
            "survey_id": saved_config["id"],
            "name": saved_config["name"],
            "description": saved_config["description"],
            "status": saved_config["status"],
            "created_at": saved_config["created_at"],
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create survey: {str(e)}")


@router.get("/{survey_id}", response_model=Dict[str, Any])
async def get_survey(survey_id: str):
    """
    Get survey configuration by ID.

    Args:
        survey_id: Survey ID

    Returns:
        Full survey configuration
    """
    survey_config = await get_survey_config(survey_id)

    if not survey_config:
        raise HTTPException(status_code=404, detail="Survey not found")

    return {
        "survey_id": survey_config["id"],
        "name": survey_config["name"],
        "description": survey_config["description"],
        "status": survey_config["status"],
        "form": survey_config["form_json"],
        "deployed_to": survey_config["deployed_to"],
        "response_count": survey_config["response_count"],
        "created_at": survey_config["created_at"],
        "updated_at": survey_config["updated_at"],
    }


@router.get("/", response_model=List[Dict[str, Any]])
async def list_surveys(
    status: Optional[SurveyStatus] = None,
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0, ge=0)
):
    """
    List all surveys with optional filtering.

    Args:
        status: Filter by status (draft, active, archived)
        limit: Maximum number of surveys to return
        offset: Number of surveys to skip

    Returns:
        List of survey summaries
    """
    surveys = await list_survey_configs(
        status=status.value if status else None,
        limit=limit,
        offset=offset
    )

    return [
        {
            "survey_id": s["id"],
            "name": s["name"],
            "status": s["status"],
            "response_count": s["response_count"],
            "deployed_to": s["deployed_to"],
            "created_at": s["created_at"],
        }
        for s in surveys
    ]


@router.put("/{survey_id}/status")
async def update_survey_status(survey_id: str, status: SurveyStatus):
    """
    Update survey status.

    Args:
        survey_id: Survey ID
        status: New status (draft, active, archived)

    Returns:
        Updated survey configuration
    """
    # Check if survey exists
    survey_config = await get_survey_config(survey_id)
    if not survey_config:
        raise HTTPException(status_code=404, detail="Survey not found")

    # Update status in Supabase
    updated_config = await db_update_survey_status(survey_id, status.value)

    return {
        "survey_id": updated_config["id"],
        "status": updated_config["status"],
        "updated_at": updated_config["updated_at"],
    }


@router.delete("/{survey_id}")
async def delete_survey(survey_id: str):
    """
    Delete (archive) a survey.

    Args:
        survey_id: Survey ID

    Returns:
        Success message
    """
    # Check if survey exists
    survey_config = await get_survey_config(survey_id)
    if not survey_config:
        raise HTTPException(status_code=404, detail="Survey not found")

    # Archive instead of hard delete
    await db_update_survey_status(survey_id, SurveyStatus.ARCHIVED.value)

    return {"message": "Survey archived successfully", "survey_id": survey_id}


# ============================================================================
# Survey Deployment Endpoints
# ============================================================================

@router.post("/{survey_id}/deploy", response_model=Dict[str, Any])
async def deploy_survey(survey_id: str, request: DeployRequest):
    """
    Deploy survey to a specific platform.

    Args:
        survey_id: Survey ID
        request: DeployRequest with target platform

    Returns:
        Deployment configuration for the target platform
    """
    survey_config = await get_survey_config(survey_id)
    if not survey_config:
        raise HTTPException(status_code=404, detail="Survey not found")

    # Reconstruct FormConfiguration from JSON
    form_json = survey_config["form_json"]
    form = FormConfiguration(**form_json)

    target = request.target.lower()

    try:
        # Generate deployment configuration
        if target == "json":
            deployment_data = FormGenerator.to_json(form)
        elif target == "n8n":
            deployment_data = SurveyDeploymentConfig.get_n8n_deployment_config(form)
        elif target == "html":
            deployment_data = FormGenerator.to_html_form(form)
        elif target == "google_forms":
            deployment_data = SurveyDeploymentConfig.get_google_forms_config(form)
        elif target == "web":
            deployment_data = SurveyDeploymentConfig.get_web_deployment_config(form)
        elif target == "markdown":
            deployment_data = FormGenerator.to_markdown(form)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown target: {target}")

        # Update deployed_to status
        if target in ["n8n", "google_forms", "web"]:
            deployed_to = survey_config["deployed_to"].copy()
            deployed_to[target] = True
            await update_survey_deployment(survey_id, deployed_to)

        # Get deployment instructions
        instructions = SurveyDeploymentConfig.get_deployment_instructions(form, target)

        return {
            "survey_id": survey_id,
            "target": target,
            "deployed_at": datetime.utcnow().isoformat(),
            "deployment_data": deployment_data,
            "instructions": instructions,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Deployment failed: {str(e)}")


# ============================================================================
# Survey Response Endpoints
# ============================================================================

@router.post("/submit", response_model=Dict[str, Any])
async def submit_survey_response(request: Request, body: SubmitSurveyRequest):
    """
    Submit a survey response (webhook endpoint).

    Args:
        request: FastAPI Request object (for IP address)
        body: SubmitSurveyRequest with survey data

    Returns:
        Success response with response ID
    """
    survey_config = await get_survey_config(body.survey_id)
    if not survey_config:
        raise HTTPException(status_code=404, detail="Survey not found")

    # Check if survey is active
    if survey_config["status"] != SurveyStatus.ACTIVE.value:
        raise HTTPException(
            status_code=400,
            detail=f"Survey is not active (status: {survey_config['status']})"
        )

    # TODO: Validate response data against form schema

    # Create response
    response_id = str(uuid.uuid4())
    ip_address = request.client.host if request.client else None

    # Normalize response data
    normalized_data = _normalize_response_data(body.response_data)

    survey_response = SurveyResponse(
        id=response_id,
        survey_id=body.survey_id,
        response_data=body.response_data,
        normalized_data=normalized_data,
        ip_address=ip_address,
        source=body.source,
        user_id=body.user_id,
    )

    # Save to Supabase (triggers response_count increment via DB trigger)
    saved_response = await save_survey_response(survey_response.dict())

    # Convert survey response to CustomerProfile
    profile_created = False
    profile_id = None
    try:
        customer_profile = SurveyResponseToProfile.convert(normalized_data)

        # Save profile to Supabase profiles table
        saved_profile = await save_customer_profile(customer_profile.dict())
        profile_created = True
        profile_id = saved_profile.get("id")

    except ValueError as e:
        # Log error but don't fail the survey submission
        # The survey response is already saved
        print(f"Warning: Failed to create profile from survey response: {e}")
    except Exception as e:
        print(f"Error: Unexpected error creating profile: {e}")

    return {
        "success": True,
        "message": "Survey submitted successfully",
        "response_id": saved_response["id"],
        "survey_id": saved_response["survey_id"],
        "submitted_at": saved_response["submitted_at"],
        "profile_created": profile_created,
        "profile_id": profile_id,
    }


@router.get("/{survey_id}/responses", response_model=Dict[str, Any])
async def get_survey_responses(
    survey_id: str,
    limit: int = Query(default=100, le=500),
    offset: int = Query(default=0, ge=0),
    source: Optional[SurveySource] = None
):
    """
    Get all responses for a survey with pagination.

    Args:
        survey_id: Survey ID
        limit: Maximum number of responses to return
        offset: Number of responses to skip
        source: Filter by response source

    Returns:
        List of survey responses
    """
    # Check if survey exists
    survey_config = await get_survey_config(survey_id)
    if not survey_config:
        raise HTTPException(status_code=404, detail="Survey not found")

    # Load from Supabase with pagination
    result = await list_survey_responses(
        survey_id=survey_id,
        limit=limit,
        offset=offset,
        source=source.value if source else None
    )

    return {
        "survey_id": survey_id,
        "total": result["total"],
        "limit": limit,
        "offset": offset,
        "responses": [
            {
                "response_id": r["id"],
                "submitted_at": r["submitted_at"],
                "source": r["source"],
                "data": r["normalized_data"],
            }
            for r in result["responses"]
        ]
    }


@router.get("/{survey_id}/summary", response_model=SurveyResponseSummary)
async def get_survey_summary(survey_id: str):
    """
    Get summary statistics for a survey.

    Args:
        survey_id: Survey ID

    Returns:
        SurveyResponseSummary with statistics
    """
    # Check if survey exists
    survey_config = await get_survey_config(survey_id)
    if not survey_config:
        raise HTTPException(status_code=404, detail="Survey not found")

    # Calculate from Supabase
    summary = await get_survey_response_summary(survey_id)

    return SurveyResponseSummary(
        survey_id=summary["survey_id"],
        total_responses=summary["total_responses"],
        responses_by_source=summary["responses_by_source"],
        responses_by_date=summary["responses_by_date"],
        completion_rate=1.0,  # TODO: Calculate actual completion rate
        average_completion_time_seconds=None,  # TODO: Track completion time
    )


# ============================================================================
# Helper Functions
# ============================================================================

def _normalize_response_data(response_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize survey response data to standard format.

    Args:
        response_data: Raw survey response

    Returns:
        Normalized data structure
    """
    normalized = {
        "profile": {},
        "personality": {},
        "interests": {},
        "activities": {},
        "format": {},
        "communication": {},
        "metadata": {}
    }

    # Profile fields
    if "name" in response_data:
        normalized["profile"]["name"] = response_data["name"]
    if "email" in response_data:
        normalized["profile"]["email"] = response_data["email"]
    if "birth_date" in response_data:
        normalized["profile"]["birth_date"] = response_data["birth_date"]
    if "gender" in response_data:
        normalized["profile"]["gender"] = _normalize_gender(response_data["gender"])
    if "primary_role" in response_data:
        normalized["profile"]["role"] = _normalize_role(response_data["primary_role"])

    # Personality scores
    personality_fields = [
        "p_extroversion", "p_structured", "p_openness", "p_empathy",
        "p_calm", "p_focus", "p_creative", "p_logical"
    ]
    for field in personality_fields:
        if field in response_data:
            key = field.replace("p_", "")
            normalized["personality"][key] = int(response_data[field])

    # Interests
    if "topics" in response_data:
        normalized["interests"]["topics"] = response_data["topics"]
    if "tone_preference" in response_data:
        normalized["interests"]["tone_preference"] = response_data["tone_preference"]

    # Activity preferences (role-specific)
    activity_fields = [
        # Student activities
        "study_type", "student_exercise_type", "student_social_type",
        # Office worker activities
        "work_type", "worker_exercise_type", "worker_social_type",
        # Freelancer activities
        "freelance_work_type", "freelancer_exercise_type", "freelancer_social_type",
        # Parent activities
        "parent_activity_type", "parent_exercise_type", "parent_social_type",
    ]
    for field in activity_fields:
        if field in response_data and response_data[field]:
            normalized["activities"][field] = response_data[field]

    # Format preferences
    if "diary_preference" in response_data:
        normalized["format"]["diary_type"] = _normalize_diary_type(response_data["diary_preference"])
    if "paper_size" in response_data:
        normalized["format"]["paper_size"] = response_data["paper_size"]
    if "delivery_frequency" in response_data:
        normalized["format"]["delivery_frequency"] = response_data["delivery_frequency"]
    if "delivery_address" in response_data:
        normalized["format"]["delivery_address"] = response_data["delivery_address"]

    # Communication
    if "email_frequency" in response_data:
        normalized["communication"]["email_frequency"] = response_data["email_frequency"]

    consents = {}
    if "privacy_consent" in response_data:
        consents["privacy"] = bool(response_data["privacy_consent"])
    if "marketing_consent" in response_data:
        consents["marketing"] = bool(response_data["marketing_consent"])
    if "research_consent" in response_data:
        consents["research"] = bool(response_data["research_consent"])
    normalized["communication"]["consents"] = consents

    # Metadata
    normalized["metadata"]["submitted_at"] = datetime.utcnow().isoformat()

    return normalized


def _normalize_gender(gender: str) -> str:
    """Normalize gender value to standard format."""
    mapping = {
        "Male": "male",
        "남성": "male",
        "Female": "female",
        "여성": "female",
        "Other": "other",
        "기타": "other",
        "Prefer not to say": "not_specified",
        "답변 안 함": "not_specified",
    }
    return mapping.get(gender, "not_specified")


def _normalize_role(role: str) -> str:
    """Normalize role value to standard format."""
    mapping = {
        "Student": "student",
        "학생": "student",
        "Office Worker": "office_worker",
        "직장인": "office_worker",
        "Freelancer / Self-employed": "freelancer",
        "프리랜서 / 자영업": "freelancer",
        "Parent": "parent",
        "부모": "parent",
        "Other": "other",
        "기타": "other",
    }
    return mapping.get(role, "other")


def _normalize_diary_type(diary_preference: str) -> str:
    """Normalize diary type to standard format."""
    mapping = {
        "App only (web/mobile)": "app_only",
        "앱 전용 (웹/모바일)": "app_only",
        "Hybrid (app + monthly printed version)": "hybrid",
        "하이브리드 (앱 + 월간 인쇄본)": "hybrid",
        "Paper diary only (printed monthly delivery)": "paper_only",
        "종이 다이어리 전용 (월간 배송)": "paper_only",
    }
    return mapping.get(diary_preference, "app_only")
