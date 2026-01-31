"""Korean localization for survey forms."""

from __future__ import annotations

from typing import Dict, Any

from ...skills.form_builder.models import FormConfiguration, FormField, FormSection


# Korean language settings
KOREAN_SETTINGS = {
    "locale": "ko-KR",
    "timezone": "Asia/Seoul",
    "date_format": "YYYY-MM-DD",
    "currency": "KRW",

    # Field labels and options
    "gender_options": ["남성", "여성", "기타", "답변 안 함"],

    "role_options": [
        "학생",
        "직장인",
        "프리랜서 / 자영업",
        "부모",
        "기타"
    ],

    "interests": [
        "커리어 / 일자리",
        "자기개발",
        "건강 / 피트니스",
        "인간관계",
        "재무",
        "취미 / 창작",
        "영성 / 철학",
        "교육 / 학습",
        "여행",
        "기타"
    ],

    "tone_preferences": [
        "따뜻하고 지지적인",
        "직접적이고 실용적인",
        "동기부여적이고 활력적인",
        "차분하고 성찰적인"
    ],

    "diary_format_options": [
        "앱 전용 (웹/모바일)",
        "하이브리드 (앱 + 월간 인쇄본)",
        "종이 다이어리 전용 (월간 배송)"
    ],

    "paper_sizes": ["A5 (컴팩트)", "A4 (표준)", "Custom (맞춤)"],

    "delivery_frequencies": ["월간", "분기별", "연간"],

    "email_frequencies": [
        "매일 인사이트",
        "주간 요약",
        "월간 뉴스레터",
        "받지 않음"
    ],

    # Section titles and descriptions
    "sections": {
        "basic_info": {
            "title": "기본 정보",
            "description": "당신에 대해 알려주세요"
        },
        "role": {
            "title": "역할 선택",
            "description": "당신의 상황에 맞는 콘텐츠를 제공하기 위해 필요합니다"
        },
        "personality": {
            "title": "성격 평가",
            "description": "각 문항이 당신을 얼마나 잘 설명하는지 평가해주세요 (1 = 전혀 그렇지 않다, 5 = 매우 그렇다)"
        },
        "interests": {
            "title": "관심사 및 선호도",
            "description": "당신에게 가장 중요한 것이 무엇인지 알려주세요"
        },
        "format": {
            "title": "다이어리 형식",
            "description": "다이어리를 어떻게 사용하고 싶으신가요?"
        },
        "paper_details": {
            "title": "종이 배송 상세정보",
            "description": "종이 다이어리 선호사항을 알려주세요"
        },
        "communication": {
            "title": "커뮤니케이션 선호도",
            "description": "어떻게 연락드릴까요?"
        }
    },

    # Field labels
    "fields": {
        "name": "이름",
        "email": "이메일 주소",
        "birth_date": "생년월일",
        "gender": "성별",
        "primary_role": "주요 역할이 무엇인가요?",
        "topics": "어떤 주제에 관심이 있으신가요? (최대 5개)",
        "tone_preference": "선호하는 커뮤니케이션 톤",
        "diary_preference": "다이어리를 어떻게 사용하고 싶으신가요?",
        "paper_size": "선호하는 종이 크기",
        "delivery_frequency": "인쇄본 배송 주기",
        "delivery_address": "배송 주소",
        "email_frequency": "이메일 업데이트 주기",
        "privacy_consent": "개인정보 처리방침에 동의합니다",
        "marketing_consent": "마케팅 이메일을 받고 싶습니다",
        "research_consent": "사용자 연구에 참여할 의향이 있습니다"
    },

    # Personality questions (Korean)
    "personality_questions": {
        "p_extroversion": "나는 새로운 사람을 만나고 사교 활동을 즐긴다",
        "p_structured": "나는 즉흥적인 행동보다 구조화된 계획을 선호한다",
        "p_openness": "나는 새로운 아이디어와 경험에 열려 있다",
        "p_empathy": "나는 다른 사람의 감정을 깊이 공감한다",
        "p_calm": "나는 스트레스 상황에서도 침착하고 평온을 유지한다",
        "p_focus": "나는 완료할 때까지 작업에 깊이 집중한다",
        "p_creative": "나는 창의적이고 예술적인 활동을 즐긴다",
        "p_logical": "나는 감정보다 논리에 기반하여 결정을 내린다"
    },

    # Placeholders
    "placeholders": {
        "name": "이름을 입력하세요",
        "email": "you@example.com",
        "delivery_address": "도로명 주소, 도시, 우편번호, 국가"
    },

    # Descriptions
    "descriptions": {
        "email": "개인화된 다이어리를 전송하는 데 사용됩니다",
        "birth_date": "개인화된 리듬 분석에 필요합니다",
        "diary_preference": "종이 버전은 개인화된 일일 가이드가 인쇄되어 제공됩니다",
        "privacy_consent": "서비스 이용에 필수입니다",
        "marketing_consent": "언제든지 구독 취소할 수 있습니다",
        "research_consent": "제품 개선에 도움을 주세요"
    }
}


def apply_korean_localization(form: FormConfiguration) -> FormConfiguration:
    """
    Apply Korean-specific labels and options to a form.

    Args:
        form: English form configuration

    Returns:
        Korean-localized form configuration
    """
    # Create a copy to avoid modifying the original
    korean_form = FormConfiguration(
        id=form.id,
        name=_translate_form_name(form.name),
        description=_translate_form_description(form.description),
        sections=[],
        metadata={**form.metadata, "locale": "ko-KR"},
        webhook_url=form.webhook_url,
        version=form.version,
        created_at=form.created_at,
    )

    # Translate sections
    for section in form.sections:
        korean_section = _translate_section(section)
        korean_form.sections.append(korean_section)

    return korean_form


def _translate_form_name(name: str) -> str:
    """Translate form name to Korean."""
    translations = {
        "R³ Diary - Personal Assessment Survey": "R³ 다이어리 - 개인 평가 설문",
        "Quick Profile Survey": "빠른 프로필 설문",
        "Student Survey": "학생 설문",
        "Office Worker Survey": "직장인 설문",
    }
    return translations.get(name, name)


def _translate_form_description(description: str) -> str:
    """Translate form description to Korean."""
    translations = {
        "Help us create your personalized diary experience": "개인화된 다이어리 경험을 만들어드리겠습니다",
        "Get started in 2 minutes": "2분 만에 시작하기",
        "Personalized diary for students": "학생을 위한 개인화된 다이어리",
        "Personalized diary for professionals": "전문가를 위한 개인화된 다이어리",
    }
    return translations.get(description, description)


def _translate_section(section: FormSection) -> FormSection:
    """Translate section to Korean."""
    section_id = section.id

    # Get Korean section info
    section_info = KOREAN_SETTINGS["sections"].get(section_id, {})
    korean_title = section_info.get("title", section.title)
    korean_description = section_info.get("description", section.description)

    # Create new section with Korean labels
    korean_section = FormSection(
        id=section.id,
        title=korean_title,
        description=korean_description,
        fields=[_translate_field(field) for field in section.fields],
        order=section.order,
    )

    return korean_section


def _translate_field(field: FormField) -> FormField:
    """Translate field to Korean."""
    field_id = field.id

    # Get Korean label
    korean_label = KOREAN_SETTINGS["fields"].get(field_id, field.label)

    # Get Korean label for personality questions
    if field_id.startswith("p_"):
        korean_label = KOREAN_SETTINGS["personality_questions"].get(field_id, field.label)

    # Get Korean options
    korean_options = _translate_options(field_id, field.options)

    # Get Korean placeholder
    korean_placeholder = None
    if field.placeholder:
        korean_placeholder = KOREAN_SETTINGS["placeholders"].get(field_id, field.placeholder)

    # Get Korean description
    korean_description = None
    if field.description:
        korean_description = KOREAN_SETTINGS["descriptions"].get(field_id, field.description)

    # Create new field with Korean labels
    korean_field = FormField(
        id=field.id,
        label=korean_label,
        field_type=field.field_type,
        required=field.required,
        options=korean_options,
        description=korean_description,
        placeholder=korean_placeholder,
        default_value=field.default_value,
        validation_rules=field.validation_rules,
        conditional_logic=field.conditional_logic,
        likert_config=field.likert_config,
        matrix_config=field.matrix_config,
    )

    return korean_field


def _translate_options(field_id: str, options: list[str] | None) -> list[str] | None:
    """Translate field options to Korean."""
    if not options:
        return None

    # Map field IDs to Korean option sets
    option_mappings = {
        "gender": KOREAN_SETTINGS["gender_options"],
        "primary_role": KOREAN_SETTINGS["role_options"],
        "topics": KOREAN_SETTINGS["interests"],
        "tone_preference": KOREAN_SETTINGS["tone_preferences"],
        "diary_preference": KOREAN_SETTINGS["diary_format_options"],
        "paper_size": KOREAN_SETTINGS["paper_sizes"],
        "delivery_frequency": KOREAN_SETTINGS["delivery_frequencies"],
        "email_frequency": KOREAN_SETTINGS["email_frequencies"],
    }

    return option_mappings.get(field_id, options)


def get_korean_form_by_template(template_name: str) -> FormConfiguration:
    """
    Get Korean-localized survey template.

    Args:
        template_name: One of "default", "quick_profile", "student", "office_worker"

    Returns:
        Korean-localized FormConfiguration
    """
    from .default_survey import get_survey_by_template

    # Get English template
    english_form = get_survey_by_template(template_name)

    # Apply Korean localization
    return apply_korean_localization(english_form)
