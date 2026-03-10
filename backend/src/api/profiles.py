"""
Profile Management API Endpoints

CRUD operations for customer profiles created from survey responses.
"""

from typing import Dict, Optional
from fastapi import APIRouter, HTTPException, Depends, Header
from supabase import Client

from ..db.supabase import get_supabase_service
from ..data_processor import DataProcessor

router = APIRouter(prefix="/api/profiles", tags=["profiles"])


def _get_current_user_from_header(
    authorization: Optional[str],
    supabase: Client,
) -> object:
    """Authorization 헤더에서 현재 사용자 가져오기."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="인증 토큰이 필요합니다.")
    token = authorization.split(" ")[1]
    try:
        user_response = supabase.auth.get_user(token)
        if not user_response or not user_response.user:
            raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.")
        return user_response.user
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=401, detail="인증에 실패했습니다.")


@router.post("/create")
async def create_profile(
    survey_response: Dict,
    authorization: Optional[str] = Header(None),
    supabase: Client = Depends(get_supabase_service),
) -> Dict:
    """
    Create customer profile from survey response.

    Input: Raw survey response JSON with fields:
        - name, email, birth_date, gender, role
        - personality_scores (list of 8 ints, 1-5 Likert)
        - interests (list of strings)
        - subscription_type, paper_size, delivery_frequency
        - email_frequency, consent_privacy, consent_marketing

    Returns: { success, customer_id, profile, warnings, errors }
    """
    _get_current_user_from_header(authorization, supabase)

    processor = DataProcessor()
    success, profile, errors = await processor.process_survey_response(
        survey_response
    )

    if not success:
        raise HTTPException(status_code=400, detail={"errors": errors})

    try:
        customer_id = await processor.create_customer_in_db(profile, supabase)
    except ValueError as e:
        raise HTTPException(status_code=409, detail={"errors": [str(e)]})

    from ..data_processor.validator import ProfileValidator
    warnings = ProfileValidator.detect_anomalies(profile)

    return {
        "success": True,
        "customer_id": customer_id,
        "profile": profile.model_dump(mode="json"),
        "warnings": warnings,
        "errors": [],
    }


@router.get("/{customer_id}")
async def get_profile(
    customer_id: str,
    authorization: Optional[str] = Header(None),
    supabase: Client = Depends(get_supabase_service),
) -> Dict:
    """Get customer profile by ID."""
    current_user = _get_current_user_from_header(authorization, supabase)
    if str(getattr(current_user, "id", "")) != str(customer_id):
        raise HTTPException(status_code=403, detail="Access denied")

    result = (
        supabase.table("customers")
        .select("*")
        .eq("id", customer_id)
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Customer not found")

    customer = result.data[0]

    # Fetch sub-profiles
    personality = (
        supabase.table("customer_personalities")
        .select("*")
        .eq("customer_id", customer_id)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    interests = (
        supabase.table("customer_interests")
        .select("*")
        .eq("customer_id", customer_id)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    preferences = (
        supabase.table("customer_preferences")
        .select("*")
        .eq("customer_id", customer_id)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )

    return {
        "customer": customer,
        "personality": personality.data[0] if personality.data else None,
        "interests": interests.data[0] if interests.data else None,
        "preferences": preferences.data[0] if preferences.data else None,
    }


@router.put("/{customer_id}")
async def update_profile(
    customer_id: str,
    updates: Dict,
    authorization: Optional[str] = Header(None),
    supabase: Client = Depends(get_supabase_service),
) -> Dict:
    """Update customer profile fields."""
    current_user = _get_current_user_from_header(authorization, supabase)
    if str(getattr(current_user, "id", "")) != str(customer_id):
        raise HTTPException(status_code=403, detail="Access denied")

    processor = DataProcessor()
    try:
        result = await processor.update_customer_profile(
            customer_id, updates, supabase
        )
        return {"success": True, "customer": result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{customer_id}/personality")
async def get_personality_profile(
    customer_id: str,
    authorization: Optional[str] = Header(None),
    supabase: Client = Depends(get_supabase_service),
) -> Dict:
    """Get personality analysis only."""
    current_user = _get_current_user_from_header(authorization, supabase)
    if str(getattr(current_user, "id", "")) != str(customer_id):
        raise HTTPException(status_code=403, detail="Access denied")

    result = (
        supabase.table("customer_personalities")
        .select("*")
        .eq("customer_id", customer_id)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Personality profile not found")
    return result.data[0]


@router.get("/{customer_id}/interests")
async def get_interests_profile(
    customer_id: str,
    authorization: Optional[str] = Header(None),
    supabase: Client = Depends(get_supabase_service),
) -> Dict:
    """Get interests analysis only."""
    current_user = _get_current_user_from_header(authorization, supabase)
    if str(getattr(current_user, "id", "")) != str(customer_id):
        raise HTTPException(status_code=403, detail="Access denied")

    result = (
        supabase.table("customer_interests")
        .select("*")
        .eq("customer_id", customer_id)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Interests profile not found")
    return result.data[0]
