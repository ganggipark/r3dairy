"""
Content Assembly Engine - 데이터 모델
DailyContent 및 관련 모델 정의 (DAILY_CONTENT_SCHEMA.json 기반)
"""
from pydantic import BaseModel, Field, field_validator
from datetime import date
from typing import List, Optional, Dict, Any


class FocusCaution(BaseModel):
    """집중/주의 포인트"""
    focus: List[str] = Field(default_factory=list, description="집중할 영역")
    caution: List[str] = Field(default_factory=list, description="주의할 영역")


class ActionGuide(BaseModel):
    """행동 가이드 (Do/Avoid)"""
    do: List[str] = Field(default_factory=list, description="추천 행동")
    avoid: List[str] = Field(default_factory=list, description="피할 행동")


class TimeDirection(BaseModel):
    """시간/방향 정보"""
    good_time: str = Field(..., description="좋은 시간대")
    avoid_time: str = Field(..., description="피할 시간대")
    good_direction: str = Field(..., description="좋은 방향")
    avoid_direction: str = Field(..., description="피할 방향")
    notes: str = Field(default="", description="추가 설명")


class StateTrigger(BaseModel):
    """상태 트리거 (페이스 조절 기법)"""
    gesture: str = Field(..., description="제스처/동작")
    phrase: str = Field(..., description="문구/주문")
    how_to: str = Field(..., description="사용 방법")


class LengthRequirements(BaseModel):
    """길이 요구사항"""
    left_page_min_chars: int = Field(default=400, description="좌측 페이지 최소 글자 수")
    left_page_target_chars: int = Field(default=900, description="좌측 페이지 목표 글자 수")
    left_page_rule: str = Field(
        default="Left page must include explanatory sentences; no card-only summaries.",
        description="좌측 페이지 규칙"
    )


class DailyContent(BaseModel):
    """
    일간 콘텐츠 (사용자 노출)

    ✅ 이 모델은 사용자에게 노출됩니다!
    ⚠️ 내부 전문 용어 사용 금지 (사주명리, 기문둔갑 등)
    ✅ 일반적인 언어 사용 (흐름, 리듬, 에너지, 집중 등)

    DAILY_CONTENT_SCHEMA.json을 준수합니다.
    """
    date: date = Field(..., description="날짜 (YYYY-MM-DD)")

    # 1. 요약
    summary: str = Field(
        ...,
        min_length=30,
        max_length=200,
        description="오늘의 한 줄 요약"
    )

    # 2. 키워드
    keywords: List[str] = Field(
        ...,
        min_length=2,
        max_length=5,
        description="오늘의 키워드 (2-5개)"
    )

    # 3. 리듬 해설
    rhythm_description: str = Field(
        ...,
        min_length=100,
        max_length=500,
        description="오늘의 리듬 상세 해설 (설명형 문단)"
    )

    # 4. 집중/주의 포인트
    focus_caution: FocusCaution = Field(..., description="집중/주의 포인트")

    # 5. 행동 가이드
    action_guide: ActionGuide = Field(..., description="행동 가이드 (Do/Avoid)")

    # 6. 시간/방향
    time_direction: TimeDirection = Field(..., description="시간/방향 정보")

    # 7. 상태 트리거
    state_trigger: StateTrigger = Field(..., description="상태 트리거 (페이스 조절)")

    # 8. 의미 전환
    meaning_shift: str = Field(
        ...,
        min_length=50,
        max_length=300,
        description="불안/충동을 재해석하는 문장"
    )

    # 9. 리듬 질문
    rhythm_question: str = Field(
        ...,
        min_length=20,
        max_length=150,
        description="자기 성찰을 위한 질문"
    )

    # 10. 길이 요구사항 (메타데이터)
    length_requirements: LengthRequirements = Field(default_factory=LengthRequirements)

    @field_validator('keywords')
    @classmethod
    def validate_keywords_count(cls, v):
        """키워드 개수 검증 (2-5개)"""
        if not (2 <= len(v) <= 5):
            raise ValueError("키워드는 2-5개여야 합니다")
        return v

    def get_total_text_length(self) -> int:
        """좌측 페이지 총 텍스트 길이 계산"""
        total = 0
        total += len(self.summary)
        total += sum(len(k) for k in self.keywords)
        total += len(self.rhythm_description)
        total += sum(len(f) for f in self.focus_caution.focus)
        total += sum(len(c) for c in self.focus_caution.caution)
        total += sum(len(d) for d in self.action_guide.do)
        total += sum(len(a) for a in self.action_guide.avoid)
        total += len(self.time_direction.good_time)
        total += len(self.time_direction.avoid_time)
        total += len(self.time_direction.good_direction)
        total += len(self.time_direction.avoid_direction)
        total += len(self.time_direction.notes)
        total += len(self.state_trigger.gesture)
        total += len(self.state_trigger.phrase)
        total += len(self.state_trigger.how_to)
        total += len(self.meaning_shift)
        total += len(self.rhythm_question)
        return total

    def validate_length_requirements(self) -> tuple[bool, int, str]:
        """
        길이 요구사항 검증

        Returns:
            (통과 여부, 총 글자 수, 메시지)
        """
        total_length = self.get_total_text_length()
        min_required = self.length_requirements.left_page_min_chars
        target = self.length_requirements.left_page_target_chars

        if total_length < min_required:
            return (
                False,
                total_length,
                f"좌측 페이지 글자 수 부족: {total_length}자 (최소 {min_required}자 필요)"
            )
        elif total_length < target:
            return (
                True,
                total_length,
                f"길이 요구사항 충족 (목표 미달): {total_length}자 (목표 {target}자)"
            )
        else:
            return (
                True,
                total_length,
                f"길이 요구사항 충족: {total_length}자"
            )

    class Config:
        json_schema_extra = {
            "example": {
                "date": "2026-01-20",
                "summary": "오늘은 안정과 정리가 필요한 날입니다. 새로운 시작보다는 기존 작업을 마무리하는 데 집중하세요.",
                "keywords": ["안정", "정리", "마무리"],
                "rhythm_description": "오늘의 리듬은 차분하고 안정적입니다. 에너지가 내부로 향하며, 외부 활동보다는 내면 정리와 기존 작업 완성에 적합한 흐름입니다. 급하게 새로운 일을 시작하기보다는 지금까지 해온 일들을 점검하고 마무리하는 시간으로 활용하면 좋습니다.",
                "focus_caution": {
                    "focus": ["기존 작업 완료", "정리 정돈", "내면 성찰"],
                    "caution": ["새로운 시작", "큰 결정", "과도한 약속"]
                },
                "action_guide": {
                    "do": ["할 일 목록 정리", "미루던 일 마무리", "공간 정리"],
                    "avoid": ["충동 구매", "중요한 계약", "큰 변화 시도"]
                },
                "time_direction": {
                    "good_time": "오전 9-11시, 오후 2-4시",
                    "avoid_time": "오후 5-7시",
                    "good_direction": "북동쪽",
                    "avoid_direction": "남서쪽",
                    "notes": "집중이 필요한 작업은 오전 시간대에 하세요"
                },
                "state_trigger": {
                    "gesture": "양손을 가슴에 모으고 천천히 호흡",
                    "phrase": "지금 이 순간, 나는 충분히 잘하고 있다",
                    "how_to": "불안감이 올라올 때 3번 반복하세요"
                },
                "meaning_shift": "오늘의 차분한 에너지는 '무기력'이 아니라 '내면 충전'의 시간입니다. 급하지 않게 한 걸음씩 나아가는 것이 오늘의 지혜입니다.",
                "rhythm_question": "오늘 마무리하고 싶은 일은 무엇인가요? 그것을 완성하면 어떤 기분이 들까요?"
            }
        }


class MonthlyContent(BaseModel):
    """월간 콘텐츠 (사용자 노출)"""
    year: int
    month: int
    theme: str = Field(..., min_length=50, max_length=300, description="이번 달 테마 해설")
    priorities: List[str] = Field(..., min_length=3, max_length=3, description="월간 우선순위 3개")
    calendar_keywords: Dict[int, str] = Field(
        default_factory=dict,
        description="날짜별 키워드 (1-31)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "year": 2026,
                "month": 1,
                "theme": "2026년 1월은 새로운 시작과 계획을 위한 달입니다. 지난 해를 정리하고 올해의 방향을 설정하기에 좋은 에너지가 흐릅니다.",
                "priorities": [
                    "연간 목표 구체화",
                    "건강 루틴 확립",
                    "관계 정리 및 강화"
                ],
                "calendar_keywords": {
                    1: "새 시작",
                    2: "계획",
                    15: "점검"
                }
            }
        }


class YearlyContent(BaseModel):
    """연간 콘텐츠 (사용자 노출)"""
    year: int
    summary: str = Field(..., min_length=100, max_length=500, description="연간 흐름 요약")
    keywords: List[str] = Field(..., min_length=3, max_length=5, description="연간 키워드")
    monthly_themes: Dict[int, str] = Field(
        default_factory=dict,
        description="월별 테마 (1-12)"
    )
    growth_focus: List[str] = Field(default_factory=list, description="성장 집중 영역")

    class Config:
        json_schema_extra = {
            "example": {
                "year": 2026,
                "summary": "2026년은 확장과 실험의 해입니다. 새로운 기회를 탐색하고, 기존 틀을 벗어나 시도하는 것이 성장으로 이어지는 한 해입니다.",
                "keywords": ["확장", "실험", "학습", "관계"],
                "monthly_themes": {
                    1: "새 시작",
                    2: "관계 강화",
                    3: "학습 집중"
                },
                "growth_focus": ["전문성 강화", "네트워크 확대", "자기 관리"]
            }
        }
