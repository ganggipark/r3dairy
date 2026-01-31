"""Tests for form builder models."""

import pytest
from datetime import datetime

from ..models import (
    ConditionalLogic,
    FieldType,
    FormConfiguration,
    FormField,
    FormSection,
    LikertConfig,
    MatrixConfig,
    ValidationRule,
)


class TestFieldType:
    def test_all_field_types_exist(self):
        assert len(FieldType) == 9
        assert FieldType.SINGLE_CHOICE.value == "single_choice"
        assert FieldType.MATRIX.value == "matrix"

    def test_field_type_is_string_enum(self):
        assert isinstance(FieldType.TEXT, str)
        assert FieldType.TEXT == "text"


class TestFormField:
    def test_minimal_field(self):
        f = FormField(id="q1", label="Name", field_type=FieldType.TEXT, order=1)
        assert f.required is True
        assert f.options is None

    def test_choice_field_with_options(self):
        f = FormField(
            id="q2", label="Color", field_type=FieldType.SINGLE_CHOICE,
            options=["Red", "Blue", "Green"], order=1,
        )
        assert len(f.options) == 3

    def test_likert_field(self):
        f = FormField(
            id="q3", label="Agree?", field_type=FieldType.LIKERT_SCALE,
            likert_config=LikertConfig(scale_min=1, scale_max=7), order=1,
        )
        assert f.likert_config.scale_max == 7

    def test_matrix_field(self):
        f = FormField(
            id="q4", label="Rate", field_type=FieldType.MATRIX,
            matrix_config=MatrixConfig(rows=["Q1", "Q2"], columns=["Good", "Bad", "Neutral"]),
            order=1,
        )
        assert len(f.matrix_config.rows) == 2

    def test_conditional_logic(self):
        cl = ConditionalLogic(if_field="role", equals="student")
        f = FormField(id="q5", label="School", field_type=FieldType.TEXT,
                      conditional_logic=cl, order=1)
        assert f.conditional_logic.if_field == "role"

    def test_validation_rules(self):
        vr = ValidationRule(min_length=1, max_length=100)
        f = FormField(id="q6", label="Bio", field_type=FieldType.LONG_TEXT,
                      validation_rules=vr, order=1)
        assert f.validation_rules.max_length == 100


class TestFormSection:
    def test_empty_section(self):
        s = FormSection(id="s1", title="Intro", order=1)
        assert len(s.fields) == 0

    def test_section_with_fields(self):
        s = FormSection(
            id="s1", title="Intro", order=1,
            fields=[FormField(id="q1", label="Name", field_type=FieldType.TEXT, order=1)],
        )
        assert len(s.fields) == 1


class TestFormConfiguration:
    def test_get_all_fields(self):
        form = FormConfiguration(
            id="f1", name="Test", description="desc",
            sections=[
                FormSection(id="s1", title="A", order=1, fields=[
                    FormField(id="q1", label="Q1", field_type=FieldType.TEXT, order=1),
                    FormField(id="q2", label="Q2", field_type=FieldType.TEXT, order=2),
                ]),
                FormSection(id="s2", title="B", order=2, fields=[
                    FormField(id="q3", label="Q3", field_type=FieldType.EMAIL, order=1),
                ]),
            ],
        )
        assert len(form.get_all_fields()) == 3

    def test_get_field_by_id(self):
        form = FormConfiguration(
            id="f1", name="Test", description="desc",
            sections=[
                FormSection(id="s1", title="A", order=1, fields=[
                    FormField(id="q1", label="Q1", field_type=FieldType.TEXT, order=1),
                ]),
            ],
        )
        assert form.get_field_by_id("q1") is not None
        assert form.get_field_by_id("nonexistent") is None
