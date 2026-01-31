"""
PDF API Endpoints
일간/월간 콘텐츠 PDF 생성 API
"""
from fastapi import APIRouter, Header, Query, HTTPException, Depends
from fastapi.responses import FileResponse
from supabase import Client
from typing import Optional
import datetime
import os
import sys
from pathlib import Path
import tempfile

# PDF Generator import
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "pdf-generator"))
from generator import PDFGenerator

# Backend imports
from src.api.auth import get_current_user
from src.db.supabase import get_supabase, SupabaseClient
from src.rhythm.models import BirthInfo, Gender
from src.rhythm.saju import calculate_saju, analyze_daily_fortune, analyze_monthly_rhythm
from src.content.assembly import assemble_daily_content, assemble_monthly_content
from src.translation import translate_daily_content, Role

router = APIRouter(prefix="/api/pdf", tags=["PDF"])

# PDF Generator 인스턴스
pdf_generator = PDFGenerator()


def _get_profile_data(user_id: str, supabase: Client) -> dict:
    """프로필 데이터 조회 (내부 헬퍼)"""
    result = supabase.table("profiles").select("*").eq("id", user_id).execute()

    if not result.data:
        raise HTTPException(
            status_code=404,
            detail="프로필이 존재하지 않습니다."
        )

    return result.data[0]


@router.get("/daily/{target_date}")
async def generate_daily_pdf(
    target_date: datetime.date,
    role: Optional[Role] = Query(None, description="역할 (학생/직장인/프리랜서)"),
    use_markdown: bool = Query(False, description="Markdown 파일 사용 여부"),
    authorization: str = Header(...),
    supabase: Client = Depends(get_supabase)
):
    """
    일간 콘텐츠 PDF 생성 및 다운로드

    - **target_date**: 조회할 날짜 (YYYY-MM-DD)
    - **role**: 역할 (student, office_worker, freelancer) - 선택사항
    - **use_markdown**: True로 설정 시 backend/daily/{date}_new_format.md 파일 사용

    **Response**: PDF 파일 (application/pdf)

    **사용 예시**:
    ```bash
    # 기본 (DB에서 생성)
    curl -H "Authorization: Bearer {token}" \\
         http://localhost:8000/api/pdf/daily/2026-01-20?role=student \\
         --output diary_2026-01-20.pdf

    # Markdown 파일 사용
    curl -H "Authorization: Bearer {token}" \\
         http://localhost:8000/api/pdf/daily/2026-01-31?use_markdown=true \\
         --output diary_2026-01-31.pdf
    ```
    """
    # 1. 사용자 인증
    user = get_current_user(authorization, supabase)
    user_id = user.id

    token = authorization.split(" ")[1]
    supabase_db = SupabaseClient.create_user_db_client(token)

    try:
        # 2. Markdown 파일 사용 또는 기존 생성 로직
        if use_markdown:
            # Load from Markdown file
            md_file_path = Path(__file__).parent.parent.parent / "daily" / f"{target_date}_new_format.md"

            if not md_file_path.exists():
                raise HTTPException(
                    status_code=404,
                    detail=f"Markdown 파일을 찾을 수 없습니다: {md_file_path}"
                )

            with open(md_file_path, 'r', encoding='utf-8') as f:
                md_content = f.read()

            # 7. 임시 PDF 파일 생성
            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".pdf",
                prefix=f"diary_{target_date}_"
            ) as tmp_file:
                output_path = tmp_file.name

            # 8. PDF 생성 (Markdown mode)
            pdf_generator.generate_daily_pdf(
                content=md_content,
                output_path=output_path,
                role=role.value if role else None,
                is_markdown=True
            )

        else:
            # Existing logic: Generate from DB
            # 2. 프로필 조회
            profile = _get_profile_data(user_id, supabase_db)

            # 3. BirthInfo 생성
            birth_info = BirthInfo(
                name=profile["name"],
                birth_date=datetime.date.fromisoformat(profile["birth_date"]),
                birth_time=datetime.time.fromisoformat(profile["birth_time"]),
                gender=Gender(profile["gender"]),
                birth_place=profile["birth_place"]
            )

            # 4. 사주 계산 및 리듬 분석
            saju_result = calculate_saju(birth_info, target_date)
            daily_rhythm = analyze_daily_fortune(birth_info, target_date, saju_result)

            # 5. 콘텐츠 생성
            daily_content = assemble_daily_content(target_date, saju_result, daily_rhythm)

            # 6. 역할별 변환
            if role:
                daily_content = translate_daily_content(daily_content, role.value)

            # 7. 임시 PDF 파일 생성
            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".pdf",
                prefix=f"diary_{target_date}_"
            ) as tmp_file:
                output_path = tmp_file.name

            # 8. PDF 생성
            pdf_generator.generate_daily_pdf(
                content=daily_content,
                output_path=output_path,
                role=role.value if role else None,
                is_markdown=False
            )

        # 9. 파일 다운로드 응답
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

    except HTTPException:
        raise
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
    authorization: str = Header(...),
    supabase: Client = Depends(get_supabase)
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
    user = get_current_user(authorization, supabase)
    user_id = user.id

    try:
        # 2. 연도/월 검증
        if year < 2000 or year > 2100:
            raise HTTPException(
                status_code=400,
                detail="연도는 2000-2100 범위여야 합니다."
            )
        if month < 1 or month > 12:
            raise HTTPException(
                status_code=400,
                detail="월은 1-12 범위여야 합니다."
            )

        # 3. 프로필 조회
        profile = _get_profile_data(user_id, supabase_db)

        # 4. BirthInfo 생성
        birth_info = BirthInfo(
            name=profile["name"],
            birth_date=datetime.date.fromisoformat(profile["birth_date"]),
            birth_time=datetime.time.fromisoformat(profile["birth_time"]),
            gender=Gender(profile["gender"]),
            birth_place=profile["birth_place"]
        )

        # 5. 사주 계산 및 월간 리듬 분석
        target_date = datetime.date(year, month, 1)
        saju_result = calculate_saju(birth_info, target_date)
        monthly_rhythm = analyze_monthly_rhythm(birth_info, year, month, saju_result)

        # 6. 월간 콘텐츠 생성
        monthly_content = assemble_monthly_content(year, month, monthly_rhythm)

        # 7. 역할별 변환 (월간은 Phase 4에서 TODO)
        # TODO: Phase 4에서 월간 번역 추가 필요
        # if role:
        #     monthly_content = translate_monthly_content(monthly_content, role.value)

        # 8. 임시 PDF 파일 생성
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf",
            prefix=f"diary_{year}_{month:02d}_"
        ) as tmp_file:
            output_path = tmp_file.name

        # 9. PDF 생성
        pdf_generator.generate_monthly_pdf(
            year=year,
            month=month,
            content=monthly_content,
            output_path=output_path,
            role=role.value if role else None
        )

        # 10. 파일 다운로드 응답
        filename = f"R3_Diary_{year}_{month:02d}"
        if role:
            filename += f"_{role.value}"
        filename += ".pdf"

        return FileResponse(
            path=output_path,
            media_type="application/pdf",
            filename=filename,
            background=None  # 파일 전송 후 자동 삭제
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"PDF 생성 실패: {str(e)}"
        )
