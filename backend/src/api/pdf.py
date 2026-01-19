"""
PDF API Endpoints
일간/월간 콘텐츠 PDF 생성 API
"""
from fastapi import APIRouter, Header, Query, HTTPException
from fastapi.responses import FileResponse
from typing import Optional
from datetime import date
import os
import sys
from pathlib import Path
import tempfile

# PDF Generator import
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "pdf-generator"))
from generator import PDFGenerator

# Backend imports
from ..api.auth import get_current_user
from ..api.daily import _get_profile_data, _generate_daily_content_internal
from ..db.supabase import get_supabase_client
from ..translation.models import Role

router = APIRouter(prefix="/api/pdf", tags=["PDF"])

# PDF Generator 인스턴스
pdf_generator = PDFGenerator()


@router.get("/daily/{target_date}")
async def generate_daily_pdf(
    target_date: date,
    role: Optional[Role] = Query(None, description="역할 (학생/직장인/프리랜서)"),
    authorization: str = Header(..., description="Bearer {access_token}")
):
    """
    일간 콘텐츠 PDF 생성 및 다운로드

    - **target_date**: 조회할 날짜 (YYYY-MM-DD)
    - **role**: 역할 (student, office_worker, freelancer) - 선택사항

    **Response**: PDF 파일 (application/pdf)

    **사용 예시**:
    ```bash
    curl -H "Authorization: Bearer {token}" \\
         http://localhost:8000/api/pdf/daily/2026-01-20?role=student \\
         --output diary_2026-01-20.pdf
    ```
    """
    # 1. 사용자 인증
    supabase = get_supabase_client()
    user = get_current_user(authorization, supabase)
    user_id = user["id"]

    try:
        # 2. 일간 콘텐츠 생성 (daily.py의 내부 로직 재사용)
        daily_content = _generate_daily_content_internal(
            user_id=user_id,
            target_date=target_date,
            role=role,
            supabase=supabase
        )

        # 3. 임시 PDF 파일 생성
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf",
            prefix=f"diary_{target_date}_"
        ) as tmp_file:
            output_path = tmp_file.name

        # 4. PDF 생성
        pdf_generator.generate_daily_pdf(
            content=daily_content.content.model_dump(),
            output_path=output_path,
            role=role.value if role else None
        )

        # 5. 파일 다운로드 응답
        filename = f"R3_Diary_{target_date}"
        if role:
            filename += f"_{role.value}"
        filename += ".pdf"

        return FileResponse(
            path=output_path,
            media_type="application/pdf",
            filename=filename,
            background=None  # 파일 전송 후 자동 삭제
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"PDF 생성 실패: {str(e)}"
        )


@router.get("/monthly/{year}/{month}")
async def generate_monthly_pdf(
    year: int,
    month: int,
    role: Optional[Role] = Query(None, description="역할 (학생/직장인/프리랜서)"),
    authorization: str = Header(..., description="Bearer {access_token}")
):
    """
    월간 콘텐츠 PDF 생성 및 다운로드

    - **year**: 연도 (YYYY)
    - **month**: 월 (1-12)
    - **role**: 역할 (student, office_worker, freelancer) - 선택사항

    **Response**: PDF 파일 (application/pdf)

    **사용 예시**:
    ```bash
    curl -H "Authorization: Bearer {token}" \\
         http://localhost:8000/api/pdf/monthly/2026/1?role=student \\
         --output diary_2026-01.pdf
    ```
    """
    # 1. 사용자 인증
    supabase = get_supabase_client()
    user = get_current_user(authorization, supabase)
    user_id = user["id"]

    try:
        # 2. 월간 콘텐츠 생성
        # TODO: monthly.py에서 _generate_monthly_content_internal 함수 구현 필요
        # 현재는 임시로 에러 반환
        raise HTTPException(
            status_code=501,
            detail="월간 PDF 생성 기능은 아직 구현되지 않았습니다 (Phase 3에서 MonthlyContent 정의 필요)"
        )

        # 향후 구현 예시:
        # monthly_content = _generate_monthly_content_internal(
        #     user_id=user_id,
        #     year=year,
        #     month=month,
        #     role=role,
        #     supabase=supabase
        # )
        #
        # with tempfile.NamedTemporaryFile(...) as tmp_file:
        #     output_path = tmp_file.name
        #
        # pdf_generator.generate_monthly_pdf(
        #     content=monthly_content.content.model_dump(),
        #     output_path=output_path,
        #     role=role.value if role else None
        # )
        #
        # filename = f"R3_Diary_{year}_{month:02d}"
        # if role:
        #     filename += f"_{role.value}"
        # filename += ".pdf"
        #
        # return FileResponse(
        #     path=output_path,
        #     media_type="application/pdf",
        #     filename=filename
        # )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"PDF 생성 실패: {str(e)}"
        )
