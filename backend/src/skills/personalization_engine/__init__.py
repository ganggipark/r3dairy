"""
Personalization Engine

CustomerProfile + target date -> personalized daily diary content.
Integrates rhythm analysis, role translation, and content generation.
"""

from .models import (
    ContentBlockType,
    ContentBlock,
    PersonalizedDailyContent,
    PersonalizationContext,
    ContentQualityReport,
    CustomerProfile,
    PersonalityProfile,
    InterestsProfile,
)
from .personalizer import PersonalizationEngine
from .profile_analyzer import ProfileAnalyzer
from .content_mapper import ContentMapper
from .content_generator import ContentBlockGenerator
from .rhythm_integrator import RhythmIntegrator

__all__ = [
    "ContentBlockType",
    "ContentBlock",
    "PersonalizedDailyContent",
    "PersonalizationContext",
    "ContentQualityReport",
    "CustomerProfile",
    "PersonalityProfile",
    "InterestsProfile",
    "PersonalizationEngine",
    "ProfileAnalyzer",
    "ContentMapper",
    "ContentBlockGenerator",
    "RhythmIntegrator",
]
