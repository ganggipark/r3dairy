"""
Content Block Generator

Generate individual content blocks with personalized Korean text.
All output uses user-friendly language; no internal terminology.
"""

from typing import Dict, Any, List, Optional
from .models import (
    PersonalizationContext,
    ContentBlock,
    ContentBlockType,
    EnergyLevel,
)
from ...content.char_optimizer import BLOCK_CHAR_TARGETS


class ContentBlockGenerator:
    """Generate individual content blocks."""

    # ==================================================================
    # 1. Summary
    # ==================================================================

    @staticmethod
    def generate_summary(
        context: PersonalizationContext,
        rhythm: Dict[str, Any],
        target_chars: Optional[int] = None,
    ) -> ContentBlock:
        energy = rhythm.get("energy_level", 3)
        theme = rhythm.get("main_theme", "균형")

        energy_adj = {5: "매우 활기찬", 4: "충만한", 3: "안정적인", 2: "차분한", 1: "고요한"}
        adj = energy_adj.get(energy, "안정적인")

        role = context.role.value
        role_suffix = {
            "student": "학습과 성장에 좋은 흐름이 있습니다.",
            "office_worker": "업무와 소통에 집중하기 좋은 날입니다.",
            "freelancer": "창작과 기획에 좋은 에너지가 흐릅니다.",
        }
        suffix = role_suffix.get(role, "하루를 의미 있게 보낼 수 있습니다.")
        text = f"오늘은 {adj} 에너지와 '{theme}'의 흐름이 함께하는 날입니다. {suffix}"

        return ContentBlock(
            id="block_01",
            type=ContentBlockType.SUMMARY,
            title="오늘의 한 줄 요약",
            content=text,
            tags=["summary", context.role.value],
            personalization_level=0.7,
        )

    # ==================================================================
    # 2. Keywords
    # ==================================================================

    @staticmethod
    def generate_keywords(
        context: PersonalizationContext,
        keywords: List[str],
        target_chars: Optional[int] = None,
    ) -> ContentBlock:
        return ContentBlock(
            id="block_02",
            type=ContentBlockType.KEYWORDS,
            title="오늘의 키워드",
            content=keywords,
            tags=["keywords"],
            personalization_level=0.8,
        )

    # ==================================================================
    # 3. Rhythm description (long paragraph, >= 200 chars)
    # ==================================================================

    @staticmethod
    def generate_rhythm_description(
        context: PersonalizationContext,
        rhythm: Dict[str, Any],
        target_chars: Optional[int] = None,
    ) -> ContentBlock:
        # Use target_chars from BLOCK_CHAR_TARGETS if not provided
        if target_chars is None:
            target_chars = BLOCK_CHAR_TARGETS.get("rhythm_description", {}).get("target", 300)

        energy = rhythm.get("energy_level", 3)
        theme = rhythm.get("main_theme", "균형")
        opportunities = rhythm.get("opportunities", [])
        challenges = rhythm.get("challenges", [])

        opp_text = ", ".join(opportunities[:3]) if opportunities else "내면 성장"
        chal_text = ", ".join(challenges[:2]) if challenges else "과도한 긴장"

        tone_map = {
            "analytical": "객관적으로 바라보면",
            "supportive": "마음 편히 받아들이면",
            "formal": "차분하게 접근하면",
            "casual": "가볍게 생각하면",
        }
        tone_phrase = tone_map.get(context.content_tone, "차분하게 바라보면")

        energy_desc = {
            5: "에너지가 매우 높아 적극적인 활동에 적합합니다",
            4: "에너지가 충분하여 새로운 시도가 가능합니다",
            3: "에너지가 안정적이어서 꾸준한 진행이 가능합니다",
            2: "에너지가 낮은 편이므로 무리하지 않는 것이 좋습니다",
            1: "에너지가 많이 낮으므로 휴식과 충전이 필요합니다",
        }
        e_desc = energy_desc.get(energy, energy_desc[3])

        # Role context sentence
        role = context.role.value
        role_context = {
            "student": "학습 계획을 세우고 집중 시간을 확보하면 효과적입니다.",
            "office_worker": "업무 우선순위를 정하고 핵심 과제에 먼저 집중하세요.",
            "freelancer": "창작이나 기획에 에너지를 집중하면 좋은 결과를 기대할 수 있습니다.",
        }
        r_ctx = role_context.get(role, "하루의 흐름을 따라가며 자연스럽게 행동하세요.")

        # Pain-point aware sentence
        pain_sentence = ""
        if "anxiety_management" in context.pain_points:
            pain_sentence = " 불안감이 올라올 수 있지만, 이는 자연스러운 반응입니다. 잠시 멈추고 호흡에 집중해보세요."
        elif "procrastination" in context.pain_points:
            pain_sentence = " 미루고 싶은 마음이 들 수 있지만, 작은 한 걸음부터 시작해보세요."

        # Seasonal context
        season_note = {
            "spring": "봄의 새로운 에너지가 하루를 감싸고 있습니다.",
            "summer": "여름의 활기찬 기운이 함께하는 시간입니다.",
            "autumn": "가을의 깊어지는 기운 속에서 내면을 돌아보세요.",
            "winter": "겨울의 고요한 에너지가 내면의 힘을 키워줍니다.",
        }
        s_note = season_note.get(context.seasonal_context, "")

        text = (
            f"오늘의 리듬은 '{theme}'을 중심으로 흐릅니다. {e_desc}. "
            f"{tone_phrase}, 오늘은 {opp_text}의 기회가 열려 있으며, "
            f"{chal_text}에 대한 주의가 필요합니다. "
            f"{r_ctx}{pain_sentence} "
            f"{s_note} "
            f"하루 전체의 흐름을 믿고, 자신만의 속도로 나아가세요. "
            f"작은 실천 하나가 오늘을 특별하게 만들어줄 것입니다."
        )

        return ContentBlock(
            id="block_03",
            type=ContentBlockType.RHYTHM_DESCRIPTION,
            title="오늘의 리듬 해설",
            content=text,
            tags=["rhythm", theme],
            personalization_level=0.8,
        )

    # ==================================================================
    # 4. Focus / Caution
    # ==================================================================

    @staticmethod
    def generate_focus_caution(
        focus_caution: Dict[str, List[str]],
        target_chars: Optional[int] = None,
    ) -> ContentBlock:
        return ContentBlock(
            id="block_04",
            type=ContentBlockType.FOCUS_CAUTION,
            title="집중 포인트 / 주의할 점",
            content=focus_caution,
            tags=["focus", "caution"],
            personalization_level=0.7,
        )

    # ==================================================================
    # 5. Action guide (Do / Avoid)
    # ==================================================================

    @staticmethod
    def generate_action_guide(
        action_guide: Dict[str, List[str]],
        target_chars: Optional[int] = None,
    ) -> ContentBlock:
        return ContentBlock(
            id="block_05",
            type=ContentBlockType.ACTION_GUIDE,
            title="행동 가이드",
            content=action_guide,
            tags=["action", "do", "avoid"],
            personalization_level=0.8,
        )

    # ==================================================================
    # 6. Time / Direction
    # ==================================================================

    @staticmethod
    def generate_time_direction(
        context: PersonalizationContext,
        rhythm: Dict[str, Any],
        target_chars: Optional[int] = None,
    ) -> ContentBlock:
        fav_times = rhythm.get("favorable_times", ["오전 9-11시"])
        cau_times = rhythm.get("caution_times", ["오후 5-7시"])
        fav_dirs = rhythm.get("favorable_directions", ["북동"])

        good_time = ", ".join(fav_times) if fav_times else "오전 10-12시"
        avoid_time = ", ".join(cau_times) if cau_times else "오후 5-7시"
        good_dir = fav_dirs[0] if fav_dirs else "북동"

        role = context.role.value
        note_map = {
            "student": "집중 학습은 좋은 시간대에, 복습은 저녁에 하면 효과적입니다.",
            "office_worker": "중요한 회의나 결정은 좋은 시간대에 배치하세요.",
            "freelancer": "창작 활동은 좋은 시간대에, 행정은 오후에 처리하세요.",
        }
        note = note_map.get(role, "집중이 필요한 활동은 좋은 시간대에 하세요.")

        data = {
            "good_time": good_time,
            "avoid_time": avoid_time,
            "good_direction": f"{good_dir}쪽",
            "avoid_direction": "반대쪽",
            "notes": note,
        }

        return ContentBlock(
            id="block_06",
            type=ContentBlockType.TIME_DIRECTION,
            title="시간 / 방향",
            content=data,
            tags=["time", "direction"],
            personalization_level=0.6,
        )

    # ==================================================================
    # 7. State trigger
    # ==================================================================

    @staticmethod
    def generate_state_trigger(
        context: PersonalizationContext,
        target_chars: Optional[int] = None,
    ) -> ContentBlock:
        # Personalize based on pain points and personality
        if "anxiety_management" in context.pain_points:
            gesture = "양손을 가슴에 모으고 천천히 세 번 호흡하세요"
            phrase = "지금 이 순간, 나는 안전합니다"
            how_to = "불안감이 올라올 때 눈을 감고 이 동작을 3번 반복하세요"
        elif "procrastination" in context.pain_points:
            gesture = "책상을 가볍게 두 번 두드리세요"
            phrase = "지금 시작하면 충분합니다"
            how_to = "미루고 싶을 때 이 동작과 함께 5분만 시작해보세요"
        elif "social_energy_drain" in context.pain_points:
            gesture = "두 손으로 따뜻한 음료를 감싸세요"
            phrase = "나만의 시간은 소중합니다"
            how_to = "사람들 사이에서 지칠 때 잠시 혼자만의 시간을 가지세요"
        else:
            gesture = "양손을 가슴에 대고 천천히 호흡하세요"
            phrase = "지금 이 순간, 나는 충분히 잘하고 있습니다"
            how_to = "긴장되거나 불안할 때 이 동작을 3번 반복하세요"

        data = {"gesture": gesture, "phrase": phrase, "how_to": how_to}

        return ContentBlock(
            id="block_07",
            type=ContentBlockType.STATE_TRIGGER,
            title="페이스 조절 (상태 트리거)",
            content=data,
            tags=["trigger", "self_care"],
            personalization_level=0.9,
        )

    # ==================================================================
    # 8. Meaning shift
    # ==================================================================

    @staticmethod
    def generate_meaning_shift(
        context: PersonalizationContext,
        rhythm: Dict[str, Any],
        target_chars: Optional[int] = None,
    ) -> ContentBlock:
        energy = rhythm.get("energy_level", 3)
        challenges = rhythm.get("challenges", [])
        challenge_text = challenges[0] if challenges else "작은 어려움"

        if energy >= 4:
            text = (
                f"오늘 느끼는 높은 에너지는 단순한 흥분이 아니라, "
                f"성장을 위한 추진력입니다. {challenge_text}이(가) 찾아오더라도 "
                f"이것은 더 나은 방향으로 가기 위한 자연스러운 과정입니다. "
                f"이 에너지를 믿고 한 걸음 더 나아가세요."
            )
        elif energy <= 2:
            text = (
                f"오늘의 차분한 에너지는 '무기력'이 아니라 '내면 충전'의 시간입니다. "
                f"{challenge_text}이(가) 마음을 흔들 수 있지만, "
                f"이 고요함 속에서 진짜 중요한 것을 발견할 수 있습니다. "
                f"급하지 않게 한 걸음씩 나아가는 것이 오늘의 지혜입니다."
            )
        else:
            text = (
                f"오늘은 균형 잡힌 에너지가 흐르는 날입니다. "
                f"{challenge_text}이(가) 나타나더라도 당황하지 마세요. "
                f"이것은 더 단단해지기 위한 과정이며, "
                f"지금의 안정감을 바탕으로 차근차근 대응하면 됩니다."
            )

        return ContentBlock(
            id="block_08",
            type=ContentBlockType.MEANING_SHIFT,
            title="의미 전환",
            content=text,
            tags=["reframe", "meaning"],
            personalization_level=0.8,
        )

    # ==================================================================
    # 9. Rhythm question
    # ==================================================================

    _ROLE_QUESTIONS: Dict[str, Dict[str, List[str]]] = {
        "student": {
            "high": [
                "오늘 가장 도전해보고 싶은 학습 목표는 무엇인가요?",
                "에너지가 높은 지금, 어떤 새로운 것을 시도해볼까요?",
            ],
            "medium": [
                "오늘 집중해서 마무리하고 싶은 과제는 무엇인가요?",
                "지금 가장 궁금한 것은 무엇인가요?",
            ],
            "low": [
                "오늘 나에게 가장 필요한 휴식은 어떤 모습인가요?",
                "지금 가장 편안함을 느끼는 순간은 언제인가요?",
            ],
        },
        "office_worker": {
            "high": [
                "오늘 주도적으로 이끌고 싶은 일은 무엇인가요?",
                "에너지가 높은 지금, 미뤄왔던 결정을 해볼까요?",
            ],
            "medium": [
                "오늘 가장 중요한 업무 한 가지는 무엇인가요?",
                "동료와 나누고 싶은 이야기가 있나요?",
            ],
            "low": [
                "오늘 나를 위해 할 수 있는 작은 일은 무엇인가요?",
                "지금 가장 쉬고 싶은 방법은 무엇인가요?",
            ],
        },
        "freelancer": {
            "high": [
                "오늘 영감을 받은 것이 있다면 무엇인가요?",
                "새롭게 시도해보고 싶은 프로젝트가 있나요?",
            ],
            "medium": [
                "지금 진행 중인 작업에서 가장 만족스러운 부분은?",
                "오늘 한 가지 마무리할 수 있는 일은 무엇인가요?",
            ],
            "low": [
                "나만의 시간에서 가장 소중한 순간은 언제인가요?",
                "오늘은 어떤 방식으로 재충전하고 싶나요?",
            ],
        },
    }

    @classmethod
    def generate_rhythm_question(
        cls,
        context: PersonalizationContext,
        rhythm: Dict[str, Any],
        target_chars: Optional[int] = None,
    ) -> ContentBlock:
        energy = rhythm.get("energy_level", 3)
        bucket = "high" if energy >= 4 else ("low" if energy <= 2 else "medium")
        role = context.role.value

        questions = cls._ROLE_QUESTIONS.get(role, cls._ROLE_QUESTIONS["office_worker"])
        q_list = questions.get(bucket, questions["medium"])
        # Pick based on date to give variety
        idx = context.target_date.day % len(q_list)
        question = q_list[idx]

        return ContentBlock(
            id="block_09",
            type=ContentBlockType.RHYTHM_QUESTION,
            title="오늘의 리듬 질문",
            content=question,
            tags=["question", "reflection"],
            personalization_level=0.9,
        )
