"""
Rhythm Integrator

Bridge between the existing rhythm analysis system and the personalization engine.
"""

import datetime
from typing import Dict, Any
from .models import CustomerProfile, Role

# Import existing rhythm modules
try:
    from ...rhythm.models import BirthInfo, RhythmSignal, Gender
    from ...rhythm.signals import RhythmAnalyzer
    _HAS_RHYTHM = True
except (ImportError, Exception):
    _HAS_RHYTHM = False


class RhythmIntegrator:
    """Integrate rhythm analysis from saju/qimen calculators."""

    def __init__(self):
        if _HAS_RHYTHM:
            self._analyzer = RhythmAnalyzer()
        else:
            self._analyzer = None

    # ------------------------------------------------------------------
    # Core
    # ------------------------------------------------------------------

    def get_daily_rhythm(
        self,
        customer_profile: CustomerProfile,
        target_date: datetime.date,
    ) -> Dict[str, Any]:
        """
        Get daily rhythm signal as a plain dict.
        Falls back to sensible defaults if rhythm module unavailable.
        """
        if self._analyzer is not None:
            try:
                birth_info = self._profile_to_birth_info(customer_profile)
                signal: RhythmSignal = self._analyzer.generate_daily_signal(
                    birth_info, target_date
                )
                return self._signal_to_dict(signal)
            except Exception:
                pass

        # Fallback: generate plausible defaults based on date
        return self._fallback_rhythm(target_date)

    # ------------------------------------------------------------------
    # Translation helpers (internal terms -> user language)
    # ------------------------------------------------------------------

    # Internal terms that must be scrubbed from user-facing text
    _INTERNAL_TERMS = [
        "사주명리", "기문둔갑", "천간", "지지", "오행", "십성",
        "천을귀인", "역마", "공망", "NLP", "알고리즘", "엔진",
        "계산 모듈", "분석 모듈", "사주", "기문", "명리",
        "금 오행", "수 오행", "목 오행", "화 오행", "토 오행",
    ]

    # Replacement map for internal terms -> user-friendly alternatives
    _TERM_REPLACEMENTS: Dict[str, str] = {
        "금 오행 활용": "집중력 강화",
        "수 오행 활용": "유연한 대처",
        "목 오행 활용": "성장과 시작",
        "화 오행 활용": "열정과 소통",
        "토 오행 활용": "안정과 균형",
        "오행 충돌": "에너지 충돌",
        "오행 조화": "에너지 조화",
    }

    @classmethod
    def translate_rhythm_to_user_language(cls, rhythm: Dict[str, Any]) -> Dict[str, Any]:
        """Strip internal terminology and convert to user-safe dict."""
        result = dict(rhythm)
        result.pop("saju_data", None)
        result.pop("qimen_data", None)
        result.pop("internal_terms", None)

        # Scrub internal terms from string values
        cls._scrub_dict(result)
        return result

    @classmethod
    def _scrub_dict(cls, d: Dict[str, Any]) -> None:
        """In-place scrub of internal terms from dict values."""
        for key in list(d.keys()):
            val = d[key]
            if isinstance(val, str):
                d[key] = cls._scrub_text(val)
            elif isinstance(val, list):
                d[key] = [cls._scrub_text(item) if isinstance(item, str) else item for item in val]
            elif isinstance(val, dict):
                cls._scrub_dict(val)

    @classmethod
    def _scrub_text(cls, text: str) -> str:
        """Replace internal terms with user-friendly alternatives."""
        # Apply specific replacements first (longer phrases)
        for internal, replacement in sorted(cls._TERM_REPLACEMENTS.items(), key=lambda x: len(x[0]), reverse=True):
            text = text.replace(internal, replacement)
        # Remove any remaining forbidden terms
        for term in cls._INTERNAL_TERMS:
            if term in text:
                text = text.replace(term, "흐름")
        return text

    @staticmethod
    def adapt_rhythm_to_role(rhythm: Dict[str, Any], role: Role) -> Dict[str, Any]:
        """Adjust rhythm emphasis based on role."""
        adapted = dict(rhythm)
        role_emphasis = {
            "student": {"opportunities_focus": "learning", "challenge_focus": "exam_stress"},
            "office_worker": {"opportunities_focus": "career", "challenge_focus": "burnout"},
            "freelancer": {"opportunities_focus": "creativity", "challenge_focus": "income"},
        }
        adapted["role_emphasis"] = role_emphasis.get(role.value, {})
        return adapted

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _profile_to_birth_info(profile: CustomerProfile) -> "BirthInfo":
        """Convert CustomerProfile to BirthInfo for rhythm module."""
        gender_map = {"male": Gender.MALE, "female": Gender.FEMALE}
        gender = gender_map.get(profile.gender, Gender.OTHER)

        birth_time_str = profile.birth_time or "12:00"
        parts = birth_time_str.split(":")
        hour = int(parts[0]) if len(parts) >= 1 else 12
        minute = int(parts[1]) if len(parts) >= 2 else 0

        return BirthInfo(
            name=profile.name or "User",
            birth_date=profile.birth_date,
            birth_time=datetime.time(hour, minute),
            gender=gender,
            birth_place=profile.birth_place or "Seoul",
        )

    @staticmethod
    def _signal_to_dict(signal: "RhythmSignal") -> Dict[str, Any]:
        return {
            "energy_level": signal.energy_level,
            "focus_capacity": signal.focus_capacity,
            "social_energy": signal.social_energy,
            "decision_clarity": signal.decision_clarity,
            "favorable_times": signal.favorable_times,
            "caution_times": signal.caution_times,
            "favorable_directions": signal.favorable_directions,
            "main_theme": signal.main_theme,
            "opportunities": signal.opportunities,
            "challenges": signal.challenges,
            "saju_data": signal.saju_data,
        }

    @staticmethod
    def _fallback_rhythm(target_date: datetime.date) -> Dict[str, Any]:
        """Date-deterministic fallback rhythm."""
        day = target_date.day
        month = target_date.month

        # Simple deterministic variation
        energy = ((day * 7 + month * 3) % 5) + 1
        themes = ["안정과 정리", "새로운 시작", "관계와 소통", "집중과 실행", "변화와 성장"]
        theme = themes[(day + month) % len(themes)]

        opportunities_pool = [
            ["관계 강화", "학습", "자기 성찰"],
            ["새로운 만남", "창작", "기획"],
            ["소통", "협력", "정리"],
            ["집중", "실행", "결정"],
            ["변화 수용", "도전", "확장"],
        ]
        challenges_pool = [
            ["충동 조절", "과로"],
            ["불안감", "망설임"],
            ["갈등 관리", "피로"],
            ["완벽주의", "조급함"],
            ["불확실성", "외로움"],
        ]

        idx = (day + month) % 5

        fav_hours = [
            ["오전 9-11시", "오후 2-4시"],
            ["오전 10-12시"],
            ["오후 1-3시", "오후 5-6시"],
            ["오전 8-10시"],
            ["오전 11시-오후 1시"],
        ]
        cau_hours = [
            ["오후 5-7시"],
            ["오후 3-5시"],
            ["오전 7-9시"],
            ["오후 6-8시"],
            ["오후 4-6시"],
        ]
        directions = ["북동", "남서", "동", "서", "남동"]

        return {
            "energy_level": energy,
            "focus_capacity": ((day * 3 + month) % 5) + 1,
            "social_energy": ((day * 5 + month * 2) % 5) + 1,
            "decision_clarity": ((day * 2 + month * 7) % 5) + 1,
            "favorable_times": fav_hours[idx],
            "caution_times": cau_hours[idx],
            "favorable_directions": [directions[idx]],
            "main_theme": theme,
            "opportunities": opportunities_pool[idx],
            "challenges": challenges_pool[idx],
            "saju_data": {},
        }
