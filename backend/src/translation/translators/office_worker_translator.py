"""
Office Worker Translator - 직장인 역할 번역기
업무/관계/결정/보고 강조
"""
from typing import Dict

from ..models import RoleAdaptationRules
from .base_translator import BaseTranslator


class OfficeWorkerTranslator(BaseTranslator):
    """직장인 역할 콘텐츠 번역기"""

    def __init__(self):
        super().__init__("office_worker")

    def _load_vocabulary(self) -> Dict[str, str]:
        return {
            # Activity
            "학습": "업무",
            "공부": "일",
            "과제": "프로젝트",
            "토론": "회의",
            "스터디": "협업",
            # Time
            "수업": "일정",
            "모임": "미팅",
            # Results
            "성적": "성과",
            "과제물": "결과물",
            "발표": "보고",
            # Relationships
            "친구": "동료",
            "선생님": "상사",
            # Extended
            "작업 완료": "업무 마무리",
            "작업 시작": "업무 착수",
            "중요한 결정": "업무 의사결정",
            "집중 시간": "집중 업무 시간",
            "관계 조율": "동료 관계",
            "체력 관리": "업무 체력 관리",
            "계획 수립": "업무 계획",
            "정리 정돈": "자료 정리",
            "새로운 시도": "새로운 프로젝트 도전",
            "안정적인 흐름": "안정적인 업무 리듬",
            "활동적인 에너지": "적극적인 업무 추진력",
            # Generic
            "결정": "중요한 결정",
            "스트레스": "업무 스트레스",
            "관계": "직장 관계",
        }

    def _load_rules(self) -> RoleAdaptationRules:
        return RoleAdaptationRules(
            role="office_worker",
            vocabulary_map=self._load_vocabulary(),
            emphasis_areas=["work", "decision_making", "relationships", "meetings"],
            de_emphasis_areas=["creative", "casual", "play"],
            tone_preference="formal",
            time_focus="morning",
            example_patterns=[
                "오늘은 {decision}를 하기 좋은 날입니다.",
                "{time}에 회의나 중요한 대화를 하는 것이 좋습니다.",
                "{action}으로 직장 관계를 개선할 수 있습니다.",
            ],
            forbidden_terms=["시험", "과제", "학교", "친구들", "클라이언트", "마감"],
        )

    def _adjust_tone(self, text: str) -> str:
        """직장인 공식적 톤 유지"""
        return text
