"""
Student Translator - 학생 역할 번역기
학습/집중/페이스 관리 강조, 업무/계약 표현 최소화
"""
from typing import Dict

from ..models import RoleAdaptationRules
from .base_translator import BaseTranslator


class StudentTranslator(BaseTranslator):
    """학생 역할 콘텐츠 번역기"""

    def __init__(self):
        super().__init__("student")

    def _load_vocabulary(self) -> Dict[str, str]:
        return {
            # Activity
            "활동": "공부",
            "프로젝트": "과제",
            "업무": "학습",
            "일": "공부",
            "작업": "학습",
            "교류": "토론",
            "네트워킹": "스터디",
            # Time
            "일정": "수업",
            "약속": "모임",
            # Results
            "성과": "성적",
            "결과물": "과제물",
            "보고": "발표",
            # Energy
            "체력": "집중력",
            "에너지": "학습 의욕",
            # Extended
            "작업 완료": "과제 마무리",
            "작업 시작": "공부 시작",
            "중요한 결정": "진로 결정",
            "집중 시간": "집중 학습 시간",
            "관계 조율": "친구 관계",
            "체력 관리": "컨디션 관리",
            "계획 수립": "학습 계획",
            "정리 정돈": "노트 정리",
            "새로운 시도": "새로운 과목 도전",
            "안정적인 흐름": "안정적인 학습 리듬",
            "활동적인 에너지": "활발한 학습 에너지",
            # Decision/meeting generic
            "결정": "선택",
            "회의": "수업/스터디",
            "스트레스": "시험/과제 스트레스",
            "관계": "친구관계/소속감",
        }

    def _load_rules(self) -> RoleAdaptationRules:
        return RoleAdaptationRules(
            role="student",
            vocabulary_map=self._load_vocabulary(),
            emphasis_areas=["learning", "focus", "exam_prep", "time_management"],
            de_emphasis_areas=["business", "contracts", "negotiations"],
            tone_preference="supportive",
            time_focus="evening",
            example_patterns=[
                "오늘은 {task}를 시작하기 좋은 날입니다.",
                "{time}에 집중력이 최고조입니다.",
                "시험 준비를 할 때는 {action}이 도움이 됩니다.",
            ],
            forbidden_terms=["계약", "보고서", "회의실", "협상", "상사", "부서", "클라이언트"],
        )

    def _adjust_tone(self, text: str) -> str:
        """학생 친화적 톤 조정 - 지지적/격려적"""
        # Replace overly formal endings if present
        replacements = {
            "하십시오": "하세요",
            "바랍니다": "좋겠어요",
        }
        result = text
        for old, new in replacements.items():
            result = result.replace(old, new)
        return result
