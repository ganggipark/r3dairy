"""Tests for PersonalizationEngine (end-to-end)."""

import pytest
from datetime import date

from ..models import (
    CustomerProfile,
    PersonalityProfile,
    InterestsProfile,
    Role,
)
from ..personalizer import PersonalizationEngine, _FORBIDDEN_TERMS


def _make_profile(
    role=Role.OFFICE_WORKER,
    **personality_kw,
) -> CustomerProfile:
    return CustomerProfile(
        id="test-user-001",
        name="Park Ji-hoon",
        birth_date=date(1988, 7, 22),
        birth_time="14:30",
        gender="male",
        birth_place="Seoul",
        primary_role=role,
        personality=PersonalityProfile(
            extraversion=50,
            conscientiousness=75,
            openness=60,
            agreeableness=70,
            neuroticism=40,
            analytical_vs_intuitive=60,
            proactive_vs_reactive=70,
            detail_vs_big_picture=75,
            **personality_kw,
        ),
        interests=InterestsProfile(
            primary_interests=["career", "finance", "personal_growth"]
        ),
    )


class TestGenerateDailyContent:
    def setup_method(self):
        self.engine = PersonalizationEngine()
        self.target = date(2026, 2, 1)

    def test_success(self):
        ok, content, errors = self.engine.generate_daily_content(
            _make_profile(), self.target
        )
        assert ok is True
        assert content is not None
        assert content.target_date == self.target

    def test_has_9_blocks(self):
        ok, content, _ = self.engine.generate_daily_content(
            _make_profile(), self.target
        )
        assert len(content.blocks) >= 9

    def test_schema_output_has_required_keys(self):
        _, content, _ = self.engine.generate_daily_content(
            _make_profile(), self.target
        )
        schema = content.schema_output
        required = [
            "date", "summary", "keywords", "rhythm_description",
            "focus_caution", "action_guide", "time_direction",
            "state_trigger", "meaning_shift", "rhythm_question",
        ]
        for key in required:
            assert key in schema, f"Missing key: {key}"

    def test_char_count_above_400(self):
        _, content, _ = self.engine.generate_daily_content(
            _make_profile(), self.target
        )
        assert content.total_chars >= 400

    def test_no_forbidden_terms(self):
        _, content, _ = self.engine.generate_daily_content(
            _make_profile(), self.target
        )
        text = _flatten(content.schema_output)
        for term in _FORBIDDEN_TERMS:
            assert term not in text, f"Forbidden term '{term}' found in output"

    def test_personalization_score(self):
        _, content, _ = self.engine.generate_daily_content(
            _make_profile(), self.target
        )
        assert content.personalization_score >= 5.0

    def test_role_metadata(self):
        _, content, _ = self.engine.generate_daily_content(
            _make_profile(Role.STUDENT), self.target
        )
        assert content.role == "student"


class TestRoleVariation:
    def setup_method(self):
        self.engine = PersonalizationEngine()
        self.target = date(2026, 2, 1)

    def test_different_roles_different_content(self):
        _, student, _ = self.engine.generate_daily_content(
            _make_profile(Role.STUDENT), self.target
        )
        _, worker, _ = self.engine.generate_daily_content(
            _make_profile(Role.OFFICE_WORKER), self.target
        )
        _, freelancer, _ = self.engine.generate_daily_content(
            _make_profile(Role.FREELANCER), self.target
        )

        # Summaries should differ
        assert student.schema_output["summary"] != worker.schema_output["summary"]
        assert worker.schema_output["summary"] != freelancer.schema_output["summary"]

    def test_keywords_vary_by_role(self):
        _, student, _ = self.engine.generate_daily_content(
            _make_profile(Role.STUDENT), self.target
        )
        _, worker, _ = self.engine.generate_daily_content(
            _make_profile(Role.OFFICE_WORKER), self.target
        )
        assert student.schema_output["keywords"] != worker.schema_output["keywords"]


class TestValidation:
    def setup_method(self):
        self.engine = PersonalizationEngine()

    def test_validation_passes(self):
        _, content, _ = self.engine.generate_daily_content(
            _make_profile(), date(2026, 2, 1)
        )
        valid, report = self.engine.validate_content_quality(content)
        assert valid is True
        assert report.block_count_valid is True
        assert report.char_count_valid is True
        assert report.no_internal_terminology is True

    def test_quality_report_fields(self):
        _, content, _ = self.engine.generate_daily_content(
            _make_profile(), date(2026, 2, 1)
        )
        _, report = self.engine.validate_content_quality(content)
        assert report.char_count > 0
        assert report.block_count >= 9


class TestMultipleDays:
    def test_range_generation(self):
        engine = PersonalizationEngine()
        ok_count, fail_count, errors = engine.generate_multiple_days(
            _make_profile(),
            date(2026, 2, 1),
            date(2026, 2, 3),
        )
        assert ok_count == 3
        assert fail_count == 0


class TestPerformance:
    def test_single_day_under_2_seconds(self):
        import time
        engine = PersonalizationEngine()
        start = time.time()
        engine.generate_daily_content(_make_profile(), date(2026, 2, 1))
        elapsed = time.time() - start
        assert elapsed < 2.0, f"Generation took {elapsed:.2f}s (> 2s limit)"


def _flatten(obj) -> str:
    if isinstance(obj, str):
        return obj
    if isinstance(obj, list):
        return " ".join(_flatten(i) for i in obj)
    if isinstance(obj, dict):
        return " ".join(_flatten(v) for v in obj.values())
    return str(obj)
