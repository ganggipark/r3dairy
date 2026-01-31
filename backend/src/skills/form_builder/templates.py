"""Pre-built form templates for common diary project use cases."""

from __future__ import annotations

from .builder import FormBuilder
from .models import FieldType, LikertConfig, MatrixConfig, ValidationRule


class FormTemplates:
    """Factory methods returning pre-configured FormBuilder instances."""

    @staticmethod
    def basic_profile_form() -> FormBuilder:
        """Basic user profile collection."""
        return (
            FormBuilder("Basic Profile", "Collect basic user information")
            .add_section("profile", "Profile Information", "Tell us about yourself")
            .add_field("profile", "name", "Full Name", FieldType.TEXT,
                       placeholder="Enter your full name")
            .add_field("profile", "email", "Email Address", FieldType.EMAIL,
                       placeholder="you@example.com")
            .add_field("profile", "birth_date", "Birth Date", FieldType.DATE)
            .add_field("profile", "gender", "Gender", FieldType.SINGLE_CHOICE,
                       options=["Male", "Female", "Non-binary", "Prefer not to say"])
        )

    @staticmethod
    def personality_assessment_form() -> FormBuilder:
        """Personality assessment with Likert scale questions."""
        likert = LikertConfig(scale_min=1, scale_max=5,
                              min_label="Strongly Disagree", max_label="Strongly Agree")
        questions = [
            ("extroversion_1", "I enjoy meeting new people"),
            ("extroversion_2", "I feel energized in social situations"),
            ("extroversion_3", "I prefer group activities over solo ones"),
            ("extroversion_4", "I like being the center of attention"),
            ("introversion_1", "I need alone time to recharge"),
            ("openness_1", "I am open to new experiences"),
            ("openness_2", "I enjoy abstract thinking"),
            ("openness_3", "I appreciate art and creativity"),
            ("openness_4", "I like trying new foods and activities"),
            ("conscient_1", "I keep my workspace organized"),
            ("conscient_2", "I plan my day in advance"),
            ("conscient_3", "I follow through on commitments"),
            ("agreeable_1", "I care about others' feelings"),
            ("agreeable_2", "I avoid conflicts when possible"),
            ("agreeable_3", "I enjoy helping others"),
            ("neurotic_1", "I often feel anxious"),
            ("neurotic_2", "I worry about the future"),
            ("neurotic_3", "Small setbacks upset me"),
            ("resilience_1", "I recover quickly from stress"),
            ("resilience_2", "I stay calm under pressure"),
        ]

        builder = (
            FormBuilder("Personality Assessment", "Understand your personality traits")
            .add_section("personality", "Personality Questions",
                         "Rate how much each statement describes you")
        )
        for fid, label in questions:
            builder.add_field("personality", fid, label, FieldType.LIKERT_SCALE,
                              likert_config=likert)
        return builder

    @staticmethod
    def interests_form() -> FormBuilder:
        """Interests and lifestyle preferences."""
        return (
            FormBuilder("Interests Survey", "Tell us about your interests")
            .add_section("hobbies", "Hobbies & Activities")
            .add_field("hobbies", "hobbies", "Select your hobbies",
                       FieldType.MULTIPLE_CHOICE,
                       options=["Reading", "Sports", "Music", "Art", "Cooking",
                                "Travel", "Gaming", "Gardening", "Photography",
                                "Writing"])
            .add_field("hobbies", "hobby_frequency", "How often do you engage in hobbies?",
                       FieldType.SINGLE_CHOICE,
                       options=["Daily", "Several times a week", "Weekly",
                                "Monthly", "Rarely"])
            .add_section("work_style", "Work Style")
            .add_field("work_style", "work_preference", "Preferred work style",
                       FieldType.SINGLE_CHOICE,
                       options=["Structured routine", "Flexible schedule",
                                "Creative freedom", "Team collaboration"])
            .add_field("work_style", "peak_hours", "Most productive time of day",
                       FieldType.SINGLE_CHOICE,
                       options=["Early morning", "Mid-morning", "Afternoon",
                                "Evening", "Late night"])
        )

    @staticmethod
    def preferences_form() -> FormBuilder:
        """Diary content and style preferences."""
        return (
            FormBuilder("Diary Preferences", "Customize your diary experience")
            .add_section("tone", "Tone & Style")
            .add_field("tone", "preferred_tone", "Preferred communication tone",
                       FieldType.SINGLE_CHOICE,
                       options=["Warm and supportive", "Direct and practical",
                                "Motivational", "Calm and reflective"])
            .add_field("tone", "content_depth", "How detailed should guidance be?",
                       FieldType.SINGLE_CHOICE,
                       options=["Brief highlights", "Moderate detail",
                                "In-depth analysis"])
            .add_section("content", "Content Preferences")
            .add_field("content", "focus_areas", "Areas of focus",
                       FieldType.MULTIPLE_CHOICE,
                       options=["Career", "Health", "Relationships", "Creativity",
                                "Finance", "Personal growth", "Emotional wellbeing"])
            .add_field("content", "additional_notes", "Any other preferences?",
                       FieldType.LONG_TEXT, required=False,
                       placeholder="Share anything else...")
        )

    @staticmethod
    def role_selection_form() -> FormBuilder:
        """Role selection form for the R3 diary system."""
        return (
            FormBuilder("Role Selection", "Select your primary role")
            .add_section("role", "Your Role")
            .add_field("role", "primary_role", "What best describes you?",
                       FieldType.SINGLE_CHOICE,
                       options=["Student", "Office Worker", "Freelancer / Self-employed"])
            .add_field("role", "role_detail", "More about your role",
                       FieldType.TEXT, required=False,
                       placeholder="e.g., university student, software engineer...")
        )

    @staticmethod
    def comprehensive_survey_form() -> FormBuilder:
        """Combined form with all major sections."""
        likert = LikertConfig(scale_min=1, scale_max=5)
        return (
            FormBuilder("Comprehensive Survey",
                        "Complete onboarding survey for the R3 diary")
            # Profile
            .add_section("profile", "Basic Information", "Tell us about yourself")
            .add_field("profile", "name", "Full Name", FieldType.TEXT)
            .add_field("profile", "email", "Email", FieldType.EMAIL)
            .add_field("profile", "birth_date", "Birth Date", FieldType.DATE)
            .add_field("profile", "gender", "Gender", FieldType.SINGLE_CHOICE,
                       options=["Male", "Female", "Non-binary", "Prefer not to say"])
            # Role
            .add_section("role", "Your Role")
            .add_field("role", "primary_role", "What best describes you?",
                       FieldType.SINGLE_CHOICE,
                       options=["Student", "Office Worker", "Freelancer / Self-employed"])
            # Personality (brief)
            .add_section("personality", "Quick Personality Check",
                         "Rate how much each statement describes you")
            .add_field("personality", "p_social", "I enjoy meeting new people",
                       FieldType.LIKERT_SCALE, likert_config=likert)
            .add_field("personality", "p_organized", "I keep things organized",
                       FieldType.LIKERT_SCALE, likert_config=likert)
            .add_field("personality", "p_creative", "I value creativity",
                       FieldType.LIKERT_SCALE, likert_config=likert)
            .add_field("personality", "p_calm", "I stay calm under pressure",
                       FieldType.LIKERT_SCALE, likert_config=likert)
            # Preferences
            .add_section("preferences", "Diary Preferences")
            .add_field("preferences", "tone", "Preferred tone",
                       FieldType.SINGLE_CHOICE,
                       options=["Warm", "Direct", "Motivational", "Reflective"])
            .add_field("preferences", "focus_areas", "Focus areas",
                       FieldType.MULTIPLE_CHOICE,
                       options=["Career", "Health", "Relationships", "Creativity",
                                "Finance", "Growth", "Emotional wellbeing"])
            .add_field("preferences", "extra_notes", "Anything else?",
                       FieldType.LONG_TEXT, required=False)
        )
