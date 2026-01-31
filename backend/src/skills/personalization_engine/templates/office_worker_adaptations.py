"""Office worker-specific content adaptations."""

from typing import Dict, List

OFFICE_WORKER_KEYWORDS: Dict[str, List[str]] = {
    "high": ["결정", "주도", "소통", "성과", "실행"],
    "medium": ["협력", "진행", "정리", "조율", "점검"],
    "low": ["반성", "휴식", "회복", "재충전", "관망"],
}

OFFICE_WORKER_ACTION_GUIDES: Dict[str, Dict[str, List[str]]] = {
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
}

OFFICE_WORKER_QUESTIONS: Dict[str, List[str]] = {
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
}
