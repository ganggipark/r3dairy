"""
Content Assembly Engine

리듬 신호를 사용자 노출 콘텐츠로 변환하는 엔진입니다.

주요 컴포넌트:
- validator.py: DAILY_CONTENT_SCHEMA.json 검증
- assembly.py: 리듬 신호 → 콘텐츠 블록 변환
- models.py: 콘텐츠 데이터 모델 (Pydantic)
"""

from .models import (
    FocusCaution,
    ActionGuide,
    TimeDirection,
    StateTrigger,
    LengthRequirements,
    DailyContent,
    MonthlyContent,
    YearlyContent,
    # 새로운 10개 라이프스타일 카테고리 모델들
    DailyHealthSports,
    DailyMealNutrition,
    DailyFashionBeauty,
    DailyShoppingFinance,
    DailyLivingSpace,
    DailyRoutines,
    DigitalCommunication,
    HobbiesCreativity,
    RelationshipsSocial,
    SeasonalEnvironment,
)
from .validator import validate_daily_content
from .assembly import assemble_daily_content, assemble_monthly_content, assemble_yearly_content

__all__ = [
    # 기존 모델들
    "FocusCaution",
    "ActionGuide", 
    "TimeDirection",
    "StateTrigger",
    "LengthRequirements",
    "DailyContent",
    "MonthlyContent",
    "YearlyContent",
    # 새로운 10개 라이프스타일 카테고리 모델들
    "DailyHealthSports",
    "DailyMealNutrition",
    "DailyFashionBeauty",
    "DailyShoppingFinance",
    "DailyLivingSpace",
    "DailyRoutines",
    "DigitalCommunication",
    "HobbiesCreativity",
    "RelationshipsSocial",
    "SeasonalEnvironment",
    # 함수들
    "validate_daily_content",
    "assemble_daily_content",
    "assemble_monthly_content",
    "assemble_yearly_content",
]
