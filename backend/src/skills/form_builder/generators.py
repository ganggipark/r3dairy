"""Output generators: n8n workflow, HTML, Google Forms config, JSON, Markdown."""

from __future__ import annotations

import html as html_mod
import json
from typing import Any, Dict, List

from .models import FieldType, FormConfiguration, FormField, FormSection


class FormGenerator:
    """Convert FormConfiguration to various output formats."""

    # -- JSON -----------------------------------------------------------------

    @staticmethod
    def to_json(form: FormConfiguration) -> Dict[str, Any]:
        """Export form as a JSON-serializable dict."""
        return form.model_dump(mode="json")

    # -- n8n workflow ----------------------------------------------------------

    @staticmethod
    def to_n8n_workflow(form: FormConfiguration) -> Dict[str, Any]:
        """Generate an n8n-compatible webhook workflow JSON."""
        webhook_path = form.webhook_url or f"/webhook/form-{form.id}"

        fields_spec: List[Dict[str, Any]] = []
        for field in form.get_all_fields():
            spec: Dict[str, Any] = {
                "name": field.id,
                "label": field.label,
                "type": _n8n_field_type(field.field_type),
                "required": field.required,
            }
            if field.options:
                spec["options"] = [{"name": o, "value": o} for o in field.options]
            if field.description:
                spec["description"] = field.description
            fields_spec.append(spec)

        return {
            "name": f"Form: {form.name}",
            "nodes": [
                {
                    "name": "Webhook",
                    "type": "n8n-nodes-base.webhook",
                    "parameters": {
                        "path": webhook_path,
                        "httpMethod": "POST",
                        "responseMode": "onReceived",
                        "responseData": "allEntries",
                    },
                    "position": [250, 300],
                },
                {
                    "name": "Process Form",
                    "type": "n8n-nodes-base.set",
                    "parameters": {
                        "values": {
                            "string": [
                                {"name": "form_id", "value": form.id},
                                {"name": "form_name", "value": form.name},
                            ]
                        }
                    },
                    "position": [500, 300],
                },
            ],
            "connections": {
                "Webhook": {"main": [[{"node": "Process Form", "type": "main", "index": 0}]]}
            },
            "settings": {"executionOrder": "v1"},
            "meta": {
                "form_fields": fields_spec,
                "form_version": form.version,
            },
        }

    # -- HTML -----------------------------------------------------------------

    @staticmethod
    def to_html_form(form: FormConfiguration, action_url: str = "#") -> str:
        """Generate an HTML form with Tailwind CSS styling."""
        sections_html = "\n".join(
            _render_section_html(section) for section in form.sections
        )
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html_mod.escape(form.name)}</title>
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50 min-h-screen py-12 px-4">
  <div class="max-w-2xl mx-auto bg-white rounded-xl shadow-md p-8">
    <h1 class="text-2xl font-bold text-gray-900 mb-2">{html_mod.escape(form.name)}</h1>
    <p class="text-gray-600 mb-8">{html_mod.escape(form.description)}</p>
    <form action="{html_mod.escape(action_url)}" method="POST" class="space-y-8" id="survey-form">
{sections_html}
      <button type="submit"
        class="w-full bg-indigo-600 text-white py-3 px-6 rounded-lg hover:bg-indigo-700 transition font-medium">
        Submit
      </button>
    </form>
  </div>
  <script>
{_conditional_logic_js(form)}
  </script>
</body>
</html>"""

    # -- Google Forms ----------------------------------------------------------

    @staticmethod
    def to_google_forms_config(form: FormConfiguration) -> Dict[str, Any]:
        """Generate a Google Forms API-compatible configuration."""
        items = []
        for section in form.sections:
            # Section header
            items.append({
                "title": section.title,
                "description": section.description or "",
                "type": "SECTION_HEADER",
            })
            for field in section.fields:
                item: Dict[str, Any] = {
                    "title": field.label,
                    "description": field.description or "",
                    "required": field.required,
                    "type": _google_forms_type(field.field_type),
                }
                if field.options:
                    item["choices"] = [{"value": o} for o in field.options]
                if field.field_type == FieldType.LIKERT_SCALE and field.likert_config:
                    item["scale"] = {
                        "low": field.likert_config.scale_min,
                        "high": field.likert_config.scale_max,
                        "lowLabel": field.likert_config.min_label,
                        "highLabel": field.likert_config.max_label,
                    }
                items.append(item)

        return {
            "info": {
                "title": form.name,
                "description": form.description,
            },
            "items": items,
        }

    # -- Markdown --------------------------------------------------------------

    @staticmethod
    def to_markdown(form: FormConfiguration) -> str:
        """Export form as Markdown documentation."""
        lines = [
            f"# {form.name}",
            "",
            form.description,
            "",
            f"**Version:** {form.version}",
            "",
        ]
        for section in form.sections:
            lines.append(f"## {section.title}")
            if section.description:
                lines.append(f"_{section.description}_")
            lines.append("")
            for field in section.fields:
                req = " *(required)*" if field.required else ""
                lines.append(f"### {field.label}{req}")
                lines.append(f"- **Type:** {field.field_type.value}")
                if field.description:
                    lines.append(f"- **Description:** {field.description}")
                if field.options:
                    lines.append("- **Options:** " + ", ".join(field.options))
                if field.conditional_logic:
                    cl = field.conditional_logic
                    lines.append(
                        f"- **Show when:** `{cl.if_field}` equals `{cl.equals}`"
                    )
                lines.append("")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _n8n_field_type(ft: FieldType) -> str:
    mapping = {
        FieldType.TEXT: "string",
        FieldType.EMAIL: "string",
        FieldType.LONG_TEXT: "string",
        FieldType.NUMBER: "number",
        FieldType.DATE: "dateTime",
        FieldType.SINGLE_CHOICE: "options",
        FieldType.MULTIPLE_CHOICE: "multiOptions",
        FieldType.LIKERT_SCALE: "number",
        FieldType.MATRIX: "json",
    }
    return mapping.get(ft, "string")


def _google_forms_type(ft: FieldType) -> str:
    mapping = {
        FieldType.TEXT: "SHORT_ANSWER",
        FieldType.EMAIL: "SHORT_ANSWER",
        FieldType.LONG_TEXT: "PARAGRAPH",
        FieldType.NUMBER: "SHORT_ANSWER",
        FieldType.DATE: "DATE",
        FieldType.SINGLE_CHOICE: "MULTIPLE_CHOICE",
        FieldType.MULTIPLE_CHOICE: "CHECKBOX",
        FieldType.LIKERT_SCALE: "SCALE",
        FieldType.MATRIX: "GRID",
    }
    return mapping.get(ft, "SHORT_ANSWER")


def _render_section_html(section: FormSection) -> str:
    fields = "\n".join(_render_field_html(f) for f in section.fields)
    desc = (
        f'<p class="text-gray-500 text-sm">{html_mod.escape(section.description)}</p>'
        if section.description else ""
    )
    return f"""      <fieldset class="space-y-6">
        <legend class="text-lg font-semibold text-gray-800">{html_mod.escape(section.title)}</legend>
        {desc}
{fields}
      </fieldset>"""


def _render_field_html(field: FormField) -> str:
    req = " required" if field.required else ""
    cond_attr = ""
    if field.conditional_logic:
        cond_attr = (
            f' data-condition-field="{field.conditional_logic.if_field}"'
            f' data-condition-value="{field.conditional_logic.equals}"'
            f' style="display:none"'
        )
    label = html_mod.escape(field.label)
    desc = (
        f'<p class="text-gray-400 text-xs">{html_mod.escape(field.description)}</p>'
        if field.description else ""
    )
    ph = html_mod.escape(field.placeholder or "")

    wrapper_open = f'        <div class="space-y-1" id="field-{field.id}"{cond_attr}>'
    wrapper_close = "        </div>"
    label_html = f'          <label class="block text-sm font-medium text-gray-700" for="{field.id}">{label}</label>'

    if field.field_type in (FieldType.TEXT, FieldType.EMAIL, FieldType.NUMBER, FieldType.DATE):
        input_type = {
            FieldType.TEXT: "text", FieldType.EMAIL: "email",
            FieldType.NUMBER: "number", FieldType.DATE: "date",
        }[field.field_type]
        inp = (
            f'          <input type="{input_type}" name="{field.id}" id="{field.id}"'
            f' placeholder="{ph}" class="w-full border rounded-lg px-3 py-2"{req}/>'
        )
        return f"{wrapper_open}\n{label_html}\n{desc}\n{inp}\n{wrapper_close}"

    if field.field_type == FieldType.LONG_TEXT:
        inp = (
            f'          <textarea name="{field.id}" id="{field.id}" rows="4"'
            f' placeholder="{ph}" class="w-full border rounded-lg px-3 py-2"{req}></textarea>'
        )
        return f"{wrapper_open}\n{label_html}\n{desc}\n{inp}\n{wrapper_close}"

    if field.field_type == FieldType.SINGLE_CHOICE and field.options:
        opts = "\n".join(
            f'            <label class="flex items-center gap-2">'
            f'<input type="radio" name="{field.id}" value="{html_mod.escape(o)}"{req}/>'
            f' {html_mod.escape(o)}</label>'
            for o in field.options
        )
        return f"{wrapper_open}\n{label_html}\n{desc}\n{opts}\n{wrapper_close}"

    if field.field_type == FieldType.MULTIPLE_CHOICE and field.options:
        opts = "\n".join(
            f'            <label class="flex items-center gap-2">'
            f'<input type="checkbox" name="{field.id}" value="{html_mod.escape(o)}"/>'
            f' {html_mod.escape(o)}</label>'
            for o in field.options
        )
        return f"{wrapper_open}\n{label_html}\n{desc}\n{opts}\n{wrapper_close}"

    if field.field_type == FieldType.LIKERT_SCALE:
        cfg = field.likert_config
        if cfg:
            points = range(cfg.scale_min, cfg.scale_max + 1)
            opts = (
                f'          <div class="flex items-center gap-4">'
                f'<span class="text-xs text-gray-400">{html_mod.escape(cfg.min_label)}</span>'
                + "".join(
                    f'<label class="flex flex-col items-center">'
                    f'<input type="radio" name="{field.id}" value="{p}"{req}/>'
                    f'<span class="text-xs">{p}</span></label>'
                    for p in points
                )
                + f'<span class="text-xs text-gray-400">{html_mod.escape(cfg.max_label)}</span>'
                f"</div>"
            )
            return f"{wrapper_open}\n{label_html}\n{desc}\n{opts}\n{wrapper_close}"

    # Fallback
    inp = f'          <input type="text" name="{field.id}" id="{field.id}" class="w-full border rounded-lg px-3 py-2"{req}/>'
    return f"{wrapper_open}\n{label_html}\n{desc}\n{inp}\n{wrapper_close}"


def _conditional_logic_js(form: FormConfiguration) -> str:
    """Generate JS for conditional field visibility."""
    conditionals = []
    for field in form.get_all_fields():
        if field.conditional_logic:
            conditionals.append({
                "fieldId": field.id,
                "ifField": field.conditional_logic.if_field,
                "equals": field.conditional_logic.equals,
            })
    if not conditionals:
        return "// No conditional logic"

    return f"""
    const conditions = {json.dumps(conditionals)};
    function updateVisibility() {{
      conditions.forEach(c => {{
        const el = document.getElementById('field-' + c.fieldId);
        if (!el) return;
        const inputs = document.querySelectorAll('[name="' + c.ifField + '"]');
        let val = '';
        inputs.forEach(inp => {{
          if (inp.type === 'radio' || inp.type === 'checkbox') {{
            if (inp.checked) val = inp.value;
          }} else {{
            val = inp.value;
          }}
        }});
        el.style.display = (val === String(c.equals)) ? '' : 'none';
      }});
    }}
    document.getElementById('survey-form').addEventListener('change', updateVisibility);
    updateVisibility();
    """
