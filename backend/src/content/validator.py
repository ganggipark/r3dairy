"""
DAILY_CONTENT_SCHEMA.json 검증기

생성된 콘텐츠가 스키마를 준수하는지 검증합니다.
"""
from typing import Dict, Any, List, Tuple
from .char_optimizer import CharOptimizer


def validate_daily_content(content: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    일간 콘텐츠가 DAILY_CONTENT_SCHEMA.json을 준수하는지 검증

    Args:
        content: 검증할 콘텐츠 딕셔너리

    Returns:
        (is_valid, errors): 검증 성공 여부와 에러 메시지 리스트
    """
    errors = []

    # 필수 필드 검증
    required_fields = [
        "date",
        "summary",
        "keywords",
        "rhythm_description",
        "focus_caution",
        "action_guide",
        "time_direction",
        "state_trigger",
        "meaning_shift",
        "rhythm_question",
    ]

    for field in required_fields:
        if field not in content:
            errors.append(f"필수 필드 누락: {field}")

    # date 검증
    if "date" in content:
        if not isinstance(content["date"], str):
            errors.append("date는 문자열이어야 합니다")
        elif not _is_valid_date_format(content["date"]):
            errors.append("date는 YYYY-MM-DD 형식이어야 합니다")

    # summary 검증
    if "summary" in content:
        if not isinstance(content["summary"], str):
            errors.append("summary는 문자열이어야 합니다")
        elif len(content["summary"]) < 10:
            errors.append("summary는 최소 10자 이상이어야 합니다")

    # keywords 검증
    if "keywords" in content:
        if not isinstance(content["keywords"], list):
            errors.append("keywords는 리스트여야 합니다")
        elif len(content["keywords"]) < 3:
            errors.append("keywords는 최소 3개 이상이어야 합니다")
        elif len(content["keywords"]) > 8:
            errors.append("keywords는 최대 8개 이하여야 합니다")

    # rhythm_description 검증
    if "rhythm_description" in content:
        if not isinstance(content["rhythm_description"], str):
            errors.append("rhythm_description은 문자열이어야 합니다")
        elif len(content["rhythm_description"]) < 50:
            errors.append("rhythm_description은 최소 50자 이상이어야 합니다")

    # focus_caution 검증
    if "focus_caution" in content:
        fc = content["focus_caution"]
        if not isinstance(fc, dict):
            errors.append("focus_caution은 딕셔너리여야 합니다")
        else:
            if "focus" not in fc or not isinstance(fc["focus"], list):
                errors.append("focus_caution.focus는 리스트여야 합니다")
            if "caution" not in fc or not isinstance(fc["caution"], list):
                errors.append("focus_caution.caution은 리스트여야 합니다")

    # action_guide 검증
    if "action_guide" in content:
        ag = content["action_guide"]
        if not isinstance(ag, dict):
            errors.append("action_guide는 딕셔너리여야 합니다")
        else:
            if "do" not in ag or not isinstance(ag["do"], list):
                errors.append("action_guide.do는 리스트여야 합니다")
            if "avoid" not in ag or not isinstance(ag["avoid"], list):
                errors.append("action_guide.avoid는 리스트여야 합니다")

    # time_direction 검증
    if "time_direction" in content:
        td = content["time_direction"]
        if not isinstance(td, dict):
            errors.append("time_direction은 딕셔너리여야 합니다")
        else:
            required_td_fields = ["good_time", "avoid_time", "good_direction", "avoid_direction", "notes"]
            for field in required_td_fields:
                if field not in td:
                    errors.append(f"time_direction.{field} 필드 누락")

    # state_trigger 검증
    if "state_trigger" in content:
        st = content["state_trigger"]
        if not isinstance(st, dict):
            errors.append("state_trigger는 딕셔너리여야 합니다")
        else:
            required_st_fields = ["gesture", "phrase", "how_to"]
            for field in required_st_fields:
                if field not in st:
                    errors.append(f"state_trigger.{field} 필드 누락")

    # meaning_shift 검증
    if "meaning_shift" in content:
        if not isinstance(content["meaning_shift"], str):
            errors.append("meaning_shift는 문자열이어야 합니다")
        elif len(content["meaning_shift"]) < 30:
            errors.append("meaning_shift는 최소 30자 이상이어야 합니다")

    # rhythm_question 검증
    if "rhythm_question" in content:
        if not isinstance(content["rhythm_question"], str):
            errors.append("rhythm_question은 문자열이어야 합니다")
        elif len(content["rhythm_question"]) < 10:
            errors.append("rhythm_question은 최소 10자 이상이어야 합니다")

    # 좌측 페이지 최소 글자 수 검증
    left_page_length = _calculate_left_page_length(content)
    if left_page_length < 400:
        errors.append(f"좌측 페이지 총 글자 수 부족: {left_page_length}자 (최소 400자 필요)")

    # 설명형 문단 존재 여부 검증
    if not _has_explanatory_paragraphs(content):
        errors.append("좌측 페이지에 설명형 문단이 필요합니다 (카드 전용 요약만으로는 불충분)")

    # CharOptimizer를 사용한 블록별 글자 수 검증
    char_valid, total_chars, char_issues = CharOptimizer.validate_page(content)
    if not char_valid:
        for issue in char_issues:
            errors.append(issue.get("message", "글자 수 검증 실패"))

    is_valid = len(errors) == 0
    return is_valid, errors


def _is_valid_date_format(date_str: str) -> bool:
    """YYYY-MM-DD 형식 검증"""
    import re
    pattern = r"^\d{4}-\d{2}-\d{2}$"
    return bool(re.match(pattern, date_str))


def _calculate_left_page_length(content: Dict[str, Any]) -> int:
    """좌측 페이지 총 글자 수 계산"""
    total_length = 0

    # summary
    total_length += len(content.get("summary", ""))

    # rhythm_description (주요 설명 블록)
    total_length += len(content.get("rhythm_description", ""))

    # focus_caution의 모든 항목
    fc = content.get("focus_caution", {})
    for item in fc.get("focus", []):
        total_length += len(item)
    for item in fc.get("caution", []):
        total_length += len(item)

    # action_guide의 모든 항목
    ag = content.get("action_guide", {})
    for item in ag.get("do", []):
        total_length += len(item)
    for item in ag.get("avoid", []):
        total_length += len(item)

    # time_direction의 notes (설명)
    td = content.get("time_direction", {})
    total_length += len(td.get("notes", ""))

    # state_trigger의 how_to (설명)
    st = content.get("state_trigger", {})
    total_length += len(st.get("how_to", ""))

    # meaning_shift (의미 전환 설명)
    total_length += len(content.get("meaning_shift", ""))

    # rhythm_question
    total_length += len(content.get("rhythm_question", ""))

    return total_length


def _has_explanatory_paragraphs(content: Dict[str, Any]) -> bool:
    """설명형 문단 존재 여부 확인"""
    # rhythm_description이 충분히 긴지 확인 (최소 200자)
    if len(content.get("rhythm_description", "")) >= 200:
        return True

    # meaning_shift가 충분히 긴지 확인 (최소 80자)
    if len(content.get("meaning_shift", "")) >= 80:
        return True

    # time_direction.notes가 충분히 긴지 확인
    td = content.get("time_direction", {})
    if len(td.get("notes", "")) >= 30:
        return True

    # state_trigger.how_to가 충분히 긴지 확인
    st = content.get("state_trigger", {})
    if len(st.get("how_to", "")) >= 30:
        return True

    return False


def validate_monthly_content(content: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    월간 콘텐츠 검증

    Args:
        content: 검증할 월간 콘텐츠

    Returns:
        (is_valid, errors)
    """
    errors = []

    required_fields = ["year_month", "theme", "priorities", "calendar_data"]

    for field in required_fields:
        if field not in content:
            errors.append(f"필수 필드 누락: {field}")

    # priorities 검증
    if "priorities" in content:
        if not isinstance(content["priorities"], list):
            errors.append("priorities는 리스트여야 합니다")
        elif len(content["priorities"]) < 3:
            errors.append("priorities는 최소 3개 이상이어야 합니다")

    # calendar_data 검증
    if "calendar_data" in content:
        if not isinstance(content["calendar_data"], dict):
            errors.append("calendar_data는 딕셔너리여야 합니다")

    is_valid = len(errors) == 0
    return is_valid, errors


def validate_yearly_content(content: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    연간 콘텐츠 검증

    Args:
        content: 검증할 연간 콘텐츠

    Returns:
        (is_valid, errors)
    """
    errors = []

    required_fields = ["year", "theme", "flow_summary", "monthly_signals"]

    for field in required_fields:
        if field not in content:
            errors.append(f"필수 필드 누락: {field}")

    # monthly_signals 검증 (12개월)
    if "monthly_signals" in content:
        if not isinstance(content["monthly_signals"], dict):
            errors.append("monthly_signals는 딕셔너리여야 합니다")
        elif len(content["monthly_signals"]) != 12:
            errors.append(f"monthly_signals는 12개월이어야 합니다 (현재: {len(content['monthly_signals'])}개)")

    is_valid = len(errors) == 0
    return is_valid, errors
