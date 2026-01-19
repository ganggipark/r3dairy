"""
Daily Log API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Header
from supabase import Client
from datetime import date
from src.db.supabase import get_supabase
from src.api.auth import get_current_user
from src.api.models import DailyLogCreate, DailyLogUpdate, DailyLogResponse, SuccessResponse

router = APIRouter(prefix="/api/logs", tags=["Daily Logs"])


@router.post("/{target_date}", response_model=DailyLogResponse, status_code=status.HTTP_201_CREATED)
async def create_daily_log(
    target_date: date,
    request: DailyLogCreate,
    authorization: str = Header(...),
    supabase: Client = Depends(get_supabase)
):
    """
    일간 기록 생성

    Args:
        target_date: 기록 날짜
        request: 기록 내용
        authorization: Bearer {access_token}

    Returns:
        DailyLogResponse: 생성된 기록

    Raises:
        HTTPException 400: 해당 날짜에 이미 기록 존재
    """
    user = get_current_user(authorization, supabase)
    user_id = user.id

    try:
        # 기존 기록 확인
        existing = supabase.table("daily_logs").select("*").eq(
            "profile_id", user_id
        ).eq("date", target_date.isoformat()).execute()

        if existing.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="해당 날짜에 이미 기록이 존재합니다."
            )

        # 기록 생성
        log_data = {
            "profile_id": user_id,
            "date": target_date.isoformat(),
            "schedule": request.schedule,
            "todos": request.todos,
            "mood": request.mood,
            "energy": request.energy,
            "notes": request.notes,
            "gratitude": request.gratitude
        }

        result = supabase.table("daily_logs").insert(log_data).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="기록 생성에 실패했습니다."
            )

        return DailyLogResponse(**result.data[0])

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"기록 생성 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/{target_date}", response_model=DailyLogResponse)
async def get_daily_log(
    target_date: date,
    authorization: str = Header(...),
    supabase: Client = Depends(get_supabase)
):
    """
    일간 기록 조회

    Args:
        target_date: 조회할 날짜
        authorization: Bearer {access_token}

    Returns:
        DailyLogResponse: 기록 내용

    Raises:
        HTTPException 404: 기록이 존재하지 않음
    """
    user = get_current_user(authorization, supabase)
    user_id = user.id

    try:
        result = supabase.table("daily_logs").select("*").eq(
            "profile_id", user_id
        ).eq("date", target_date.isoformat()).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="기록이 존재하지 않습니다."
            )

        return DailyLogResponse(**result.data[0])

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"기록 조회 중 오류가 발생했습니다: {str(e)}"
        )


@router.put("/{target_date}", response_model=DailyLogResponse)
async def update_daily_log(
    target_date: date,
    request: DailyLogUpdate,
    authorization: str = Header(...),
    supabase: Client = Depends(get_supabase)
):
    """
    일간 기록 수정

    Args:
        target_date: 수정할 날짜
        request: 수정할 내용 (모든 필드 optional)
        authorization: Bearer {access_token}

    Returns:
        DailyLogResponse: 수정된 기록

    Raises:
        HTTPException 404: 기록이 존재하지 않음
    """
    user = get_current_user(authorization, supabase)
    user_id = user.id

    try:
        # 기존 기록 확인
        existing = supabase.table("daily_logs").select("*").eq(
            "profile_id", user_id
        ).eq("date", target_date.isoformat()).execute()

        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="기록이 존재하지 않습니다."
            )

        # 수정할 데이터 준비
        update_data = {}
        if request.schedule is not None:
            update_data["schedule"] = request.schedule
        if request.todos is not None:
            update_data["todos"] = request.todos
        if request.mood is not None:
            update_data["mood"] = request.mood
        if request.energy is not None:
            update_data["energy"] = request.energy
        if request.notes is not None:
            update_data["notes"] = request.notes
        if request.gratitude is not None:
            update_data["gratitude"] = request.gratitude

        # 기록 수정
        result = supabase.table("daily_logs").update(update_data).eq(
            "profile_id", user_id
        ).eq("date", target_date.isoformat()).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="기록 수정에 실패했습니다."
            )

        return DailyLogResponse(**result.data[0])

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"기록 수정 중 오류가 발생했습니다: {str(e)}"
        )


@router.delete("/{target_date}", response_model=SuccessResponse)
async def delete_daily_log(
    target_date: date,
    authorization: str = Header(...),
    supabase: Client = Depends(get_supabase)
):
    """
    일간 기록 삭제

    Args:
        target_date: 삭제할 날짜
        authorization: Bearer {access_token}

    Returns:
        SuccessResponse: 삭제 성공 메시지

    Raises:
        HTTPException 404: 기록이 존재하지 않음
    """
    user = get_current_user(authorization, supabase)
    user_id = user.id

    try:
        result = supabase.table("daily_logs").delete().eq(
            "profile_id", user_id
        ).eq("date", target_date.isoformat()).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="기록이 존재하지 않습니다."
            )

        return SuccessResponse(message="기록이 삭제되었습니다.")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"기록 삭제 중 오류가 발생했습니다: {str(e)}"
        )
