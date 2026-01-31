"""Default survey configuration for R³ Diary customer onboarding."""

from __future__ import annotations

from typing import Dict, Any

from ...skills.form_builder import FormBuilder, FieldType
from ...skills.form_builder.models import FormConfiguration, LikertConfig
from .activity_templates import add_activity_sections


def create_default_survey() -> FormConfiguration:
    """
    Generate default survey for customer onboarding.

    Survey Structure:
    1. Basic Information (name, email, birth date, gender)
    2. Role Selection (conditional)
    3. Personality Assessment (8 Likert questions)
    4. Interests & Preferences
    5. Diary Format Preference
    6. Paper Delivery Details (conditional)
    7. Communication Preferences

    Returns:
        FormConfiguration ready for deployment
    """
    likert = LikertConfig(
        scale_min=1,
        scale_max=5,
        min_label="Strongly Disagree",
        max_label="Strongly Agree"
    )

    builder = (
        FormBuilder(
            "R³ Diary - Personal Assessment Survey",
            "Help us create your personalized diary experience"
        )
        .set_metadata("version", "1.0")
        .set_metadata("purpose", "customer_onboarding")
        .set_metadata("estimated_time_minutes", 5)
    )

    # =========================================================================
    # Section 1: Basic Information
    # =========================================================================
    builder.add_section(
        "basic_info",
        "Basic Information",
        "Tell us about yourself"
    )

    builder.add_field(
        "basic_info", "name", "Full Name",
        FieldType.TEXT,
        required=True,
        placeholder="Enter your full name"
    )

    builder.add_field(
        "basic_info", "email", "Email Address",
        FieldType.EMAIL,
        required=True,
        placeholder="you@example.com",
        description="We'll use this to send your personalized diary"
    )

    builder.add_field(
        "basic_info", "birth_date", "Birth Date",
        FieldType.DATE,
        required=True,
        description="Required for personalized rhythm analysis"
    )

    builder.add_field(
        "basic_info", "gender", "Gender",
        FieldType.SINGLE_CHOICE,
        required=False,
        options=["Male", "Female", "Other", "Prefer not to say"]
    )

    # =========================================================================
    # Section 2: Role Selection
    # =========================================================================
    builder.add_section(
        "role",
        "Your Role",
        "This helps us personalize content for your situation"
    )

    builder.add_field(
        "role", "primary_role", "What is your primary role?",
        FieldType.SINGLE_CHOICE,
        required=True,
        options=[
            "Student",
            "Office Worker",
            "Freelancer / Self-employed",
            "Parent",
            "Other"
        ]
    )

    # =========================================================================
    # Section 2.5: Activity Preferences (conditional based on role)
    # =========================================================================
    add_activity_sections(builder, include_conditional=True)

    # =========================================================================
    # Section 3: Personality Assessment
    # =========================================================================
    builder.add_section(
        "personality",
        "Personality Assessment",
        "Rate how much each statement describes you (1 = Strongly Disagree, 5 = Strongly Agree)"
    )

    personality_questions = [
        ("p_extroversion", "I enjoy meeting new people and social activities"),
        ("p_structured", "I prefer structured planning to spontaneous action"),
        ("p_openness", "I am open to trying new ideas and experiences"),
        ("p_empathy", "I care deeply about others' feelings"),
        ("p_calm", "I stay calm and composed even in stressful situations"),
        ("p_focus", "I focus deeply on tasks until completion"),
        ("p_creative", "I enjoy creative and artistic pursuits"),
        ("p_logical", "I make decisions based on logic rather than emotions"),
    ]

    for field_id, label in personality_questions:
        builder.add_field(
            "personality", field_id, label,
            FieldType.LIKERT_SCALE,
            required=True,
            likert_config=likert
        )

    # =========================================================================
    # Section 4: Interests & Preferences
    # =========================================================================
    builder.add_section(
        "interests",
        "Interests & Preferences",
        "Help us understand what matters most to you"
    )

    builder.add_field(
        "interests", "topics", "Which topics interest you most? (Select up to 5)",
        FieldType.MULTIPLE_CHOICE,
        required=True,
        options=[
            "Career / Work",
            "Personal Growth",
            "Health / Fitness",
            "Relationships",
            "Finance",
            "Hobbies / Creative",
            "Spirituality",
            "Education",
            "Travel",
            "Other"
        ]
    )

    builder.add_field(
        "interests", "tone_preference", "Preferred communication tone",
        FieldType.SINGLE_CHOICE,
        required=True,
        options=[
            "Warm and supportive",
            "Direct and practical",
            "Motivational and energizing",
            "Calm and reflective"
        ]
    )

    # =========================================================================
    # Section 5: Diary Format Preference
    # =========================================================================
    builder.add_section(
        "format",
        "Diary Format",
        "Choose how you'd like to use your diary"
    )

    builder.add_field(
        "format", "diary_preference", "How would you prefer to use your diary?",
        FieldType.SINGLE_CHOICE,
        required=True,
        options=[
            "App only (web/mobile)",
            "Hybrid (app + monthly printed version)",
            "Paper diary only (printed monthly delivery)"
        ],
        description="Paper versions come with personalized daily guidance printed inside"
    )

    # =========================================================================
    # Section 6: Paper Delivery Details (CONDITIONAL)
    # =========================================================================
    builder.add_section(
        "paper_details",
        "Paper Delivery Details",
        "Tell us your paper diary preferences"
    )

    builder.add_field(
        "paper_details", "paper_size", "Preferred paper size",
        FieldType.SINGLE_CHOICE,
        required=False,
        options=["A5 (Compact)", "A4 (Standard)", "Custom"]
    )

    builder.add_field(
        "paper_details", "delivery_frequency", "How often would you like printed deliveries?",
        FieldType.SINGLE_CHOICE,
        required=False,
        options=["Monthly", "Quarterly", "Annually"]
    )

    builder.add_field(
        "paper_details", "delivery_address", "Delivery Address",
        FieldType.LONG_TEXT,
        required=False,
        placeholder="Street address, city, postal code, country"
    )

    # Apply conditional logic to each field in paper_details section
    # Note: ConditionalLogic model expects if_field and equals parameters
    # This shows fields only if diary_preference != "App only (web/mobile)"
    # We'll need to handle "not_equals" logic in the renderer
    conditional_logic = {
        "if_field": "diary_preference",
        "equals": "Hybrid (app + monthly printed version)"  # or "Paper diary only"
    }

    # Note: This is a simplified conditional. Full "not_equals" support
    # would require extended ConditionalLogic model.
    # For now, fields will show for hybrid/paper-only selections
    builder.add_conditional_logic("paper_size", conditional_logic)
    builder.add_conditional_logic("delivery_frequency", conditional_logic)
    builder.add_conditional_logic("delivery_address", conditional_logic)

    # =========================================================================
    # Section 7: Communication Preferences
    # =========================================================================
    builder.add_section(
        "communication",
        "Communication Preferences",
        "How would you like to stay in touch?"
    )

    builder.add_field(
        "communication", "email_frequency", "How often would you like email updates?",
        FieldType.SINGLE_CHOICE,
        required=True,
        options=["Daily insights", "Weekly summary", "Monthly newsletter", "None"]
    )

    builder.add_field(
        "communication", "privacy_consent", "I agree to the Privacy Policy",
        FieldType.SINGLE_CHOICE,
        required=True,
        options=["Yes", "No"],
        description="Required to use the service"
    )

    builder.add_field(
        "communication", "marketing_consent", "I'd like to receive marketing emails",
        FieldType.SINGLE_CHOICE,
        required=False,
        options=["Yes", "No"],
        description="You can unsubscribe anytime"
    )

    builder.add_field(
        "communication", "research_consent", "I'm willing to participate in user research",
        FieldType.SINGLE_CHOICE,
        required=False,
        options=["Yes", "No"],
        description="Help us improve the product"
    )

    # Build and return
    return builder.build()


def create_quick_profile_survey() -> FormConfiguration:
    """Create a shorter version for quick onboarding."""
    likert = LikertConfig(scale_min=1, scale_max=5)

    return (
        FormBuilder(
            "Quick Profile Survey",
            "Get started in 2 minutes"
        )
        .add_section("essentials", "Essential Information")
        .add_field("essentials", "name", "Full Name", FieldType.TEXT)
        .add_field("essentials", "email", "Email", FieldType.EMAIL)
        .add_field("essentials", "birth_date", "Birth Date", FieldType.DATE)
        .add_field("essentials", "role", "Your Role", FieldType.SINGLE_CHOICE,
                   options=["Student", "Office Worker", "Freelancer", "Other"])
        .add_section("personality_brief", "Quick Personality Check")
        .add_field("personality_brief", "p1", "I am outgoing and social",
                   FieldType.LIKERT_SCALE, likert_config=likert)
        .add_field("personality_brief", "p2", "I prefer planning over spontaneity",
                   FieldType.LIKERT_SCALE, likert_config=likert)
        .add_field("personality_brief", "p3", "I am creative and open-minded",
                   FieldType.LIKERT_SCALE, likert_config=likert)
        .add_section("format_quick", "Format Preference")
        .add_field("format_quick", "format", "Preferred Format", FieldType.SINGLE_CHOICE,
                   options=["App only", "Hybrid (app + print)", "Print only"])
        .build()
    )


def create_student_survey() -> FormConfiguration:
    """Create student-focused survey with relevant questions."""
    likert = LikertConfig(scale_min=1, scale_max=5)

    return (
        FormBuilder(
            "Student Survey",
            "Personalized diary for students"
        )
        .add_section("student_info", "About You")
        .add_field("student_info", "name", "Full Name", FieldType.TEXT)
        .add_field("student_info", "email", "Email", FieldType.EMAIL)
        .add_field("student_info", "birth_date", "Birth Date", FieldType.DATE)
        .add_field("student_info", "education_level", "Education Level",
                   FieldType.SINGLE_CHOICE,
                   options=["High School", "Undergraduate", "Graduate", "Other"])
        .add_section("study_style", "Study Preferences")
        .add_field("study_style", "learning_style", "I learn best through",
                   FieldType.MULTIPLE_CHOICE,
                   options=["Reading", "Visuals", "Hands-on practice", "Discussion", "Teaching others"])
        .add_field("study_style", "peak_focus", "Best study time",
                   FieldType.SINGLE_CHOICE,
                   options=["Early morning", "Mid-morning", "Afternoon", "Evening", "Late night"])
        .add_section("goals", "Academic Goals")
        .add_field("goals", "focus_areas", "Focus areas this semester",
                   FieldType.MULTIPLE_CHOICE,
                   options=["Exam preparation", "Project completion", "Time management",
                            "Stress management", "Social connections", "Career planning"])
        .build()
    )


def create_office_worker_survey() -> FormConfiguration:
    """Create office worker-focused survey."""
    likert = LikertConfig(scale_min=1, scale_max=5)

    return (
        FormBuilder(
            "Office Worker Survey",
            "Personalized diary for professionals"
        )
        .add_section("professional_info", "Professional Profile")
        .add_field("professional_info", "name", "Full Name", FieldType.TEXT)
        .add_field("professional_info", "email", "Work Email", FieldType.EMAIL)
        .add_field("professional_info", "birth_date", "Birth Date", FieldType.DATE)
        .add_field("professional_info", "industry", "Industry",
                   FieldType.SINGLE_CHOICE,
                   options=["Technology", "Finance", "Healthcare", "Education",
                            "Marketing", "Manufacturing", "Other"])
        .add_section("work_style", "Work Style")
        .add_field("work_style", "work_environment", "Work Environment",
                   FieldType.SINGLE_CHOICE,
                   options=["Office", "Remote", "Hybrid", "Field work"])
        .add_field("work_style", "peak_productivity", "Most productive time",
                   FieldType.SINGLE_CHOICE,
                   options=["Early morning", "Mid-morning", "Afternoon", "Evening"])
        .add_section("priorities", "Professional Priorities")
        .add_field("priorities", "focus_areas", "Key focus areas",
                   FieldType.MULTIPLE_CHOICE,
                   options=["Career advancement", "Work-life balance", "Skill development",
                            "Team leadership", "Project completion", "Stress management",
                            "Relationship building"])
        .build()
    )


def get_survey_by_template(template_name: str) -> FormConfiguration:
    """
    Get pre-built survey template.

    Args:
        template_name: One of "default", "quick_profile", "student", "office_worker"

    Returns:
        FormConfiguration ready for deployment

    Raises:
        ValueError: If template_name is not recognized
    """
    templates = {
        "default": create_default_survey,
        "quick_profile": create_quick_profile_survey,
        "student": create_student_survey,
        "office_worker": create_office_worker_survey,
    }

    if template_name not in templates:
        raise ValueError(
            f"Unknown template: {template_name}. "
            f"Available templates: {list(templates.keys())}"
        )

    return templates[template_name]()
