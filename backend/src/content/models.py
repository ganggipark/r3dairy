"""
Content Assembly Engine - 데이터 모델
DailyContent 및 관련 모델 정의 (DAILY_CONTENT_SCHEMA.json 기반)
"""
from pydantic import BaseModel, Field, field_validator
import datetime
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


# 새로운 10개 라이프스타일 카테고리 모델들

class DailyHealthSports(BaseModel):
    """운동/건강"""
    recommended_activities: List[str] = Field(..., min_length=2, description="추천 활동")
    health_tips: List[str] = Field(..., min_length=2, description="건강 팁")
    wellness_focused: List[str] = Field(..., min_length=1, description="웰니스 집중")
    explanation: str = Field(..., min_length=50, description="설명")


class DailyMealNutrition(BaseModel):
    """음식/영양/건강식단"""
    flavor_profile: List[str] = Field(..., min_length=2, description="맛 프로필")
    food_recommendations: List[str] = Field(..., min_length=2, description="음식 추천")
    nutritional_tips: List[str] = Field(..., min_length=2, description="영양 팁")
    avoid_foods: List[str] = Field(default_factory=list, description="피해야 할 음식")
    explanation: str = Field(..., min_length=50, description="설명")


class DailyFashionBeauty(BaseModel):
    """의류/뷰티/화장"""
    clothing_style: List[str] = Field(..., min_length=2, description="의류 스타일")
    color_recommendations: List[str] = Field(..., min_length=2, description="색상 추천")
    grooming_tips: List[str] = Field(..., min_length=2, description="그루밍 팁")
    avoid_styles: List[str] = Field(default_factory=list, description="피해야 할 스타일")
    explanation: str = Field(..., min_length=50, description="설명")


class DailyShoppingFinance(BaseModel):
    """쇼핑/재테크/소비"""
    good_purchases: List[str] = Field(..., min_length=2, description="좋은 구매")
    spending_tips: List[str] = Field(..., min_length=2, description="소비 팁")
    value_recommendations: List[str] = Field(..., min_length=1, description="가치 추천")
    avoid_purchases: List[str] = Field(default_factory=list, description="피해야 할 구매")
    explanation: str = Field(..., min_length=50, description="설명")


class DailyLivingSpace(BaseModel):
    """주거/인테리어/식물"""
    interior_style: List[str] = Field(..., min_length=2, description="인테리어 스타일")
    plant_recommendations: List[str] = Field(..., min_length=2, description="식물 추천")
    organization_tips: List[str] = Field(..., min_length=2, description="정리 팁")
    explanation: str = Field(..., min_length=50, description="설명")


class DailyRoutines(BaseModel):
    """수면/기상/일상루틴"""
    sleep_pattern: List[str] = Field(..., min_length=2, description="수면 패턴")
    morning_routine: List[str] = Field(..., min_length=2, description="아침 루틴")
    evening_routine: List[str] = Field(..., min_length=2, description="저녁 루틴")
    explanation: str = Field(..., min_length=50, description="설명")


class DigitalCommunication(BaseModel):
    """스마트폰/SNS/온라인"""
    phone_usage_tips: List[str] = Field(..., min_length=2, description="폰 사용 팁")
    social_media_guidance: List[str] = Field(..., min_length=2, description="소셜미디어 가이드")
    app_recommendations: List[str] = Field(..., min_length=2, description="앱 추천")
    optimal_timing: str = Field(..., description="최적 타이밍")
    explanation: str = Field(..., min_length=50, description="설명")


class HobbiesCreativity(BaseModel):
    """취미/창작/학습"""
    creative_hobbies: List[str] = Field(..., min_length=2, description="창작 취미")
    learning_activities: List[str] = Field(..., min_length=2, description="학습 활동")
    recommended_time: str = Field(..., description="추천 시간")
    social_hobbies: List[str] = Field(default_factory=list, description="사교 취미")
    explanation: str = Field(..., min_length=50, description="설명")


class RelationshipsSocial(BaseModel):
    """인간관계/소통"""
    relationship_focus: List[str] = Field(..., min_length=2, description="관계 집중")
    communication_style: List[str] = Field(..., min_length=2, description="소통 스타일")
    social_activities: List[str] = Field(..., min_length=2, description="사교 활동")
    avoid_situations: List[str] = Field(default_factory=list, description="피해야 할 상황")
    explanation: str = Field(..., min_length=50, description="설명")


class SeasonalEnvironment(BaseModel):
    """날씨/계절/환경"""
    weather_adaptation: List[str] = Field(..., min_length=2, description="날씨 적응")
    seasonal_activities: List[str] = Field(..., min_length=2, description="계절 활동")
    environment_setup: List[str] = Field(..., min_length=2, description="환경 설정")
    outdoor_recommendations: List[str] = Field(..., min_length=2, description="야외 추천")
    explanation: str = Field(..., min_length=50, description="설명")


class DailyContent(BaseModel):
    """
    일간 콘텐츠 (사용자 노출)

    ✅ 이 모델은 사용자에게 노출됩니다!
    ⚠️ 내부 전문 용어 사용 금지 (사주명리, 기문둔갑 등)
    ✅ 일반적인 언어 사용 (흐름, 리듬, 에너지, 집중 등)

    DAILY_CONTENT_SCHEMA.json을 준수합니다.
    """
    date: datetime.date = Field(..., description="날짜 (YYYY-MM-DD)")

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
        min_length=200,
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
        min_length=80,
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

    # 새로운 10개 라이프스타일 카테고리
    daily_health_sports: DailyHealthSports = Field(..., description="운동/건강")
    daily_meal_nutrition: DailyMealNutrition = Field(..., description="음식/영양")
    daily_fashion_beauty: DailyFashionBeauty = Field(..., description="의류/뷰티")
    daily_shopping_finance: DailyShoppingFinance = Field(..., description="쇼핑/재테크")
    daily_living_space: DailyLivingSpace = Field(..., description="주거공간")
    daily_routines: DailyRoutines = Field(..., description="일상루틴")
    digital_communication: DigitalCommunication = Field(..., description="디지털소통")
    hobbies_creativity: HobbiesCreativity = Field(..., description="취미/창작")
    relationships_social: RelationshipsSocial = Field(..., description="인간관계")
    seasonal_environment: SeasonalEnvironment = Field(..., description="계절환경")

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
        
        # 새로운 10개 라이프스타일 카테고리 길이 추가
        total += sum(len(r) for r in self.daily_health_sports.recommended_activities)
        total += sum(len(h) for h in self.daily_health_sports.health_tips)
        total += sum(len(w) for w in self.daily_health_sports.wellness_focused)
        total += len(self.daily_health_sports.explanation)
        
        total += sum(len(f) for f in self.daily_meal_nutrition.flavor_profile)
        total += sum(len(f) for f in self.daily_meal_nutrition.food_recommendations)
        total += sum(len(n) for n in self.daily_meal_nutrition.nutritional_tips)
        total += sum(len(a) for a in self.daily_meal_nutrition.avoid_foods)
        total += len(self.daily_meal_nutrition.explanation)
        
        total += sum(len(c) for c in self.daily_fashion_beauty.clothing_style)
        total += sum(len(c) for c in self.daily_fashion_beauty.color_recommendations)
        total += sum(len(g) for g in self.daily_fashion_beauty.grooming_tips)
        total += sum(len(a) for a in self.daily_fashion_beauty.avoid_styles)
        total += len(self.daily_fashion_beauty.explanation)
        
        total += sum(len(g) for g in self.daily_shopping_finance.good_purchases)
        total += sum(len(s) for s in self.daily_shopping_finance.spending_tips)
        total += sum(len(v) for v in self.daily_shopping_finance.value_recommendations)
        total += sum(len(a) for a in self.daily_shopping_finance.avoid_purchases)
        total += len(self.daily_shopping_finance.explanation)
        
        total += sum(len(i) for i in self.daily_living_space.interior_style)
        total += sum(len(p) for p in self.daily_living_space.plant_recommendations)
        total += sum(len(o) for o in self.daily_living_space.organization_tips)
        total += len(self.daily_living_space.explanation)
        
        total += sum(len(s) for s in self.daily_routines.sleep_pattern)
        total += sum(len(m) for m in self.daily_routines.morning_routine)
        total += sum(len(e) for e in self.daily_routines.evening_routine)
        total += len(self.daily_routines.explanation)
        
        total += sum(len(p) for p in self.digital_communication.phone_usage_tips)
        total += sum(len(s) for s in self.digital_communication.social_media_guidance)
        total += sum(len(a) for a in self.digital_communication.app_recommendations)
        total += len(self.digital_communication.optimal_timing)
        total += len(self.digital_communication.explanation)
        
        total += sum(len(c) for c in self.hobbies_creativity.creative_hobbies)
        total += sum(len(l) for l in self.hobbies_creativity.learning_activities)
        total += len(self.hobbies_creativity.recommended_time)
        total += sum(len(s) for s in self.hobbies_creativity.social_hobbies)
        total += len(self.hobbies_creativity.explanation)
        
        total += sum(len(r) for r in self.relationships_social.relationship_focus)
        total += sum(len(c) for c in self.relationships_social.communication_style)
        total += sum(len(s) for s in self.relationships_social.social_activities)
        total += sum(len(a) for a in self.relationships_social.avoid_situations)
        total += len(self.relationships_social.explanation)
        
        total += sum(len(w) for w in self.seasonal_environment.weather_adaptation)
        total += sum(len(s) for s in self.seasonal_environment.seasonal_activities)
        total += sum(len(e) for e in self.seasonal_environment.environment_setup)
        total += sum(len(o) for o in self.seasonal_environment.outdoor_recommendations)
        total += len(self.seasonal_environment.explanation)
        
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


# 새로운 10개 라이프스타일 카테고리 모델들

class DailyHealthSports(BaseModel):
    """운동/건강"""
    recommended_activities: List[str] = Field(..., min_length=2, description="추천 활동")
    health_tips: List[str] = Field(..., min_length=2, description="건강 팁")
    wellness_focused: List[str] = Field(..., min_length=1, description="웰니스 집중")
    explanation: str = Field(..., min_length=50, description="설명")


class DailyMealNutrition(BaseModel):
    """음식/영양/건강식단"""
    flavor_profile: List[str] = Field(..., min_length=2, description="맛 프로필")
    food_recommendations: List[str] = Field(..., min_length=2, description="음식 추천")
    nutritional_tips: List[str] = Field(..., min_length=2, description="영양 팁")
    avoid_foods: List[str] = Field(default_factory=list, description="피해야 할 음식")
    explanation: str = Field(..., min_length=50, description="설명")


class DailyFashionBeauty(BaseModel):
    """의류/뷰티/화장"""
    clothing_style: List[str] = Field(..., min_length=2, description="의류 스타일")
    color_recommendations: List[str] = Field(..., min_length=2, description="색상 추천")
    grooming_tips: List[str] = Field(..., min_length=2, description="그루밍 팁")
    avoid_styles: List[str] = Field(default_factory=list, description="피해야 할 스타일")
    explanation: str = Field(..., min_length=50, description="설명")


class DailyShoppingFinance(BaseModel):
    """쇼핑/재테크/소비"""
    good_purchases: List[str] = Field(..., min_length=2, description="좋은 구매")
    spending_tips: List[str] = Field(..., min_length=2, description="소비 팁")
    value_recommendations: List[str] = Field(..., min_length=1, description="가치 추천")
    avoid_purchases: List[str] = Field(default_factory=list, description="피해야 할 구매")
    explanation: str = Field(..., min_length=50, description="설명")


class DailyLivingSpace(BaseModel):
    """주거/인테리어/식물"""
    interior_style: List[str] = Field(..., min_length=2, description="인테리어 스타일")
    plant_recommendations: List[str] = Field(..., min_length=2, description="식물 추천")
    organization_tips: List[str] = Field(..., min_length=2, description="정리 팁")
    explanation: str = Field(..., min_length=50, description="설명")


class DailyRoutines(BaseModel):
    """수면/기상/일상루틴"""
    sleep_pattern: List[str] = Field(..., min_length=2, description="수면 패턴")
    morning_routine: List[str] = Field(..., min_length=2, description="아침 루틴")
    evening_routine: List[str] = Field(..., min_length=2, description="저녁 루틴")
    explanation: str = Field(..., min_length=50, description="설명")


class DigitalCommunication(BaseModel):
    """스마트폰/SNS/온라인"""
    phone_usage_tips: List[str] = Field(..., min_length=2, description="폰 사용 팁")
    social_media_guidance: List[str] = Field(..., min_length=2, description="소셜미디어 가이드")
    app_recommendations: List[str] = Field(..., min_length=2, description="앱 추천")
    optimal_timing: str = Field(..., description="최적 타이밍")
    explanation: str = Field(..., min_length=50, description="설명")


class HobbiesCreativity(BaseModel):
    """취미/창작/학습"""
    creative_hobbies: List[str] = Field(..., min_length=2, description="창작 취미")
    learning_activities: List[str] = Field(..., min_length=2, description="학습 활동")
    recommended_time: str = Field(..., description="추천 시간")
    social_hobbies: List[str] = Field(default_factory=list, description="사교 취미")
    explanation: str = Field(..., min_length=50, description="설명")


class RelationshipsSocial(BaseModel):
    """인간관계/소통"""
    relationship_focus: List[str] = Field(..., min_length=2, description="관계 집중")
    communication_style: List[str] = Field(..., min_length=2, description="소통 스타일")
    social_activities: List[str] = Field(..., min_length=2, description="사교 활동")
    avoid_situations: List[str] = Field(default_factory=list, description="피해야 할 상황")
    explanation: str = Field(..., min_length=50, description="설명")


class SeasonalEnvironment(BaseModel):
    """날씨/계절/환경"""
    weather_adaptation: List[str] = Field(..., min_length=2, description="날씨 적응")
    seasonal_activities: List[str] = Field(..., min_length=2, description="계절 활동")
    environment_setup: List[str] = Field(..., min_length=2, description="환경 설정")
    outdoor_recommendations: List[str] = Field(..., min_length=2, description="야외 추천")
    explanation: str = Field(..., min_length=50, description="설명")


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
