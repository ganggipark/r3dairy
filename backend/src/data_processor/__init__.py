"""
Data Processor Module - Survey response normalization and profile generation.

Converts raw survey responses into structured CustomerProfile objects,
enriches with derived attributes, validates, and persists to database.
"""

from .models import (
    Role,
    SubscriptionType,
    PaperSize,
    PersonalityProfile,
    InterestsProfile,
    PreferencesProfile,
    CustomerProfile,
)
from .normalizer import SurveyResponseNormalizer
from .enricher import ProfileEnricher
from .validator import ProfileValidator
from .processor import DataProcessor

__all__ = [
    "Role",
    "SubscriptionType",
    "PaperSize",
    "PersonalityProfile",
    "InterestsProfile",
    "PreferencesProfile",
    "CustomerProfile",
    "SurveyResponseNormalizer",
    "ProfileEnricher",
    "ProfileValidator",
    "DataProcessor",
]
