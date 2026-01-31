"""Tests for FormGenerator."""

import json

import pytest

from ..builder import FormBuilder
from ..generators import FormGenerator
from ..models import FieldType, LikertConfig
from ..templates import FormTemplates


@pytest.fixture
def sample_form():
    return (
        FormBuilder("Test Survey", "A test survey")
        .add_section("profile", "Profile")
        .add_field("profile", "name", "Full Name", FieldType.TEXT)
        .add_field("profile", "email", "Email", FieldType.EMAIL)
        .add_field("profile", "role", "Role", FieldType.SINGLE_CHOICE,
                   options=["Student", "Worker"])
        .add_field("profile", "school", "School Name", FieldType.TEXT, required=False)
        .add_conditional_logic("school", {"if_field": "role", "equals": "Student"})
        .add_section("assess", "Assessment")
        .add_field("assess", "q1", "I enjoy learning", FieldType.LIKERT_SCALE)
        .add_field("assess", "interests", "Interests", FieldType.MULTIPLE_CHOICE,
                   options=["Sports", "Music", "Art"])
        .build()
    )


class TestToJson:
    def test_serializable(self, sample_form):
        data = FormGenerator.to_json(sample_form)
        # Should be JSON-serializable
        s = json.dumps(data)
        assert '"Test Survey"' in s

    def test_round_trip(self, sample_form):
        data = FormGenerator.to_json(sample_form)
        assert data["name"] == "Test Survey"
        assert len(data["sections"]) == 2


class TestToN8nWorkflow:
    def test_structure(self, sample_form):
        wf = FormGenerator.to_n8n_workflow(sample_form)
        assert "nodes" in wf
        assert "connections" in wf
        assert wf["nodes"][0]["type"] == "n8n-nodes-base.webhook"

    def test_meta_fields(self, sample_form):
        wf = FormGenerator.to_n8n_workflow(sample_form)
        fields = wf["meta"]["form_fields"]
        assert len(fields) == 6
        names = [f["name"] for f in fields]
        assert "name" in names
        assert "email" in names


class TestToHtml:
    def test_contains_html_structure(self, sample_form):
        html = FormGenerator.to_html_form(sample_form)
        assert "<!DOCTYPE html>" in html
        assert "tailwindcss" in html
        assert "Test Survey" in html

    def test_contains_all_fields(self, sample_form):
        html = FormGenerator.to_html_form(sample_form)
        assert 'name="name"' in html
        assert 'name="email"' in html
        assert 'name="role"' in html

    def test_conditional_logic_js(self, sample_form):
        html = FormGenerator.to_html_form(sample_form)
        assert "data-condition-field" in html
        assert "updateVisibility" in html

    def test_custom_action_url(self, sample_form):
        html = FormGenerator.to_html_form(sample_form, action_url="/submit")
        assert 'action="/submit"' in html


class TestToGoogleForms:
    def test_structure(self, sample_form):
        cfg = FormGenerator.to_google_forms_config(sample_form)
        assert "info" in cfg
        assert cfg["info"]["title"] == "Test Survey"
        assert "items" in cfg

    def test_field_types(self, sample_form):
        cfg = FormGenerator.to_google_forms_config(sample_form)
        types = [item["type"] for item in cfg["items"] if "type" in item]
        assert "SECTION_HEADER" in types
        assert "MULTIPLE_CHOICE" in types


class TestToMarkdown:
    def test_contains_header(self, sample_form):
        md = FormGenerator.to_markdown(sample_form)
        assert "# Test Survey" in md

    def test_contains_fields(self, sample_form):
        md = FormGenerator.to_markdown(sample_form)
        assert "Full Name" in md
        assert "*(required)*" in md

    def test_conditional_logic_shown(self, sample_form):
        md = FormGenerator.to_markdown(sample_form)
        assert "Show when" in md


class TestTemplateGenerators:
    """Test that all templates generate valid output in all formats."""

    @pytest.mark.parametrize("template_fn", [
        FormTemplates.basic_profile_form,
        FormTemplates.personality_assessment_form,
        FormTemplates.interests_form,
        FormTemplates.preferences_form,
        FormTemplates.role_selection_form,
        FormTemplates.comprehensive_survey_form,
    ])
    def test_all_templates_generate_all_formats(self, template_fn):
        form = template_fn().build()
        assert FormGenerator.to_json(form) is not None
        assert FormGenerator.to_n8n_workflow(form) is not None
        assert len(FormGenerator.to_html_form(form)) > 100
        assert FormGenerator.to_google_forms_config(form) is not None
        assert len(FormGenerator.to_markdown(form)) > 50
