"""
Monthly/Yearly Content API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Header, Query
from supabase import Client
import datetime
from datetime import date, time
from typing import Optional
from src.db.supabase import get_supabase, SupabaseClient
from src.api.auth import get_current_user
from src.rhythm.models import BirthInfo, Gender
from src.rhythm.saju import calculate_saju, analyze_monthly_rhythm, analyze_yearly_rhythm
from src.content.assembly import assemble_monthly_content, assemble_yearly_content
from src.translation.models import Role

router = APIRouter(prefix="/api/content", tags=["Monthly/Yearly Content"])


def _get_profile_data(user_id: str, supabase_db: Client) -> dict:
    """프로필 데이터 조회 (내부 헬퍼)

    Args:
        user_id: 사용자 ID
        supabase_db: Supabase DB client (RLS 적용)
    """
    result = supabase_db.table("profiles").select("*").eq("id", user_id).execute()

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
    authorization: Optional[str] = Header(None),
    supabase_auth: Client = Depends(get_supabase),
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
    # 인증 확인
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증이 필요합니다."
        )

    user = get_current_user(authorization, supabase_auth)
    user_id = user.id

    token = authorization.split(" ")[1]
    supabase_db = SupabaseClient.create_user_db_client(token)

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

        # 프로필 조회 (RLS 적용)
        profile = _get_profile_data(user_id, supabase_db)

        # BirthInfo 생성
        birth_info = BirthInfo(
            name=profile["name"],
            birth_date=datetime.date.fromisoformat(profile["birth_date"]),
            birth_time=datetime.time.fromisoformat(profile["birth_time"]),
            gender=Gender(profile["gender"]),
            birth_place=profile["birth_place"]
        )

        # 사주 계산 (대표 날짜 사용)
        target_date = datetime.date(year, month, 1)
        saju_result = calculate_saju(birth_info, target_date)

        # 월간 리듬 분석
        monthly_rhythm = analyze_monthly_rhythm(birth_info, year, month, saju_result)

        # 월간 콘텐츠 조립
        monthly_content = assemble_monthly_content(year, month, monthly_rhythm)

        # 역할별 번역 적용
        if role:
            from src.translation.translator import translate_monthly_content
            monthly_content = translate_monthly_content(monthly_content, role.value)

        return {
            "year": year,
            "month": month,
            "role": role.value if role else None,
            "content": monthly_content
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
    authorization: Optional[str] = Header(None),
    supabase_auth: Client = Depends(get_supabase),
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
    # 인증 확인
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증이 필요합니다."
        )

    user = get_current_user(authorization, supabase_auth)
    user_id = user.id

    token = authorization.split(" ")[1]
    supabase_db = SupabaseClient.create_user_db_client(token)

    try:
        # 연도 검증
        if year < 2000 or year > 2100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="연도는 2000-2100 범위여야 합니다."
            )

        # 프로필 조회 (RLS 적용)
        profile = _get_profile_data(user_id, supabase_db)

        # BirthInfo 생성
        birth_info = BirthInfo(
            name=profile["name"],
            birth_date=datetime.date.fromisoformat(profile["birth_date"]),
            birth_time=datetime.time.fromisoformat(profile["birth_time"]),
            gender=Gender(profile["gender"]),
            birth_place=profile["birth_place"]
        )

        # 사주 계산 (대표 날짜 사용)
        target_date = datetime.date(year, 1, 1)
        saju_result = calculate_saju(birth_info, target_date)

        # 연간 리듬 분석
        yearly_rhythm = analyze_yearly_rhythm(birth_info, year, saju_result)

        # 연간 콘텐츠 조립
        yearly_content = assemble_yearly_content(year, yearly_rhythm)

        # 역할별 번역 적용
        if role:
            from src.translation.translator import translate_yearly_content
            yearly_content = translate_yearly_content(yearly_content, role.value)

        return {
            "year": year,
            "role": role.value if role else None,
            "content": yearly_content
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"연간 콘텐츠 생성 중 오류가 발생했습니다: {str(e)}"
        )
