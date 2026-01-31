"""
Profile Data Models

Pydantic models for customer profiles including personality, interests,
and preferences. All models use strict validation.
"""

from enum import Enum
from typing import Optional, Dict, List
from datetime import date, datetime
from pydantic import BaseModel, Field, field_validator
import re


class Role(str, Enum):
    STUDENT = "student"
    OFFICE_WORKER = "office_worker"
    FREELANCER = "freelancer"
    PARENT = "parent"
    OTHER = "other"


class SubscriptionType(str, Enum):
    APP_ONLY = "app_only"
    HYBRID = "hybrid"
    PAPER_ONLY = "paper_only"


class PaperSize(str, Enum):
    A5 = "a5"
    A4 = "a4"
    CUSTOM = "custom"


class PersonalityProfile(BaseModel):
    """Standardized personality profile from survey responses."""

    # Big Five dimensions (0-100 scale)
    extraversion: float = Field(ge=0, le=100)
    conscientiousness: float = Field(ge=0, le=100)
    openness: float = Field(ge=0, le=100)
    agreeableness: float = Field(ge=0, le=100)
    neuroticism: float = Field(ge=0, le=100)

    # Additional traits
    analytical_vs_intuitive: float = Field(ge=0, le=100)
    proactive_vs_reactive: float = Field(ge=0, le=100)
    detail_vs_big_picture: float = Field(ge=0, le=100)

    # Derived classifications
    dominant_trait: str
    secondary_traits: List[str]
    personality_type: str

    # Raw survey responses
    raw_scores: Dict[str, float]


class InterestsProfile(BaseModel):
    """User interests and focus areas."""

    primary_interests: List[str] = Field(max_length=5)
    all_interests: List[str]
    interest_categories: Dict[str, List[str]]

    # Derived attributes
    is_growth_focused: bool = False
    is_career_focused: bool = False
    is_lifestyle_focused: bool = False
    is_creative_focused: bool = False


class PreferencesProfile(BaseModel):
    """User preferences for diary format and communication."""

    subscription_type: SubscriptionType

    # Paper options
    paper_size: Optional[PaperSize] = None
    delivery_frequency: Optional[str] = None
    delivery_address: Optional[str] = None

    # Communication
    email_frequency: str = "weekly"
    consent_privacy: bool = True
    consent_marketing: bool = False
    consent_research: bool = False

    # Tone (derived from personality)
    preferred_tone: str = "supportive"
    content_depth: str = "standard"

    @field_validator("email_frequency")
    @classmethod
    def validate_email_frequency(cls, v: str) -> str:
        allowed = {"daily", "weekly", "monthly", "none"}
        if v not in allowed:
            raise ValueError(f"email_frequency must be one of {allowed}")
        return v

    @field_validator("delivery_frequency")
    @classmethod
    def validate_delivery_frequency(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            allowed = {"monthly", "quarterly", "annually"}
            if v not in allowed:
                raise ValueError(f"delivery_frequency must be one of {allowed}")
        return v


class CustomerProfile(BaseModel):
    """Complete customer profile."""

    id: str

    # Basic information
    name: str
    email: str
    birth_date: date
    gender: str

    # Derived basic info
    age: int = 0
    zodiac_sign: str = ""
    korean_zodiac: str = ""

    # Role and segmentation
    primary_role: Role
    secondary_roles: List[Role] = []

    # Profiles
    personality: PersonalityProfile
    interests: InterestsProfile
    preferences: PreferencesProfile

    # Metadata
    survey_completed_at: str = ""
    profile_created_at: str = ""
    profile_version: str = "1.0"

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(pattern, v):
            raise ValueError("Invalid email format")
        return v.lower()

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Name cannot be empty")
        if len(v) > 255:
            raise ValueError("Name too long (max 255 characters)")
        return v
