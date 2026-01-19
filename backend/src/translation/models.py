"""
Role Translation Models
역할별 표현 변환을 위한 데이터 모델
"""
from enum import Enum
from typing import Dict, List, Any
from pydantic import BaseModel, Field


class Role(str, Enum):
    """사용자 역할 정의"""
    STUDENT = "student"  # 학생
    OFFICE_WORKER = "office_worker"  # 직장인
    FREELANCER = "freelancer"  # 프리랜서/자영업


class ExpressionMapping(BaseModel):
    """표현 매핑 (내부 표현 → 역할별 표현)"""
    internal: str  # 내부 표현 (중립적 표현)
    student: str  # 학생용 표현
    office_worker: str  # 직장인용 표현
    freelancer: str  # 프리랜서용 표현


class RoleTemplate(BaseModel):
    """역할별 템플릿"""
    role: Role

    # 표현 매핑 사전
    expressions: Dict[str, str] = Field(
        description="핵심 표현 매핑 (일반 표현 → 역할별 표현)"
    )

    # 추천 행동 키워드
    action_keywords: List[str] = Field(
        description="역할에 맞는 행동 키워드"
    )

    # 피할 행동 키워드
    avoid_keywords: List[str] = Field(
        description="역할에 맞는 주의 키워드"
    )

    # 질문 템플릿
    question_templates: List[str] = Field(
        description="역할에 맞는 질문 패턴 (변수: {theme}, {action}, {focus})"
    )

    # 예시 문장 템플릿
    example_sentences: Dict[str, List[str]] = Field(
        description="상황별 예시 문장 (focus, caution, do, avoid 등)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "role": "student",
                "expressions": {
                    "작업 완료": "과제 마무리",
                    "중요한 결정": "진로 결정",
                    "휴식 필요": "재충전 필요"
                },
                "action_keywords": ["학습", "복습", "정리", "집중"],
                "avoid_keywords": ["무리한 일정", "과도한 비교", "집중력 분산"],
                "question_templates": [
                    "오늘 집중해서 공부할 과목은 무엇인가요?",
                    "이번 주 목표를 달성하려면 어떤 준비가 필요한가요?"
                ]
            }
        }


class TranslationContext(BaseModel):
    """변환 컨텍스트 (변환에 필요한 추가 정보)"""
    target_role: Role
    user_preferences: Dict[str, Any] = Field(default_factory=dict)
    # 사용자 관심사, 상황 등

    class Config:
        json_schema_extra = {
            "example": {
                "target_role": "student",
                "user_preferences": {
                    "interests": ["수학", "과학"],
                    "grade": "고3",
                    "exam_period": False
                }
            }
        }
