"""
Profile Enricher

Calculates derived attributes: age, zodiac signs, preferred tone,
content depth, and interest focus areas.
"""

from datetime import date
from typing import Dict

from .models import (
    Role,
    PersonalityProfile,
    InterestsProfile,
    CustomerProfile,
)

# Western zodiac date ranges (month, day) pairs for start of each sign
_ZODIAC_RANGES = [
    ((1, 20), "Aquarius"),
    ((2, 19), "Pisces"),
    ((3, 21), "Aries"),
    ((4, 20), "Taurus"),
    ((5, 21), "Gemini"),
    ((6, 21), "Cancer"),
    ((7, 23), "Leo"),
    ((8, 23), "Virgo"),
    ((9, 23), "Libra"),
    ((10, 23), "Scorpio"),
    ((11, 22), "Sagittarius"),
    ((12, 22), "Capricorn"),
]

# Korean zodiac animals (12-year cycle, starting from Rat at year % 12 == 4)
_KOREAN_ZODIAC = [
    "Rat", "Ox", "Tiger", "Rabbit", "Dragon", "Snake",
    "Horse", "Goat", "Monkey", "Rooster", "Dog", "Pig",
]


class ProfileEnricher:
    """Enrich profile with calculated and derived attributes."""

    @staticmethod
    def calculate_age(birth_date: date, reference: date | None = None) -> int:
        """Calculate age from birth date."""
        today = reference or date.today()
        age = today.year - birth_date.year
        if (today.month, today.day) < (birth_date.month, birth_date.day):
            age -= 1
        return max(0, age)

    @staticmethod
    def get_zodiac_sign(birth_date: date) -> str:
        """Get Western zodiac sign."""
        md = (birth_date.month, birth_date.day)
        for (start_month, start_day), sign in _ZODIAC_RANGES:
            if md < (start_month, start_day):
                # Return previous sign
                idx = _ZODIAC_RANGES.index(((start_month, start_day), sign))
                return _ZODIAC_RANGES[idx - 1][1]
        return "Capricorn"  # Dec 22 - Jan 19

    @staticmethod
    def get_korean_zodiac(birth_date: date) -> str:
        """Get Korean zodiac animal based on birth year."""
        # Year 2000 = Dragon (index 4 in cycle)
        # General formula: (year - 4) % 12
        idx = (birth_date.year - 4) % 12
        return _KOREAN_ZODIAC[idx]

    @staticmethod
    def derive_tone_preference(personality: PersonalityProfile) -> str:
        """
        Determine preferred communication tone based on personality.

        Rules:
        - High openness + high agreeableness -> "supportive"
        - High conscientiousness + low openness -> "formal"
        - High extraversion + high openness -> "casual"
        - High analytical -> "analytical"
        - Default -> "supportive"
        """
        if personality.analytical_vs_intuitive >= 70:
            return "analytical"
        if personality.conscientiousness >= 65 and personality.openness < 50:
            return "formal"
        if personality.extraversion >= 65 and personality.openness >= 65:
            return "casual"
        if personality.openness >= 55 and personality.agreeableness >= 55:
            return "supportive"
        return "supportive"

    @staticmethod
    def derive_content_depth(personality: PersonalityProfile, role: Role) -> str:
        """
        Determine content depth preference.

        Rules:
        - Student + high conscientiousness -> "detailed"
        - Office worker + low conscientiousness -> "brief"
        - High openness + high conscientiousness -> "detailed"
        - Default -> "standard"
        """
        if role == Role.STUDENT and personality.conscientiousness >= 60:
            return "detailed"
        if role == Role.OFFICE_WORKER and personality.conscientiousness < 40:
            return "brief"
        if personality.openness >= 70 and personality.conscientiousness >= 70:
            return "detailed"
        if personality.conscientiousness < 35:
            return "brief"
        return "standard"

    @classmethod
    def enrich_profile(cls, profile: CustomerProfile) -> CustomerProfile:
        """
        Enrich profile with all calculated attributes.
        Returns a new CustomerProfile with enriched fields.
        """
        profile.age = cls.calculate_age(profile.birth_date)
        profile.zodiac_sign = cls.get_zodiac_sign(profile.birth_date)
        profile.korean_zodiac = cls.get_korean_zodiac(profile.birth_date)
        profile.preferences.preferred_tone = cls.derive_tone_preference(
            profile.personality
        )
        profile.preferences.content_depth = cls.derive_content_depth(
            profile.personality, profile.primary_role
        )
        return profile
