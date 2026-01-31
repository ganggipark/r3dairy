"""Tests for ContentMapper."""

import pytest
from datetime import date

from ..models import (
    CustomerProfile,
    PersonalityProfile,
    InterestsProfile,
    PersonalizationContext,
    Role,
    EnergyLevel,
)
from ..content_mapper import ContentMapper
from ..profile_analyzer import ProfileAnalyzer


def _make_context(role=Role.OFFICE_WORKER, energy=EnergyLevel.MEDIUM, **kw) -> PersonalizationContext:
    profile = CustomerProfile(
        id="test", name="Test", primary_role=role,
        personality=PersonalityProfile(**kw.get("personality_kw", {})),
        interests=InterestsProfile(primary_interests=kw.get("interests", ["career"])),
    )
    return ProfileAnalyzer.analyze_profile(profile, date(2026, 2, 1))


class TestMapToKeywords:
    def test_returns_3_to_5(self):
        ctx = _make_context()
        kw = ContentMapper.map_to_keywords(ctx, rhythm_energy=3)
        assert 3 <= len(kw) <= 5

    def test_high_energy_student(self):
        ctx = _make_context(role=Role.STUDENT)
        kw = ContentMapper.map_to_keywords(ctx, rhythm_energy=5)
        assert "집중" in kw or "도전" in kw

    def test_low_energy_freelancer(self):
        ctx = _make_context(role=Role.FREELANCER)
        kw = ContentMapper.map_to_keywords(ctx, rhythm_energy=1)
        assert "회복" in kw or "휴식" in kw


class TestMapToActionGuide:
    def test_returns_do_and_avoid(self):
        ctx = _make_context()
        guide = ContentMapper.map_to_action_guide(ctx, rhythm_energy=3)
        assert "do" in guide
        assert "avoid" in guide
        assert len(guide["do"]) >= 2
        assert len(guide["avoid"]) >= 1

    def test_role_specific_actions(self):
        student_ctx = _make_context(role=Role.STUDENT)
        worker_ctx = _make_context(role=Role.OFFICE_WORKER)
        s_guide = ContentMapper.map_to_action_guide(student_ctx, 4)
        w_guide = ContentMapper.map_to_action_guide(worker_ctx, 4)
        # Should be different content
        assert s_guide["do"] != w_guide["do"]


class TestMapToFocusPoints:
    def test_returns_focus_and_caution(self):
        ctx = _make_context()
        points = ContentMapper.map_to_focus_points(ctx, 3)
        assert "focus" in points
        assert "caution" in points
        assert len(points["focus"]) >= 2
        assert len(points["caution"]) >= 1


class TestPersonalityToTone:
    def test_analytical(self):
        p = PersonalityProfile(analytical_vs_intuitive=80)
        assert ContentMapper.map_personality_to_tone(p) == "analytical"

    def test_supportive(self):
        p = PersonalityProfile(extraversion=70, agreeableness=70)
        assert ContentMapper.map_personality_to_tone(p) == "supportive"


class TestShouldEmphasizeTopic:
    def test_interest_match(self):
        p = PersonalityProfile()
        assert ContentMapper.should_emphasize_topic("career", ["career"], p) is True

    def test_personality_match(self):
        p = PersonalityProfile(openness=80)
        assert ContentMapper.should_emphasize_topic("creativity", [], p) is True

    def test_no_match(self):
        p = PersonalityProfile(openness=30)
        assert ContentMapper.should_emphasize_topic("creativity", [], p) is False
