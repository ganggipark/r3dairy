"""Freelancer-specific content adaptations."""

from typing import Dict, List

FREELANCER_KEYWORDS: Dict[str, List[str]] = {
    "high": ["창작", "도전", "성장", "확장", "영감"],
    "medium": ["진행", "관계", "정리", "기획", "소통"],
    "low": ["회복", "자기관리", "휴식", "재정비", "성찰"],
}

FREELANCER_ACTION_GUIDES: Dict[str, Dict[str, List[str]]] = {
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
}

FREELANCER_QUESTIONS: Dict[str, List[str]] = {
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
}
