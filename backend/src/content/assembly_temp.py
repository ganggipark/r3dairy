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
    date: datetime.date,
    saju_data: Dict[str, Any],
    daily_rhythm: Dict[str, Any]
) -> Dict[str, Any]:
    """
    일간 콘텐츠 조합

    Args:
        date: 대상 날짜
        saju_data: 사주 계산 결과 (내부 데이터)
        daily_rhythm: 일간 리듬 분석 결과 (내부 데이터)

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

    # 6. 시간/방향 (time_direction)
    time_direction = _generate_time_direction(daily_rhythm)

    # 7. 상태 트리거 (state_trigger)
    state_trigger = _generate_state_trigger(daily_rhythm)

    # 8. 의미 전환 (meaning_shift) - 설명형 문단
    meaning_shift = _generate_meaning_shift(daily_rhythm, saju_data)

    # 9. 리듬 질문 (rhythm_question)
    rhythm_question = _generate_rhythm_question(daily_rhythm)

    content = {
        "date": date.strftime("%Y-%m-%d"),
        "summary": summary,
        "keywords": keywords,
        "rhythm_description": rhythm_description,
        "focus_caution": focus_caution,
        "action_guide": action_guide,
        "time_direction": time_direction,
        "state_trigger": state_trigger,
        "meaning_shift": meaning_shift,
        "rhythm_question": rhythm_question,
        
        # Extended blocks (placeholder - to be fully implemented)
        "saju_summary": _generate_saju_summary if '_generate_saju_summary' in globals() else "Pending implementation - saju_summary will show overall fortune patterns",
        "sinsal_influence": _generate_sinsal_influence if '_generate_sinsal_influence' in globals() else "Pending implementation - sinsal_influence will show auspicious effects",
        "direction_detail": _generate_direction_detail if '_generate_direction_detail' in globals() else "Pending implementation - direction_detail will show detailed direction guidance",
        "palace_insight": _generate_palace_insight if '_generate_palace_insight' in globals() else "Pending implementation - palace_insight will show life palace analysis",
        "yongsin_utilization": _generate_yongsin_utilization if '_generate_yongsin_utilization' in globals() else "Pending implementation - yongsin_utilization will show how to use beneficial stars",
        "daewoon_entry": _generate_daewoon_entry if '_generate_daewoon_entry' in globals() else "Pending implementation - daewoon_entry will show ten-year luck context",
        "sewon_summary": _generate_sewon_summary if '_generate_sewon_summary' in globals() else "Pending implementation - sewon_summary will show yearly luck overview",
    }

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

    return f"오늘은 {energy_text} 에너지가 흐르는 날입니다. {flow}을 경험하게 됩니다."


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
    """리듬 해설 생성 (설명형 문단, 200-300자 목표)"""
    energy = daily_rhythm.get("에너지_수준", 3)
    concentration = daily_rhythm.get("집중력", 3)
    social = daily_rhythm.get("사회운", 3)
    decision = daily_rhythm.get("결정력", 3)
    flow = daily_rhythm.get("주요_흐름", "균형의 시기")

    description = f"오늘의 리듬은 '{flow}'로 요약됩니다. "

    # 에너지 수준별 상세 설명
    if energy >= 4:
        description += "높은 에너지가 흐르면서 활동적인 하루가 예상됩니다. 이 시기에는 새로운 프로젝트를 시작하거나 중요한 업무를 처리하기에 최적의 조건을 갖추고 있습니다. 넘치는 에너지를 방향성 있게 활용하면 평소보다 훨씬 효율적인 결과를 얻을 수 있습니다. "
    elif energy <= 2:
        description += "에너지가 차분하게 흐르며 내면의 목소리에 귀 기울일 필요가 있습니다. 무리한 활동보다는 충분한 휴식과 재충전 시간을 확보하여 다음 날을 준비하는 것이 현명합니다. 이 시간을 통해 얻은 내면의 통찰이 곧 중요한 자산이 될 것입니다. "
    else:
        description += "안정적인 에너지가 유지되며 일상 활동을 꾸준히 이어갈 수 있는 좋은 균형 상태입니다. 큰 변화 없이도 충분히 의미 있는 하루를 보낼 수 있습니다. 꾸준함이 쌓여 만들어내는 안정감이 오늘의 가장 큰 자원입니다. "

    # 인지적 기능별 설명
    if concentration >= 4:
        description += "집중력이 최고조에 달하므로 복잡한 문제 해결이나 깊이 있는 학습에 몰입하기 좋은 시간입니다. 이 시간대의 깊은 사고는 평소보다 더 뛰어난 통찰력을 발휘하게 할 것입니다. "
    elif concentration <= 2:
        description += "집중력이 분산되기 쉬우므로 중요한 작업은 에너지가 좋은 시간대로 미루거나, 여러 작은 단계로 나누어 진행하는 것이 좋습니다. 부드러운 접근이 더 효율적인 결과를 낳습니다. "

    # 사회적 기능별 설명
    if social >= 4:
        description += "사람들과의 교류가 자연스럽게 활발해지므로 네트워킹이나 관계 형성에 좋은 기회를 맞이하게 됩니다. 이러한 소통은 예상치 못한 새로운 가능성을 열어줄 수 있습니다. "
    elif social <= 2:
        description += "혼자만의 시간이 더 필요한 시기이므로 과도한 사교 활동보다는 내면 정리에 집중하는 것이 에너지 효율성을 높입니다. 내면의 소리를 듣는 것이 외부의 소음보다 더 가치 있습니다. "

    # 결정력별 설명
    if decision >= 4:
        description += "결단력이 강화되어 망설였던 중요한 선택이나 새로운 실행을 시작하기에 적합한 날입니다. 확신이 서는 순간 망설임 없이 행동하는 용기가 필요합니다. "
    elif decision <= 2:
        description += "결정이 필요한 일들은 잠시 미루고 충분한 정보 수집과 준비 시간을 갖는 것이 현명한 접근입니다. 성급한 선택보다는 신중한 고려가 더 나은 결과를 가져올 것입니다. "

    # 종합적인 하루 가이드
    description += "오늘 하루 동안 자신의 리듬을 잘 관찰하고 그에 맞춰 활동의 강도와 종류를 조절해 나가는 것이 중요합니다. 자연스러운 흐름에 저항하지 않고 그 에너지를 현명하게 활용하는 지혜가 필요합니다. "

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
            "활발한 움직임과 교류",
            "긴급한 결정사항 처리하기",
            "에너지가 필요한 중요한 만남 준비하기"
        ])
    elif energy >= 3:
        do.extend([
            "일상 업무를 차분히 처리하기",
            "계획 점검 및 정리",
            "편안한 대화와 소통",
            "균형 잡힌 활동 계획하기",
            "중간 목표 점검하고 조정하기"
        ])
    else:
        do.extend([
            "충분한 휴식 취하기",
            "내면 성찰과 기록",
            "가벼운 정리 활동",
            "몸과 마음 돌보기",
            "느린 호흡과 명상 시간 갖기"
        ])

    # Avoid 항목
    if energy <= 2:
        avoid.extend([
            "과도한 일정 잡기",
            "중요한 결정 서두르기", 
            "무리한 약속",
            "에너지 소모가 큰 사회 활동",
            "새로운 프로젝트 시작하기"
        ])
    else:
        avoid.extend([
            "충동적 선택",
            "피로를 무시한 활동",
            "불필요한 갈등",
            "과도한 욕심으로 인한 스트레스",
            "에너지 분산되는 여러 활동 동시에 하기"
        ])

    return {
        "do": do[:5],
        "avoid": avoid[:5]
    }


def _generate_time_direction(daily_rhythm: Dict[str, Any]) -> Dict[str, str]:
    """시간/방향 정보 생성"""
    good_times = daily_rhythm.get("유리한_시간", [])
    caution_times = daily_rhythm.get("주의_시간", [])
    good_directions = daily_rhythm.get("유리한_방향", [])

    good_time_str = ", ".join(good_times) if good_times else "오전 시간대"
    avoid_time_str = ", ".join(caution_times) if caution_times else "늦은 밤"
    good_direction_str = ", ".join(good_directions) if good_directions else "동쪽"
    avoid_direction_str = "특별히 피할 방향 없음"

    notes = f"오늘은 {good_time_str}에 집중력과 효율이 높아집니다. 이 시간대는 자연스럽게 리듬이 맞춰지므로 중요한 작업이나 결정을 처리하기에 최적입니다. "
    notes += f"가능하다면 {good_direction_str} 방향으로의 활동이나 이동을 고려해보세요. 방향성은 무의식적인 안정감과 긍정적 에너지를 불러일으키는 효과가 있습니다. "
    notes += f"{avoid_time_str}에는 중요한 일을 피하고 휴식이나 가벼운 활동으로 전환하는 것이 좋습니다."

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
    """의미 전환 생성 (설명형 문단, 80-120자 목표)"""
    energy = daily_rhythm.get("에너지_수준", 3)
    challenges = daily_rhythm.get("도전_요소", [])

    if energy <= 2:
        shift = "에너지가 낮다는 것은 무능력이 아니라, 자연스러운 충전 신호입니다. "
        shift += "에너지가 적을 때 억지로 생산성을 내려는 압박감에서 벗어나, 휴식 그 자체를 의미 있는 활동으로 인식하는 전환이 필요합니다. "
        shift += "이 시간은 다음 에너지 주기를 위한 준비 과정입니다."
    elif energy >= 4:
        shift = "넘치는 에너지는 무조건 소모해야 할 대상이 아니라, 방향성 있게 활용할 기회입니다. "
        shift += "활동성이 높을 때 무분별하게 분산시키기보다, 가장 중요한 목표에 집중하고 때로는 내일을 위해 에너지를 보존하는 지혜가 필요합니다. "
        shift += "이는 단기적 성과보다는 장기적 균형을 위한 현명한 선택입니다."
    else:
        shift = "평범한 하루라는 느낌은 오히려 안정의 증거이자 내면이 정리되는 과정입니다. "
        shift += "특별함을 강요하지 않고 지금 이 순간을 있는 그대로 받아들이는 것 자체가 의미 있는 성장이며, "
        shift += "일상의 작은 성취들이 쌓여 더 큰 변화를 만들어간다는 사실을 기억하세요."

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


