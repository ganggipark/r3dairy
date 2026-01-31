"""Tests for FormBuilder."""

import pytest

from ..builder import FormBuilder
from ..models import FieldType, FormConfiguration, LikertConfig


class TestFormBuilder:
    def test_basic_build(self):
        form = (
            FormBuilder("Test Form", "A test")
            .add_section("s1", "Section 1")
            .add_field("s1", "q1", "Question 1", FieldType.TEXT)
            .build()
        )
        assert isinstance(form, FormConfiguration)
        assert form.name == "Test Form"
        assert len(form.sections) == 1
        assert len(form.sections[0].fields) == 1

    def test_fluent_chaining(self):
        builder = FormBuilder("Test", "")
        result = builder.add_section("s1", "S1")
        assert result is builder  # Returns self

    def test_multiple_sections_and_fields(self):
        form = (
            FormBuilder("Multi", "desc")
            .add_section("s1", "First")
            .add_field("s1", "q1", "Q1", FieldType.TEXT)
            .add_field("s1", "q2", "Q2", FieldType.EMAIL)
            .add_section("s2", "Second")
            .add_field("s2", "q3", "Q3", FieldType.NUMBER)
            .build()
        )
        assert len(form.sections) == 2
        assert len(form.get_all_fields()) == 3

    def test_duplicate_section_raises(self):
        builder = FormBuilder("Test", "").add_section("s1", "S1")
        with pytest.raises(ValueError, match="already exists"):
            builder.add_section("s1", "S1 again")

    def test_field_in_nonexistent_section_raises(self):
        builder = FormBuilder("Test", "")
        with pytest.raises(ValueError, match="does not exist"):
            builder.add_field("nope", "q1", "Q1", FieldType.TEXT)

    def test_conditional_logic(self):
        form = (
            FormBuilder("Test", "")
            .add_section("s1", "S1")
            .add_field("s1", "role", "Role", FieldType.SINGLE_CHOICE,
                       options=["Student", "Worker"])
            .add_field("s1", "school", "School", FieldType.TEXT)
            .add_conditional_logic("school", {"if_field": "role", "equals": "Student"})
            .build()
        )
        school = form.get_field_by_id("school")
        assert school.conditional_logic is not None
        assert school.conditional_logic.if_field == "role"

    def test_conditional_logic_nonexistent_field_raises(self):
        builder = FormBuilder("Test", "").add_section("s1", "S1")
        with pytest.raises(ValueError, match="not found"):
            builder.add_conditional_logic("ghost", {"if_field": "x", "equals": "y"})

    def test_metadata_and_webhook(self):
        form = (
            FormBuilder("Test", "")
            .add_section("s1", "S1")
            .add_field("s1", "q1", "Q1", FieldType.TEXT)
            .set_metadata("locale", "ko")
            .set_webhook_url("https://example.com/hook")
            .build()
        )
        assert form.metadata["locale"] == "ko"
        assert form.webhook_url == "https://example.com/hook"

    def test_generate_form_json(self):
        builder = (
            FormBuilder("Test", "desc")
            .add_section("s1", "S1")
            .add_field("s1", "q1", "Q1", FieldType.TEXT)
        )
        data = builder.generate_form_json()
        assert data["name"] == "Test"
        assert isinstance(data["sections"], list)

    def test_validate_form(self):
        builder = (
            FormBuilder("Test", "desc")
            .add_section("s1", "S1")
            .add_field("s1", "q1", "Q1", FieldType.TEXT)
        )
        is_valid, errors = builder.validate_form()
        assert is_valid is True
        assert errors == []

    def test_build_invalid_form_raises(self):
        builder = (
            FormBuilder("Test", "desc")
            .add_section("s1", "S1")
            .add_field("s1", "q1", "Q1", FieldType.SINGLE_CHOICE)  # No options
        )
        with pytest.raises(ValueError, match="validation failed"):
            builder.build()

    def test_auto_likert_config(self):
        form = (
            FormBuilder("Test", "")
            .add_section("s1", "S1")
            .add_field("s1", "q1", "I like tests", FieldType.LIKERT_SCALE)
            .build()
        )
        assert form.get_field_by_id("q1").likert_config is not None

    def test_section_ordering(self):
        form = (
            FormBuilder("Test", "")
            .add_section("a", "Alpha")
            .add_section("b", "Beta")
            .add_section("c", "Charlie")
            .add_field("a", "q1", "Q1", FieldType.TEXT)
            .add_field("b", "q2", "Q2", FieldType.TEXT)
            .add_field("c", "q3", "Q3", FieldType.TEXT)
            .build()
        )
        assert [s.order for s in form.sections] == [1, 2, 3]
