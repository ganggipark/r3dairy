"""Tests for survey template deployment system."""

import pytest
import json
from datetime import datetime

from src.config.survey_templates import (
    create_default_survey,
    get_survey_by_template,
    apply_korean_localization,
    SurveyDeploymentConfig,
    KOREAN_SETTINGS,
)
from src.skills.form_builder.models import FormConfiguration, FieldType


class TestSurveyCreation:
    """Test survey creation from templates."""

    def test_create_default_survey(self):
        """Test creating default survey."""
        form = create_default_survey()

        assert form is not None
        assert isinstance(form, FormConfiguration)
        assert form.name == "R³ Diary - Personal Assessment Survey"
        assert len(form.sections) == 8

        # Check section IDs
        section_ids = [s.id for s in form.sections]
        assert "basic_info" in section_ids
        assert "role" in section_ids
        assert "activity_preferences" in section_ids
        assert "personality" in section_ids
        assert "interests" in section_ids
        assert "format" in section_ids
        assert "paper_details" in section_ids
        assert "communication" in section_ids

    def test_get_survey_by_template_default(self):
        """Test getting default survey template."""
        form = get_survey_by_template("default")
        assert form.name == "R³ Diary - Personal Assessment Survey"

    def test_get_survey_by_template_quick_profile(self):
        """Test getting quick profile template."""
        form = get_survey_by_template("quick_profile")
        assert form.name == "Quick Profile Survey"
        assert len(form.sections) < 7  # Should be shorter

    def test_get_survey_by_template_student(self):
        """Test getting student template."""
        form = get_survey_by_template("student")
        assert form.name == "Student Survey"

    def test_get_survey_by_template_office_worker(self):
        """Test getting office worker template."""
        form = get_survey_by_template("office_worker")
        assert form.name == "Office Worker Survey"

    def test_get_survey_by_template_invalid(self):
        """Test getting invalid template raises error."""
        with pytest.raises(ValueError) as exc_info:
            get_survey_by_template("nonexistent")
        assert "Unknown template" in str(exc_info.value)


class TestSurveyStructure:
    """Test survey structure and fields."""

    def test_basic_info_section(self):
        """Test basic information section."""
        form = create_default_survey()
        basic_info = next(s for s in form.sections if s.id == "basic_info")

        assert basic_info.title == "Basic Information"
        assert len(basic_info.fields) == 4

        # Check required fields
        field_ids = [f.id for f in basic_info.fields]
        assert "name" in field_ids
        assert "email" in field_ids
        assert "birth_date" in field_ids
        assert "gender" in field_ids

    def test_personality_section_has_8_questions(self):
        """Test personality section has exactly 8 Likert questions."""
        form = create_default_survey()
        personality = next(s for s in form.sections if s.id == "personality")

        assert len(personality.fields) == 8

        # All should be Likert scale
        for field in personality.fields:
            assert field.field_type == FieldType.LIKERT_SCALE
            assert field.likert_config is not None
            assert field.likert_config.scale_min == 1
            assert field.likert_config.scale_max == 5

    def test_conditional_logic_on_paper_details(self):
        """Test that paper_details fields have conditional logic."""
        form = create_default_survey()
        paper_details = next(s for s in form.sections if s.id == "paper_details")

        # Check that fields have conditional logic
        for field in paper_details.fields:
            assert field.conditional_logic is not None
            assert field.conditional_logic.if_field == "diary_preference"
            # Note: Current implementation uses simple equality check
            # Full "not_equals" support would require extended ConditionalLogic model

    def test_interests_section_has_multiple_choice(self):
        """Test interests section has multiple choice field."""
        form = create_default_survey()
        interests = next(s for s in form.sections if s.id == "interests")

        topics_field = next(f for f in interests.fields if f.id == "topics")
        assert topics_field.field_type == FieldType.MULTIPLE_CHOICE
        assert len(topics_field.options) >= 10

    def test_communication_section_has_consent_fields(self):
        """Test communication section has consent fields."""
        form = create_default_survey()
        communication = next(s for s in form.sections if s.id == "communication")

        # Find consent fields (implemented as single_choice Yes/No)
        consent_fields = [f for f in communication.fields if "consent" in f.id]
        assert len(consent_fields) >= 3

        # Privacy consent should be required
        privacy_field = next(f for f in consent_fields if f.id == "privacy_consent")
        assert privacy_field.required is True
        assert privacy_field.options == ["Yes", "No"]


class TestKoreanLocalization:
    """Test Korean localization."""

    def test_apply_korean_localization(self):
        """Test applying Korean localization to form."""
        english_form = create_default_survey()
        korean_form = apply_korean_localization(english_form)

        assert korean_form.name == "R³ 다이어리 - 개인 평가 설문"
        assert korean_form.metadata.get("locale") == "ko-KR"

    def test_korean_section_titles(self):
        """Test Korean section titles."""
        english_form = create_default_survey()
        korean_form = apply_korean_localization(english_form)

        basic_info = next(s for s in korean_form.sections if s.id == "basic_info")
        assert basic_info.title == "기본 정보"

        personality = next(s for s in korean_form.sections if s.id == "personality")
        assert personality.title == "성격 평가"

    def test_korean_field_labels(self):
        """Test Korean field labels."""
        english_form = create_default_survey()
        korean_form = apply_korean_localization(english_form)

        basic_info = next(s for s in korean_form.sections if s.id == "basic_info")
        name_field = next(f for f in basic_info.fields if f.id == "name")
        assert name_field.label == "이름"

        email_field = next(f for f in basic_info.fields if f.id == "email")
        assert email_field.label == "이메일 주소"

    def test_korean_options(self):
        """Test Korean options for choice fields."""
        english_form = create_default_survey()
        korean_form = apply_korean_localization(english_form)

        basic_info = next(s for s in korean_form.sections if s.id == "basic_info")
        gender_field = next(f for f in basic_info.fields if f.id == "gender")
        assert "남성" in gender_field.options
        assert "여성" in gender_field.options

        role = next(s for s in korean_form.sections if s.id == "role")
        role_field = next(f for f in role.fields if f.id == "primary_role")
        assert "학생" in role_field.options
        assert "직장인" in role_field.options

    def test_korean_personality_questions(self):
        """Test Korean personality question labels."""
        english_form = create_default_survey()
        korean_form = apply_korean_localization(english_form)

        personality = next(s for s in korean_form.sections if s.id == "personality")

        extroversion_field = next(f for f in personality.fields if f.id == "p_extroversion")
        assert "새로운 사람을 만나고" in extroversion_field.label


class TestSurveyDeployment:
    """Test survey deployment configurations."""

    def test_get_n8n_deployment_config(self):
        """Test n8n deployment configuration."""
        form = create_default_survey()
        config = SurveyDeploymentConfig.get_n8n_deployment_config(form)

        assert "nodes" in config
        assert "connections" in config
        assert len(config["nodes"]) >= 5  # At least webhook, normalize, db, email, response

        # Check webhook node exists
        webhook_nodes = [n for n in config["nodes"] if n.get("type") == "n8n-nodes-base.webhook"]
        assert len(webhook_nodes) > 0

        # Check database node exists
        db_nodes = [n for n in config["nodes"] if n.get("type") == "n8n-nodes-base.supabase"]
        assert len(db_nodes) > 0

    def test_get_google_forms_config(self):
        """Test Google Forms deployment configuration."""
        form = create_default_survey()
        config = SurveyDeploymentConfig.get_google_forms_config(form)

        assert "info" in config
        assert "items" in config
        assert config["info"]["title"] == form.name

    def test_get_web_deployment_config(self):
        """Test web deployment configuration."""
        form = create_default_survey()
        config = SurveyDeploymentConfig.get_web_deployment_config(form)

        assert "form_id" in config
        assert "html" in config
        assert "react_component" in config
        assert "api" in config
        assert config["api"]["submit_endpoint"] == f"/api/surveys/{form.id}/submit"

    def test_deployment_instructions_n8n(self):
        """Test n8n deployment instructions."""
        form = create_default_survey()
        instructions = SurveyDeploymentConfig.get_deployment_instructions(form, "n8n")

        assert "n8n" in instructions
        assert "Import Workflow" in instructions
        assert "Supabase" in instructions
        assert form.id in instructions

    def test_deployment_instructions_web(self):
        """Test web deployment instructions."""
        form = create_default_survey()
        instructions = SurveyDeploymentConfig.get_deployment_instructions(form, "web")

        assert "React Component" in instructions
        assert "API Endpoint" in instructions
        assert form.id in instructions


class TestSurveyResponseNormalization:
    """Test survey response normalization."""

    def test_normalize_student_response(self):
        """Test normalizing student response."""
        from src.api.surveys import _normalize_response_data

        # Load example from examples.json
        with open("src/config/survey_templates/examples.json", encoding="utf-8") as f:
            examples = json.load(f)

        student_response = examples["example_student"]
        normalized = _normalize_response_data(student_response)

        assert "profile" in normalized
        assert normalized["profile"]["name"] == "김학생"
        assert normalized["profile"]["email"] == "student@example.com"
        assert normalized["profile"]["role"] == "student"

        assert "personality" in normalized
        assert normalized["personality"]["extroversion"] == 4
        assert normalized["personality"]["structured"] == 3

        assert "interests" in normalized
        assert "topics" in normalized["interests"]

        assert "format" in normalized
        assert normalized["format"]["diary_type"] == "hybrid"

        assert "communication" in normalized
        assert normalized["communication"]["consents"]["privacy"] is True

    def test_normalize_office_worker_response(self):
        """Test normalizing office worker response."""
        from src.api.surveys import _normalize_response_data

        with open("src/config/survey_templates/examples.json", encoding="utf-8") as f:
            examples = json.load(f)

        office_worker_response = examples["example_office_worker"]
        normalized = _normalize_response_data(office_worker_response)

        assert normalized["profile"]["role"] == "office_worker"
        assert normalized["format"]["diary_type"] == "app_only"

    def test_normalize_gender_values(self):
        """Test gender normalization."""
        from src.api.surveys import _normalize_gender

        assert _normalize_gender("Male") == "male"
        assert _normalize_gender("남성") == "male"
        assert _normalize_gender("Female") == "female"
        assert _normalize_gender("여성") == "female"
        assert _normalize_gender("Other") == "other"
        assert _normalize_gender("기타") == "other"

    def test_normalize_role_values(self):
        """Test role normalization."""
        from src.api.surveys import _normalize_role

        assert _normalize_role("Student") == "student"
        assert _normalize_role("학생") == "student"
        assert _normalize_role("Office Worker") == "office_worker"
        assert _normalize_role("직장인") == "office_worker"
        assert _normalize_role("Freelancer / Self-employed") == "freelancer"


class TestExamples:
    """Test example survey responses."""

    def test_examples_file_exists(self):
        """Test that examples.json exists and is valid."""
        with open("src/config/survey_templates/examples.json", encoding="utf-8") as f:
            examples = json.load(f)

        assert "example_student" in examples
        assert "example_office_worker" in examples
        assert "example_freelancer" in examples
        assert "example_parent" in examples
        assert "example_minimal" in examples
        assert "normalized_example_student" in examples
        assert "validation_test_cases" in examples

    def test_example_student_complete(self):
        """Test student example has all required fields."""
        with open("src/config/survey_templates/examples.json", encoding="utf-8") as f:
            examples = json.load(f)

        student = examples["example_student"]

        # Basic info
        assert "name" in student
        assert "email" in student
        assert "birth_date" in student
        assert "primary_role" in student

        # Personality scores (8 questions)
        assert "p_extroversion" in student
        assert "p_structured" in student
        assert "p_openness" in student
        assert "p_empathy" in student
        assert "p_calm" in student
        assert "p_focus" in student
        assert "p_creative" in student
        assert "p_logical" in student

        # Interests
        assert "topics" in student
        assert isinstance(student["topics"], list)

        # Format
        assert "diary_preference" in student

        # Communication
        assert "email_frequency" in student
        assert "privacy_consent" in student


class TestFormMetadata:
    """Test form metadata."""

    def test_default_survey_metadata(self):
        """Test default survey has correct metadata."""
        form = create_default_survey()

        assert form.metadata.get("version") == "1.0"
        assert form.metadata.get("purpose") == "customer_onboarding"
        assert form.metadata.get("estimated_time_minutes") == 5

    def test_korean_form_locale_metadata(self):
        """Test Korean form has locale metadata."""
        english_form = create_default_survey()
        korean_form = apply_korean_localization(english_form)

        assert korean_form.metadata.get("locale") == "ko-KR"


@pytest.mark.asyncio
class TestAPIEndpoints:
    """Test API endpoints (requires FastAPI test client)."""

    # Note: These tests require FastAPI TestClient
    # They are placeholders for future integration tests

    async def test_create_survey_endpoint(self):
        """Test creating survey via API."""
        # TODO: Implement with FastAPI TestClient
        pass

    async def test_get_survey_endpoint(self):
        """Test getting survey via API."""
        # TODO: Implement with FastAPI TestClient
        pass

    async def test_submit_survey_response_endpoint(self):
        """Test submitting survey response via API."""
        # TODO: Implement with FastAPI TestClient
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
