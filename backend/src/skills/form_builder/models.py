"""Pydantic models for form structures."""

from __future__ import annotations

import enum
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class FieldType(str, enum.Enum):
    """Supported form field types."""

    SINGLE_CHOICE = "single_choice"
    MULTIPLE_CHOICE = "multiple_choice"
    TEXT = "text"
    EMAIL = "email"
    DATE = "date"
    NUMBER = "number"
    LIKERT_SCALE = "likert_scale"
    MATRIX = "matrix"
    LONG_TEXT = "long_text"


class ConditionalLogic(BaseModel):
    """Conditional display logic for a field."""

    if_field: str
    equals: Any

    def to_dict(self) -> Dict[str, Any]:
        return {"if_field": self.if_field, "equals": self.equals}


class ValidationRule(BaseModel):
    """Validation constraints for a field."""

    min_length: Optional[int] = None
    max_length: Optional[int] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    pattern: Optional[str] = None
    min_selections: Optional[int] = None
    max_selections: Optional[int] = None


class LikertConfig(BaseModel):
    """Configuration for Likert scale fields."""

    scale_min: int = 1
    scale_max: int = 5
    min_label: str = "Strongly Disagree"
    max_label: str = "Strongly Agree"


class MatrixConfig(BaseModel):
    """Configuration for matrix fields."""

    rows: List[str]
    columns: List[str]


class FormField(BaseModel):
    """A single form field."""

    id: str
    label: str
    field_type: FieldType
    description: Optional[str] = None
    required: bool = True
    options: Optional[List[str]] = None
    default_value: Optional[Any] = None
    placeholder: Optional[str] = None
    conditional_logic: Optional[ConditionalLogic] = None
    validation_rules: Optional[ValidationRule] = None
    likert_config: Optional[LikertConfig] = None
    matrix_config: Optional[MatrixConfig] = None
    order: int = 0

    @field_validator("options")
    @classmethod
    def options_required_for_choice(cls, v: Optional[List[str]], info) -> Optional[List[str]]:
        # Validation done at form level to allow builder pattern
        return v


class FormSection(BaseModel):
    """A section grouping related fields."""

    id: str
    title: str
    description: Optional[str] = None
    fields: List[FormField] = Field(default_factory=list)
    order: int = 0


class FormConfiguration(BaseModel):
    """Complete form configuration."""

    id: str
    name: str
    description: str
    version: str = "1.0"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    sections: List[FormSection] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    webhook_url: Optional[str] = None

    def get_all_fields(self) -> List[FormField]:
        """Return all fields across all sections."""
        fields = []
        for section in self.sections:
            fields.extend(section.fields)
        return fields

    def get_field_by_id(self, field_id: str) -> Optional[FormField]:
        """Find a field by its ID."""
        for section in self.sections:
            for field in section.fields:
                if field.id == field_id:
                    return field
        return None
