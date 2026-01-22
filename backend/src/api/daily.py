"""
Daily Content API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Header, Query
from supabase import Client
import datetime
from datetime import date, time
from typing import Optional
from src.db.supabase import get_supabase, get_supabase_service
from src.api.auth import get_current_user
from src.api.models import DailyContentResponse
from src.rhythm.models import BirthInfo, Gender
from src.rhythm.saju import calculate_saju, analyze_daily_fortune
from src.content.assembly import assemble_daily_content
from src.translation import translate_daily_content, Role

router = APIRouter(prefix="/api/daily", tags=["Daily Content"])


def _get_profile_data(user_id: str, supabase_db: Client) -> dict:
    """프로필 데이터 조회 (내부 헬퍼)

    Args:
        user_id: 사용자 ID
        supabase_db: Service role Supabase client (RLS 우회용)
    """
    result = supabase_db.table("profiles").select("*").eq("id", user_id).execute()

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="프로필이 존재하지 않습니다. 먼저 프로필을 생성해주세요."
        )

    return result.data[0]


@router.get("/{target_date}", response_model=DailyContentResponse)
async def get_daily_content(
    target_date: datetime.date,
    role: Optional[Role] = Query(None, description="역할 (student, office_worker, freelancer)"),
    authorization: str = Header(...),
    supabase_auth: Client = Depends(get_supabase),
    supabase_db: Client = Depends(get_supabase_service)
):
    """
    일간 콘텐츠 조회

    Args:
        target_date: 조회할 날짜 (YYYY-MM-DD)
        role: 역할 (optional, None이면 중립 콘텐츠)
        authorization: Bearer {access_token}

    Returns:
        DailyContentResponse: 일간 콘텐츠 (역할별로 변환됨)

    Raises:
        HTTPException 404: 프로필이 존재하지 않음
        HTTPException 401: 인증되지 않은 요청
        HTTPException 500: 서버 오류

    Example:
        GET /api/daily/2026-01-20?role=student
        → 학생용 일간 콘텐츠 반환
    """
    user = get_current_user(authorization, supabase_auth)
    user_id = user.id

    try:
        # 1. 프로필 데이터 조회 (Service client 사용 - RLS 우회)
        profile = _get_profile_data(user_id, supabase_db)

        # 2. BirthInfo 생성
        birth_info = BirthInfo(
            name=profile["name"],
            birth_date=datetime.date.fromisoformat(profile["birth_date"]),
            birth_time=datetime.time.fromisoformat(profile["birth_time"]),
            gender=Gender(profile["gender"]),
            birth_place=profile["birth_place"]
        )

        # 3. 사주 계산 (내부 계산)
        saju_result = calculate_saju(birth_info, target_date)

        # 4. 일간 리듬 분석 (내부 해석)
        daily_rhythm = analyze_daily_fortune(birth_info, target_date, saju_result)

        # 5. 사용자 노출 콘텐츠 생성 (중립 콘텐츠)
        daily_content = assemble_daily_content(target_date, saju_result, daily_rhythm)

        # 6. 역할별 변환 (role 파라미터가 있으면)
        if role:
            daily_content = translate_daily_content(daily_content, role.value)

        # 7. 응답 생성
        # Note: Pydantic V2는 datetime.date를 자동으로 직렬화하지만 명시적으로 변환
        return {
            "date": target_date.isoformat(),
            "role": role.value if role else None,
            "content": daily_content
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"일간 콘텐츠 생성 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/range/{start_date}/{end_date}")
async def get_daily_content_range(
    start_date: datetime.date,
    end_date: datetime.date,
    role: Optional[Role] = Query(None),
    authorization: str = Header(...),
    supabase_auth: Client = Depends(get_supabase),
    supabase_db: Client = Depends(get_supabase_service)
):
    """
    기간별 일간 콘텐츠 조회

    Args:
        start_date: 시작 날짜
        end_date: 종료 날짜
        role: 역할 (optional)
        authorization: Bearer {access_token}

    Returns:
        List[DailyContentResponse]: 일간 콘텐츠 리스트

    Raises:
        HTTPException 400: 잘못된 날짜 범위 (최대 31일)
        HTTPException 404: 프로필이 존재하지 않음

    Example:
        GET /api/daily/range/2026-01-01/2026-01-31?role=office_worker
        → 2026년 1월 전체 일간 콘텐츠 (직장인용)
    """
    user = get_current_user(authorization, supabase_auth)
    user_id = user.id

    try:
        # 날짜 범위 검증 (최대 31일)
        delta = (end_date - start_date).days
        if delta < 0 or delta > 31:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="날짜 범위는 최대 31일까지 가능합니다."
            )

        # 프로필 데이터 조회 (Service client 사용 - RLS 우회)
        profile = _get_profile_data(user_id, supabase_db)

        # BirthInfo 생성
        birth_info = BirthInfo(
            name=profile["name"],
            birth_date=datetime.date.fromisoformat(profile["birth_date"]),
            birth_time=datetime.time.fromisoformat(profile["birth_time"]),
            gender=Gender(profile["gender"]),
            birth_place=profile["birth_place"]
        )

        # 기간별 콘텐츠 생성
        results = []
        current_date = start_date
        while current_date <= end_date:
            # 사주 계산 → 리듬 분석 → 콘텐츠 생성
            saju_result = calculate_saju(birth_info, current_date)
            daily_rhythm = analyze_daily_fortune(birth_info, current_date, saju_result)
            daily_content = assemble_daily_content(current_date, saju_result, daily_rhythm)

            # 역할별 변환
            if role:
                daily_content = translate_daily_content(daily_content, role.value)

            results.append({
                "date": current_date.isoformat(),
                "role": role.value if role else None,
                "content": daily_content
            })

            # 다음 날로 이동
            current_date += datetime.timedelta(days=1)

        return results

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"기간별 콘텐츠 생성 중 오류가 발생했습니다: {str(e)}"
        )
