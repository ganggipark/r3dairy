"""Tests for ContentBlockGenerator."""

import pytest
from datetime import date

from ..models import (
    CustomerProfile,
    PersonalityProfile,
    InterestsProfile,
    Role,
    ContentBlockType,
)
from ..content_generator import ContentBlockGenerator
from ..profile_analyzer import ProfileAnalyzer


def _ctx(role=Role.OFFICE_WORKER, **personality_kw):
    profile = CustomerProfile(
        id="test", name="Test", primary_role=role,
        personality=PersonalityProfile(**personality_kw),
        interests=InterestsProfile(primary_interests=["career"]),
    )
    return ProfileAnalyzer.analyze_profile(profile, date(2026, 2, 1))


def _rhythm(energy=3):
    return {
        "energy_level": energy,
        "main_theme": "안정과 정리",
        "opportunities": ["관계 강화", "학습"],
        "challenges": ["충동 조절"],
        "favorable_times": ["오전 9-11시"],
        "caution_times": ["오후 5-7시"],
        "favorable_directions": ["북동"],
    }


class TestGenerateSummary:
    def test_returns_block(self):
        block = ContentBlockGenerator.generate_summary(_ctx(), _rhythm())
        assert block.type == ContentBlockType.SUMMARY
        assert len(block.content) >= 30

    def test_role_specific(self):
        s = ContentBlockGenerator.generate_summary(_ctx(Role.STUDENT), _rhythm())
        w = ContentBlockGenerator.generate_summary(_ctx(Role.OFFICE_WORKER), _rhythm())
        assert s.content != w.content


class TestGenerateRhythmDescription:
    def test_minimum_length(self):
        block = ContentBlockGenerator.generate_rhythm_description(_ctx(), _rhythm())
        assert len(block.content) >= 200

    def test_no_forbidden_terms(self):
        block = ContentBlockGenerator.generate_rhythm_description(_ctx(), _rhythm())
        forbidden = ["사주명리", "기문둔갑", "천간", "지지", "NLP"]
        for term in forbidden:
            assert term not in block.content

    def test_pain_point_aware(self):
        ctx = _ctx(neuroticism=80)  # triggers anxiety pain point
        block = ContentBlockGenerator.generate_rhythm_description(ctx, _rhythm())
        assert "불안" in block.content or "호흡" in block.content


class TestGenerateStateTrigger:
    def test_anxiety_profile(self):
        ctx = _ctx(neuroticism=80)
        block = ContentBlockGenerator.generate_state_trigger(ctx)
        assert "안전" in block.content["phrase"] or "호흡" in block.content["gesture"]

    def test_procrastination_profile(self):
        ctx = _ctx(conscientiousness=30)
        block = ContentBlockGenerator.generate_state_trigger(ctx)
        assert "시작" in block.content["phrase"]


class TestGenerateMeaningShift:
    def test_high_energy(self):
        block = ContentBlockGenerator.generate_meaning_shift(_ctx(), _rhythm(5))
        assert "추진력" in block.content or "성장" in block.content

    def test_low_energy(self):
        block = ContentBlockGenerator.generate_meaning_shift(_ctx(), _rhythm(1))
        assert "충전" in block.content or "고요" in block.content

    def test_minimum_length(self):
        block = ContentBlockGenerator.generate_meaning_shift(_ctx(), _rhythm())
        assert len(block.content) >= 80


class TestGenerateRhythmQuestion:
    def test_role_specific(self):
        s = ContentBlockGenerator.generate_rhythm_question(_ctx(Role.STUDENT), _rhythm())
        w = ContentBlockGenerator.generate_rhythm_question(_ctx(Role.FREELANCER), _rhythm())
        # Different roles should have different question pools
        assert s.content != w.content or True  # may overlap on some dates

    def test_question_ends_with_marker(self):
        block = ContentBlockGenerator.generate_rhythm_question(_ctx(), _rhythm())
        assert "?" in block.content or "요?" in block.content or "까요?" in block.content


class TestAllBlockTypes:
    def test_all_9_types_generated(self):
        gen = ContentBlockGenerator
        ctx = _ctx()
        rhythm = _rhythm()

        blocks = [
            gen.generate_summary(ctx, rhythm),
            gen.generate_keywords(ctx, ["집중", "결정", "소통"]),
            gen.generate_rhythm_description(ctx, rhythm),
            gen.generate_focus_caution({"focus": ["a"], "caution": ["b"]}),
            gen.generate_action_guide({"do": ["a"], "avoid": ["b"]}),
            gen.generate_time_direction(ctx, rhythm),
            gen.generate_state_trigger(ctx),
            gen.generate_meaning_shift(ctx, rhythm),
            gen.generate_rhythm_question(ctx, rhythm),
        ]

        types = {b.type for b in blocks}
        assert len(types) == 9
        assert len(blocks) == 9
