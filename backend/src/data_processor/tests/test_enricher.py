"""Tests for ProfileEnricher."""

import pytest
from datetime import date

from ..models import Role, PersonalityProfile
from ..enricher import ProfileEnricher
from ..normalizer import SurveyResponseNormalizer


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
        "secondary_traits": ["agreeableness"],
        "personality_type": "ENTJ",
        "raw_scores": {},
    }
    defaults.update(overrides)
    return PersonalityProfile(**defaults)


class TestCalculateAge:
    def test_basic_age(self):
        assert ProfileEnricher.calculate_age(
            date(1990, 5, 15), reference=date(2026, 1, 30)
        ) == 35

    def test_birthday_not_yet(self):
        assert ProfileEnricher.calculate_age(
            date(1990, 12, 31), reference=date(2026, 1, 1)
        ) == 35

    def test_birthday_today(self):
        assert ProfileEnricher.calculate_age(
            date(1990, 1, 30), reference=date(2026, 1, 30)
        ) == 36


class TestGetZodiacSign:
    def test_aquarius(self):
        assert ProfileEnricher.get_zodiac_sign(date(2000, 2, 1)) == "Aquarius"

    def test_pisces(self):
        assert ProfileEnricher.get_zodiac_sign(date(2000, 3, 10)) == "Pisces"

    def test_capricorn_dec(self):
        assert ProfileEnricher.get_zodiac_sign(date(2000, 12, 25)) == "Capricorn"

    def test_capricorn_jan(self):
        assert ProfileEnricher.get_zodiac_sign(date(2000, 1, 10)) == "Capricorn"

    def test_taurus(self):
        assert ProfileEnricher.get_zodiac_sign(date(1990, 5, 15)) == "Taurus"


class TestGetKoreanZodiac:
    def test_dragon_2000(self):
        assert ProfileEnricher.get_korean_zodiac(date(2000, 1, 1)) == "Dragon"

    def test_rat_2008(self):
        assert ProfileEnricher.get_korean_zodiac(date(2008, 1, 1)) == "Rat"

    def test_horse_1990(self):
        assert ProfileEnricher.get_korean_zodiac(date(1990, 1, 1)) == "Horse"


class TestDeriveTonePreference:
    def test_analytical(self):
        p = _make_personality(analytical_vs_intuitive=80)
        assert ProfileEnricher.derive_tone_preference(p) == "analytical"

    def test_formal(self):
        p = _make_personality(conscientiousness=70, openness=40, analytical_vs_intuitive=50)
        assert ProfileEnricher.derive_tone_preference(p) == "formal"

    def test_casual(self):
        p = _make_personality(extraversion=70, openness=70, analytical_vs_intuitive=50, conscientiousness=50)
        assert ProfileEnricher.derive_tone_preference(p) == "casual"

    def test_supportive_default(self):
        p = _make_personality(
            extraversion=50, openness=60, agreeableness=60,
            analytical_vs_intuitive=50, conscientiousness=50,
        )
        assert ProfileEnricher.derive_tone_preference(p) == "supportive"


class TestDeriveContentDepth:
    def test_student_detailed(self):
        p = _make_personality(conscientiousness=70)
        assert ProfileEnricher.derive_content_depth(p, Role.STUDENT) == "detailed"

    def test_office_worker_brief(self):
        p = _make_personality(conscientiousness=30)
        assert ProfileEnricher.derive_content_depth(p, Role.OFFICE_WORKER) == "brief"

    def test_default_standard(self):
        p = _make_personality(conscientiousness=50, openness=50)
        assert ProfileEnricher.derive_content_depth(p, Role.FREELANCER) == "standard"


class TestEnrichProfile:
    def test_full_enrichment(self):
        raw = {
            "name": "Test User",
            "email": "test@example.com",
            "birth_date": "1990-05-15",
            "gender": "Male",
            "role": "student",
            "personality_scores": [4, 4, 4, 4, 2, 4, 3, 3],
            "interests": ["career", "health"],
            "subscription_type": "app_only",
            "consent_privacy": True,
        }
        profile = SurveyResponseNormalizer.normalize_response(raw)
        enriched = ProfileEnricher.enrich_profile(profile)

        assert enriched.age > 0
        assert enriched.zodiac_sign == "Taurus"
        assert enriched.korean_zodiac == "Horse"
        assert enriched.preferences.preferred_tone in {
            "analytical", "formal", "casual", "supportive"
        }
        assert enriched.preferences.content_depth in {"brief", "standard", "detailed"}
