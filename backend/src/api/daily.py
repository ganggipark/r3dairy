"""
Daily Content API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Header, Query
from fastapi.responses import Response, JSONResponse
from supabase import Client
import datetime
from datetime import date, time
from typing import Optional
import os
from pathlib import Path
from src.db.supabase import get_supabase, SupabaseClient
from src.api.auth import get_current_user
from src.api.models import DailyContentResponse
from src.rhythm.models import BirthInfo, Gender
from src.rhythm.saju import calculate_saju, analyze_daily_fortune
from src.content.assembly import assemble_daily_content
from src.translation import translate_daily_content, Role

# Import markdown library (install with: pip install markdown)
try:
    import markdown
    MARKDOWN_AVAILABLE = True
except ImportError:
    MARKDOWN_AVAILABLE = False

router = APIRouter(prefix="/api/daily", tags=["Daily Content"])

# Cache for markdown content (simple in-memory cache)
_markdown_cache = {}
_cache_timeout = 3600  # 1 hour in seconds


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
            detail="프로필이 존재하지 않습니다. 먼저 프로필을 생성해주세요."
        )

    return result.data[0]


@router.get("/{target_date}/markdown")
async def get_daily_markdown(
    target_date: datetime.date,
    authorization: Optional[str] = Header(None),
    supabase_auth: Client = Depends(get_supabase),
):
    """
    일간 콘텐츠를 Markdown 형식으로 조회

    Args:
        target_date: 조회할 날짜 (YYYY-MM-DD)
        authorization: Bearer {access_token}

    Returns:
        Markdown 텍스트 (text/markdown)

    Raises:
        HTTPException 404: 날짜에 해당하는 마크다운 파일이 없음
        HTTPException 401: 인증되지 않은 요청
        HTTPException 500: 서버 오류

    Example:
        GET /api/daily/2026-01-31/markdown
        → 2026-01-31.md 파일 내용 반환 (또는 생성)
    """
    # 인증 확인
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증이 필요합니다."
        )

    user = get_current_user(authorization, supabase_auth)

    try:
        # 캐시 확인
        cache_key = f"md_{target_date.isoformat()}"
        if cache_key in _markdown_cache:
            cached_data = _markdown_cache[cache_key]
            if datetime.datetime.now().timestamp() - cached_data["timestamp"] < _cache_timeout:
                return Response(
                    content=cached_data["content"],
                    media_type="text/markdown; charset=utf-8"
                )

        # backend/daily/ 디렉토리에서 마크다운 파일 찾기
        daily_dir = Path(__file__).parent.parent.parent / "daily"
        md_file = daily_dir / f"{target_date.isoformat()}_new_format.md"

        # 파일이 없으면 기본 형식 파일도 확인
        if not md_file.exists():
            md_file = daily_dir / f"{target_date.isoformat()}.md"

        if md_file.exists():
            # 파일 읽기
            markdown_content = md_file.read_text(encoding="utf-8")
        else:
            # 파일이 없으면 404 반환
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{target_date.isoformat()} 날짜에 해당하는 콘텐츠를 찾을 수 없습니다."
            )

        # 캐시 저장
        _markdown_cache[cache_key] = {
            "content": markdown_content,
            "timestamp": datetime.datetime.now().timestamp()
        }

        return Response(
            content=markdown_content,
            media_type="text/markdown; charset=utf-8"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"마크다운 콘텐츠 조회 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/{target_date}/markdown-html")
async def get_daily_markdown_html(
    target_date: datetime.date,
    authorization: Optional[str] = Header(None),
    supabase_auth: Client = Depends(get_supabase),
):
    """
    일간 콘텐츠를 Markdown → HTML로 변환하여 조회

    Args:
        target_date: 조회할 날짜 (YYYY-MM-DD)
        authorization: Bearer {access_token}

    Returns:
        JSON {"html": "...", "date": "..."}

    Raises:
        HTTPException 404: 날짜에 해당하는 마크다운 파일이 없음
        HTTPException 401: 인증되지 않은 요청
        HTTPException 500: 서버 오류, markdown 라이브러리 미설치

    Example:
        GET /api/daily/2026-01-31/markdown-html
        → {"html": "<h1>오늘의 안내</h1>...", "date": "2026-01-31"}
    """
    # 인증 확인
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증이 필요합니다."
        )

    user = get_current_user(authorization, supabase_auth)

    if not MARKDOWN_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="markdown 라이브러리가 설치되지 않았습니다. 'pip install markdown'을 실행하세요."
        )

    try:
        # 캐시 확인
        cache_key = f"html_{target_date.isoformat()}"
        if cache_key in _markdown_cache:
            cached_data = _markdown_cache[cache_key]
            if datetime.datetime.now().timestamp() - cached_data["timestamp"] < _cache_timeout:
                return JSONResponse(content=cached_data["content"])

        # backend/daily/ 디렉토리에서 마크다운 파일 찾기
        daily_dir = Path(__file__).parent.parent.parent / "daily"
        md_file = daily_dir / f"{target_date.isoformat()}_new_format.md"

        # 파일이 없으면 기본 형식 파일도 확인
        if not md_file.exists():
            md_file = daily_dir / f"{target_date.isoformat()}.md"

        if md_file.exists():
            # 파일 읽기
            markdown_content = md_file.read_text(encoding="utf-8")
        else:
            # 파일이 없으면 404 반환
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{target_date.isoformat()} 날짜에 해당하는 콘텐츠를 찾을 수 없습니다."
            )

        # Markdown → HTML 변환
        html_content = markdown.markdown(
            markdown_content,
            extensions=['extra', 'nl2br', 'sane_lists']
        )

        # 기본 스타일링 클래스 추가
        html_with_classes = html_content.replace(
            '<h1>', '<h1 class="text-3xl font-bold mb-4">'
        ).replace(
            '<h2>', '<h2 class="text-2xl font-semibold mb-3 mt-6">'
        ).replace(
            '<h3>', '<h3 class="text-xl font-medium mb-2 mt-4">'
        ).replace(
            '<ul>', '<ul class="list-disc list-inside mb-4 space-y-1">'
        ).replace(
            '<ol>', '<ol class="list-decimal list-inside mb-4 space-y-1">'
        ).replace(
            '<p>', '<p class="mb-3 leading-relaxed">'
        ).replace(
            '<hr>', '<hr class="my-6 border-gray-300">'
        )

        response_data = {
            "html": html_with_classes,
            "date": target_date.isoformat()
        }

        # 캐시 저장
        _markdown_cache[cache_key] = {
            "content": response_data,
            "timestamp": datetime.datetime.now().timestamp()
        }

        return JSONResponse(content=response_data)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"HTML 변환 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/{target_date}", response_model=DailyContentResponse)
async def get_daily_content(
    target_date: datetime.date,
    role: Optional[Role] = Query(None, description="역할 (student, office_worker, freelancer)"),
    authorization: Optional[str] = Header(None),
    supabase_auth: Client = Depends(get_supabase),
):
    """
    일간 콘텐츠 조회 (JSON 형식)

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
        # 1. 프로필 데이터 조회 (RLS 적용)
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
    authorization: Optional[str] = Header(None),
    supabase_auth: Client = Depends(get_supabase),
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
        # 날짜 범위 검증 (최대 31일)
        delta = (end_date - start_date).days
        if delta < 0 or delta > 31:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="날짜 범위는 최대 31일까지 가능합니다."
            )

        # 프로필 데이터 조회 (RLS 적용)
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
