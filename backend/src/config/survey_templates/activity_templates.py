"""Activity sub-categorization templates for role-specific surveys."""

from __future__ import annotations

from typing import Dict, List
from ...skills.form_builder import FormBuilder, FieldType


# Role -> Activity category mapping with Korean options
ROLE_ACTIVITIES = {
    "student": {
        "study_type": ["시험 준비", "프로젝트", "독서", "자격증", "어학"],
        "exercise_type": ["러닝", "헬스", "요가", "수영", "팀스포츠"],
        "social_type": ["스터디그룹", "동아리", "멘토링", "친구모임"],
    },
    "office_worker": {
        "work_type": ["보고서/기획", "회의/소통", "분석/리서치", "프레젠테이션", "프로젝트관리"],
        "exercise_type": ["러닝", "헬스", "요가", "등산", "골프"],
        "social_type": ["팀빌딩", "네트워킹", "멘토링", "회식"],
    },
    "freelancer": {
        "work_type": ["창작/디자인", "클라이언트미팅", "기획/제안", "마감작업", "자기계발"],
        "exercise_type": ["러닝", "헬스", "요가", "수영", "자전거"],
        "social_type": ["콜라보", "커뮤니티", "워크샵", "네트워킹"],
    },
    "parent": {
        "activity_type": ["육아", "가사", "자기계발", "운동", "취미"],
        "exercise_type": ["걷기", "요가", "필라테스", "수영", "홈트레이닝"],
        "social_type": ["부모모임", "가족시간", "친구만남", "봉사활동"],
    },
}


# Role display names for conditional logic matching
ROLE_MAPPING = {
    "Student": "student",
    "학생": "student",
    "Office Worker": "office_worker",
    "직장인": "office_worker",
    "Freelancer / Self-employed": "freelancer",
    "프리랜서 / 자영업": "freelancer",
    "Parent": "parent",
    "부모": "parent",
}


def add_activity_sections(builder: FormBuilder, include_conditional: bool = True) -> FormBuilder:
    """
    Add activity sub-categorization sections to a survey.

    Sections are added with conditional logic based on role selection.
    Each role gets 2-3 activity category questions with multiple choice options.

    Args:
        builder: FormBuilder instance to add sections to
        include_conditional: Whether to add conditional logic (default True)

    Returns:
        Modified FormBuilder instance
    """

    # =========================================================================
    # Activity Preferences Section
    # =========================================================================
    builder.add_section(
        "activity_preferences",
        "Activity Preferences",
        "Tell us about your typical activities"
    )

    # Student-specific activities
    _add_student_activities(builder, include_conditional)

    # Office Worker-specific activities
    _add_office_worker_activities(builder, include_conditional)

    # Freelancer-specific activities
    _add_freelancer_activities(builder, include_conditional)

    # Parent-specific activities
    _add_parent_activities(builder, include_conditional)

    return builder


def _add_student_activities(builder: FormBuilder, include_conditional: bool):
    """Add student-specific activity fields."""
    activities = ROLE_ACTIVITIES["student"]

    # Study type
    builder.add_field(
        "activity_preferences",
        "study_type",
        "학습 활동 유형 (복수 선택 가능)",
        FieldType.MULTIPLE_CHOICE,
        required=False,
        options=activities["study_type"],
        description="주로 집중하는 학습 활동을 선택해주세요"
    )

    # Exercise type
    builder.add_field(
        "activity_preferences",
        "student_exercise_type",
        "운동 활동 유형 (복수 선택 가능)",
        FieldType.MULTIPLE_CHOICE,
        required=False,
        options=activities["exercise_type"],
        description="선호하는 운동 방식을 선택해주세요"
    )

    # Social type
    builder.add_field(
        "activity_preferences",
        "student_social_type",
        "사회 활동 유형 (복수 선택 가능)",
        FieldType.MULTIPLE_CHOICE,
        required=False,
        options=activities["social_type"],
        description="참여하는 사회 활동을 선택해주세요"
    )

    if include_conditional:
        # Show these fields only for students
        conditional_logic = {
            "if_field": "primary_role",
            "equals": "Student"
        }
        builder.add_conditional_logic("study_type", conditional_logic)
        builder.add_conditional_logic("student_exercise_type", conditional_logic)
        builder.add_conditional_logic("student_social_type", conditional_logic)

        # Also add Korean version conditional
        conditional_logic_ko = {
            "if_field": "primary_role",
            "equals": "학생"
        }
        builder.add_conditional_logic("study_type", conditional_logic_ko)
        builder.add_conditional_logic("student_exercise_type", conditional_logic_ko)
        builder.add_conditional_logic("student_social_type", conditional_logic_ko)


def _add_office_worker_activities(builder: FormBuilder, include_conditional: bool):
    """Add office worker-specific activity fields."""
    activities = ROLE_ACTIVITIES["office_worker"]

    # Work type
    builder.add_field(
        "activity_preferences",
        "work_type",
        "업무 활동 유형 (복수 선택 가능)",
        FieldType.MULTIPLE_CHOICE,
        required=False,
        options=activities["work_type"],
        description="주로 하는 업무 유형을 선택해주세요"
    )

    # Exercise type
    builder.add_field(
        "activity_preferences",
        "worker_exercise_type",
        "운동 활동 유형 (복수 선택 가능)",
        FieldType.MULTIPLE_CHOICE,
        required=False,
        options=activities["exercise_type"],
        description="선호하는 운동 방식을 선택해주세요"
    )

    # Social type
    builder.add_field(
        "activity_preferences",
        "worker_social_type",
        "사회 활동 유형 (복수 선택 가능)",
        FieldType.MULTIPLE_CHOICE,
        required=False,
        options=activities["social_type"],
        description="참여하는 사회 활동을 선택해주세요"
    )

    if include_conditional:
        # Show these fields only for office workers
        conditional_logic = {
            "if_field": "primary_role",
            "equals": "Office Worker"
        }
        builder.add_conditional_logic("work_type", conditional_logic)
        builder.add_conditional_logic("worker_exercise_type", conditional_logic)
        builder.add_conditional_logic("worker_social_type", conditional_logic)

        # Also add Korean version conditional
        conditional_logic_ko = {
            "if_field": "primary_role",
            "equals": "직장인"
        }
        builder.add_conditional_logic("work_type", conditional_logic_ko)
        builder.add_conditional_logic("worker_exercise_type", conditional_logic_ko)
        builder.add_conditional_logic("worker_social_type", conditional_logic_ko)


def _add_freelancer_activities(builder: FormBuilder, include_conditional: bool):
    """Add freelancer-specific activity fields."""
    activities = ROLE_ACTIVITIES["freelancer"]

    # Work type
    builder.add_field(
        "activity_preferences",
        "freelance_work_type",
        "작업 활동 유형 (복수 선택 가능)",
        FieldType.MULTIPLE_CHOICE,
        required=False,
        options=activities["work_type"],
        description="주로 하는 작업 유형을 선택해주세요"
    )

    # Exercise type
    builder.add_field(
        "activity_preferences",
        "freelancer_exercise_type",
        "운동 활동 유형 (복수 선택 가능)",
        FieldType.MULTIPLE_CHOICE,
        required=False,
        options=activities["exercise_type"],
        description="선호하는 운동 방식을 선택해주세요"
    )

    # Social type
    builder.add_field(
        "activity_preferences",
        "freelancer_social_type",
        "사회 활동 유형 (복수 선택 가능)",
        FieldType.MULTIPLE_CHOICE,
        required=False,
        options=activities["social_type"],
        description="참여하는 사회 활동을 선택해주세요"
    )

    if include_conditional:
        # Show these fields only for freelancers
        conditional_logic = {
            "if_field": "primary_role",
            "equals": "Freelancer / Self-employed"
        }
        builder.add_conditional_logic("freelance_work_type", conditional_logic)
        builder.add_conditional_logic("freelancer_exercise_type", conditional_logic)
        builder.add_conditional_logic("freelancer_social_type", conditional_logic)

        # Also add Korean version conditional
        conditional_logic_ko = {
            "if_field": "primary_role",
            "equals": "프리랜서 / 자영업"
        }
        builder.add_conditional_logic("freelance_work_type", conditional_logic_ko)
        builder.add_conditional_logic("freelancer_exercise_type", conditional_logic_ko)
        builder.add_conditional_logic("freelancer_social_type", conditional_logic_ko)


def _add_parent_activities(builder: FormBuilder, include_conditional: bool):
    """Add parent-specific activity fields."""
    activities = ROLE_ACTIVITIES["parent"]

    # Activity type
    builder.add_field(
        "activity_preferences",
        "parent_activity_type",
        "일상 활동 유형 (복수 선택 가능)",
        FieldType.MULTIPLE_CHOICE,
        required=False,
        options=activities["activity_type"],
        description="주로 하는 일상 활동을 선택해주세요"
    )

    # Exercise type
    builder.add_field(
        "activity_preferences",
        "parent_exercise_type",
        "운동 활동 유형 (복수 선택 가능)",
        FieldType.MULTIPLE_CHOICE,
        required=False,
        options=activities["exercise_type"],
        description="선호하는 운동 방식을 선택해주세요"
    )

    # Social type
    builder.add_field(
        "activity_preferences",
        "parent_social_type",
        "사회 활동 유형 (복수 선택 가능)",
        FieldType.MULTIPLE_CHOICE,
        required=False,
        options=activities["social_type"],
        description="참여하는 사회 활동을 선택해주세요"
    )

    if include_conditional:
        # Show these fields only for parents
        conditional_logic = {
            "if_field": "primary_role",
            "equals": "Parent"
        }
        builder.add_conditional_logic("parent_activity_type", conditional_logic)
        builder.add_conditional_logic("parent_exercise_type", conditional_logic)
        builder.add_conditional_logic("parent_social_type", conditional_logic)

        # Also add Korean version conditional
        conditional_logic_ko = {
            "if_field": "primary_role",
            "equals": "부모"
        }
        builder.add_conditional_logic("parent_activity_type", conditional_logic_ko)
        builder.add_conditional_logic("parent_exercise_type", conditional_logic_ko)
        builder.add_conditional_logic("parent_social_type", conditional_logic_ko)


def get_activity_categories_for_role(role: str) -> List[str]:
    """
    Get list of activity category field names for a given role.

    Args:
        role: Role name (e.g., "student", "office_worker")

    Returns:
        List of field names for that role's activity categories
    """
    role_lower = role.lower()

    category_map = {
        "student": ["study_type", "student_exercise_type", "student_social_type"],
        "office_worker": ["work_type", "worker_exercise_type", "worker_social_type"],
        "freelancer": ["freelance_work_type", "freelancer_exercise_type", "freelancer_social_type"],
        "parent": ["parent_activity_type", "parent_exercise_type", "parent_social_type"],
    }

    return category_map.get(role_lower, [])
