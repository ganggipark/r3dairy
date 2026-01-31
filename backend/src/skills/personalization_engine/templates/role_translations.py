"""
Role Translation Mapping

Maps generic concepts to role-specific expressions.
Used to ensure consistent language across all content blocks.
"""

from typing import Dict

ROLE_TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "meeting": {
        "student": "수업/스터디",
        "office_worker": "회의/보고",
        "freelancer": "미팅/협의",
    },
    "decision": {
        "student": "선택/방향 결정",
        "office_worker": "중요한 결정",
        "freelancer": "프로젝트/사업 결정",
    },
    "task": {
        "student": "과제/공부",
        "office_worker": "업무/프로젝트",
        "freelancer": "작업/의뢰",
    },
    "colleague": {
        "student": "친구/동기",
        "office_worker": "동료/상사",
        "freelancer": "클라이언트/파트너",
    },
    "rest": {
        "student": "재충전/기분전환",
        "office_worker": "휴식/워라밸",
        "freelancer": "자기관리/재정비",
    },
    "achievement": {
        "student": "성적/학습 성과",
        "office_worker": "성과/실적",
        "freelancer": "수익/작품 완성",
    },
    "stress": {
        "student": "시험 압박/진로 고민",
        "office_worker": "업무 과중/인간관계",
        "freelancer": "수입 불안/마감 압박",
    },
}


def translate_concept(concept: str, role: str) -> str:
    """Translate a generic concept to role-specific expression."""
    mapping = ROLE_TRANSLATIONS.get(concept, {})
    return mapping.get(role, concept)
