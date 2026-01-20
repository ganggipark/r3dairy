"""
Profile API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Header
from supabase import Client
from typing import Optional
from src.db.supabase import get_supabase, get_supabase_service
from src.api.models import ProfileCreate, ProfileUpdate, ProfileResponse, SuccessResponse
from src.api.auth import get_current_user

router = APIRouter(prefix="/api/profile", tags=["Profile"])


@router.post("", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_profile(
    request: ProfileCreate,
    authorization: str = Header(...),
    supabase_auth: Client = Depends(get_supabase),
    supabase_db: Client = Depends(get_supabase_service)
):
    """
    프로필 생성

    Args:
        request: 프로필 생성 정보
        authorization: Bearer {access_token}

    Returns:
        ProfileResponse: 생성된 프로필

    Raises:
        HTTPException 400: 이미 프로필이 존재함
        HTTPException 401: 인증되지 않은 요청
        HTTPException 500: 서버 오류
    """
    # 현재 사용자 확인 (Auth client 사용)
    user = get_current_user(authorization, supabase_auth)
    user_id = user.id

    try:
        # 기존 프로필 확인 (Service client 사용 - RLS 우회)
        existing = supabase_db.table("profiles").select("*").eq("id", user_id).execute()
        if existing.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 프로필이 존재합니다."
            )

        # 프로필 생성 (Service client 사용 - RLS 우회)
        profile_data = {
            "id": user_id,
            "name": request.name,
            "birth_date": request.birth_date.isoformat(),
            "birth_time": request.birth_time.isoformat(),
            "gender": request.gender.value,
            "birth_place": request.birth_place,
            "roles": [role.value for role in request.roles],
            "preferences": request.preferences or {}
        }

        result = supabase_db.table("profiles").insert(profile_data).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="프로필 생성에 실패했습니다."
            )

        return ProfileResponse(**result.data[0])

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"프로필 생성 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("", response_model=ProfileResponse)
async def get_profile(
    authorization: str = Header(...),
    supabase_auth: Client = Depends(get_supabase),
    supabase_db: Client = Depends(get_supabase_service)
):
    """
    프로필 조회

    Args:
        authorization: Bearer {access_token}

    Returns:
        ProfileResponse: 프로필 정보

    Raises:
        HTTPException 404: 프로필이 존재하지 않음
        HTTPException 401: 인증되지 않은 요청
    """
    user = get_current_user(authorization, supabase_auth)
    user_id = user.id

    try:
        result = supabase_db.table("profiles").select("*").eq("id", user_id).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="프로필이 존재하지 않습니다."
            )

        return ProfileResponse(**result.data[0])

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"프로필 조회 중 오류가 발생했습니다: {str(e)}"
        )


@router.put("", response_model=ProfileResponse)
async def update_profile(
    request: ProfileUpdate,
    authorization: str = Header(...),
    supabase_auth: Client = Depends(get_supabase),
    supabase_db: Client = Depends(get_supabase_service)
):
    """
    프로필 수정

    Args:
        request: 프로필 수정 정보 (모든 필드 optional)
        authorization: Bearer {access_token}

    Returns:
        ProfileResponse: 수정된 프로필

    Raises:
        HTTPException 404: 프로필이 존재하지 않음
        HTTPException 401: 인증되지 않은 요청
    """
    user = get_current_user(authorization, supabase_auth)
    user_id = user.id

    try:
        # 기존 프로필 확인
        existing = supabase_db.table("profiles").select("*").eq("id", user_id).execute()
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="프로필이 존재하지 않습니다."
            )

        # 수정할 데이터 준비 (None이 아닌 것만)
        update_data = {}
        if request.name is not None:
            update_data["name"] = request.name
        if request.birth_date is not None:
            update_data["birth_date"] = request.birth_date.isoformat()
        if request.birth_time is not None:
            update_data["birth_time"] = request.birth_time.isoformat()
        if request.gender is not None:
            update_data["gender"] = request.gender.value
        if request.birth_place is not None:
            update_data["birth_place"] = request.birth_place
        if request.roles is not None:
            update_data["roles"] = [role.value for role in request.roles]
        if request.preferences is not None:
            update_data["preferences"] = request.preferences

        # 프로필 수정
        result = supabase_db.table("profiles").update(update_data).eq("id", user_id).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="프로필 수정에 실패했습니다."
            )

        return ProfileResponse(**result.data[0])

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"프로필 수정 중 오류가 발생했습니다: {str(e)}"
        )


@router.delete("", response_model=SuccessResponse)
async def delete_profile(
    authorization: str = Header(...),
    supabase_auth: Client = Depends(get_supabase),
    supabase_db: Client = Depends(get_supabase_service)
):
    """
    프로필 삭제

    Args:
        authorization: Bearer {access_token}

    Returns:
        SuccessResponse: 삭제 성공 메시지

    Raises:
        HTTPException 404: 프로필이 존재하지 않음
        HTTPException 401: 인증되지 않은 요청
    """
    user = get_current_user(authorization, supabase_auth)
    user_id = user.id

    try:
        # 프로필 삭제
        result = supabase_db.table("profiles").delete().eq("id", user_id).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="프로필이 존재하지 않습니다."
            )

        return SuccessResponse(message="프로필이 삭제되었습니다.")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"프로필 삭제 중 오류가 발생했습니다: {str(e)}"
        )
