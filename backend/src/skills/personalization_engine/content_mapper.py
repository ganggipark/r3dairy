"""
Content Mapper

Map personality traits and role characteristics to content decisions.
"""

from typing import List, Dict, Any
from .models import PersonalizationContext, PersonalityProfile, Role, EnergyLevel


class ContentMapper:
    """Map personality traits to content block decisions."""

    # ------------------------------------------------------------------
    # Keywords
    # ------------------------------------------------------------------

    _ROLE_KEYWORDS: Dict[str, Dict[str, List[str]]] = {
        "student": {
            "high": ["집중", "도전", "학습", "성장", "열정"],
            "medium": ["복습", "준비", "계획", "균형", "정리"],
            "low": ["휴식", "회복", "정리", "충전", "자기돌봄"],
        },
        "office_worker": {
            "high": ["결정", "주도", "소통", "성과", "실행"],
            "medium": ["협력", "진행", "정리", "조율", "점검"],
            "low": ["반성", "휴식", "회복", "재충전", "관망"],
        },
        "freelancer": {
            "high": ["창작", "도전", "성장", "확장", "영감"],
            "medium": ["진행", "관계", "정리", "기획", "소통"],
            "low": ["회복", "자기관리", "휴식", "재정비", "성찰"],
        },
    }

    @classmethod
    def map_to_keywords(
        cls,
        context: PersonalizationContext,
        rhythm_energy: int = 3,
    ) -> List[str]:
        """Generate 3-5 personalized keywords."""
        role = context.role.value
        if rhythm_energy >= 4:
            bucket = "high"
        elif rhythm_energy <= 2:
            bucket = "low"
        else:
            bucket = "medium"

        pool = cls._ROLE_KEYWORDS.get(role, cls._ROLE_KEYWORDS["office_worker"])
        base = pool.get(bucket, pool["medium"])

        # Add interest-based keyword if available
        if context.interests:
            interest_kw = _INTEREST_KEYWORD_MAP.get(context.interests[0])
            if interest_kw and interest_kw not in base:
                base = base[:4] + [interest_kw]

        return base[:5]

    # ------------------------------------------------------------------
    # Action guide
    # ------------------------------------------------------------------

    _ROLE_ACTIONS: Dict[str, Dict[str, Dict[str, List[str]]]] = {
        "student": {
            "high": {
                "do": ["새로운 과목에 도전하기", "어려운 문제에 집중하기", "스터디 그룹 참여하기"],
                "avoid": ["무리한 일정 세우기", "밤샘 공부"],
            },
            "medium": {
                "do": ["복습 시간 확보하기", "노트 정리하기", "질문 목록 만들기"],
                "avoid": ["새로운 과목 무리하게 시작", "집중력 분산"],
            },
            "low": {
                "do": ["가벼운 복습하기", "산책으로 기분 전환하기", "내일 계획 세우기"],
                "avoid": ["시험 준비 억지로 하기", "자신을 비교하기"],
            },
        },
        "office_worker": {
            "high": {
                "do": ["중요한 회의 주도하기", "결정을 미루지 않기", "팀원과 아이디어 공유하기"],
                "avoid": ["지나친 완벽주의", "불필요한 야근"],
            },
            "medium": {
                "do": ["할 일 우선순위 정리하기", "동료와 소통하기", "진행 상황 점검하기"],
                "avoid": ["새로운 프로젝트 무리하게 수락", "감정적 이메일 보내기"],
            },
            "low": {
                "do": ["단순 업무 처리하기", "점심 시간에 산책하기", "내일 일정 확인하기"],
                "avoid": ["중요한 결정", "과도한 약속"],
            },
        },
        "freelancer": {
            "high": {
                "do": ["새로운 프로젝트 기획하기", "클라이언트에게 제안하기", "창작에 집중하기"],
                "avoid": ["저가 의뢰 수락", "무리한 납기 약속"],
            },
            "medium": {
                "do": ["진행 중인 작업 마무리하기", "네트워킹하기", "포트폴리오 정리하기"],
                "avoid": ["계약 조건 양보", "일과 생활 경계 무너뜨리기"],
            },
            "low": {
                "do": ["자료 정리하기", "영감 수집하기", "건강 관리하기"],
                "avoid": ["중요한 계약 체결", "새 프로젝트 시작"],
            },
        },
    }

    @classmethod
    def map_to_action_guide(
        cls,
        context: PersonalizationContext,
        rhythm_energy: int = 3,
    ) -> Dict[str, List[str]]:
        role = context.role.value
        bucket = "high" if rhythm_energy >= 4 else ("low" if rhythm_energy <= 2 else "medium")
        role_actions = cls._ROLE_ACTIONS.get(role, cls._ROLE_ACTIONS["office_worker"])
        return role_actions.get(bucket, role_actions["medium"])

    # ------------------------------------------------------------------
    # Focus / caution points
    # ------------------------------------------------------------------

    @classmethod
    def map_to_focus_points(
        cls,
        context: PersonalizationContext,
        rhythm_energy: int = 3,
    ) -> Dict[str, List[str]]:
        """Generate focus and caution lists."""
        focus: List[str] = []
        caution: List[str] = []

        # Personality-driven
        p = context.customer_profile.personality
        if p.conscientiousness >= 65:
            focus.append("계획한 일 실행하기")
        else:
            focus.append("오늘 하나만 완수하기")

        if p.openness >= 65:
            focus.append("새로운 아이디어 탐색하기")
        else:
            focus.append("기존 방식 점검하기")

        if p.neuroticism >= 60:
            caution.append("불안할 때 깊은 호흡하기")
        if p.extraversion <= 40:
            caution.append("에너지 소모되는 만남 줄이기")

        # Role-driven
        role = context.role.value
        if role == "student":
            focus.append("집중 학습 시간 확보")
            caution.append("과도한 비교 금지")
        elif role == "office_worker":
            focus.append("핵심 업무 우선 처리")
            caution.append("불필요한 회의 참석")
        elif role == "freelancer":
            focus.append("창작 시간 보호하기")
            caution.append("저가 수주 유혹")

        # Energy-driven
        if rhythm_energy <= 2:
            caution.append("무리한 일정 피하기")

        return {"focus": focus[:3], "caution": caution[:3]}

    # ------------------------------------------------------------------
    # Tone mapping
    # ------------------------------------------------------------------

    @staticmethod
    def map_personality_to_tone(personality: PersonalityProfile) -> str:
        if personality.analytical_vs_intuitive >= 65:
            return "analytical"
        if personality.extraversion >= 65 and personality.agreeableness >= 60:
            return "supportive"
        if personality.conscientiousness >= 65 and personality.openness < 50:
            return "formal"
        if personality.openness >= 65:
            return "casual"
        return "supportive"

    # ------------------------------------------------------------------
    # Topic emphasis
    # ------------------------------------------------------------------

    @staticmethod
    def should_emphasize_topic(
        topic: str,
        interests: List[str],
        personality: PersonalityProfile,
    ) -> bool:
        if topic in interests:
            return True
        topic_personality_map = {
            "career": personality.proactive_vs_reactive >= 60,
            "finance": personality.conscientiousness >= 60,
            "health": personality.neuroticism >= 55,
            "creativity": personality.openness >= 60,
            "relationships": personality.agreeableness >= 60,
        }
        return topic_personality_map.get(topic, False)


# ---------------------------------------------------------------------------
# Interest -> keyword mapping
# ---------------------------------------------------------------------------

_INTEREST_KEYWORD_MAP: Dict[str, str] = {
    "career": "성장",
    "finance": "재정",
    "personal_growth": "자기개발",
    "health": "건강",
    "creativity": "창작",
    "relationships": "관계",
    "technology": "기술",
    "travel": "탐험",
    "education": "학습",
    "spirituality": "내면",
}
