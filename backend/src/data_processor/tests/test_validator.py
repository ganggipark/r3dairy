"""Tests for ProfileValidator."""

import pytest
from datetime import date

from ..models import (
    Role,
    SubscriptionType,
    PaperSize,
    PersonalityProfile,
    InterestsProfile,
    PreferencesProfile,
    CustomerProfile,
)
from ..validator import ProfileValidator


def _make_personality(**overrides):
    defaults = {
        "extraversion": 60, "conscientiousness": 70, "openness": 55,
        "agreeableness": 65, "neuroticism": 40,
        "analytical_vs_intuitive": 50, "proactive_vs_reactive": 60,
        "detail_vs_big_picture": 55,
        "dominant_trait": "conscientiousness",
        "secondary_traits": ["agreeableness"],
        "personality_type": "ENTJ",
        "raw_scores": {},
    }
    defaults.update(overrides)
    return PersonalityProfile(**defaults)


def _make_profile(**overrides):
    defaults = {
        "id": "test-123",
        "name": "Kim",
        "email": "kim@example.com",
        "birth_date": date(1990, 5, 15),
        "gender": "Male",
        "age": 35,
        "primary_role": Role.OFFICE_WORKER,
        "personality": _make_personality(),
        "interests": InterestsProfile(
            primary_interests=["career"],
            all_interests=["career", "health"],
            interest_categories={"career": ["career"]},
        ),
        "preferences": PreferencesProfile(
            subscription_type=SubscriptionType.APP_ONLY,
            consent_privacy=True,
        ),
    }
    defaults.update(overrides)
    return CustomerProfile(**defaults)


class TestValidateBasicInfo:
    def test_valid(self):
        ok, errors = ProfileValidator.validate_basic_info(
            "Kim", "kim@example.com", date(1990, 5, 15)
        )
        assert ok is True
        assert errors == []

    def test_empty_name(self):
        ok, errors = ProfileValidator.validate_basic_info(
            "", "kim@example.com", date(1990, 5, 15)
        )
        assert ok is False
        assert any("Name" in e for e in errors)

    def test_too_young(self):
        ok, errors = ProfileValidator.validate_basic_info(
            "Kim", "kim@example.com", date(2020, 1, 1)
        )
        assert ok is False
        assert any("13" in e for e in errors)

    def test_future_birth(self):
        ok, errors = ProfileValidator.validate_basic_info(
            "Kim", "kim@example.com", date(2030, 1, 1)
        )
        assert ok is False
        assert any("future" in e for e in errors)

    def test_empty_email(self):
        ok, errors = ProfileValidator.validate_basic_info(
            "Kim", "", date(1990, 1, 1)
        )
        assert ok is False


class TestValidatePersonalityProfile:
    def test_valid(self):
        ok, errors = ProfileValidator.validate_personality_profile(_make_personality())
        assert ok is True

    def test_missing_dominant_trait(self):
        ok, errors = ProfileValidator.validate_personality_profile(
            _make_personality(dominant_trait="")
        )
        assert ok is False

    def test_invalid_personality_type(self):
        ok, errors = ProfileValidator.validate_personality_profile(
            _make_personality(personality_type="XY")
        )
        assert ok is False


class TestValidateInterestsProfile:
    def test_valid(self):
        ip = InterestsProfile(
            primary_interests=["career"],
            all_interests=["career"],
            interest_categories={},
        )
        ok, errors = ProfileValidator.validate_interests_profile(ip)
        assert ok is True

    def test_empty_interests(self):
        ip = InterestsProfile(
            primary_interests=[],
            all_interests=[],
            interest_categories={},
        )
        ok, errors = ProfileValidator.validate_interests_profile(ip)
        assert ok is False


class TestValidatePreferencesProfile:
    def test_valid(self):
        pp = PreferencesProfile(
            subscription_type=SubscriptionType.APP_ONLY,
            consent_privacy=True,
        )
        ok, errors = ProfileValidator.validate_preferences_profile(pp)
        assert ok is True

    def test_no_privacy_consent(self):
        pp = PreferencesProfile(
            subscription_type=SubscriptionType.APP_ONLY,
            consent_privacy=False,
        )
        ok, errors = ProfileValidator.validate_preferences_profile(pp)
        assert ok is False

    def test_paper_without_size(self):
        pp = PreferencesProfile(
            subscription_type=SubscriptionType.PAPER_ONLY,
            consent_privacy=True,
        )
        ok, errors = ProfileValidator.validate_preferences_profile(pp)
        assert ok is False
        assert any("Paper size" in e for e in errors)

    def test_hybrid_with_paper_details(self):
        pp = PreferencesProfile(
            subscription_type=SubscriptionType.HYBRID,
            paper_size=PaperSize.A5,
            delivery_frequency="monthly",
            consent_privacy=True,
        )
        ok, errors = ProfileValidator.validate_preferences_profile(pp)
        assert ok is True


class TestValidateCustomerProfile:
    def test_valid_full_profile(self):
        ok, errors = ProfileValidator.validate_customer_profile(_make_profile())
        assert ok is True
        assert errors == []


class TestDetectAnomalies:
    def test_young_office_worker(self):
        profile = _make_profile(
            birth_date=date(2010, 1, 1),
            age=16,
            primary_role=Role.OFFICE_WORKER,
        )
        warnings = ProfileValidator.detect_anomalies(profile)
        assert any("under 18" in w for w in warnings)

    def test_old_student(self):
        profile = _make_profile(
            birth_date=date(1950, 1, 1),
            age=76,
            primary_role=Role.STUDENT,
        )
        warnings = ProfileValidator.detect_anomalies(profile)
        assert any("over 65" in w for w in warnings)

    def test_no_anomalies(self):
        warnings = ProfileValidator.detect_anomalies(_make_profile())
        assert warnings == []
