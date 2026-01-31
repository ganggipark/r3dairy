"""
Survey Response Normalizer

Converts raw survey responses into standardized profile objects.
Handles Korean/English input, various formats, and edge cases.
"""

from typing import Dict, List, Optional
from datetime import date, datetime
import uuid

from .models import (
    Role,
    SubscriptionType,
    PaperSize,
    PersonalityProfile,
    InterestsProfile,
    PreferencesProfile,
    CustomerProfile,
)

# Role mapping (Korean + English variants)
ROLE_MAP: Dict[str, Role] = {
    "student": Role.STUDENT,
    "학생": Role.STUDENT,
    "office_worker": Role.OFFICE_WORKER,
    "office worker": Role.OFFICE_WORKER,
    "직장인": Role.OFFICE_WORKER,
    "회사원": Role.OFFICE_WORKER,
    "freelancer": Role.FREELANCER,
    "프리랜서": Role.FREELANCER,
    "자영업": Role.FREELANCER,
    "자영업자": Role.FREELANCER,
    "parent": Role.PARENT,
    "부모": Role.PARENT,
    "주부": Role.PARENT,
    "other": Role.OTHER,
    "기타": Role.OTHER,
}

# Interest categories
INTEREST_CATEGORIES: Dict[str, List[str]] = {
    "growth": [
        "personal_growth", "자기개발", "education", "교육/학습", "학습",
        "self_improvement", "목표설정",
    ],
    "career": [
        "career", "커리어", "커리어/일자리", "직업", "업무", "비즈니스",
        "networking", "리더십",
    ],
    "lifestyle": [
        "health", "건강", "건강/피트니스", "fitness", "여행", "travel",
        "음식", "food", "wellness",
    ],
    "creative": [
        "hobby", "취미", "취미/창작", "creative", "창작", "음악",
        "art", "예술", "디자인", "writing", "글쓰기",
    ],
    "social": [
        "relationships", "인간관계", "소통", "가족", "family", "사회활동",
    ],
    "finance": [
        "finance", "재테크", "투자", "저축", "경제",
    ],
}

# Flatten for lookup
_INTEREST_TO_CATEGORY: Dict[str, str] = {}
for cat, items in INTEREST_CATEGORIES.items():
    for item in items:
        _INTEREST_TO_CATEGORY[item.lower()] = cat


# Personality dimension labels
DIMENSION_LABELS = [
    "extraversion",
    "conscientiousness",
    "openness",
    "agreeableness",
    "neuroticism",
    "detail_vs_big_picture",
    "proactive_vs_reactive",
    "analytical_vs_intuitive",
]

# MBTI-like mapping thresholds
MBTI_THRESHOLD = 50.0


class SurveyResponseNormalizer:
    """Normalize survey responses to standard format."""

    @staticmethod
    def normalize_role(role_raw: str) -> Role:
        """Map raw role input to standard enum."""
        key = role_raw.strip().lower()
        return ROLE_MAP.get(key, Role.OTHER)

    @staticmethod
    def normalize_interests(interests_raw: List[str]) -> Dict:
        """
        Normalize interests list into InterestsProfile-compatible dict.
        Maps to standard categories, identifies primary interests.
        """
        all_interests = [i.strip() for i in interests_raw if i.strip()]

        # Categorize
        categories: Dict[str, List[str]] = {}
        for interest in all_interests:
            cat = _INTEREST_TO_CATEGORY.get(interest.lower(), "other")
            categories.setdefault(cat, []).append(interest)

        primary = all_interests[:5]

        # Derive focus booleans
        all_lower = {i.lower() for i in all_interests}
        growth_keywords = {"personal_growth", "자기개발", "education", "교육/학습", "학습"}
        career_keywords = {"career", "커리어", "커리어/일자리", "직업", "업무"}
        lifestyle_keywords = {"health", "건강", "건강/피트니스", "fitness", "여행", "travel"}
        creative_keywords = {"hobby", "취미", "취미/창작", "creative", "창작"}

        return {
            "primary_interests": primary,
            "all_interests": all_interests,
            "interest_categories": categories,
            "is_growth_focused": bool(all_lower & growth_keywords),
            "is_career_focused": bool(all_lower & career_keywords),
            "is_lifestyle_focused": bool(all_lower & lifestyle_keywords),
            "is_creative_focused": bool(all_lower & creative_keywords),
        }

    @staticmethod
    def normalize_personality(likert_responses: List[int]) -> Dict:
        """
        Convert 8 Likert scale responses (1-5) to personality profile.

        Question mapping:
          Q1 -> extraversion
          Q2 -> conscientiousness
          Q3 -> openness
          Q4 -> agreeableness
          Q5 -> neuroticism (reversed: high score = low neuroticism)
          Q6 -> detail_vs_big_picture
          Q7 -> proactive_vs_reactive
          Q8 -> analytical_vs_intuitive
        """
        if len(likert_responses) < 8:
            # Pad with neutral (3)
            likert_responses = list(likert_responses) + [3] * (8 - len(likert_responses))

        # Convert 1-5 to 0-100
        def to_100(val: int) -> float:
            return round(max(0, min(100, (val - 1) * 25.0)), 1)

        scores = [to_100(v) for v in likert_responses[:8]]

        # Reverse neuroticism (Q5): high Likert = low neuroticism
        scores[4] = round(100.0 - scores[4], 1)

        raw_scores = {DIMENSION_LABELS[i]: scores[i] for i in range(8)}

        # Determine dominant/secondary traits
        trait_scores = {
            "extraversion": scores[0],
            "conscientiousness": scores[1],
            "openness": scores[2],
            "agreeableness": scores[3],
            "emotional_stability": 100.0 - scores[4],  # invert neuroticism
            "analytical": scores[7],
            "proactive": scores[6],
            "detail_oriented": scores[5],
        }
        sorted_traits = sorted(trait_scores.items(), key=lambda x: x[1], reverse=True)
        dominant = sorted_traits[0][0]
        secondary = [t[0] for t in sorted_traits[1:4]]

        # MBTI-like type
        e_i = "E" if scores[0] >= MBTI_THRESHOLD else "I"
        s_n = "N" if scores[2] >= MBTI_THRESHOLD else "S"
        t_f = "T" if scores[7] >= MBTI_THRESHOLD else "F"
        j_p = "J" if scores[1] >= MBTI_THRESHOLD else "P"
        personality_type = f"{e_i}{s_n}{t_f}{j_p}"

        return {
            "extraversion": scores[0],
            "conscientiousness": scores[1],
            "openness": scores[2],
            "agreeableness": scores[3],
            "neuroticism": scores[4],
            "detail_vs_big_picture": scores[5],
            "proactive_vs_reactive": scores[6],
            "analytical_vs_intuitive": scores[7],
            "dominant_trait": dominant,
            "secondary_traits": secondary,
            "personality_type": personality_type,
            "raw_scores": raw_scores,
        }

    @staticmethod
    def normalize_preferences(raw_prefs: Dict) -> Dict:
        """Normalize preferences to PreferencesProfile format."""
        sub_type = raw_prefs.get("subscription_type", "app_only")
        try:
            subscription = SubscriptionType(sub_type)
        except ValueError:
            subscription = SubscriptionType.APP_ONLY

        paper_size = None
        if raw_prefs.get("paper_size"):
            try:
                paper_size = PaperSize(raw_prefs["paper_size"].lower())
            except ValueError:
                paper_size = None

        return {
            "subscription_type": subscription,
            "paper_size": paper_size,
            "delivery_frequency": raw_prefs.get("delivery_frequency"),
            "delivery_address": raw_prefs.get("delivery_address"),
            "email_frequency": raw_prefs.get("email_frequency", "weekly"),
            "consent_privacy": raw_prefs.get("consent_privacy", True),
            "consent_marketing": raw_prefs.get("consent_marketing", False),
            "consent_research": raw_prefs.get("consent_research", False),
            "preferred_tone": "supportive",  # Will be enriched later
            "content_depth": "standard",      # Will be enriched later
        }

    @classmethod
    def normalize_response(cls, survey_response: Dict) -> CustomerProfile:
        """
        Main normalization: raw survey JSON -> CustomerProfile.
        """
        # Parse birth_date
        bd_raw = survey_response.get("birth_date", "2000-01-01")
        if isinstance(bd_raw, str):
            birth_date = date.fromisoformat(bd_raw)
        else:
            birth_date = bd_raw

        # Normalize sub-profiles
        personality_data = cls.normalize_personality(
            survey_response.get("personality_scores", [3] * 8)
        )
        interests_data = cls.normalize_interests(
            survey_response.get("interests", [])
        )
        preferences_data = cls.normalize_preferences(survey_response)

        now_iso = datetime.utcnow().isoformat()

        return CustomerProfile(
            id=survey_response.get("id", str(uuid.uuid4())),
            name=survey_response.get("name", ""),
            email=survey_response.get("email", ""),
            birth_date=birth_date,
            gender=survey_response.get("gender", ""),
            primary_role=cls.normalize_role(
                survey_response.get("role", "other")
            ),
            secondary_roles=[],
            personality=PersonalityProfile(**personality_data),
            interests=InterestsProfile(**interests_data),
            preferences=PreferencesProfile(**preferences_data),
            survey_completed_at=now_iso,
            profile_created_at=now_iso,
        )
