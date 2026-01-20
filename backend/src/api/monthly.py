"""
Monthly/Yearly Content API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Header, Query
from supabase import Client
import datetime
from typing import Optional
from src.db.supabase import get_supabase
from src.api.auth import get_current_user
from src.rhythm.models import BirthInfo, Gender
from src.rhythm.signals import create_monthly_rhythm, create_yearly_rhythm
from src.translation.models import Role

router = APIRouter(prefix="/api/content", tags=["Monthly/Yearly Content"])


def _get_profile_data(user_id: str, supabase: Client) -> dict:
    """프로필 데이터 조회 (내부 헬퍼)"""
    result = supabase.table("profiles").select("*").eq("id", user_id).execute()

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="프로필이 존재하지 않습니다."
        )

    return result.data[0]


@router.get("/monthly/{year}/{month}")
async def get_monthly_content(
    year: int,
    month: int,
    role: Optional[Role] = Query(None),
    authorization: str = Header(...),
    supabase: Client = Depends(get_supabase)
):
    """
    월간 콘텐츠 조회

    Args:
        year: 연도 (2000-2100)
        month: 월 (1-12)
        role: 역할 (optional)
        authorization: Bearer {access_token}

    Returns:
        월간 콘텐츠 (MonthlyRhythmSignal)

    Example:
        GET /api/content/monthly/2026/1?role=student
    """
    user = get_current_user(authorization, supabase)
    user_id = user.id

    try:
        # 날짜 검증
        if year < 2000 or year > 2100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="연도는 2000-2100 범위여야 합니다."
            )
        if month < 1 or month > 12:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="월은 1-12 범위여야 합니다."
            )

        # 프로필 조회
        profile = _get_profile_data(user_id, supabase)

        # BirthInfo 생성
        birth_info = BirthInfo(
            name=profile["name"],
            birth_date=date.fromisoformat(profile["birth_date"]),
            birth_time=time.fromisoformat(profile["birth_time"]),
            gender=Gender(profile["gender"]),
            birth_place=profile["birth_place"]
        )

        # MonthlyRhythmSignal 생성
        monthly_signal = create_monthly_rhythm(birth_info, year, month)

        # TODO: 월간 콘텐츠 조립 및 역할별 변환
        # (Phase 3에서 MonthlyContent 생성 로직 필요)

        return {
            "year": year,
            "month": month,
            "role": role.value if role else None,
            "content": monthly_signal.model_dump()
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"월간 콘텐츠 생성 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/yearly/{year}")
async def get_yearly_content(
    year: int,
    role: Optional[Role] = Query(None),
    authorization: str = Header(...),
    supabase: Client = Depends(get_supabase)
):
    """
    연간 콘텐츠 조회

    Args:
        year: 연도 (2000-2100)
        role: 역할 (optional)
        authorization: Bearer {access_token}

    Returns:
        연간 콘텐츠 (YearlyRhythmSignal)

    Example:
        GET /api/content/yearly/2026?role=office_worker
    """
    user = get_current_user(authorization, supabase)
    user_id = user.id

    try:
        # 연도 검증
        if year < 2000 or year > 2100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="연도는 2000-2100 범위여야 합니다."
            )

        # 프로필 조회
        profile = _get_profile_data(user_id, supabase)

        # BirthInfo 생성
        birth_info = BirthInfo(
            name=profile["name"],
            birth_date=date.fromisoformat(profile["birth_date"]),
            birth_time=time.fromisoformat(profile["birth_time"]),
            gender=Gender(profile["gender"]),
            birth_place=profile["birth_place"]
        )

        # YearlyRhythmSignal 생성
        yearly_signal = create_yearly_rhythm(birth_info, year)

        # TODO: 연간 콘텐츠 조립 및 역할별 변환
        # (Phase 3에서 YearlyContent 생성 로직 필요)

        return {
            "year": year,
            "role": role.value if role else None,
            "content": yearly_signal.model_dump()
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"연간 콘텐츠 생성 중 오류가 발생했습니다: {str(e)}"
        )
