"""Tests for ProfileAnalyzer."""

import pytest
from datetime import date

from ..models import (
    CustomerProfile,
    PersonalityProfile,
    InterestsProfile,
    Role,
    EnergyLevel,
)
from ..profile_analyzer import ProfileAnalyzer


def _make_profile(**overrides) -> CustomerProfile:
    defaults = dict(
        id="test-001",
        name="Test User",
        birth_date=date(1990, 7, 15),
        primary_role=Role.OFFICE_WORKER,
        personality=PersonalityProfile(),
        interests=InterestsProfile(primary_interests=["career", "health"]),
    )
    defaults.update(overrides)
    return CustomerProfile(**defaults)


class TestGetDominantTraits:
    def test_high_extraversion(self):
        p = PersonalityProfile(extraversion=85, openness=30)
        traits = ProfileAnalyzer.get_dominant_traits(p)
        assert "extraverted" in traits

    def test_high_neuroticism(self):
        p = PersonalityProfile(neuroticism=80)
        traits = ProfileAnalyzer.get_dominant_traits(p)
        assert "sensitive" in traits

    def test_balanced_returns_balanced(self):
        p = PersonalityProfile(
            extraversion=50, conscientiousness=50, openness=50,
            agreeableness=50, neuroticism=50,
            analytical_vs_intuitive=50, proactive_vs_reactive=50,
            detail_vs_big_picture=50,
        )
        traits = ProfileAnalyzer.get_dominant_traits(p)
        assert "balanced" in traits

    def test_returns_max_3(self):
        p = PersonalityProfile(
            extraversion=90, conscientiousness=90, openness=90,
            agreeableness=90, neuroticism=10,
        )
        traits = ProfileAnalyzer.get_dominant_traits(p)
        assert len(traits) <= 3


class TestRoleCharacteristics:
    def test_student_has_learning(self):
        chars = ProfileAnalyzer.get_role_characteristics(Role.STUDENT)
        assert "learning" in chars["focus_areas"]

    def test_office_worker_has_career(self):
        chars = ProfileAnalyzer.get_role_characteristics(Role.OFFICE_WORKER)
        assert "career" in chars["focus_areas"]

    def test_freelancer_has_creative_energy(self):
        chars = ProfileAnalyzer.get_role_characteristics(Role.FREELANCER)
        assert "creative_energy" in chars["focus_areas"]


class TestContentStyle:
    def test_analytical_tone(self):
        p = PersonalityProfile(analytical_vs_intuitive=80)
        style = ProfileAnalyzer.determine_content_style(p, InterestsProfile())
        assert style["tone"] == "analytical"

    def test_detailed_depth(self):
        p = PersonalityProfile(detail_vs_big_picture=80)
        style = ProfileAnalyzer.determine_content_style(p, InterestsProfile())
        assert style["depth"] == "detailed"

    def test_brief_depth(self):
        p = PersonalityProfile(detail_vs_big_picture=20)
        style = ProfileAnalyzer.determine_content_style(p, InterestsProfile())
        assert style["depth"] == "brief"


class TestPainPoints:
    def test_high_neuroticism_anxiety(self):
        p = PersonalityProfile(neuroticism=80)
        points = ProfileAnalyzer.identify_pain_points(p, Role.OFFICE_WORKER)
        assert "anxiety_management" in points

    def test_low_conscientiousness_procrastination(self):
        p = PersonalityProfile(conscientiousness=30)
        points = ProfileAnalyzer.identify_pain_points(p, Role.STUDENT)
        assert "procrastination" in points
        assert "study_discipline" in points

    def test_freelancer_income_anxiety(self):
        p = PersonalityProfile(neuroticism=70, conscientiousness=40)
        points = ProfileAnalyzer.identify_pain_points(p, Role.FREELANCER)
        assert "income_anxiety" in points


class TestAnalyzeProfile:
    def test_returns_context(self):
        profile = _make_profile()
        ctx = ProfileAnalyzer.analyze_profile(profile, date(2026, 2, 1))
        assert ctx.role == Role.OFFICE_WORKER
        assert len(ctx.dominant_traits) >= 1
        assert ctx.content_tone in ("analytical", "supportive", "formal", "casual")
        assert ctx.seasonal_context == "winter"

    def test_summer_season(self):
        profile = _make_profile()
        ctx = ProfileAnalyzer.analyze_profile(profile, date(2026, 7, 15))
        assert ctx.seasonal_context == "summer"

    def test_energy_level_high(self):
        profile = _make_profile(
            personality=PersonalityProfile(extraversion=80, proactive_vs_reactive=80)
        )
        ctx = ProfileAnalyzer.analyze_profile(profile, date(2026, 2, 1))
        assert ctx.energy_level == EnergyLevel.HIGH
