"""
Personalization Engine - Data Models

CustomerProfile, PersonalizationContext, ContentBlock, quality metrics.
"""

from enum import Enum
from typing import Optional, Dict, List, Any
from datetime import date, datetime
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class Role(str, Enum):
    STUDENT = "student"
    OFFICE_WORKER = "office_worker"
    FREELANCER = "freelancer"


class ContentBlockType(str, Enum):
    SUMMARY = "summary"
    KEYWORDS = "keywords"
    RHYTHM_DESCRIPTION = "rhythm_description"
    FOCUS_CAUTION = "focus_caution"
    ACTION_GUIDE = "action_guide"
    TIME_DIRECTION = "time_direction"
    STATE_TRIGGER = "state_trigger"
    MEANING_SHIFT = "meaning_shift"
    RHYTHM_QUESTION = "rhythm_question"


class EnergyLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# ---------------------------------------------------------------------------
# Profile models
# ---------------------------------------------------------------------------

class PersonalityProfile(BaseModel):
    """8-dimension personality profile (0-100 scales)."""
    extraversion: int = Field(50, ge=0, le=100)
    conscientiousness: int = Field(50, ge=0, le=100)
    openness: int = Field(50, ge=0, le=100)
    agreeableness: int = Field(50, ge=0, le=100)
    neuroticism: int = Field(50, ge=0, le=100)
    analytical_vs_intuitive: int = Field(50, ge=0, le=100, description="0=intuitive, 100=analytical")
    proactive_vs_reactive: int = Field(50, ge=0, le=100, description="0=reactive, 100=proactive")
    detail_vs_big_picture: int = Field(50, ge=0, le=100, description="0=big_picture, 100=detail")


class InterestsProfile(BaseModel):
    """User interests."""
    primary_interests: List[str] = Field(default_factory=list)
    secondary_interests: List[str] = Field(default_factory=list)


class CustomerProfile(BaseModel):
    """Complete customer profile for personalization."""
    id: str = ""
    name: str = ""
    birth_date: date = Field(default_factory=lambda: date(1990, 1, 1))
    birth_time: Optional[str] = None
    gender: str = "other"
    birth_place: str = ""
    primary_role: Role = Role.OFFICE_WORKER
    personality: PersonalityProfile = Field(default_factory=PersonalityProfile)
    interests: InterestsProfile = Field(default_factory=InterestsProfile)
    activity_preferences: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Activity preferences by category (e.g., {'study': ['시험 준비'], 'exercise': ['러닝']})"
    )


# ---------------------------------------------------------------------------
# Content models
# ---------------------------------------------------------------------------

class ContentBlock(BaseModel):
    """Single content block."""
    id: str
    type: ContentBlockType
    title: str
    content: Any  # str or list or dict depending on type
    tags: List[str] = Field(default_factory=list)
    personalization_level: float = Field(0.7, ge=0.0, le=1.0)

    class Config:
        use_enum_values = True


class PersonalizedDailyContent(BaseModel):
    """Complete personalized daily diary content."""
    id: str
    customer_id: str
    target_date: date
    generated_at: datetime = Field(default_factory=datetime.now)

    # Core content
    blocks: List[ContentBlock] = Field(default_factory=list)
    total_chars: int = 0

    # Metadata
    role: str = ""
    personality_primary: str = ""
    mood_suggestion: str = ""
    energy_level: str = "medium"
    focus_areas: List[str] = Field(default_factory=list)

    # Rhythm data (internal, not exposed to user)
    rhythm_signals: Dict[str, Any] = Field(default_factory=dict)

    # Quality metrics
    personalization_score: float = 0.0
    uniqueness_score: float = 0.0
    relevance_score: float = 0.0

    # Schema-compatible output (matches existing DailyContent structure)
    schema_output: Dict[str, Any] = Field(default_factory=dict)


class PersonalizationContext(BaseModel):
    """All decisions needed for content generation."""
    customer_profile: CustomerProfile
    target_date: date
    role: Role
    dominant_traits: List[str] = Field(default_factory=list)
    personality_traits: Dict[str, float] = Field(default_factory=dict)
    interests: List[str] = Field(default_factory=list)
    pain_points: List[str] = Field(default_factory=list)
    content_tone: str = "supportive"
    content_depth: str = "standard"
    role_characteristics: Dict[str, Any] = Field(default_factory=dict)
    seasonal_context: str = ""
    energy_level: EnergyLevel = EnergyLevel.MEDIUM


class ContentQualityReport(BaseModel):
    """Quality assessment of generated content."""
    char_count: int = 0
    char_count_valid: bool = False
    block_count: int = 0
    block_count_valid: bool = False
    personalization_level: float = 0.0
    personalization_valid: bool = False
    content_depth: str = "standard"
    tone_matches_profile: bool = True
    no_internal_terminology: bool = True
    issues: List[str] = Field(default_factory=list)
    passed_validation: bool = False
