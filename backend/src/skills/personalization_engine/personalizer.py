"""
Personalization Engine - Main Orchestrator

CustomerProfile + date -> PersonalizedDailyContent
"""

import uuid
from datetime import date, datetime
from typing import Tuple, Optional, List, Dict, Any

from .models import (
    CustomerProfile,
    PersonalizedDailyContent,
    PersonalizationContext,
    ContentQualityReport,
    ContentBlock,
)
from .profile_analyzer import ProfileAnalyzer
from .content_mapper import ContentMapper
from .content_generator import ContentBlockGenerator
from .rhythm_integrator import RhythmIntegrator

# Internal terminology that must NOT appear in user-facing content
_FORBIDDEN_TERMS = [
    "사주명리", "기문둔갑", "천간", "지지", "오행", "십성",
    "천을귀인", "역마", "공망", "NLP", "알고리즘", "엔진",
    "계산 모듈", "분석 모듈", "사주", "기문", "명리",
]


class PersonalizationEngine:
    """Main engine that orchestrates all personalization."""

    def __init__(self):
        self.rhythm_integrator = RhythmIntegrator()

    # ------------------------------------------------------------------
    # Primary API
    # ------------------------------------------------------------------

    def generate_daily_content(
        self,
        customer_profile: CustomerProfile,
        target_date: date,
    ) -> Tuple[bool, Optional[PersonalizedDailyContent], List[str]]:
        """
        Main generation pipeline.
        Returns (success, content, error_list).
        """
        errors: List[str] = []

        try:
            # 1. Analyze profile
            context = ProfileAnalyzer.analyze_profile(customer_profile, target_date)

            # 2. Get rhythm signal
            rhythm = self.rhythm_integrator.get_daily_rhythm(customer_profile, target_date)
            rhythm = RhythmIntegrator.translate_rhythm_to_user_language(rhythm)
            rhythm = RhythmIntegrator.adapt_rhythm_to_role(rhythm, context.role)

            energy = rhythm.get("energy_level", 3)

            # 3. Map profile to content decisions
            keywords = ContentMapper.map_to_keywords(context, energy)
            action_guide = ContentMapper.map_to_action_guide(context, energy)
            focus_caution = ContentMapper.map_to_focus_points(context, energy)

            # 4. Generate content blocks
            gen = ContentBlockGenerator
            blocks: List[ContentBlock] = [
                gen.generate_summary(context, rhythm),
                gen.generate_keywords(context, keywords),
                gen.generate_rhythm_description(context, rhythm),
                gen.generate_focus_caution(focus_caution),
                gen.generate_action_guide(action_guide),
                gen.generate_time_direction(context, rhythm),
                gen.generate_state_trigger(context),
                gen.generate_meaning_shift(context, rhythm),
                gen.generate_rhythm_question(context, rhythm),
            ]

            # 5. Build schema-compatible output
            schema_output = self._blocks_to_schema(blocks, target_date)

            # 6. Compute total chars
            total_chars = self._compute_total_chars(schema_output)

            # 7. Assemble result
            content = PersonalizedDailyContent(
                id=str(uuid.uuid4()),
                customer_id=customer_profile.id or "unknown",
                target_date=target_date,
                generated_at=datetime.now(),
                blocks=blocks,
                total_chars=total_chars,
                role=context.role.value,
                personality_primary=context.dominant_traits[0] if context.dominant_traits else "balanced",
                mood_suggestion=rhythm.get("main_theme", ""),
                energy_level=context.energy_level.value,
                focus_areas=[fc for fc in focus_caution.get("focus", [])[:3]],
                rhythm_signals=rhythm,
                schema_output=schema_output,
            )

            # 8. Enrich quality metrics
            content = self._enrich_quality(content, context)

            # 9. Validate
            valid, report = self.validate_content_quality(content)
            if not valid:
                errors.extend(report.issues)
                # Still return content even if validation has warnings
                return (True, content, errors)

            return (True, content, [])

        except Exception as e:
            errors.append(f"Generation error: {str(e)}")
            return (False, None, errors)

    # ------------------------------------------------------------------
    # Batch generation
    # ------------------------------------------------------------------

    def generate_multiple_days(
        self,
        customer_profile: CustomerProfile,
        start_date: date,
        end_date: date,
    ) -> Tuple[int, int, List[str]]:
        """Generate content for date range. Returns (success_count, fail_count, errors)."""
        from datetime import timedelta

        successes = 0
        failures = 0
        all_errors: List[str] = []
        current = start_date

        while current <= end_date:
            ok, _, errs = self.generate_daily_content(customer_profile, current)
            if ok:
                successes += 1
            else:
                failures += 1
            all_errors.extend(errs)
            current += timedelta(days=1)

        return successes, failures, all_errors

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def validate_content_quality(
        self,
        content: PersonalizedDailyContent,
    ) -> Tuple[bool, ContentQualityReport]:
        issues: List[str] = []

        # Block count
        block_count = len(content.blocks)
        block_ok = block_count >= 8

        if not block_ok:
            issues.append(f"Block count {block_count} < 8 minimum")

        # Char count (target 400-1200)
        char_count = content.total_chars
        char_ok = char_count >= 400

        if not char_ok:
            issues.append(f"Char count {char_count} < 400 minimum")

        # Personalization
        p_level = content.personalization_score
        p_ok = p_level >= 6.0

        if not p_ok:
            issues.append(f"Personalization score {p_level:.1f} < 6.0")

        # Forbidden terms check
        term_ok = True
        schema = content.schema_output
        # Only check user-facing text fields, exclude internal data keys
        user_facing = {k: v for k, v in schema.items() if k != "date"}
        text_blob = _flatten_to_text(user_facing)
        for term in _FORBIDDEN_TERMS:
            if term in text_blob:
                issues.append(f"Forbidden term found: '{term}'")
                term_ok = False

        passed = block_ok and char_ok and term_ok
        # personalization is a soft check

        report = ContentQualityReport(
            char_count=char_count,
            char_count_valid=char_ok,
            block_count=block_count,
            block_count_valid=block_ok,
            personalization_level=p_level,
            personalization_valid=p_ok,
            content_depth="standard",
            tone_matches_profile=True,
            no_internal_terminology=term_ok,
            issues=issues,
            passed_validation=passed,
        )
        return passed, report

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _blocks_to_schema(
        blocks: List[ContentBlock],
        target_date: date,
    ) -> Dict[str, Any]:
        """Convert blocks to schema-compatible dict matching DAILY_CONTENT_SCHEMA.json."""
        schema: Dict[str, Any] = {"date": target_date.strftime("%Y-%m-%d")}

        for block in blocks:
            btype = block.type
            c = block.content

            if btype == "summary":
                schema["summary"] = c
            elif btype == "keywords":
                schema["keywords"] = c if isinstance(c, list) else [c]
            elif btype == "rhythm_description":
                schema["rhythm_description"] = c
            elif btype == "focus_caution":
                schema["focus_caution"] = c if isinstance(c, dict) else {"focus": [], "caution": []}
            elif btype == "action_guide":
                schema["action_guide"] = c if isinstance(c, dict) else {"do": [], "avoid": []}
            elif btype == "time_direction":
                schema["time_direction"] = c if isinstance(c, dict) else {}
            elif btype == "state_trigger":
                schema["state_trigger"] = c if isinstance(c, dict) else {}
            elif btype == "meaning_shift":
                schema["meaning_shift"] = c
            elif btype == "rhythm_question":
                schema["rhythm_question"] = c

        return schema

    @staticmethod
    def _compute_total_chars(schema: Dict[str, Any]) -> int:
        return len(_flatten_to_text(schema))

    @staticmethod
    def _enrich_quality(
        content: PersonalizedDailyContent,
        context: PersonalizationContext,
    ) -> PersonalizedDailyContent:
        """Compute quality scores."""
        # Personalization score (0-10)
        levels = [b.personalization_level for b in content.blocks]
        avg_p = sum(levels) / len(levels) if levels else 0.5
        content.personalization_score = round(avg_p * 10, 1)

        # Uniqueness: how many blocks vary from default (approximate)
        # Higher pain_points and interests = more unique
        unique_factors = len(context.pain_points) + len(context.interests)
        content.uniqueness_score = round(min(10.0, unique_factors * 1.5 + 3), 1)

        # Relevance: based on role match + interest alignment
        content.relevance_score = round(min(10.0, avg_p * 8 + 2), 1)

        return content


def _flatten_to_text(obj: Any) -> str:
    """Recursively flatten a dict/list/str to a single text blob."""
    if isinstance(obj, str):
        return obj
    if isinstance(obj, list):
        return " ".join(_flatten_to_text(item) for item in obj)
    if isinstance(obj, dict):
        return " ".join(_flatten_to_text(v) for v in obj.values())
    return str(obj)
