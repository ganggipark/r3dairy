"""
Profile Validator

Validates profile data integrity, completeness, and detects anomalies.
"""

from datetime import date
from typing import List, Tuple

from .models import (
    CustomerProfile,
    PersonalityProfile,
    InterestsProfile,
    PreferencesProfile,
    SubscriptionType,
    Role,
)


class ProfileValidator:
    """Validate profile data integrity and completeness."""

    @staticmethod
    def validate_basic_info(
        name: str, email: str, birth_date: date
    ) -> Tuple[bool, List[str]]:
        """
        Validate basic info fields.
        Returns (is_valid, list_of_errors).
        """
        errors: List[str] = []

        if not name or not name.strip():
            errors.append("Name is required")
        elif len(name) > 255:
            errors.append("Name too long (max 255 characters)")

        if not email:
            errors.append("Email is required")

        today = date.today()
        age = today.year - birth_date.year
        if (today.month, today.day) < (birth_date.month, birth_date.day):
            age -= 1

        if age < 13:
            errors.append("User must be at least 13 years old")
        if age > 120:
            errors.append("Birth date seems unreasonable (age > 120)")
        if birth_date > today:
            errors.append("Birth date cannot be in the future")

        return (len(errors) == 0, errors)

    @staticmethod
    def validate_personality_profile(
        profile: PersonalityProfile,
    ) -> Tuple[bool, List[str]]:
        """Validate all personality dimensions are within range."""
        errors: List[str] = []
        dimensions = [
            ("extraversion", profile.extraversion),
            ("conscientiousness", profile.conscientiousness),
            ("openness", profile.openness),
            ("agreeableness", profile.agreeableness),
            ("neuroticism", profile.neuroticism),
            ("analytical_vs_intuitive", profile.analytical_vs_intuitive),
            ("proactive_vs_reactive", profile.proactive_vs_reactive),
            ("detail_vs_big_picture", profile.detail_vs_big_picture),
        ]
        for name, val in dimensions:
            if not (0 <= val <= 100):
                errors.append(f"{name} must be between 0 and 100, got {val}")

        if not profile.dominant_trait:
            errors.append("dominant_trait is required")
        if not profile.personality_type or len(profile.personality_type) != 4:
            errors.append("personality_type must be 4 characters (e.g., ENFP)")

        return (len(errors) == 0, errors)

    @staticmethod
    def validate_interests_profile(
        profile: InterestsProfile,
    ) -> Tuple[bool, List[str]]:
        """Validate interests are non-empty and within limits."""
        errors: List[str] = []

        if not profile.all_interests:
            errors.append("At least one interest is required")
        if len(profile.primary_interests) > 5:
            errors.append("Maximum 5 primary interests allowed")

        return (len(errors) == 0, errors)

    @staticmethod
    def validate_preferences_profile(
        profile: PreferencesProfile,
    ) -> Tuple[bool, List[str]]:
        """Validate preferences, including paper delivery requirements."""
        errors: List[str] = []

        if not profile.consent_privacy:
            errors.append("Privacy consent is required")

        needs_paper = profile.subscription_type in (
            SubscriptionType.HYBRID,
            SubscriptionType.PAPER_ONLY,
        )
        if needs_paper and not profile.paper_size:
            errors.append("Paper size required for paper/hybrid subscription")
        if needs_paper and not profile.delivery_frequency:
            errors.append("Delivery frequency required for paper/hybrid subscription")

        return (len(errors) == 0, errors)

    @classmethod
    def validate_customer_profile(
        cls, profile: CustomerProfile
    ) -> Tuple[bool, List[str]]:
        """Validate entire customer profile."""
        all_errors: List[str] = []

        ok, errs = cls.validate_basic_info(
            profile.name, profile.email, profile.birth_date
        )
        all_errors.extend(errs)

        ok, errs = cls.validate_personality_profile(profile.personality)
        all_errors.extend(errs)

        ok, errs = cls.validate_interests_profile(profile.interests)
        all_errors.extend(errs)

        ok, errs = cls.validate_preferences_profile(profile.preferences)
        all_errors.extend(errs)

        return (len(all_errors) == 0, all_errors)

    @staticmethod
    def detect_anomalies(profile: CustomerProfile) -> List[str]:
        """Detect unusual patterns (advisory warnings, not errors)."""
        warnings: List[str] = []

        if profile.age < 18 and profile.primary_role == Role.OFFICE_WORKER:
            warnings.append("User under 18 selected office worker role")
        if profile.age > 65 and profile.primary_role == Role.STUDENT:
            warnings.append("User over 65 selected student role")

        p = profile.personality
        if p.extraversion > 90 and p.neuroticism > 90:
            warnings.append("Unusual combination: very high extraversion and neuroticism")

        all_extreme = all(
            v >= 90
            for v in [
                p.extraversion, p.conscientiousness, p.openness,
                p.agreeableness,
            ]
        )
        if all_extreme:
            warnings.append("All personality scores very high - possible response bias")

        return warnings
