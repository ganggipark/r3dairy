"""Student-specific content adaptations."""

from typing import Dict, List

STUDENT_KEYWORDS: Dict[str, List[str]] = {
    "high": ["집중", "학습", "도전", "성장", "열정"],
    "medium": ["복습", "휴식", "준비", "계획", "정리"],
    "low": ["정리", "휴식", "회복", "충전", "자기돌봄"],
}

STUDENT_ACTION_GUIDES: Dict[str, Dict[str, List[str]]] = {
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
}

STUDENT_QUESTIONS: Dict[str, List[str]] = {
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
}

STUDENT_FOCUS_AREAS: List[str] = [
    "집중 학습 시간 확보",
    "효율적인 복습 계획",
    "학습 목표 설정",
]

STUDENT_CAUTION_AREAS: List[str] = [
    "과도한 비교 금지",
    "번아웃 주의",
    "SNS 사용 자제",
]
