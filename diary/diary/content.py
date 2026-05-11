"""Daily diary content generation via Anthropic Claude."""
from __future__ import annotations
import json
import os
import re
from datetime import date as _date
from pathlib import Path
from typing import Optional

from .models import CompleteSajuData, DailyContent

_PROMPTS_DIR = Path(__file__).parent / "prompts"


class ContentGenerationError(RuntimeError):
    """API failure or output parsing error."""


def _load_prompt(name: str) -> str:
    return (_PROMPTS_DIR / f"{name}.md").read_text(encoding="utf-8")


def _strip_code_fence(text: str) -> str:
    """Extract JSON from possible markdown code fence."""
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    return m.group(1) if m else text.strip()


def generate_daily_content(
    saju: CompleteSajuData,
    target_date: _date,
    client=None,
    model: Optional[str] = None,
) -> DailyContent:
    """Generate one day's content from saju + date via LLM.

    Args:
        saju: CompleteSajuData from calculate_saju()
        target_date: target date for the diary entry
        client: Anthropic client (defaults to new Anthropic() using ANTHROPIC_API_KEY)
        model: model id (defaults to env DIARY_LLM_MODEL or claude-sonnet-4-6)

    Raises:
        ContentGenerationError: on API failure, non-JSON output, or schema violation
    """
    if client is None:
        from anthropic import Anthropic
        client = Anthropic()

    model = model or os.environ.get("DIARY_LLM_MODEL", "claude-sonnet-4-6")

    prompt = _load_prompt("daily").format(
        target_date=target_date.isoformat(),
        saju_string=saju.fullSajuString,
        saju_json=json.dumps(saju.model_dump(), ensure_ascii=False, indent=2),
    )

    try:
        response = client.messages.create(
            model=model,
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}],
        )
    except Exception as e:
        raise ContentGenerationError(f"Anthropic API failed: {e}") from e

    text = response.content[0].text
    json_str = _strip_code_fence(text)

    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        preview = json_str[:300]
        raise ContentGenerationError(f"LLM output not JSON: {e}\n\n{preview}") from e

    try:
        return DailyContent.model_validate(data)
    except Exception as e:
        raise ContentGenerationError(f"DailyContent schema violation: {e}") from e
