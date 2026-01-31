"""
PDF Customer API Endpoints

Task 5: Customer profile-based personalized PDF generation
Generates PDFs using PersonalizationEngine with CustomerProfile data
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from supabase import Client
from typing import Optional
import datetime
import tempfile
import sys
from pathlib import Path

# PDF Generator import
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "pdf-generator"))
from generator import PDFGenerator

# Backend imports
from src.db.supabase import get_supabase, get_customer_profile
from src.skills.personalization_engine.personalizer import PersonalizationEngine
from src.skills.personalization_engine.models import CustomerProfile
from src.content.char_optimizer import CharOptimizer
from src.api.auth import get_current_user

router = APIRouter(prefix="/api/pdf/customer", tags=["PDF Customer"])

# Instances
pdf_generator = PDFGenerator()
personalization_engine = PersonalizationEngine()


@router.get("/{user_id}/daily/{target_date}")
async def generate_customer_daily_pdf(
    user_id: str,
    target_date: datetime.date,
    supabase: Client = Depends(get_supabase)
):
    """
    Generate personalized daily PDF using CustomerProfile

    Args:
        user_id: Customer profile ID
        target_date: Target date (YYYY-MM-DD)

    Returns:
        PDF file (application/pdf)

    Usage:
        curl http://localhost:8000/api/pdf/customer/{user_id}/daily/2026-01-30 \
             --output diary_2026-01-30.pdf
    """
    try:
        # 1. Load CustomerProfile from Supabase
        profile_data = await get_customer_profile(user_id)

        if not profile_data:
            raise HTTPException(
                status_code=404,
                detail=f"Customer profile not found: {user_id}"
            )

        # 2. Convert to CustomerProfile model
        try:
            customer_profile = CustomerProfile(**profile_data)
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid profile data: {str(e)}"
            )

        # 3. Generate personalized content using PersonalizationEngine
        success, content, errors = personalization_engine.generate_daily_content(
            customer_profile=customer_profile,
            target_date=target_date
        )

        if not success or content is None:
            error_msg = ", ".join(errors) if errors else "Unknown generation error"
            raise HTTPException(
                status_code=500,
                detail=f"Content generation failed: {error_msg}"
            )

        # 4. Get schema output
        daily_content = content.schema_output

        # 5. Validate with CharOptimizer
        is_valid, total_chars, issues = CharOptimizer.validate_page(daily_content)

        if not is_valid:
            # Log issues but don't fail (allow PDF generation with warnings)
            print(f"[Warning] Content validation issues for {user_id} on {target_date}:")
            for issue in issues:
                print(f"  - {issue.get('message', issue)}")

        print(f"[PDF Generation] User: {user_id}, Date: {target_date}, "
              f"Total chars: {total_chars}, Valid: {is_valid}")

        # 6. Create temporary PDF file
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf",
            prefix=f"diary_{user_id}_{target_date}_"
        ) as tmp_file:
            output_path = tmp_file.name

        # 7. Generate PDF using WeasyPrint template
        pdf_generator.generate_daily_pdf(
            content=daily_content,
            output_path=output_path,
            role=customer_profile.primary_role.value
        )

        # 8. Return PDF file response
        filename = f"R3_Diary_{customer_profile.name}_{target_date}.pdf"

        return FileResponse(
            path=output_path,
            media_type="application/pdf",
            filename=filename,
            background=None  # Auto-delete after sending
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"PDF generation failed: {str(e)}"
        )


@router.get("/{user_id}/monthly/{year}/{month}")
async def generate_customer_monthly_pdf(
    user_id: str,
    year: int,
    month: int,
    supabase: Client = Depends(get_supabase)
):
    """
    Generate personalized monthly PDF using CustomerProfile

    Args:
        user_id: Customer profile ID
        year: Year (YYYY)
        month: Month (1-12)

    Returns:
        PDF file (application/pdf)

    Usage:
        curl http://localhost:8000/api/pdf/customer/{user_id}/monthly/2026/1 \
             --output diary_2026-01.pdf
    """
    try:
        # 1. Validate year/month
        if year < 2000 or year > 2100:
            raise HTTPException(
                status_code=400,
                detail="Year must be between 2000-2100"
            )
        if month < 1 or month > 12:
            raise HTTPException(
                status_code=400,
                detail="Month must be between 1-12"
            )

        # 2. Load CustomerProfile
        profile_data = await get_customer_profile(user_id)

        if not profile_data:
            raise HTTPException(
                status_code=404,
                detail=f"Customer profile not found: {user_id}"
            )

        try:
            customer_profile = CustomerProfile(**profile_data)
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid profile data: {str(e)}"
            )

        # 3. Generate content for all days in month
        from calendar import monthrange
        from datetime import date, timedelta

        days_in_month = monthrange(year, month)[1]
        start_date = date(year, month, 1)
        end_date = date(year, month, days_in_month)

        daily_contents = []
        for day in range(1, days_in_month + 1):
            target_date = date(year, month, day)

            success, content, errors = personalization_engine.generate_daily_content(
                customer_profile=customer_profile,
                target_date=target_date
            )

            if success and content:
                daily_contents.append(content.schema_output)
            else:
                # Use placeholder if generation fails
                print(f"[Warning] Failed to generate content for {target_date}: {errors}")
                daily_contents.append({
                    "date": target_date.strftime("%Y-%m-%d"),
                    "summary": "콘텐츠 생성 실패",
                })

        # 4. Build monthly content structure
        monthly_content = {
            "year": year,
            "month": month,
            "daily_pages": daily_contents,
        }

        # 5. Create temporary PDF file
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf",
            prefix=f"diary_{user_id}_{year}_{month:02d}_"
        ) as tmp_file:
            output_path = tmp_file.name

        # 6. Generate PDF
        pdf_generator.generate_monthly_pdf(
            year=year,
            month=month,
            content=monthly_content,
            output_path=output_path,
            role=customer_profile.primary_role.value
        )

        # 7. Return PDF file response
        filename = f"R3_Diary_{customer_profile.name}_{year}_{month:02d}.pdf"

        return FileResponse(
            path=output_path,
            media_type="application/pdf",
            filename=filename,
            background=None
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Monthly PDF generation failed: {str(e)}"
        )
