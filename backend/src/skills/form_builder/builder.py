"""FormBuilder class with fluent API for constructing forms."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from .models import (
    ConditionalLogic,
    FieldType,
    FormConfiguration,
    FormField,
    FormSection,
    LikertConfig,
    MatrixConfig,
    ValidationRule,
)
from .validators import FormValidator


class FormBuilder:
    """Fluent API for building form configurations."""

    def __init__(self, form_name: str, form_description: str = "") -> None:
        self._id = str(uuid.uuid4())
        self._name = form_name
        self._description = form_description
        self._sections: Dict[str, FormSection] = {}
        self._section_order = 0
        self._field_counters: Dict[str, int] = {}
        self._metadata: Dict[str, Any] = {}
        self._webhook_url: Optional[str] = None
        self._version: str = "1.0"

    # -- Section management --------------------------------------------------

    def add_section(
        self,
        section_id: str,
        title: str,
        description: Optional[str] = None,
    ) -> FormBuilder:
        """Add a new section. Returns self for chaining."""
        if section_id in self._sections:
            raise ValueError(f"Section '{section_id}' already exists")
        self._section_order += 1
        self._sections[section_id] = FormSection(
            id=section_id,
            title=title,
            description=description,
            fields=[],
            order=self._section_order,
        )
        self._field_counters[section_id] = 0
        return self

    # -- Field management -----------------------------------------------------

    def add_field(
        self,
        section_id: str,
        field_id: str,
        label: str,
        field_type: FieldType,
        required: bool = True,
        options: Optional[List[str]] = None,
        description: Optional[str] = None,
        placeholder: Optional[str] = None,
        default_value: Optional[Any] = None,
        likert_config: Optional[LikertConfig] = None,
        matrix_config: Optional[MatrixConfig] = None,
        validation_rules: Optional[ValidationRule] = None,
    ) -> FormBuilder:
        """Add a field to a section. Returns self for chaining."""
        if section_id not in self._sections:
            raise ValueError(f"Section '{section_id}' does not exist. Add it first.")

        # Auto-create likert config for likert fields
        if field_type == FieldType.LIKERT_SCALE and likert_config is None:
            likert_config = LikertConfig()

        self._field_counters[section_id] += 1
        field = FormField(
            id=field_id,
            label=label,
            field_type=field_type,
            description=description,
            required=required,
            options=options,
            default_value=default_value,
            placeholder=placeholder,
            likert_config=likert_config,
            matrix_config=matrix_config,
            validation_rules=validation_rules,
            order=self._field_counters[section_id],
        )
        self._sections[section_id].fields.append(field)
        return self

    # -- Conditional logic ----------------------------------------------------

    def add_conditional_logic(
        self,
        field_id: str,
        show_when: Dict[str, Any],
    ) -> FormBuilder:
        """Attach conditional display logic to an existing field."""
        for section in self._sections.values():
            for field in section.fields:
                if field.id == field_id:
                    field.conditional_logic = ConditionalLogic(**show_when)
                    return self
        raise ValueError(f"Field '{field_id}' not found in any section")

    # -- Metadata -------------------------------------------------------------

    def set_metadata(self, key: str, value: Any) -> FormBuilder:
        self._metadata[key] = value
        return self

    def set_webhook_url(self, url: str) -> FormBuilder:
        self._webhook_url = url
        return self

    def set_version(self, version: str) -> FormBuilder:
        self._version = version
        return self

    # -- Validation & build ---------------------------------------------------

    def validate_form(self) -> Tuple[bool, List[str]]:
        """Validate current form configuration."""
        form = self._build_config()
        return FormValidator.validate_form_configuration(form)

    def generate_form_json(self) -> Dict[str, Any]:
        """Generate form as JSON-serializable dict."""
        form = self._build_config()
        return form.model_dump(mode="json")

    def build(self) -> FormConfiguration:
        """Build and return the final FormConfiguration. Raises on invalid."""
        form = self._build_config()
        is_valid, errors = FormValidator.validate_form_configuration(form)
        if not is_valid:
            raise ValueError(f"Form validation failed: {'; '.join(errors)}")
        return form

    # -- Internal helpers -----------------------------------------------------

    def _build_config(self) -> FormConfiguration:
        now = datetime.utcnow()
        return FormConfiguration(
            id=self._id,
            name=self._name,
            description=self._description,
            version=self._version,
            created_at=now,
            updated_at=now,
            sections=list(self._sections.values()),
            metadata=self._metadata,
            webhook_url=self._webhook_url,
        )
