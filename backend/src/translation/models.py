"""
Role Translation Models
역할별 표현 변환을 위한 데이터 모델
"""
from enum import Enum
from datetime import date
from typing import Dict, List, Optional, Any, Tuple
from pydantic import BaseModel, Field


class Role(str, Enum):
    """사용자 역할 정의"""
    STUDENT = "student"
    OFFICE_WORKER = "office_worker"
    FREELANCER = "freelancer"


class ExpressionMapping(BaseModel):
    """표현 매핑 (내부 표현 -> 역할별 표현)"""
    internal: str
    student: str
    office_worker: str
    freelancer: str


class RoleTemplate(BaseModel):
    """역할별 템플릿"""
    role: Role
    expressions: Dict[str, str] = Field(
        description="핵심 표현 매핑 (일반 표현 -> 역할별 표현)"
    )
    action_keywords: List[str] = Field(
        description="역할에 맞는 행동 키워드"
    )
    avoid_keywords: List[str] = Field(
        description="역할에 맞는 주의 키워드"
    )
    question_templates: List[str] = Field(
        description="역할에 맞는 질문 패턴"
    )
    example_sentences: Dict[str, List[str]] = Field(
        description="상황별 예시 문장"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "role": "student",
                "expressions": {
                    "작업 완료": "과제 마무리",
                    "중요한 결정": "진로 결정"
                },
                "action_keywords": ["학습", "복습", "정리"],
                "avoid_keywords": ["무리한 일정", "과도한 비교"],
                "question_templates": [
                    "오늘 집중해서 공부할 과목은 무엇인가요?"
                ]
            }
        }


class TranslationContext(BaseModel):
    """변환 컨텍스트"""
    source_role: str = "generic"
    target_role: str
    original_content: Optional[Dict[str, Any]] = None
    personality_traits: Dict[str, float] = Field(default_factory=dict)
    customer_role: str = ""
    target_date: Optional[date] = None
    user_preferences: Dict[str, Any] = Field(default_factory=dict)


class TranslationResult(BaseModel):
    """변환 결과"""
    success: bool
    translated_content: Dict[str, Any] = Field(default_factory=dict)
    semantic_preserved: bool = True
    tone_matched: bool = True
    role_alignment_score: float = 0.0
    issues: List[str] = Field(default_factory=list)
    mapping_used: Optional[Dict[str, str]] = None


class RoleAdaptationRules(BaseModel):
    """역할별 콘텐츠 적응 규칙"""
    role: str
    vocabulary_map: Dict[str, str]
    emphasis_areas: List[str]
    de_emphasis_areas: List[str]
    tone_preference: str  # "formal", "casual", "supportive"
    time_focus: Optional[str] = None  # "morning", "evening", "flexible"
    example_patterns: List[str] = Field(default_factory=list)
    forbidden_terms: List[str] = Field(default_factory=list)
