"""
Role Translation Layer

동일한 리듬 콘텐츠를 역할에 맞게 재표현합니다.
의미는 동일하게 유지하되, 표현만 변경합니다.

지원 역할:
- student (학생): 학습/집중/페이스 관리
- office_worker (직장인): 업무/관계/결정/보고
- freelancer (프리랜서/자영업): 결정/계약/창작/체력
"""
from typing import Dict, Any
from copy import deepcopy


# 역할별 표현 매핑
ROLE_EXPRESSIONS = {
    "student": {
        # 활동 관련
        "활동": "공부",
        "프로젝트": "과제",
        "업무": "학습",
        "일": "공부",
        "작업": "학습",
        "교류": "토론",
        "네트워킹": "스터디",

        # 시간 관련
        "일정": "수업",
        "약속": "모임",

        # 결과 관련
        "성과": "성적",
        "결과물": "과제물",
        "보고": "발표",

        # 에너지 관련
        "체력": "집중력",
        "에너지": "학습 의욕",
    },

    "office_worker": {
        # 활동 관련
        "학습": "업무",
        "공부": "일",
        "과제": "프로젝트",
        "토론": "회의",
        "스터디": "협업",

        # 시간 관련
        "수업": "일정",
        "모임": "미팅",

        # 결과 관련
        "성적": "성과",
        "과제물": "결과물",
        "발표": "보고",

        # 관계 관련
        "친구": "동료",
        "선생님": "상사",
    },

    "freelancer": {
        # 활동 관련
        "업무": "작업",
        "일": "프로젝트",
        "과제": "의뢰",
        "회의": "미팅",
        "협업": "파트너십",

        # 시간 관련
        "일정": "스케줄",
        "수업": "워크숍",

        # 결과 관련
        "성과": "수익",
        "결과물": "납품물",
        "보고": "피드백",

        # 관계 관련
        "동료": "클라이언트",
        "상사": "발주처",

        # 결정 관련
        "결정": "계약",
        "선택": "의사결정",
    }
}


def translate_daily_content(
    content: Dict[str, Any],
    target_role: str
) -> Dict[str, Any]:
    """
    일간 콘텐츠를 역할에 맞게 번역

    Args:
        content: 원본 일간 콘텐츠 (중립적 표현)
        target_role: 대상 역할 ("student", "office_worker", "freelancer")

    Returns:
        역할에 맞게 변환된 콘텐츠
    """
    if target_role not in ROLE_EXPRESSIONS:
        # 지원하지 않는 역할이면 원본 반환
        return content

    # Deep copy to avoid modifying original
    translated = deepcopy(content)
    expression_map = ROLE_EXPRESSIONS[target_role]

    # 1. Summary 번역
    translated["summary"] = _translate_text(translated["summary"], expression_map)

    # 2. Keywords 번역
    translated["keywords"] = [
        _translate_text(kw, expression_map) for kw in translated["keywords"]
    ]

    # 3. Rhythm Description 번역
    translated["rhythm_description"] = _translate_text(
        translated["rhythm_description"], expression_map
    )

    # 4. Focus/Caution 번역
    translated["focus_caution"]["focus"] = [
        _translate_text(item, expression_map)
        for item in translated["focus_caution"]["focus"]
    ]
    translated["focus_caution"]["caution"] = [
        _translate_text(item, expression_map)
        for item in translated["focus_caution"]["caution"]
    ]

    # 5. Action Guide 번역
    translated["action_guide"]["do"] = [
        _translate_text(item, expression_map)
        for item in translated["action_guide"]["do"]
    ]
    translated["action_guide"]["avoid"] = [
        _translate_text(item, expression_map)
        for item in translated["action_guide"]["avoid"]
    ]

    # 6. Time/Direction notes 번역
    translated["time_direction"]["notes"] = _translate_text(
        translated["time_direction"]["notes"], expression_map
    )

    # 7. State Trigger 번역
    translated["state_trigger"]["gesture"] = _translate_text(
        translated["state_trigger"]["gesture"], expression_map
    )
    translated["state_trigger"]["phrase"] = _translate_text(
        translated["state_trigger"]["phrase"], expression_map
    )
    translated["state_trigger"]["how_to"] = _translate_text(
        translated["state_trigger"]["how_to"], expression_map
    )

    # 8. Meaning Shift 번역
    translated["meaning_shift"] = _translate_text(
        translated["meaning_shift"], expression_map
    )

    # 9. Rhythm Question 번역 (역할별 맥락 추가)
    translated["rhythm_question"] = _translate_question(
        translated["rhythm_question"], expression_map, target_role
    )

    # 10. Daily Health Sports 번역
    if "daily_health_sports" in translated:
        block = translated["daily_health_sports"]
        block["recommended_activities"] = [
            _translate_text(item, expression_map) for item in block.get("recommended_activities", [])
        ]
        block["health_tips"] = [
            _translate_text(item, expression_map) for item in block.get("health_tips", [])
        ]
        block["wellness_focused"] = [
            _translate_text(item, expression_map) for item in block.get("wellness_focused", [])
        ]
        block["explanation"] = _translate_text(block.get("explanation", ""), expression_map)

    # 11. Daily Meal Nutrition 번역
    if "daily_meal_nutrition" in translated:
        block = translated["daily_meal_nutrition"]
        block["flavor_profile"] = [
            _translate_text(item, expression_map) for item in block.get("flavor_profile", [])
        ]
        block["recommended_foods"] = [
            _translate_text(item, expression_map) for item in block.get("recommended_foods", [])
        ]
        block["avoid_foods"] = [
            _translate_text(item, expression_map) for item in block.get("avoid_foods", [])
        ]
        block["explanation"] = _translate_text(block.get("explanation", ""), expression_map)

    # 12. Daily Fashion Beauty 번역
    if "daily_fashion_beauty" in translated:
        block = translated["daily_fashion_beauty"]
        block["clothing_style"] = [
            _translate_text(item, expression_map) for item in block.get("clothing_style", [])
        ]
        block["color_suggestions"] = [
            _translate_text(item, expression_map) for item in block.get("color_suggestions", [])
        ]
        block["beauty_tips"] = [
            _translate_text(item, expression_map) for item in block.get("beauty_tips", [])
        ]
        block["explanation"] = _translate_text(block.get("explanation", ""), expression_map)

    # 13. Daily Shopping Finance 번역
    if "daily_shopping_finance" in translated:
        block = translated["daily_shopping_finance"]
        block["good_to_buy"] = [
            _translate_text(item, expression_map) for item in block.get("good_to_buy", [])
        ]
        block["finance_advice"] = [
            _translate_text(item, expression_map) for item in block.get("finance_advice", [])
        ]
        block["investment_focus"] = [
            _translate_text(item, expression_map) for item in block.get("investment_focus", [])
        ]
        block["explanation"] = _translate_text(block.get("explanation", ""), expression_map)

    # 14. Daily Living Space 번역
    if "daily_living_space" in translated:
        block = translated["daily_living_space"]
        block["space_organization"] = [
            _translate_text(item, expression_map) for item in block.get("space_organization", [])
        ]
        block["plants_decor"] = [
            _translate_text(item, expression_map) for item in block.get("plants_decor", [])
        ]
        block["environmental_tips"] = [
            _translate_text(item, expression_map) for item in block.get("environmental_tips", [])
        ]
        block["explanation"] = _translate_text(block.get("explanation", ""), expression_map)

    # 15. Daily Routines 번역
    if "daily_routines" in translated:
        block = translated["daily_routines"]
        block["sleep_schedule"] = [
            _translate_text(item, expression_map) for item in block.get("sleep_schedule", [])
        ]
        block["morning_routine"] = [
            _translate_text(item, expression_map) for item in block.get("morning_routine", [])
        ]
        block["evening_routine"] = [
            _translate_text(item, expression_map) for item in block.get("evening_routine", [])
        ]
        block["explanation"] = _translate_text(block.get("explanation", ""), expression_map)

    # 16. Digital Communication 번역
    if "digital_communication" in translated:
        block = translated["digital_communication"]
        block["device_usage"] = [
            _translate_text(item, expression_map) for item in block.get("device_usage", [])
        ]
        block["social_media"] = [
            _translate_text(item, expression_map) for item in block.get("social_media", [])
        ]
        block["online_focus_areas"] = [
            _translate_text(item, expression_map) for item in block.get("online_focus_areas", [])
        ]
        block["explanation"] = _translate_text(block.get("explanation", ""), expression_map)

    # 17. Hobbies Creativity 번역
    if "hobbies_creativity" in translated:
        block = translated["hobbies_creativity"]
        block["creative_activities"] = [
            _translate_text(item, expression_map) for item in block.get("creative_activities", [])
        ]
        block["learning_recommendations"] = [
            _translate_text(item, expression_map) for item in block.get("learning_recommendations", [])
        ]
        block["entertainment_options"] = [
            _translate_text(item, expression_map) for item in block.get("entertainment_options", [])
        ]
        block["explanation"] = _translate_text(block.get("explanation", ""), expression_map)

    # 18. Relationships Social 번역
    if "relationships_social" in translated:
        block = translated["relationships_social"]
        block["communication_style"] = [
            _translate_text(item, expression_map) for item in block.get("communication_style", [])
        ]
        block["social_energies"] = [
            _translate_text(item, expression_map) for item in block.get("social_energies", [])
        ]
        block["relationship_tips"] = [
            _translate_text(item, expression_map) for item in block.get("relationship_tips", [])
        ]
        block["explanation"] = _translate_text(block.get("explanation", ""), expression_map)

    # 19. Seasonal Environment 번역
    if "seasonal_environment" in translated:
        block = translated["seasonal_environment"]
        block["weather_adaptation"] = [
            _translate_text(item, expression_map) for item in block.get("weather_adaptation", [])
        ]
        block["seasonal_activities"] = [
            _translate_text(item, expression_map) for item in block.get("seasonal_activities", [])
        ]
        block["environmental_focus"] = [
            _translate_text(item, expression_map) for item in block.get("environmental_focus", [])
        ]
        block["explanation"] = _translate_text(block.get("explanation", ""), expression_map)

    return translated


def _translate_text(text: str, expression_map: Dict[str, str]) -> str:
    """
    텍스트 번역 (표현 매핑 적용)

    한국어 단어 경계를 고려하여 치환합니다.
    앞뒤가 공백/문장부호/문자열 시작·끝인 경우에만 치환하여
    "스타일", "일어나기" 같은 단어 내부 오염을 방지합니다.

    Args:
        text: 원본 텍스트
        expression_map: 표현 매핑 사전

    Returns:
        번역된 텍스트
    """
    import re
    translated = text

    # 긴 표현부터 먼저 치환 (부분 매치 방지)
    sorted_expressions = sorted(
        expression_map.items(),
        key=lambda x: len(x[0]),
        reverse=True
    )

    # 단어 경계로 인정하는 문자들 (앞·뒤)
    _BOUNDARY = r'[\s\(\[\{「『【\.,!?;:·\-]'

    for original_expr, role_expr in sorted_expressions:
        # 앞: 문자열 시작 또는 경계 문자 (경계 문자는 캡처 그룹으로 유지)
        # 뒤: 문자열 끝 또는 경계 문자 (lookahead이므로 소비하지 않음)
        pattern = (
            r'(^|' + _BOUNDARY + r')'
            + re.escape(original_expr)
            + r'(?=' + _BOUNDARY + r'|$)'
        )
        replacement = r'\g<1>' + role_expr
        translated = re.sub(pattern, replacement, translated, flags=re.MULTILINE)

    return translated


def _translate_question(
    question: str,
    expression_map: Dict[str, str],
    target_role: str
) -> str:
    """
    질문 번역 (역할별 맥락 추가)

    Args:
        question: 원본 질문
        expression_map: 표현 매핑
        target_role: 대상 역할

    Returns:
        번역된 질문
    """
    # 먼저 기본 번역 적용
    translated = _translate_text(question, expression_map)

    # 역할별 맥락 추가 (선택적)
    role_contexts = {
        "student": "",  # 학생은 맥락 추가 불필요 (질문이 이미 명확)
        "office_worker": "",
        "freelancer": ""
    }

    context = role_contexts.get(target_role, "")
    if context:
        translated = f"{translated} {context}"

    return translated


def translate_monthly_content(
    content: Dict[str, Any],
    target_role: str
) -> Dict[str, Any]:
    """
    월간 콘텐츠를 역할에 맞게 번역

    Args:
        content: 원본 월간 콘텐츠
        target_role: 대상 역할 ("student", "office_worker", "freelancer")

    Returns:
        역할에 맞게 변환된 콘텐츠
    """
    if target_role not in ROLE_EXPRESSIONS:
        return content

    translated = deepcopy(content)
    expression_map = ROLE_EXPRESSIONS[target_role]

    # theme 번역
    if "theme" in translated and isinstance(translated["theme"], str):
        translated["theme"] = _translate_text(translated["theme"], expression_map)

    # priorities 번역
    if "priorities" in translated and isinstance(translated["priorities"], list):
        translated["priorities"] = [
            _translate_text(item, expression_map) if isinstance(item, str) else item
            for item in translated["priorities"]
        ]

    # opportunities 번역
    if "opportunities" in translated and isinstance(translated["opportunities"], list):
        translated["opportunities"] = [
            _translate_text(item, expression_map) if isinstance(item, str) else item
            for item in translated["opportunities"]
        ]

    # challenges 번역
    if "challenges" in translated and isinstance(translated["challenges"], list):
        translated["challenges"] = [
            _translate_text(item, expression_map) if isinstance(item, str) else item
            for item in translated["challenges"]
        ]

    # calendar_data, year_month는 번역하지 않음 (수치/날짜)

    return translated


def translate_yearly_content(
    content: Dict[str, Any],
    target_role: str
) -> Dict[str, Any]:
    """
    연간 콘텐츠를 역할에 맞게 번역

    Args:
        content: 원본 연간 콘텐츠
        target_role: 대상 역할 ("student", "office_worker", "freelancer")

    Returns:
        역할에 맞게 변환된 콘텐츠
    """
    if target_role not in ROLE_EXPRESSIONS:
        return content

    translated = deepcopy(content)
    expression_map = ROLE_EXPRESSIONS[target_role]

    # theme 번역
    if "theme" in translated and isinstance(translated["theme"], str):
        translated["theme"] = _translate_text(translated["theme"], expression_map)

    # flow_summary 번역
    if "flow_summary" in translated and isinstance(translated["flow_summary"], str):
        translated["flow_summary"] = _translate_text(translated["flow_summary"], expression_map)

    # core_tasks 번역
    if "core_tasks" in translated and isinstance(translated["core_tasks"], list):
        translated["core_tasks"] = [
            _translate_text(item, expression_map) if isinstance(item, str) else item
            for item in translated["core_tasks"]
        ]

    # monthly_signals, year는 번역하지 않음

    return translated


def validate_semantic_preservation(
    original: Dict[str, Any],
    translated: Dict[str, Any]
) -> tuple[bool, list]:
    """
    의미 불변성 검증

    원본과 번역본이 구조적으로 동일한지 확인

    Args:
        original: 원본 콘텐츠
        translated: 번역된 콘텐츠

    Returns:
        (검증 통과 여부, 차이점 메시지 리스트)
    """
    issues = []

    # 1. 날짜 동일 확인
    if original.get("date") != translated.get("date"):
        issues.append("날짜가 다릅니다")

    # 2. 키워드 개수 확인
    if len(original.get("keywords", [])) != len(translated.get("keywords", [])):
        issues.append(
            f"키워드 개수 불일치: {len(original['keywords'])} vs {len(translated['keywords'])}"
        )

    # 3. Focus/Caution 개수 확인
    orig_fc = original.get("focus_caution", {})
    trans_fc = translated.get("focus_caution", {})

    if len(orig_fc.get("focus", [])) != len(trans_fc.get("focus", [])):
        issues.append("집중 포인트 개수 불일치")
    if len(orig_fc.get("caution", [])) != len(trans_fc.get("caution", [])):
        issues.append("주의 포인트 개수 불일치")

    # 4. Action Guide 개수 확인
    orig_ag = original.get("action_guide", {})
    trans_ag = translated.get("action_guide", {})

    if len(orig_ag.get("do", [])) != len(trans_ag.get("do", [])):
        issues.append("추천 행동 개수 불일치")
    if len(orig_ag.get("avoid", [])) != len(trans_ag.get("avoid", [])):
        issues.append("피할 행동 개수 불일치")

    # 5. 콘텐츠 길이 비교 (±30% 이내여야 함)
    orig_len = _calculate_content_length(original)
    trans_len = _calculate_content_length(translated)

    if orig_len > 0:
        ratio = abs(trans_len - orig_len) / orig_len
        if ratio > 0.3:
            issues.append(
                f"콘텐츠 길이 차이가 30%를 초과합니다: {orig_len} → {trans_len} ({ratio*100:.1f}%)"
            )

    # 6. 핵심 블록 존재 여부 확인
    if not translated.get("rhythm_description"):
        issues.append("리듬 해설이 비어있습니다")
    if not translated.get("meaning_shift"):
        issues.append("의미 전환이 비어있습니다")
    if not translated.get("rhythm_question"):
        issues.append("리듬 질문이 비어있습니다")

    return (len(issues) == 0, issues)


def _calculate_content_length(content: Dict[str, Any]) -> int:
    """콘텐츠 총 길이 계산"""
    total = 0

    total += len(content.get("summary", ""))
    total += len(content.get("rhythm_description", ""))
    total += len(content.get("meaning_shift", ""))
    total += len(content.get("rhythm_question", ""))

    # Focus/Caution
    fc = content.get("focus_caution", {})
    for item in fc.get("focus", []):
        total += len(item)
    for item in fc.get("caution", []):
        total += len(item)

    # Action Guide
    ag = content.get("action_guide", {})
    for item in ag.get("do", []):
        total += len(item)
    for item in ag.get("avoid", []):
        total += len(item)

    # State Trigger
    st = content.get("state_trigger", {})
    total += len(st.get("how_to", ""))

    return total
