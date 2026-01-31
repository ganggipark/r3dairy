"""Tests for FormValidator."""

import pytest

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
from ..validators import FormValidator


def _make_form(*fields: FormField) -> FormConfiguration:
    return FormConfiguration(
        id="test", name="Test", description="desc",
        sections=[FormSection(id="s1", title="S1", order=1, fields=list(fields))],
    )


class TestValidateField:
    def test_valid_text_field(self):
        f = FormField(id="q1", label="Name", field_type=FieldType.TEXT, order=1)
        ok, msg = FormValidator.validate_field(f)
        assert ok is True

    def test_invalid_id(self):
        f = FormField(id="123bad", label="X", field_type=FieldType.TEXT, order=1)
        ok, msg = FormValidator.validate_field(f)
        assert ok is False
        assert "invalid" in msg

    def test_empty_label(self):
        f = FormField(id="q1", label="  ", field_type=FieldType.TEXT, order=1)
        ok, msg = FormValidator.validate_field(f)
        assert ok is False

    def test_choice_without_options(self):
        f = FormField(id="q1", label="Pick", field_type=FieldType.SINGLE_CHOICE, order=1)
        ok, msg = FormValidator.validate_field(f)
        assert ok is False
        assert "options" in msg.lower()

    def test_choice_with_one_option(self):
        f = FormField(id="q1", label="Pick", field_type=FieldType.SINGLE_CHOICE,
                      options=["Only"], order=1)
        ok, msg = FormValidator.validate_field(f)
        assert ok is False

    def test_valid_choice(self):
        f = FormField(id="q1", label="Pick", field_type=FieldType.SINGLE_CHOICE,
                      options=["A", "B"], order=1)
        ok, _ = FormValidator.validate_field(f)
        assert ok is True

    def test_likert_bad_scale(self):
        f = FormField(id="q1", label="Rate", field_type=FieldType.LIKERT_SCALE,
                      likert_config=LikertConfig(scale_min=5, scale_max=1), order=1)
        ok, msg = FormValidator.validate_field(f)
        assert ok is False

    def test_matrix_missing_config(self):
        f = FormField(id="q1", label="Grid", field_type=FieldType.MATRIX, order=1)
        ok, msg = FormValidator.validate_field(f)
        assert ok is False

    def test_matrix_insufficient_columns(self):
        f = FormField(id="q1", label="Grid", field_type=FieldType.MATRIX,
                      matrix_config=MatrixConfig(rows=["R1"], columns=["C1"]), order=1)
        ok, msg = FormValidator.validate_field(f)
        assert ok is False

    def test_validation_rules_min_gt_max(self):
        f = FormField(id="q1", label="Bio", field_type=FieldType.LONG_TEXT,
                      validation_rules=ValidationRule(min_length=100, max_length=10), order=1)
        ok, _ = FormValidator.validate_field(f)
        assert ok is False


class TestValidateFormConfiguration:
    def test_empty_form(self):
        form = FormConfiguration(id="f1", name="Test", description="d", sections=[])
        ok, errors = FormValidator.validate_form_configuration(form)
        assert ok is False
        assert any("no sections" in e.lower() for e in errors)

    def test_empty_name(self):
        form = FormConfiguration(id="f1", name="  ", description="d",
                                 sections=[FormSection(id="s1", title="S", order=1)])
        ok, errors = FormValidator.validate_form_configuration(form)
        assert ok is False

    def test_duplicate_field_ids(self):
        form = _make_form(
            FormField(id="q1", label="A", field_type=FieldType.TEXT, order=1),
            FormField(id="q1", label="B", field_type=FieldType.TEXT, order=2),
        )
        ok, errors = FormValidator.validate_form_configuration(form)
        assert ok is False
        assert any("duplicate" in e.lower() for e in errors)

    def test_valid_form(self):
        form = _make_form(
            FormField(id="q1", label="Name", field_type=FieldType.TEXT, order=1),
            FormField(id="q2", label="Email", field_type=FieldType.EMAIL, order=2),
        )
        ok, errors = FormValidator.validate_form_configuration(form)
        assert ok is True
        assert errors == []


class TestConditionalLogicValidation:
    def test_valid_reference(self):
        f1 = FormField(id="role", label="Role", field_type=FieldType.SINGLE_CHOICE,
                       options=["A", "B"], order=1)
        f2 = FormField(id="school", label="School", field_type=FieldType.TEXT,
                       conditional_logic=ConditionalLogic(if_field="role", equals="A"),
                       order=2)
        form = _make_form(f1, f2)
        ok, msg = FormValidator.validate_conditional_logic(f2, form)
        assert ok is True

    def test_missing_reference(self):
        f = FormField(id="school", label="School", field_type=FieldType.TEXT,
                      conditional_logic=ConditionalLogic(if_field="ghost", equals="X"),
                      order=1)
        form = _make_form(f)
        ok, msg = FormValidator.validate_conditional_logic(f, form)
        assert ok is False
        assert "non-existent" in msg

    def test_self_reference(self):
        f = FormField(id="q1", label="Q1", field_type=FieldType.TEXT,
                      conditional_logic=ConditionalLogic(if_field="q1", equals="X"),
                      order=1)
        form = _make_form(f)
        ok, msg = FormValidator.validate_conditional_logic(f, form)
        assert ok is False

    def test_circular_dependency(self):
        f1 = FormField(id="a", label="A", field_type=FieldType.TEXT,
                       conditional_logic=ConditionalLogic(if_field="b", equals="x"), order=1)
        f2 = FormField(id="b", label="B", field_type=FieldType.TEXT,
                       conditional_logic=ConditionalLogic(if_field="a", equals="y"), order=2)
        form = _make_form(f1, f2)
        ok, errors = FormValidator.validate_form_configuration(form)
        assert ok is False
        assert any("circular" in e.lower() for e in errors)
