"""API endpoints for form builder skill."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..skills.form_builder import (
    FieldType,
    FormBuilder,
    FormGenerator,
    FormTemplates,
    FormValidator,
)
from ..skills.form_builder.models import FormConfiguration

router = APIRouter(prefix="/forms", tags=["forms"])

# In-memory store (replace with DB in production)
_forms: Dict[str, FormConfiguration] = {}


# -- Request/Response models --------------------------------------------------

class FieldSpec(BaseModel):
    id: str
    label: str
    field_type: str
    required: bool = True
    options: Optional[List[str]] = None
    description: Optional[str] = None
    placeholder: Optional[str] = None
    conditional_logic: Optional[Dict[str, Any]] = None


class SectionSpec(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    fields: List[FieldSpec]


class FormRequest(BaseModel):
    name: str
    description: str = ""
    sections: List[SectionSpec]
    metadata: Dict[str, Any] = {}
    webhook_url: Optional[str] = None


class DeployRequest(BaseModel):
    target: str = "json"  # json, n8n, html, google_forms, markdown


# -- Endpoints ----------------------------------------------------------------

@router.post("/create")
async def create_form(request: FormRequest) -> Dict[str, Any]:
    """Create a new form from specification."""
    builder = FormBuilder(request.name, request.description)

    for section in request.sections:
        builder.add_section(section.id, section.title, section.description)
        for field in section.fields:
            ft = FieldType(field.field_type)
            builder.add_field(
                section.id, field.id, field.label, ft,
                required=field.required,
                options=field.options,
                description=field.description,
                placeholder=field.placeholder,
            )
            if field.conditional_logic:
                builder.add_conditional_logic(field.id, field.conditional_logic)

    if request.webhook_url:
        builder.set_webhook_url(request.webhook_url)
    for k, v in request.metadata.items():
        builder.set_metadata(k, v)

    try:
        form = builder.build()
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    _forms[form.id] = form
    return {"form_id": form.id, "name": form.name, "field_count": len(form.get_all_fields())}


@router.get("/{form_id}")
async def get_form(form_id: str) -> Dict[str, Any]:
    """Get form configuration by ID."""
    if form_id not in _forms:
        raise HTTPException(status_code=404, detail="Form not found")
    return FormGenerator.to_json(_forms[form_id])


@router.get("/{form_id}/responses")
async def get_form_responses(form_id: str, limit: int = 100) -> Dict[str, Any]:
    """Get form responses (placeholder - integrate with n8n/DB)."""
    if form_id not in _forms:
        raise HTTPException(status_code=404, detail="Form not found")
    return {"form_id": form_id, "responses": [], "total": 0, "limit": limit}


@router.post("/{form_id}/deploy")
async def deploy_form(form_id: str, request: DeployRequest) -> Dict[str, Any]:
    """Export form in the specified format."""
    if form_id not in _forms:
        raise HTTPException(status_code=404, detail="Form not found")

    form = _forms[form_id]
    target = request.target.lower()

    if target == "json":
        return {"format": "json", "data": FormGenerator.to_json(form)}
    elif target == "n8n":
        return {"format": "n8n", "data": FormGenerator.to_n8n_workflow(form)}
    elif target == "html":
        return {"format": "html", "data": FormGenerator.to_html_form(form)}
    elif target == "google_forms":
        return {"format": "google_forms", "data": FormGenerator.to_google_forms_config(form)}
    elif target == "markdown":
        return {"format": "markdown", "data": FormGenerator.to_markdown(form)}
    else:
        raise HTTPException(status_code=400, detail=f"Unknown target: {target}")


@router.get("/templates/{template_name}")
async def get_template(template_name: str) -> Dict[str, Any]:
    """Get a pre-built form template."""
    templates = {
        "basic_profile": FormTemplates.basic_profile_form,
        "personality": FormTemplates.personality_assessment_form,
        "interests": FormTemplates.interests_form,
        "preferences": FormTemplates.preferences_form,
        "role_selection": FormTemplates.role_selection_form,
        "comprehensive": FormTemplates.comprehensive_survey_form,
    }
    if template_name not in templates:
        raise HTTPException(
            status_code=404,
            detail=f"Template not found. Available: {list(templates.keys())}",
        )
    form = templates[template_name]().build()
    _forms[form.id] = form
    return {"form_id": form.id, "data": FormGenerator.to_json(form)}
