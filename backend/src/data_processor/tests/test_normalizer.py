"""Tests for SurveyResponseNormalizer."""

import pytest
from ..models import Role, SubscriptionType
from ..normalizer import SurveyResponseNormalizer


class TestNormalizeRole:
    def test_english_roles(self):
        assert SurveyResponseNormalizer.normalize_role("student") == Role.STUDENT
        assert SurveyResponseNormalizer.normalize_role("office_worker") == Role.OFFICE_WORKER
        assert SurveyResponseNormalizer.normalize_role("freelancer") == Role.FREELANCER

    def test_korean_roles(self):
        assert SurveyResponseNormalizer.normalize_role("학생") == Role.STUDENT
        assert SurveyResponseNormalizer.normalize_role("직장인") == Role.OFFICE_WORKER
        assert SurveyResponseNormalizer.normalize_role("프리랜서") == Role.FREELANCER
        assert SurveyResponseNormalizer.normalize_role("부모") == Role.PARENT

    def test_case_insensitive(self):
        assert SurveyResponseNormalizer.normalize_role("STUDENT") == Role.STUDENT
        assert SurveyResponseNormalizer.normalize_role("Office Worker") == Role.OFFICE_WORKER

    def test_unknown_defaults_to_other(self):
        assert SurveyResponseNormalizer.normalize_role("astronaut") == Role.OTHER
        assert SurveyResponseNormalizer.normalize_role("") == Role.OTHER


class TestNormalizeInterests:
    def test_basic_categorization(self):
        result = SurveyResponseNormalizer.normalize_interests(
            ["career", "health", "취미/창작"]
        )
        assert result["is_career_focused"] is True
        assert result["is_lifestyle_focused"] is True
        assert result["is_creative_focused"] is True
        assert result["is_growth_focused"] is False

    def test_primary_limited_to_5(self):
        interests = ["a", "b", "c", "d", "e", "f", "g"]
        result = SurveyResponseNormalizer.normalize_interests(interests)
        assert len(result["primary_interests"]) == 5

    def test_empty_interests(self):
        result = SurveyResponseNormalizer.normalize_interests([])
        assert result["all_interests"] == []
        assert result["is_growth_focused"] is False

    def test_korean_growth_keywords(self):
        result = SurveyResponseNormalizer.normalize_interests(["자기개발"])
        assert result["is_growth_focused"] is True


class TestNormalizePersonality:
    def test_basic_conversion(self):
        # All 3s (neutral) -> all 50.0
        result = SurveyResponseNormalizer.normalize_personality([3, 3, 3, 3, 3, 3, 3, 3])
        assert result["extraversion"] == 50.0
        assert result["conscientiousness"] == 50.0
        # Neuroticism reversed: Likert 3 -> 50, then 100-50 = 50
        assert result["neuroticism"] == 50.0

    def test_extreme_high(self):
        result = SurveyResponseNormalizer.normalize_personality([5, 5, 5, 5, 5, 5, 5, 5])
        assert result["extraversion"] == 100.0
        # Neuroticism reversed: Likert 5 -> 100, reversed -> 0
        assert result["neuroticism"] == 0.0

    def test_extreme_low(self):
        result = SurveyResponseNormalizer.normalize_personality([1, 1, 1, 1, 1, 1, 1, 1])
        assert result["extraversion"] == 0.0
        # Neuroticism reversed: Likert 1 -> 0, reversed -> 100
        assert result["neuroticism"] == 100.0

    def test_personality_type_generation(self):
        # High scores: E, N, T, J
        result = SurveyResponseNormalizer.normalize_personality([5, 5, 5, 3, 3, 3, 3, 5])
        assert result["personality_type"][0] == "E"  # extraversion >= 50
        assert result["personality_type"][1] == "N"  # openness >= 50
        assert result["personality_type"][2] == "T"  # analytical >= 50

    def test_short_responses_padded(self):
        result = SurveyResponseNormalizer.normalize_personality([4, 3])
        assert "extraversion" in result
        assert "personality_type" in result
        assert len(result["personality_type"]) == 4

    def test_dominant_trait_identified(self):
        result = SurveyResponseNormalizer.normalize_personality([5, 1, 1, 1, 3, 1, 1, 1])
        assert result["dominant_trait"] == "extraversion"


class TestNormalizePreferences:
    def test_basic_preferences(self):
        result = SurveyResponseNormalizer.normalize_preferences({
            "subscription_type": "app_only",
            "email_frequency": "daily",
            "consent_privacy": True,
        })
        assert result["subscription_type"] == SubscriptionType.APP_ONLY
        assert result["email_frequency"] == "daily"

    def test_paper_size_normalization(self):
        result = SurveyResponseNormalizer.normalize_preferences({
            "subscription_type": "hybrid",
            "paper_size": "A5",
        })
        assert result["paper_size"].value == "a5"

    def test_unknown_subscription_defaults(self):
        result = SurveyResponseNormalizer.normalize_preferences({
            "subscription_type": "unknown",
        })
        assert result["subscription_type"] == SubscriptionType.APP_ONLY


class TestNormalizeResponse:
    def test_full_response(self):
        raw = {
            "name": "Kim Sung-hoon",
            "email": "kim@example.com",
            "birth_date": "1990-05-15",
            "gender": "Male",
            "role": "office_worker",
            "personality_scores": [4, 3, 4, 4, 2, 4, 3, 3],
            "interests": ["career", "personal_growth", "health"],
            "subscription_type": "hybrid",
            "paper_size": "A5",
            "delivery_frequency": "monthly",
            "email_frequency": "weekly",
            "consent_privacy": True,
            "consent_marketing": False,
        }
        profile = SurveyResponseNormalizer.normalize_response(raw)
        assert profile.name == "Kim Sung-hoon"
        assert profile.primary_role == Role.OFFICE_WORKER
        assert profile.personality.personality_type is not None
        assert len(profile.personality.personality_type) == 4
        assert profile.interests.is_career_focused is True

    def test_minimal_response(self):
        raw = {
            "name": "Test",
            "email": "test@example.com",
            "birth_date": "2000-01-01",
            "gender": "Other",
        }
        profile = SurveyResponseNormalizer.normalize_response(raw)
        assert profile.name == "Test"
        assert profile.primary_role == Role.OTHER
