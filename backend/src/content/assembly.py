"""
Content Assembly Engine

리듬 신호를 사용자 노출 콘텐츠 블록으로 변환합니다.

**중요**: 이 모듈은 사용자 노출 텍스트만 생성합니다.
내부 전문 용어(사주명리, NLP 등)는 절대 사용 금지.
"""
import datetime
from datetime import date, time
from typing import Dict, Any


def assemble_daily_content(
    target_date: datetime.date,
    saju_data: Dict[str, Any],
    daily_rhythm: Dict[str, Any],
    qimen_summary: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    일간 콘텐츠 조합

    Args:
        date: 대상 날짜
        saju_data: 사주 계산 결과 (내부 데이터)
        daily_rhythm: 일간 리듬 분석 결과 (내부 데이터)
        qimen_summary: 기문둔갑 요약 데이터 (best_direction, avoid_direction, peak_hours)

    Returns:
        DAILY_CONTENT_SCHEMA.json 준수하는 사용자 노출 콘텐츠
    """
    # 1. 요약 (summary)
    summary = _generate_summary(daily_rhythm)

    # 2. 키워드 (keywords)
    keywords = _generate_keywords(daily_rhythm, saju_data)

    # 3. 리듬 해설 (rhythm_description) - 설명형 문단
    rhythm_description = _generate_rhythm_description(daily_rhythm, saju_data)

    # 4. 집중/주의 포인트 (focus_caution)
    focus_caution = _generate_focus_caution(daily_rhythm)

    # 5. 행동 가이드 (action_guide)
    action_guide = _generate_action_guide(daily_rhythm, saju_data)

    # 6. 시간/방향 (time_direction) - 기문둔갑 데이터 통합
    time_direction = _generate_time_direction(daily_rhythm, qimen_summary or {})

    # 7. 상태 트리거 (state_trigger)
    state_trigger = _generate_state_trigger(daily_rhythm)

    # 8. 의미 전환 (meaning_shift) - 설명형 문단
    meaning_shift = _generate_meaning_shift(daily_rhythm, saju_data)

    # 9. 리듬 질문 (rhythm_question)
    rhythm_question = _generate_rhythm_question(daily_rhythm)

    # 10-19. 라이프스타일 블록 (스키마 필수 항목)
    health_sports = _generate_daily_health_sports(daily_rhythm, saju_data)
    meal_nutrition = _generate_daily_meal_nutrition(daily_rhythm, saju_data)
    fashion_beauty = _generate_daily_fashion_beauty(daily_rhythm, saju_data)
    shopping_finance = _generate_daily_shopping_finance(daily_rhythm, saju_data)
    living_space = _generate_daily_living_space(daily_rhythm, saju_data)
    daily_routines = _generate_daily_routines(daily_rhythm, saju_data)
    digital_comm = _generate_digital_communication(daily_rhythm, saju_data)
    hobbies = _generate_hobbies_creativity(daily_rhythm, saju_data)
    relationships = _generate_relationships_social(daily_rhythm, saju_data)
    seasonal = _generate_seasonal_environment(daily_rhythm, saju_data, target_date)

    content = {
        "date": target_date.strftime("%Y-%m-%d"),
        "summary": summary,
        "keywords": keywords,
        "rhythm_description": rhythm_description,
        "focus_caution": focus_caution,
        "action_guide": action_guide,
        "time_direction": time_direction,
        "state_trigger": state_trigger,
        "meaning_shift": meaning_shift,
        "rhythm_question": rhythm_question,
        # 라이프스타일 블록 (스키마 요구사항)
        "daily_health_sports": health_sports,
        "daily_meal_nutrition": meal_nutrition,
        "daily_fashion_beauty": fashion_beauty,
        "daily_shopping_finance": shopping_finance,
        "daily_living_space": living_space,
        "daily_routines": daily_routines,
        "digital_communication": digital_comm,
        "hobbies_creativity": hobbies,
        "relationships_social": relationships,
        "seasonal_environment": seasonal,
    }

    # 좌측 페이지 최소 700자 보장
    content = _ensure_minimum_content_length(content, daily_rhythm)

    return content


def _generate_summary(daily_rhythm: Dict[str, Any]) -> str:
    """하루 요약 생성"""
    energy = daily_rhythm.get("에너지_수준", 3)
    flow = daily_rhythm.get("주요_흐름", "균형의 시기")

    energy_text = {
        5: "매우 활기찬",
        4: "충만한",
        3: "안정적인",
        2: "차분한",
        1: "고요한"
    }.get(energy, "평온한")

    if energy >= 4:
        return (
            f"오늘은 {energy_text} 에너지가 흐르는 날입니다. "
            f"{flow}의 시간을 맞이하여, 준비해온 일들을 적극적으로 펼치기에 좋은 하루입니다. "
            "활기차게 시작하고 과감히 움직여 보세요."
        )
    elif energy <= 2:
        return (
            f"오늘은 {energy_text} 에너지의 날입니다. "
            f"{flow}의 흐름 속에서 자신을 조용히 돌보는 시간이 필요합니다. "
            "무리하기보다 내면의 목소리에 귀를 기울이며 차분히 하루를 보내세요."
        )
    else:
        return (
            f"오늘은 {energy_text} 에너지가 흐르는 날입니다. "
            f"{flow}을 경험하며, 지나치게 힘을 쏟지도, 너무 물러서지도 않는 균형 잡힌 하루를 설계해보세요. "
            "안정 속에서 꾸준한 성과를 만들 수 있습니다."
        )


def _generate_keywords(daily_rhythm: Dict[str, Any], saju_data: Dict[str, Any]) -> list:
    """키워드 생성 (3-8개)"""
    keywords = []

    energy = daily_rhythm.get("에너지_수준", 3)
    concentration = daily_rhythm.get("집중력", 3)
    social = daily_rhythm.get("사회운", 3)
    decision = daily_rhythm.get("결정력", 3)

    # 에너지 기반
    if energy >= 4:
        keywords.append("활동")
    elif energy <= 2:
        keywords.append("휴식")
    else:
        keywords.append("균형")

    # 집중력 기반
    if concentration >= 4:
        keywords.extend(["집중", "학습"])
    else:
        keywords.append("유연함")

    # 사회운 기반
    if social >= 4:
        keywords.extend(["관계", "소통"])
    else:
        keywords.append("내면")

    # 결정력 기반
    if decision >= 4:
        keywords.extend(["실행", "결단"])
    else:
        keywords.append("준비")

    # 기회/도전 요소에서 추가
    opportunities = daily_rhythm.get("기회_요소", [])
    if opportunities:
        keywords.append("기회")

    # 중복 제거 및 최대 8개로 제한
    keywords = list(dict.fromkeys(keywords))[:8]

    # 최소 3개 보장
    while len(keywords) < 3:
        keywords.append("조화")

    return keywords


def _generate_rhythm_description(daily_rhythm: Dict[str, Any], saju_data: Dict[str, Any]) -> str:
    """리듬 해설 생성 (설명형 문단, 최소 200자)"""
    energy = daily_rhythm.get("에너지_수준", 3)
    concentration = daily_rhythm.get("집중력", 3)
    social = daily_rhythm.get("사회운", 3)
    decision = daily_rhythm.get("결정력", 3)
    flow = daily_rhythm.get("주요_흐름", "균형의 시기")

    description = f"오늘의 흐름은 '{flow}'으로 요약됩니다. "
    description += "이 흐름이 어떤 의미를 가지는지, 하루 동안 어떻게 활용할 수 있는지 살펴보겠습니다. "

    if energy >= 4:
        description += "현재 에너지 수준이 매우 높아, 활동적이고 적극적인 하루가 될 가능성이 큽니다. "
        description += "이 시기에는 오랫동안 미뤄두었던 과제나 새로운 시도를 실행에 옮기는 것이 효과적입니다. "
    elif energy <= 2:
        description += "에너지가 낮은 상태로, 몸과 마음 모두 충분한 쉼을 요청하고 있는 신호입니다. "
        description += "이런 날은 생산성보다 회복을 우선순위로 삼고, 가벼운 일만 처리하는 것이 지혜롭습니다. "
    else:
        description += "에너지가 안정적으로 유지되는 날입니다. "
        description += "급격한 변화보다는 꾸준한 흐름을 유지하면서 하루의 과업을 착실히 처리해나가기에 좋습니다. "

    if concentration >= 4:
        description += "오늘은 특히 집중력이 뛰어난 상태입니다. "
        description += "깊은 사고가 필요한 작업이나 학습, 창작 활동에 이 에너지를 적극 활용해보세요. "
    elif concentration <= 2:
        description += "집중력이 다소 분산되는 경향이 있으니, 너무 오래 한 가지 일에 매달리지 않는 것이 좋습니다. "
        description += "짧은 휴식과 함께 여러 가지 가벼운 작업을 번갈아 처리하는 방식을 추천합니다. "

    if social >= 4:
        description += "대인관계 에너지가 활발하여 사람들과의 교류가 원활하게 이뤄질 수 있습니다. "
        description += "중요한 미팅이나 협력이 필요한 일을 오늘 진행하면 좋은 결과를 기대할 수 있습니다. "
    elif social <= 2:
        description += "오늘은 혼자만의 시간을 갖거나 소수의 가까운 사람들과 조용히 교류하는 것이 편안합니다. "

    if decision >= 4:
        description += "결단력이 강화된 날로, 오랫동안 고민해온 선택을 내리기에 적합한 시기입니다. "

    opportunities = daily_rhythm.get("기회_요소", [])
    if opportunities:
        opp_text = ", ".join(opportunities[:2])
        description += f"특히 {opp_text} 방면에서 긍정적인 기회가 열릴 수 있으니 주의 깊게 살펴보세요. "

    description += "오늘 하루를 이 흐름에 맞게 설계한다면, 더 자연스럽고 의미 있는 하루가 될 것입니다."

    # 최소 200자 보장
    while len(description) < 200:
        description += " 오늘의 흐름을 온전히 받아들이고, 자신만의 속도로 나아가세요."

    return description.strip()


def _generate_focus_caution(daily_rhythm: Dict[str, Any]) -> Dict[str, list]:
    """집중/주의 포인트 생성"""
    energy = daily_rhythm.get("에너지_수준", 3)
    concentration = daily_rhythm.get("집중력", 3)
    social = daily_rhythm.get("사회운", 3)
    decision = daily_rhythm.get("결정력", 3)

    focus = []
    caution = []

    # Focus 항목
    if energy >= 4:
        focus.append("높은 에너지를 활용한 적극적 활동")
    if concentration >= 4:
        focus.append("중요한 작업에 대한 깊은 집중")
    if social >= 4:
        focus.append("관계 형성과 네트워킹")
    if decision >= 4:
        focus.append("결정이 필요한 사안의 처리")

    # 최소 2개 보장
    if len(focus) < 2:
        focus.extend(["일상 루틴 유지", "균형 잡힌 하루 설계"])

    # Caution 항목
    if energy <= 2:
        caution.append("무리한 활동으로 인한 피로 누적")
    if concentration <= 2:
        caution.append("주의력 분산 가능성")
    if social <= 2:
        caution.append("대인 관계에서의 오해")

    # 최소 1개 보장
    if len(caution) < 1:
        caution.append("과도한 욕심이나 조급함")

    return {
        "focus": focus[:5],  # 최대 5개
        "caution": caution[:5]  # 최대 5개
    }


def _generate_action_guide(daily_rhythm: Dict[str, Any], saju_data: Dict[str, Any]) -> Dict[str, list]:
    """행동 가이드 생성 (Do/Avoid)"""
    energy = daily_rhythm.get("에너지_수준", 3)
    opportunities = daily_rhythm.get("기회_요소", [])
    challenges = daily_rhythm.get("도전_요소", [])

    do = []
    avoid = []

    # Do 항목
    if energy >= 4:
        do.extend([
            "중요한 프로젝트 진행하기",
            "새로운 시도나 도전 계획하기",
            "활발한 움직임과 교류"
        ])
    elif energy >= 3:
        do.extend([
            "일상 업무를 차분히 처리하기",
            "계획 점검 및 정리",
            "편안한 대화와 소통"
        ])
    else:
        do.extend([
            "충분한 휴식 취하기",
            "내면 성찰과 기록",
            "가벼운 정리 활동"
        ])

    # Avoid 항목
    if energy <= 2:
        avoid.extend([
            "과도한 일정 잡기",
            "중요한 결정 서두르기",
            "무리한 약속"
        ])
    else:
        avoid.extend([
            "충동적 선택",
            "피로를 무시한 활동",
            "불필요한 갈등"
        ])

    return {
        "do": do[:5],
        "avoid": avoid[:5]
    }


def _generate_time_direction(daily_rhythm: Dict[str, Any], qimen_summary: Dict[str, Any] = None) -> Dict[str, str]:
    """시간/방향 정보 생성 (기문둔갑 데이터 통합)"""
    good_times = daily_rhythm.get("유리한_시간", [])
    caution_times = daily_rhythm.get("주의_시간", [])
    good_directions = daily_rhythm.get("유리한_방향", [])

    # 기문둔갑 데이터로 보강
    if qimen_summary:
        qimen_peak = qimen_summary.get("peak_hours")
        qimen_best_dir = qimen_summary.get("best_direction")
        qimen_avoid_dir = qimen_summary.get("avoid_direction")

        # 기문 집중 시간을 첫 번째로 추가
        if qimen_peak and qimen_peak not in good_times:
            good_times = [qimen_peak] + list(good_times)

        # 기문 최적 방향을 첫 번째로 추가
        if qimen_best_dir and qimen_best_dir not in good_directions:
            good_directions = [qimen_best_dir] + list(good_directions)

        avoid_direction_str = qimen_avoid_dir if qimen_avoid_dir else "특별히 피할 방향 없음"
    else:
        avoid_direction_str = "특별히 피할 방향 없음"

    good_time_str = ", ".join(good_times[:2]) if good_times else "오전 시간대"
    avoid_time_str = ", ".join(caution_times[:1]) if caution_times else "늦은 밤"
    good_direction_str = ", ".join(good_directions[:2]) if good_directions else "동쪽"

    notes = f"오늘은 {good_time_str}에 집중력과 효율이 높아집니다. "
    notes += f"가능하다면 {good_direction_str} 방향으로의 활동이나 이동을 고려해보세요. "
    notes += f"{avoid_time_str}에는 중요한 일을 피하는 것이 좋습니다."

    return {
        "good_time": good_time_str,
        "avoid_time": avoid_time_str,
        "good_direction": good_direction_str,
        "avoid_direction": avoid_direction_str,
        "notes": notes
    }


def _generate_state_trigger(daily_rhythm: Dict[str, Any]) -> Dict[str, str]:
    """상태 트리거 생성"""
    energy = daily_rhythm.get("에너지_수준", 3)

    if energy >= 4:
        gesture = "두 손을 가슴에 모으고 깊게 호흡하기"
        phrase = "\"오늘의 에너지를 온전히 느낀다\""
        how_to = "활기찬 에너지가 흐를 때, 잠시 멈춰 두 손을 가슴에 모으고 깊은 호흡을 세 번 반복하세요. "
        how_to += "이 동작은 넘치는 에너지를 내면으로 안정화시켜 과도한 흥분이나 조급함을 조절하는 데 도움이 됩니다."
    elif energy <= 2:
        gesture = "어깨를 가볍게 으쓱이며 긴장 풀기"
        phrase = "\"충분한 휴식이 나를 채운다\""
        how_to = "에너지가 낮게 느껴질 때, 의자에 앉아 어깨를 천천히 으쓱이며 긴장을 풀어주세요. "
        how_to += "이 동작과 함께 '휴식도 생산적인 활동이다'라는 인식을 상기하면 불필요한 죄책감을 내려놓을 수 있습니다."
    else:
        gesture = "양손을 가볍게 펴고 균형 확인하기"
        phrase = "\"지금 이대로 충분하다\""
        how_to = "평온한 에너지 속에서 양손을 앞으로 펴고 좌우 균형을 느껴보세요. "
        how_to += "이 간단한 동작은 현재 상태를 인식하고 받아들이는 마음가짐을 강화해줍니다."

    return {
        "gesture": gesture,
        "phrase": phrase,
        "how_to": how_to
    }


def _generate_meaning_shift(daily_rhythm: Dict[str, Any], saju_data: Dict[str, Any]) -> str:
    """의미 전환 생성 (설명형 문단, 최소 150자)"""
    energy = daily_rhythm.get("에너지_수준", 3)
    challenges = daily_rhythm.get("도전_요소", [])

    if energy <= 2:
        shift = "에너지가 낮다는 것은 무능력이 아니라, 충전이 필요한 자연스러운 신호입니다. "
        shift += "휴식을 선택하는 것도 자기 돌봄의 적극적 행동입니다. "
        shift += "지금 이 순간 쉬어가는 것이 내일의 나를 위한 가장 현명한 투자라는 점을 기억하세요. "
        shift += "오늘의 쉼이 내일의 나를 위한 준비임을 잊지 마세요. "
        shift += "억지로 활동하려 하지 말고, 필요한 것이 무엇인지 자신에게 솔직하게 물어보세요."
    elif energy >= 4:
        shift = "넘치는 에너지는 무조건 소모해야 할 대상이 아닙니다. "
        shift += "방향성 있는 활용이 중요하며, 때로는 내일을 위해 보존하는 것도 현명한 선택입니다. "
        shift += "에너지의 흐름을 자각하고, 가장 의미 있는 곳에 집중하여 활용해보세요. "
        shift += "지금의 이 에너지가 언제나 지속되지는 않습니다. "
        shift += "오늘의 힘을 현명하게 배분하여, 시작한 일을 마무리하는 데 집중해보세요."
    else:
        shift = "평범한 하루라는 느낌은 오히려 안정의 증거입니다. "
        shift += "특별함을 강요하지 않고 지금 이 순간을 있는 그대로 받아들이는 것도 중요한 성장입니다. "
        shift += "일상 속 작은 순간들에 감사하며, 오늘의 평온함이 주는 힘을 느껴보세요. "
        shift += "조용하지만 단단한 이 흐름 속에서, 오늘 당신이 내리는 선택들이 앞으로의 방향을 만들어갑니다. "
        shift += "작더라도 의식적인 선택을 해보세요."

    return shift


def _generate_rhythm_question(daily_rhythm: Dict[str, Any]) -> str:
    """리듬 질문 생성"""
    energy = daily_rhythm.get("에너지_수준", 3)

    if energy >= 4:
        return "오늘의 높은 에너지를 어떤 방향으로 사용하고 싶나요?"
    elif energy <= 2:
        return "지금 나에게 필요한 휴식의 형태는 무엇일까요?"
    else:
        return "오늘 하루 동안 가장 소중하게 여기고 싶은 순간은 무엇인가요?"


def _generate_daily_health_sports(daily_rhythm: Dict[str, Any], saju_data: Dict[str, Any]) -> Dict[str, Any]:
    """건강/운동 추천"""
    energy = daily_rhythm.get("에너지_수준", 3)

    if energy >= 4:
        activities = ["조깅", "수영", "자전거 타기", "테니스"]
        tips = ["활동적인 운동으로 에너지 발산", "충분한 수분 섭취"]
        wellness = ["심폐 기능 강화", "체력 향상"]
        explanation = "오늘은 에너지가 높은 날입니다. 활동적인 운동으로 에너지를 건강하게 발산하세요."
    else:
        activities = ["걷기", "요가", "스트레칭", "명상"]
        tips = ["가벼운 운동으로 컨디션 유지", "충분한 휴식"]
        wellness = ["유연성 향상", "스트레스 해소"]
        explanation = "오늘은 편안한 운동이 좋습니다. 몸과 마음을 부드럽게 풀어주는 활동을 선택하세요."

    return {
        "recommended_activities": activities[:2],
        "health_tips": tips,
        "wellness_focused": wellness[:2],
        "explanation": explanation
    }


def _generate_daily_meal_nutrition(daily_rhythm: Dict[str, Any], saju_data: Dict[str, Any]) -> Dict[str, Any]:
    """음식/영양 추천"""
    energy = daily_rhythm.get("에너지_수준", 3)

    if energy >= 4:
        flavor = ["신선한 맛", "상큼한 맛"]
        foods = ["과일", "샐러드", "생선", "견과류"]
        avoid = ["기름진 음식", "과도한 당분"]
        explanation = "오늘은 가벼우면서 영양가 있는 음식이 좋습니다. 신선한 재료로 에너지를 보충하세요."
    else:
        flavor = ["따뜻한 맛", "편안한 맛"]
        foods = ["따뜻한 국물", "죽", "야채", "두부"]
        avoid = ["자극적인 음식", "차가운 음식"]
        explanation = "오늘은 소화가 편안한 음식이 좋습니다. 따뜻하고 부드러운 음식으로 컨디션을 회복하세요."

    return {
        "flavor_profile": flavor,
        "recommended_foods": foods[:3],
        "avoid_foods": avoid[:2],
        "explanation": explanation
    }


def _generate_daily_fashion_beauty(daily_rhythm: Dict[str, Any], saju_data: Dict[str, Any]) -> Dict[str, Any]:
    """패션/뷰티 추천 (색상 포함)"""
    energy = daily_rhythm.get("에너지_수준", 3)
    social = daily_rhythm.get("사회운", 3)

    if energy >= 4 and social >= 4:
        style = ["화사한 스타일", "밝은 컬러"]
        colors = ["하얀색", "연한 파란색", "연두색"]
        beauty = ["자연스러운 메이크업", "생기있는 표정"]
        explanation = "오늘은 밝고 활기찬 스타일이 어울립니다. 깨끗하고 밝은 컬러로 좋은 인상을 주세요."
    elif energy <= 2 or social <= 2:
        style = ["편안한 스타일", "차분한 컬러"]
        colors = ["베이지", "회색", "네이비"]
        beauty = ["자연스러운 피부 표현", "편안한 헤어"]
        explanation = "오늘은 편안하고 차분한 스타일이 좋습니다. 무리하지 않는 자연스러움을 유지하세요."
    else:
        style = ["캐주얼한 스타일", "중간 톤"]
        colors = ["하늘색", "연한 노란색", "흰색"]
        beauty = ["깔끔한 스타일", "간단한 정리"]
        explanation = "오늘은 부담 없는 스타일이 어울립니다. 간편하면서도 정돈된 모습을 유지하세요."

    return {
        "clothing_style": style,
        "color_suggestions": colors[:3],
        "beauty_tips": beauty,
        "explanation": explanation
    }


def _generate_daily_shopping_finance(daily_rhythm: Dict[str, Any], saju_data: Dict[str, Any]) -> Dict[str, Any]:
    """쇼핑/금융 추천"""
    decision = daily_rhythm.get("결정력", 3)

    if decision >= 4:
        buy = ["필요한 생활용품", "건강 관련 용품", "학습 도구"]
        finance = ["계획적인 소비", "가치 있는 투자 검토"]
        investment = ["장기적 관점", "신중한 판단"]
        explanation = "오늘은 결정력이 좋은 날입니다. 필요한 것을 계획적으로 구매하기 좋은 시기입니다."
    else:
        buy = ["긴급하지 않으면 보류", "충동구매 자제"]
        finance = ["지출 기록하기", "예산 점검하기"]
        investment = ["관망", "정보 수집"]
        explanation = "오늘은 큰 지출을 미루는 것이 좋습니다. 계획을 세우고 다음을 기약하세요."

    return {
        "good_to_buy": buy[:2],
        "finance_advice": finance,
        "investment_focus": investment[:2],
        "explanation": explanation
    }


def _generate_daily_living_space(daily_rhythm: Dict[str, Any], saju_data: Dict[str, Any]) -> Dict[str, Any]:
    """생활 공간 추천"""
    energy = daily_rhythm.get("에너지_수준", 3)

    if energy >= 4:
        organization = ["불필요한 물건 정리", "공간 재배치"]
        plants = ["공기정화 식물 배치", "화분 관리"]
        env = ["환기하기", "자연광 활용"]
        explanation = "오늘은 공간을 정리하기 좋은 날입니다. 깨끗하고 상쾌한 환경을 만들어보세요."
    else:
        organization = ["작은 영역만 정리", "필수 정돈"]
        plants = ["관상용 식물 감상", "물주기"]
        env = ["편안한 조명", "쾌적한 온도 유지"]
        explanation = "오늘은 편안한 공간 유지에 집중하세요. 무리한 정리보다 현상 유지가 좋습니다."

    return {
        "space_organization": organization,
        "plants_decor": plants,
        "environmental_tips": env[:2],
        "explanation": explanation
    }


def _generate_daily_routines(daily_rhythm: Dict[str, Any], saju_data: Dict[str, Any]) -> Dict[str, Any]:
    """일상 루틴 추천"""
    energy = daily_rhythm.get("에너지_수준", 3)

    if energy >= 4:
        sleep = ["일찍 자고 일찍 일어나기", "규칙적인 수면 패턴"]
        morning = ["가벼운 스트레칭", "충분한 아침 식사", "하루 계획 세우기"]
        evening = ["활동 정리", "내일 준비", "가벼운 독서"]
        explanation = "오늘은 활동적인 루틴이 어울립니다. 아침부터 활기차게 시작하세요."
    else:
        sleep = ["충분한 수면 시간 확보", "편안한 취침 환경"]
        morning = ["천천히 일어나기", "가벼운 식사", "여유 있는 준비"]
        evening = ["이완 활동", "명상이나 음악 감상", "일찍 취침 준비"]
        explanation = "오늘은 여유로운 루틴이 좋습니다. 서두르지 말고 자신의 페이스를 유지하세요."

    return {
        "sleep_schedule": sleep,
        "morning_routine": morning[:2],
        "evening_routine": evening[:2],
        "explanation": explanation
    }


def _generate_digital_communication(daily_rhythm: Dict[str, Any], saju_data: Dict[str, Any]) -> Dict[str, Any]:
    """디지털 소통 추천"""
    social = daily_rhythm.get("사회운", 3)
    concentration = daily_rhythm.get("집중력", 3)

    if social >= 4:
        device = ["적극적인 소통", "영상 통화 활용"]
        social_media = ["긍정적인 게시물 공유", "댓글 소통"]
        focus = ["네트워킹", "정보 교환"]
        explanation = "오늘은 디지털 소통이 활발한 날입니다. 적극적으로 연락하고 교류하세요."
    elif concentration <= 2:
        device = ["스마트폰 사용 제한", "필수 연락만"]
        social_media = ["SNS 휴식", "알림 끄기"]
        focus = ["집중 시간 확보", "디지털 디톡스"]
        explanation = "오늘은 디지털 기기 사용을 줄이는 것이 좋습니다. 집중력을 보호하세요."
    else:
        device = ["적정 수준 사용", "시간 제한 설정"]
        social_media = ["필요한 정보만 확인", "수동적 소비 줄이기"]
        focus = ["업무 관련 소통", "실용적인 정보"]
        explanation = "오늘은 디지털 사용을 적절히 조절하세요. 필요한 것만 선택적으로 이용하세요."

    return {
        "device_usage": device,
        "social_media": social_media,
        "online_focus_areas": focus[:2],
        "explanation": explanation
    }


def _generate_hobbies_creativity(daily_rhythm: Dict[str, Any], saju_data: Dict[str, Any]) -> Dict[str, Any]:
    """취미/창작 추천"""
    energy = daily_rhythm.get("에너지_수준", 3)
    concentration = daily_rhythm.get("집중력", 3)

    if energy >= 4 and concentration >= 4:
        creative = ["그림 그리기", "글쓰기", "악기 연주"]
        learning = ["새로운 기술 배우기", "온라인 강의 수강"]
        entertainment = ["영화 감상", "전시회 관람", "콘서트"]
        explanation = "오늘은 창작 활동에 집중하기 좋은 날입니다. 새로운 것을 배우고 표현해보세요."
    elif concentration <= 2:
        creative = ["자유로운 낙서", "음악 듣기", "산책"]
        learning = ["가벼운 독서", "팟캐스트 듣기"]
        entertainment = ["편안한 영상 시청", "음악 감상"]
        explanation = "오늘은 가벼운 취미 활동이 어울립니다. 부담 없이 즐길 수 있는 것을 선택하세요."
    else:
        creative = ["사진 찍기", "간단한 공예", "요리"]
        learning = ["관심 분야 탐색", "짧은 학습"]
        entertainment = ["드라마 시청", "책 읽기", "게임"]
        explanation = "오늘은 적당한 취미 활동이 좋습니다. 흥미로운 것을 찾아 시간을 보내세요."

    return {
        "creative_activities": creative[:2],
        "learning_recommendations": learning[:2],
        "entertainment_options": entertainment[:2],
        "explanation": explanation
    }


def _generate_relationships_social(daily_rhythm: Dict[str, Any], saju_data: Dict[str, Any]) -> Dict[str, Any]:
    """관계/사회 추천"""
    social = daily_rhythm.get("사회운", 3)

    if social >= 4:
        communication = ["적극적인 대화", "진솔한 표현"]
        energies = ["모임 참여", "새로운 인연", "협력 활동"]
        tips = ["긍정적인 태도 유지", "경청하기", "배려하는 말투"]
        explanation = "오늘은 관계 운이 좋은 날입니다. 사람들과 적극적으로 교류하세요."
    elif social <= 2:
        communication = ["필요한 말만", "간결한 대화"]
        energies = ["혼자만의 시간", "소수와의 만남", "조용한 활동"]
        tips = ["무리하지 않기", "거절할 줄 알기", "나를 우선하기"]
        explanation = "오늘은 관계에서 에너지를 아끼는 것이 좋습니다. 혼자만의 시간을 가지세요."
    else:
        communication = ["자연스러운 대화", "편안한 소통"]
        energies = ["가까운 사람들과", "익숙한 장소에서", "부담 없는 만남"]
        tips = ["적당한 거리 유지", "선택적 교류", "편안한 관계 우선"]
        explanation = "오늘은 편안한 관계에 집중하세요. 가까운 사람들과 자연스럽게 어울리세요."

    return {
        "communication_style": communication,
        "social_energies": energies[:3],
        "relationship_tips": tips[:2],
        "explanation": explanation
    }


def _generate_seasonal_environment(daily_rhythm: Dict[str, Any], saju_data: Dict[str, Any], target_date=None) -> Dict[str, Any]:
    """계절/환경 추천"""
    # target_date 기준으로 계절 판단 (없으면 오늘 날짜)
    import datetime
    if target_date is not None:
        month = target_date.month
    else:
        month = datetime.date.today().month

    if month in [3, 4, 5]:  # 봄
        weather = ["가벼운 외출복 준비", "일교차 대비"]
        seasonal = ["봄나물 먹기", "꽃 구경", "산책"]
        env_focus = ["환절기 건강 관리", "꽃가루 알레르기 주의"]
        explanation = "봄철입니다. 화사한 계절을 즐기되, 일교차와 알레르기에 주의하세요."
    elif month in [6, 7, 8]:  # 여름
        weather = ["통풍 잘되는 옷", "자외선 차단"]
        seasonal = ["시원한 음식", "수분 보충", "물놀이"]
        env_focus = ["에어컨 적정 온도 유지", "실내외 온도차 조절"]
        explanation = "여름철입니다. 더위를 식히되, 과도한 냉방은 피하세요."
    elif month in [9, 10, 11]:  # 가을
        weather = ["겹쳐 입기", "환절기 대비"]
        seasonal = ["단풍 구경", "독서", "가을 과일"]
        env_focus = ["건조함 주의", "환기 자주 하기"]
        explanation = "가을철입니다. 선선한 날씨를 즐기되, 건조함에 대비하세요."
    else:  # 겨울
        weather = ["방한복 준비", "보온 철저"]
        seasonal = ["따뜻한 차", "실내 활동", "겨울 운동"]
        env_focus = ["실내 습도 유지", "체온 관리"]
        explanation = "겨울철입니다. 따뜻하게 지내고, 실내 습도를 유지하세요."

    return {
        "weather_adaptation": weather,
        "seasonal_activities": seasonal[:3],
        "environmental_focus": env_focus[:2],
        "explanation": explanation
    }


def _ensure_minimum_content_length(content: Dict[str, Any], daily_rhythm: Dict[str, Any]) -> Dict[str, Any]:
    """좌측 페이지 텍스트가 최소 700자 이상이 되도록 보장"""
    MIN_CHARS = 700

    def _left_page_length(c):
        return len(
            c["summary"] +
            c["rhythm_description"] +
            c["meaning_shift"] +
            c["rhythm_question"]
        )

    current = _left_page_length(content)
    if current >= MIN_CHARS:
        return content

    # 보강 블록 1: 리듬 해설 확장
    energy = daily_rhythm.get("에너지_수준", 3)
    concentration = daily_rhythm.get("집중력", 3)
    social = daily_rhythm.get("사회운", 3)

    expansion_paragraphs = []

    if concentration <= 3:
        expansion_paragraphs.append(
            "집중력이 고르게 분산되는 흐름이므로, 한 가지 일에 오래 매달리기보다는 "
            "여러 가지 작은 작업을 번갈아 처리하는 방식이 효율적입니다. "
            "짧은 휴식을 자주 취하며 리듬을 유지해보세요."
        )

    if social <= 3:
        expansion_paragraphs.append(
            "대인 관계에서는 무리하게 에너지를 쏟기보다 자연스러운 교류에 집중하는 것이 좋습니다. "
            "가까운 사람과의 편안한 대화가 오늘의 관계 에너지를 채워줄 것입니다."
        )

    if energy <= 3:
        expansion_paragraphs.append(
            "오늘은 자신의 페이스를 존중하는 것이 중요합니다. "
            "외부의 기대나 속도에 맞추려 하기보다, 내면의 리듬에 귀 기울여보세요. "
            "작은 성취를 하나씩 쌓아가는 것이 오늘의 가장 현명한 전략입니다."
        )

    # 일반 보강 블록 (항상 사용 가능)
    expansion_paragraphs.append(
        "하루를 시작하기 전 잠시 멈추어 오늘 가장 중요한 일 한 가지를 떠올려보세요. "
        "그 한 가지에 마음을 모으는 것만으로도 하루의 방향이 달라질 수 있습니다. "
        "완벽하지 않아도 괜찮으니, 오늘 할 수 있는 만큼만 정성을 다해보세요."
    )

    # 리듬 해설에 보강 문단 추가
    for para in expansion_paragraphs:
        if _left_page_length(content) >= MIN_CHARS:
            break
        content["rhythm_description"] = content["rhythm_description"] + " " + para

    # 그래도 부족하면 의미 전환 확장
    if _left_page_length(content) < MIN_CHARS:
        content["meaning_shift"] = content["meaning_shift"] + " " + (
            "오늘 하루의 의미는 결과가 아니라 과정에 있습니다. "
            "지금 이 순간 느끼는 감정과 생각을 있는 그대로 인정하고, "
            "그 안에서 작은 배움을 찾아보세요. 매일의 작은 깨달음이 모여 큰 변화를 만듭니다."
        )

    return content


def assemble_monthly_content(
    year: int,
    month: int,
    monthly_rhythm: Dict[str, Any]
) -> Dict[str, Any]:
    """
    월간 콘텐츠 조합

    Args:
        year: 년도
        month: 월
        monthly_rhythm: 월간 리듬 분석 결과

    Returns:
        월간 콘텐츠
    """
    theme = monthly_rhythm.get("주제", "균형과 조화")
    priorities = monthly_rhythm.get("우선순위", [])
    daily_energy = monthly_rhythm.get("일별_에너지", {})

    content = {
        "year_month": f"{year}년 {month}월",
        "theme": theme,
        "priorities": priorities,
        "calendar_data": daily_energy,
        "opportunities": monthly_rhythm.get("기회_요소", []),
        "challenges": monthly_rhythm.get("도전_요소", []),
    }

    return content


def assemble_yearly_content(
    year: int,
    yearly_rhythm: Dict[str, Any]
) -> Dict[str, Any]:
    """
    연간 콘텐츠 조합

    Args:
        year: 년도
        yearly_rhythm: 연간 리듬 분석 결과

    Returns:
        연간 콘텐츠
    """
    theme = yearly_rhythm.get("주제", "안정과 성장의 해")
    flow = yearly_rhythm.get("전체_흐름", "")
    monthly_signals = yearly_rhythm.get("월별_신호", {})

    content = {
        "year": year,
        "theme": theme,
        "flow_summary": flow,
        "monthly_signals": monthly_signals,
        "core_tasks": yearly_rhythm.get("핵심_과제", []),
    }

    return content
