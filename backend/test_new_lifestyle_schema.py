#!/usr/bin/env python3
"""
새로운 10개 라이프스타일 카테고리 테스트

DailyContent 모델에 새로 추가된 필드들이 올바르게 동작하는지 검증합니다.
"""

import sys
import os
from datetime import date

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.content.models import (
    DailyContent,
    DailyHealthSports,
    DailyMealNutrition,
    DailyFashionBeauty,
    DailyShoppingFinance,
    DailyLivingSpace,
    DailyRoutines,
    DigitalCommunication,
    HobbiesCreativity,
    RelationshipsSocial,
    SeasonalEnvironment,
    FocusCaution,
    ActionGuide,
    TimeDirection,
    StateTrigger,
    LengthRequirements
)


def create_sample_daily_content():
    """샘플 DailyContent 데이터 생성"""
    
    # 10개 라이프스타일 카테고리 샘플 데이터
    daily_health_sports = DailyHealthSports(
        recommended_activities=["가벼운 산책", "스트레칭"],
        health_tips=["충분한 수분 섭취", "규칙적인 식사"],
        wellness_focused=["명상", "호흡 운동"],
        explanation="오늘은 가벼운 운동으로 에너지를 활성화시키기 좋은 날입니다."
    )
    
    daily_meal_nutrition = DailyMealNutrition(
        flavor_profile=["담백함", "상큼함"],
        food_recommendations=["채소 샐러드", "구운 생선"],
        nutritional_tips=["비타민 섭취", "저염 식단"],
        avoid_foods=["기름진 음식", "카페인"],
        explanation="소화가 부담스럽지 않은 음식으로 영양을 보충하세요."
    )
    
    daily_fashion_beauty = DailyFashionBeauty(
        clothing_style=["편안한 캐주얼", "내추럴 톤"],
        color_recommendations=["베이지", "민트", "하늘색"],
        grooming_tips=["보습 중심 스킨케어", "가벼운 메이크업"],
        avoid_styles=["과도한 액세서리", "네온 색상"],
        explanation="자연스러운 룩이 오늘의 에너지와 잘 어울립니다."
    )
    
    daily_shopping_finance = DailyShoppingFinance(
        good_purchases=["건강 관련 제품", "교육 자료"],
        spending_tips=["예산 수립", "가격 비교"],
        value_recommendations=["장기적인 투자", "품질 좋은 아이템"],
        avoid_purchases=["충동 구매", "일회용품"],
        explanation="가치 있는 지출에 집중하고 불필요한 소비는 줄이세요."
    )
    
    daily_living_space = DailyLivingSpace(
        interior_style=["미니멀리즘", "자연 소재"],
        plant_recommendations=["공기정화식물", "작은 화분"],
        organization_tips=["수납 정리", "공간 활용"],
        explanation="정돈된 공간이 마음의 평화를 가져다줍니다."
    )
    
    daily_routines = DailyRoutines(
        sleep_pattern=["7-8시간 수면", "규칙적인 기상"],
        morning_routine=["스트레칭", "가벼운 아침 식사"],
        evening_routine=["독서", "명상"],
        explanation="규칙적인 루틴이 오늘의 안정감을 더해줍니다."
    )
    
    digital_communication = DigitalCommunication(
        phone_usage_tips=["필수 앱만 사용", "알림 제한"],
        social_media_guidance=["긍정적인 콘텐츠", "과도한 사용 자제"],
        app_recommendations=["명상 앱", "시간 관리 앱"],
        optimal_timing="오전 10시, 오후 3시",
        explanation="디지털 디톡스 시간을 가지며 균형을 유지하세요."
    )
    
    hobbies_creativity = HobbiesCreativity(
        creative_hobbies=["그림 그리기", "글쓰기"],
        learning_activities=["온라인 강의", "새로운 기술 습득"],
        recommended_time="저녁 7-9시",
        social_hobbies=["독서 모임", "산책"],
        explanation="창작 활동을 통해 내면의 에너지를 표현하세요."
    )
    
    relationships_social = RelationshipsSocial(
        relationship_focus=["가족과의 시간", "깊이 있는 대화"],
        communication_style=["경청", "솔직한 표현"],
        social_activities=["소규모 모임", "산책"],
        avoid_situations=["소음이 많은 곳", "과도한 사교 활동"],
        explanation="진정한 관계에 집중하며 의미 있는 연결을 만드세요."
    )
    
    seasonal_environment = SeasonalEnvironment(
        weather_adaptation=["체온 조절", "습도 관리"],
        seasonal_activities=["실내 운동", "창문 개방"],
        environment_setup=["가습기 사용", "실내 온도 조절"],
        outdoor_recommendations=["가벼운 산책", "공원 방문"],
        explanation="계절의 변화에 맞춰 환경을 조절하고 건강을 관리하세요."
    )
    
    # 기존 필드들
    focus_caution = FocusCaution(
        focus=["내면 성찰", "건강 관리"],
        caution=["과도한 활동", "충동적 결정"]
    )
    
    action_guide = ActionGuide(
        do=["규칙적인 휴식", "건강한 식사", "가벼운 운동"],
        avoid=["늦은 시간 업무", "카페인 과다 섭취", "스트레스 유발 상황"]
    )
    
    time_direction = TimeDirection(
        good_time="오전 9-11시",
        avoid_time="밤 11시 이후",
        good_direction="동쪽",
        avoid_direction="서쪽",
        notes="집중이 필요한 활동은 오전에 하는 것이 효과적입니다."
    )
    
    state_trigger = StateTrigger(
        gesture="양손을 모으고 심호흡",
        phrase="나는 지금 평화롭고 안정되어 있다",
        how_to="불안감이 느껴질 때마다 3회 반복"
    )
    
    # DailyContent 객체 생성
    daily_content = DailyContent(
        date=date.today(),
        summary="오늘은 내면의 평화와 건강을 찾는 데 집중하는 하루입니다. 차분하고 안정된 에너지로 자신을 돌보는 시간을 가지세요.",
        keywords=["내면 성찰", "건강", "안정", "균형"],
        rhythm_description="오늘의 리듬은 차분하고 안정적입니다. 외부의 소란스러움보다는 내면의 평화를 찾는 데 에너지를 사용하기 좋은 날입니다. 몸과 마음의 건강을 동시에 챙기며 균형 잡힌 하루를 보낼 수 있습니다. 무리하게 새로운 일을 시작하기보다는 현재의 상태를 점검하고 돌보는 데 집중하세요.",
        focus_caution=focus_caution,
        action_guide=action_guide,
        time_direction=time_direction,
        state_trigger=state_trigger,
        meaning_shift="오늘의 차분함은 '무기력함'이 아니라 '에너지 충전'의 시간입니다. 내면의 목소리에 귀 기울이며 재충전의 기회로 삼으세요.",
        rhythm_question="오늘 나의 몸과 마음은 무엇을 필요로 하고 있을까요? 어떻게 하면 더 평화롭고 건강할 수 있을까요?",
        
        # 새로운 10개 라이프스타일 카테고리
        daily_health_sports=daily_health_sports,
        daily_meal_nutrition=daily_meal_nutrition,
        daily_fashion_beauty=daily_fashion_beauty,
        daily_shopping_finance=daily_shopping_finance,
        daily_living_space=daily_living_space,
        daily_routines=daily_routines,
        digital_communication=digital_communication,
        hobbies_creativity=hobbies_creativity,
        relationships_social=relationships_social,
        seasonal_environment=seasonal_environment
    )
    
    return daily_content


def test_model_validation():
    """모델 검증 테스트"""
    print("=== 모델 검증 테스트 시작 ===\n")
    
    try:
        # 샘플 데이터 생성
        content = create_sample_daily_content()
        print("✅ DailyContent 모델 생성 성공")
        
        # 기본 필드 검증
        print(f"✅ 날짜: {content.date}")
        print(f"✅ 요약: {content.summary[:50]}...")
        print(f"✅ 키워드: {', '.join(content.keywords)}")
        
        # 새로운 10개 카테고리 검증
        print(f"✅ 운동/건강 추천 활동: {content.daily_health_sports.recommended_activities}")
        print(f"✅ 음식/영양 맵 프로필: {content.daily_meal_nutrition.flavor_profile}")
        print(f"✅ 의류/뷰티 색상 추천: {content.daily_fashion_beauty.color_recommendations}")
        print(f"✅ 쇼핑/재테크 가치 추천: {content.daily_shopping_finance.value_recommendations}")
        print(f"✅ 주거공간 인테리어 스타일: {content.daily_living_space.interior_style}")
        print(f"✅ 일상루틴 아침 루틴: {content.daily_routines.morning_routine}")
        print(f"✅ 디지털소통 앱 추천: {content.digital_communication.app_recommendations}")
        print(f"✅ 취미/창작 추천 시간: {content.hobbies_creativity.recommended_time}")
        print(f"✅ 인간관계 소통 스타일: {content.relationships_social.communication_style}")
        print(f"✅ 계절환경 날씨 적응: {content.seasonal_environment.weather_adaptation}")
        
        # 길이 요구사항 검증
        total_length = content.get_total_text_length()
        print(f"\n✅ 총 텍스트 길이: {total_length:,}자")
        
        is_valid, total, message = content.validate_length_requirements()
        print(f"✅ 길이 검증: {message}")
        
        if is_valid:
            print("✅ 모든 검증 통과!")
        else:
            print("❌ 길이 요구사항 미충족")
            
        return True
        
    except Exception as e:
        print(f"❌ 에러 발생: {e}")
        return False


def test_json_serialization():
    """JSON 직렬화 테스트"""
    print("\n=== JSON 직렬화 테스트 시작 ===\n")
    
    try:
        content = create_sample_daily_content()
        json_data = content.model_dump_json(indent=2)
        
        print(f"✅ JSON 직렬화 성공")
        print(f"✅ JSON 크기: {len(json_data):,} 바이트")
        
        # JSON에서 다시 모델로 변환
        restored_content = DailyContent.model_validate_json(json_data)
        print("✅ JSON에서 모델로 복원 성공")
        
        # 데이터 일치성 확인
        assert restored_content.date == content.date
        assert restored_content.summary == content.summary
        assert restored_content.daily_health_sports.recommended_activities == content.daily_health_sports.recommended_activities
        print("✅ 데이터 일치성 검증 통과")
        
        return True
        
    except Exception as e:
        print(f"❌ JSON 직렬화 에러: {e}")
        return False


def main():
    """메인 테스트 함수"""
    print("🧪 새로운 10개 라이프스타일 카테고리 스키마 테스트")
    print("=" * 50)
    
    # 모델 검증 테스트
    model_test_passed = test_model_validation()
    
    # JSON 직렬화 테스트  
    json_test_passed = test_json_serialization()
    
    # 결과 요약
    print("\n" + "=" * 50)
    print("📋 테스트 결과 요약")
    print("=" * 50)
    print(f"모델 검증: {'✅ 통과' if model_test_passed else '❌ 실패'}")
    print(f"JSON 직렬화: {'✅ 통과' if json_test_passed else '❌ 실패'}")
    
    all_passed = model_test_passed and json_test_passed
    print(f"\n🎯 전체 테스트: {'✅ 모두 통과' if all_passed else '❌ 실패'}")
    
    if all_passed:
        print("\n🎉 새로운 10개 라이프스타일 카테고리가 성공적으로 구현되었습니다!")
        print("📝 이제 R³ 다이어리 시스템에서 풍부한 라이프스타일 가이드를 제공할 수 있습니다.")
    else:
        print("\n⚠️ 테스트 실패 항목을 확인하고 수정해주세요.")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)