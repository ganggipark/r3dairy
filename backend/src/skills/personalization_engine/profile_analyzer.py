"""
Profile Analyzer

Analyze CustomerProfile to determine personalization strategy.
"""

from typing import List, Dict, Any
from .models import (
    CustomerProfile,
    PersonalityProfile,
    InterestsProfile,
    PersonalizationContext,
    Role,
    EnergyLevel,
)
from datetime import date


class ProfileAnalyzer:
    """Analyze customer profile for content personalization."""

    # ------------------------------------------------------------------
    # Dominant traits
    # ------------------------------------------------------------------

    @staticmethod
    def get_dominant_traits(personality: PersonalityProfile) -> List[str]:
        """Return top 2-3 dominant personality traits sorted by strength."""
        dimensions = {
            "extraverted": personality.extraversion,
            "introverted": 100 - personality.extraversion,
            "conscientious": personality.conscientiousness,
            "spontaneous": 100 - personality.conscientiousness,
            "open": personality.openness,
            "conventional": 100 - personality.openness,
            "agreeable": personality.agreeableness,
            "assertive": 100 - personality.agreeableness,
            "sensitive": personality.neuroticism,
            "resilient": 100 - personality.neuroticism,
            "analytical": personality.analytical_vs_intuitive,
            "intuitive": 100 - personality.analytical_vs_intuitive,
            "proactive": personality.proactive_vs_reactive,
            "reactive": 100 - personality.proactive_vs_reactive,
            "detail_oriented": personality.detail_vs_big_picture,
            "big_picture": 100 - personality.detail_vs_big_picture,
        }
        # Keep only traits with score >= 60 (above average)
        strong = {k: v for k, v in dimensions.items() if v >= 60}
        sorted_traits = sorted(strong.items(), key=lambda x: x[1], reverse=True)
        return [t[0] for t in sorted_traits[:3]] or ["balanced"]

    # ------------------------------------------------------------------
    # Role characteristics
    # ------------------------------------------------------------------

    ROLE_CHARS: Dict[str, Dict[str, Any]] = {
        "student": {
            "focus_areas": ["learning", "time_management", "concentration", "energy"],
            "key_topics": ["study", "exam", "growth", "friends", "schedule"],
            "stress_sources": ["exams", "peer_pressure", "future_uncertainty"],
            "language_style": "encouraging",
        },
        "office_worker": {
            "focus_areas": ["work_life_balance", "relationships", "decisions", "career"],
            "key_topics": ["meeting", "report", "collaboration", "promotion", "stress"],
            "stress_sources": ["deadlines", "office_politics", "burnout"],
            "language_style": "professional",
        },
        "freelancer": {
            "focus_areas": ["self_discipline", "creative_energy", "business", "autonomy"],
            "key_topics": ["project", "client", "creativity", "income", "networking"],
            "stress_sources": ["income_instability", "isolation", "overwork"],
            "language_style": "motivational",
        },
    }

    @classmethod
    def get_role_characteristics(cls, role: Role) -> Dict[str, Any]:
        return cls.ROLE_CHARS.get(role.value, cls.ROLE_CHARS["office_worker"])

    # ------------------------------------------------------------------
    # Content style
    # ------------------------------------------------------------------

    @staticmethod
    def determine_content_style(
        personality: PersonalityProfile,
        interests: InterestsProfile,
    ) -> Dict[str, str]:
        """Determine tone and depth preferences."""
        # Tone
        if personality.analytical_vs_intuitive >= 65:
            tone = "analytical"
        elif personality.extraversion >= 65 and personality.agreeableness >= 60:
            tone = "supportive"
        elif personality.conscientiousness >= 65 and personality.openness < 50:
            tone = "formal"
        elif personality.openness >= 65:
            tone = "casual"
        else:
            tone = "supportive"

        # Depth
        if personality.detail_vs_big_picture >= 65:
            depth = "detailed"
        elif personality.detail_vs_big_picture <= 35:
            depth = "brief"
        else:
            depth = "standard"

        return {"tone": tone, "depth": depth}

    # ------------------------------------------------------------------
    # Pain points
    # ------------------------------------------------------------------

    @staticmethod
    def identify_pain_points(
        personality: PersonalityProfile,
        role: Role,
    ) -> List[str]:
        """Identify likely challenges based on profile."""
        points: List[str] = []

        if personality.neuroticism >= 65:
            points.append("anxiety_management")
            points.append("stress_response")
        if personality.conscientiousness <= 40:
            points.append("procrastination")
            points.append("organization")
        if personality.openness <= 35 and role == Role.OFFICE_WORKER:
            points.append("resistance_to_change")
        if personality.extraversion <= 35:
            points.append("social_energy_drain")
        if personality.agreeableness <= 35:
            points.append("relationship_friction")
        if personality.proactive_vs_reactive <= 35:
            points.append("decision_paralysis")

        # Role-specific
        if role == Role.STUDENT:
            if personality.conscientiousness <= 50:
                points.append("study_discipline")
        elif role == Role.FREELANCER:
            if personality.conscientiousness <= 50:
                points.append("self_management")
            if personality.neuroticism >= 60:
                points.append("income_anxiety")

        return points or ["general_stress"]

    # ------------------------------------------------------------------
    # Seasonal context
    # ------------------------------------------------------------------

    @staticmethod
    def _get_seasonal_context(target_date: date) -> str:
        month = target_date.month
        if month in (3, 4, 5):
            return "spring"
        elif month in (6, 7, 8):
            return "summer"
        elif month in (9, 10, 11):
            return "autumn"
        return "winter"

    # ------------------------------------------------------------------
    # Main analysis
    # ------------------------------------------------------------------

    @classmethod
    def analyze_profile(
        cls,
        profile: CustomerProfile,
        target_date: date,
    ) -> PersonalizationContext:
        """Build PersonalizationContext from profile + date."""
        personality = profile.personality
        interests = profile.interests

        dominant = cls.get_dominant_traits(personality)
        style = cls.determine_content_style(personality, interests)
        pain_points = cls.identify_pain_points(personality, profile.primary_role)
        role_chars = cls.get_role_characteristics(profile.primary_role)

        # Derive energy level bucket from personality
        avg_energy = (personality.extraversion + personality.proactive_vs_reactive) / 2
        if avg_energy >= 65:
            energy = EnergyLevel.HIGH
        elif avg_energy <= 35:
            energy = EnergyLevel.LOW
        else:
            energy = EnergyLevel.MEDIUM

        all_interests = list(
            dict.fromkeys(interests.primary_interests + interests.secondary_interests)
        )

        traits_dict = {
            "extraversion": personality.extraversion / 100,
            "conscientiousness": personality.conscientiousness / 100,
            "openness": personality.openness / 100,
            "agreeableness": personality.agreeableness / 100,
            "neuroticism": personality.neuroticism / 100,
            "analytical": personality.analytical_vs_intuitive / 100,
            "proactive": personality.proactive_vs_reactive / 100,
            "detail": personality.detail_vs_big_picture / 100,
        }

        return PersonalizationContext(
            customer_profile=profile,
            target_date=target_date,
            role=profile.primary_role,
            dominant_traits=dominant,
            personality_traits=traits_dict,
            interests=all_interests,
            pain_points=pain_points,
            content_tone=style["tone"],
            content_depth=style["depth"],
            role_characteristics=role_chars,
            seasonal_context=cls._get_seasonal_context(target_date),
            energy_level=energy,
        )
