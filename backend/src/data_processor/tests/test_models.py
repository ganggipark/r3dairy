"""Tests for data_processor models."""

import pytest
from datetime import date
from pydantic import ValidationError

from ..models import (
    Role,
    SubscriptionType,
    PaperSize,
    PersonalityProfile,
    InterestsProfile,
    PreferencesProfile,
    CustomerProfile,
)


def _make_personality(**overrides):
    defaults = {
        "extraversion": 60,
        "conscientiousness": 70,
        "openness": 55,
        "agreeableness": 65,
        "neuroticism": 40,
        "analytical_vs_intuitive": 50,
        "proactive_vs_reactive": 60,
        "detail_vs_big_picture": 55,
        "dominant_trait": "conscientiousness",
        "secondary_traits": ["agreeableness", "extraversion"],
        "personality_type": "ENTJ",
        "raw_scores": {"extraversion": 60},
    }
    defaults.update(overrides)
    return PersonalityProfile(**defaults)


def _make_interests(**overrides):
    defaults = {
        "primary_interests": ["career", "health"],
        "all_interests": ["career", "health", "travel"],
        "interest_categories": {"career": ["career"], "lifestyle": ["health", "travel"]},
    }
    defaults.update(overrides)
    return InterestsProfile(**defaults)


def _make_preferences(**overrides):
    defaults = {
        "subscription_type": SubscriptionType.APP_ONLY,
        "consent_privacy": True,
    }
    defaults.update(overrides)
    return PreferencesProfile(**defaults)


class TestRole:
    def test_enum_values(self):
        assert Role.STUDENT.value == "student"
        assert Role.OFFICE_WORKER.value == "office_worker"


class TestPersonalityProfile:
    def test_valid_profile(self):
        p = _make_personality()
        assert p.extraversion == 60
        assert p.personality_type == "ENTJ"

    def test_out_of_range_rejected(self):
        with pytest.raises(ValidationError):
            _make_personality(extraversion=150)

    def test_negative_rejected(self):
        with pytest.raises(ValidationError):
            _make_personality(neuroticism=-5)


class TestInterestsProfile:
    def test_valid_interests(self):
        i = _make_interests()
        assert len(i.primary_interests) == 2
        assert i.is_growth_focused is False

    def test_too_many_primary(self):
        with pytest.raises(ValidationError):
            _make_interests(primary_interests=["a"] * 6)


class TestPreferencesProfile:
    def test_valid_preferences(self):
        p = _make_preferences()
        assert p.subscription_type == SubscriptionType.APP_ONLY

    def test_invalid_email_frequency(self):
        with pytest.raises(ValidationError):
            _make_preferences(email_frequency="hourly")

    def test_valid_delivery_frequency(self):
        p = _make_preferences(delivery_frequency="monthly")
        assert p.delivery_frequency == "monthly"

    def test_invalid_delivery_frequency(self):
        with pytest.raises(ValidationError):
            _make_preferences(delivery_frequency="biweekly")


class TestCustomerProfile:
    def test_valid_profile(self):
        cp = CustomerProfile(
            id="test-123",
            name="Kim",
            email="kim@example.com",
            birth_date=date(1990, 5, 15),
            gender="Male",
            primary_role=Role.OFFICE_WORKER,
            personality=_make_personality(),
            interests=_make_interests(),
            preferences=_make_preferences(),
        )
        assert cp.name == "Kim"
        assert cp.primary_role == Role.OFFICE_WORKER

    def test_invalid_email(self):
        with pytest.raises(ValidationError):
            CustomerProfile(
                id="test",
                name="Kim",
                email="not-an-email",
                birth_date=date(1990, 1, 1),
                gender="Male",
                primary_role=Role.OTHER,
                personality=_make_personality(),
                interests=_make_interests(),
                preferences=_make_preferences(),
            )

    def test_empty_name_rejected(self):
        with pytest.raises(ValidationError):
            CustomerProfile(
                id="test",
                name="   ",
                email="a@b.com",
                birth_date=date(1990, 1, 1),
                gender="Male",
                primary_role=Role.OTHER,
                personality=_make_personality(),
                interests=_make_interests(),
                preferences=_make_preferences(),
            )

    def test_email_normalized_to_lowercase(self):
        cp = CustomerProfile(
            id="test",
            name="Kim",
            email="Kim@Example.COM",
            birth_date=date(1990, 1, 1),
            gender="Male",
            primary_role=Role.OTHER,
            personality=_make_personality(),
            interests=_make_interests(),
            preferences=_make_preferences(),
        )
        assert cp.email == "kim@example.com"
