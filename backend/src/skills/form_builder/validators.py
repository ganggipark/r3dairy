"""Form and field validation logic."""

from __future__ import annotations

import re
from typing import List, Optional, Set, Tuple

from .models import FieldType, FormConfiguration, FormField


class FormValidator:
    """Validates form fields, configurations, and conditional logic."""

    # -- Field-level validation -----------------------------------------------

    @staticmethod
    def validate_field(field: FormField) -> Tuple[bool, Optional[str]]:
        """Validate a single field definition. Returns (ok, error_msg)."""

        # ID must be non-empty identifier-safe
        if not field.id or not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", field.id):
            return False, f"Field id '{field.id}' is invalid (must be identifier-safe)"

        if not field.label.strip():
            return False, f"Field '{field.id}' has empty label"

        # Choice fields require options
        if field.field_type in (FieldType.SINGLE_CHOICE, FieldType.MULTIPLE_CHOICE):
            if not field.options or len(field.options) < 2:
                return False, (
                    f"Field '{field.id}' ({field.field_type.value}) "
                    "requires at least 2 options"
                )

        # Likert scale config check
        if field.field_type == FieldType.LIKERT_SCALE:
            if field.likert_config:
                cfg = field.likert_config
                if cfg.scale_min >= cfg.scale_max:
                    return False, (
                        f"Field '{field.id}' likert scale_min must be < scale_max"
                    )

        # Matrix requires rows and columns
        if field.field_type == FieldType.MATRIX:
            if not field.matrix_config:
                return False, f"Field '{field.id}' (matrix) requires matrix_config"
            if len(field.matrix_config.rows) < 1 or len(field.matrix_config.columns) < 2:
                return False, (
                    f"Field '{field.id}' matrix needs >=1 row and >=2 columns"
                )

        # Validation rules sanity
        if field.validation_rules:
            vr = field.validation_rules
            if vr.min_length is not None and vr.max_length is not None:
                if vr.min_length > vr.max_length:
                    return False, f"Field '{field.id}' min_length > max_length"
            if vr.min_value is not None and vr.max_value is not None:
                if vr.min_value > vr.max_value:
                    return False, f"Field '{field.id}' min_value > max_value"

        return True, None

    # -- Form-level validation ------------------------------------------------

    @staticmethod
    def validate_form_configuration(
        form: FormConfiguration,
    ) -> Tuple[bool, List[str]]:
        """Validate the entire form. Returns (ok, error_list)."""
        errors: List[str] = []

        if not form.name.strip():
            errors.append("Form name is empty")

        if not form.sections:
            errors.append("Form has no sections")

        # Collect all field IDs to detect duplicates and validate references
        seen_ids: Set[str] = set()
        all_fields = form.get_all_fields()

        for field in all_fields:
            # Duplicate check
            if field.id in seen_ids:
                errors.append(f"Duplicate field id: '{field.id}'")
            seen_ids.add(field.id)

            # Per-field validation
            ok, msg = FormValidator.validate_field(field)
            if not ok:
                errors.append(msg)  # type: ignore[arg-type]

        # Conditional logic validation
        for field in all_fields:
            if field.conditional_logic:
                ok, msg = FormValidator.validate_conditional_logic(field, form)
                if not ok:
                    errors.append(msg)  # type: ignore[arg-type]

        # Circular dependency check
        circ = FormValidator._detect_circular_conditions(all_fields)
        if circ:
            errors.append(f"Circular conditional dependency detected: {circ}")

        return (len(errors) == 0, errors)

    # -- Conditional logic validation -----------------------------------------

    @staticmethod
    def validate_conditional_logic(
        field: FormField,
        form: FormConfiguration,
    ) -> Tuple[bool, Optional[str]]:
        """Validate that conditional logic references exist."""
        if not field.conditional_logic:
            return True, None

        ref_id = field.conditional_logic.if_field
        ref_field = form.get_field_by_id(ref_id)

        if ref_field is None:
            return False, (
                f"Field '{field.id}' references non-existent field '{ref_id}' "
                "in conditional logic"
            )

        # Self-reference
        if ref_id == field.id:
            return False, f"Field '{field.id}' references itself in conditional logic"

        return True, None

    # -- Circular dependency detection ----------------------------------------

    @staticmethod
    def _detect_circular_conditions(fields: List[FormField]) -> Optional[str]:
        """Detect circular conditional dependencies via DFS."""
        graph: dict[str, str] = {}
        for f in fields:
            if f.conditional_logic:
                graph[f.id] = f.conditional_logic.if_field

        visited: Set[str] = set()
        for start in graph:
            path: List[str] = []
            node: Optional[str] = start
            local_visited: Set[str] = set()
            while node and node in graph:
                if node in local_visited:
                    return " -> ".join(path + [node])
                local_visited.add(node)
                path.append(node)
                node = graph.get(node)
            visited |= local_visited

        return None
