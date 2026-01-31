"""
Freelancer Translator - 프리랜서/자영업 역할 번역기
결정/계약/창작/체력 강조
"""
from typing import Dict

from ..models import RoleAdaptationRules
from .base_translator import BaseTranslator


class FreelancerTranslator(BaseTranslator):
    """프리랜서/자영업 역할 콘텐츠 번역기"""

    def __init__(self):
        super().__init__("freelancer")

    def _load_vocabulary(self) -> Dict[str, str]:
        return {
            # Activity
            "업무": "작업",
            "일": "프로젝트",
            "과제": "의뢰",
            "회의": "미팅",
            "협업": "파트너십",
            # Time
            "일정": "스케줄",
            "수업": "워크숍",
            # Results
            "성과": "수익",
            "결과물": "납품물",
            "보고": "피드백",
            # Relationships
            "동료": "클라이언트",
            "상사": "발주처",
            # Decision
            "결정": "계약/결정",
            "선택": "의사결정",
            # Extended
            "작업 완료": "프로젝트 마감",
            "작업 시작": "프로젝트 착수",
            "중요한 결정": "사업 의사결정",
            "집중 시간": "집중 작업 시간",
            "관계 조율": "클라이언트 관계",
            "체력 관리": "장기전 체력 관리",
            "계획 수립": "프로젝트 계획",
            "정리 정돈": "업무 정리",
            "새로운 시도": "새로운 사업 기회",
            "안정적인 흐름": "안정적인 작업 리듬",
            "활동적인 에너지": "적극적인 영업력",
            # Generic
            "스트레스": "마감/수익 불안",
            "관계": "클라이언트/협력 관계",
            "에너지": "창의력/동력",
        }

    def _load_rules(self) -> RoleAdaptationRules:
        return RoleAdaptationRules(
            role="freelancer",
            vocabulary_map=self._load_vocabulary(),
            emphasis_areas=["creativity", "autonomy", "business", "self_discipline"],
            de_emphasis_areas=["hierarchy", "meetings", "reports"],
            tone_preference="casual",
            time_focus="flexible",
            example_patterns=[
                "오늘은 {task}에 최적의 창의력을 발휘할 수 있는 날입니다.",
                "{time}이 가장 창작에 집중할 수 있는 시간입니다.",
                "{action}로 자기 규율을 유지하는 것이 중요합니다.",
            ],
            forbidden_terms=["보고서", "상사", "부서", "학교", "시험", "과제"],
        )

    def _adjust_tone(self, text: str) -> str:
        """프리랜서 캐주얼 톤"""
        return text
