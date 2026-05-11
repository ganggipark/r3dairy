"""Daily diary content via OpenAI or Anthropic. Default: openai."""
from __future__ import annotations
import json
import os
import re
from datetime import date as _date
from pathlib import Path
from typing import Literal, Optional

from .models import CompleteSajuData, DailyContent

_PROMPTS_DIR = Path(__file__).parent / "prompts"

Provider = Literal["openai", "anthropic"]


class ContentGenerationError(RuntimeError):
    """API failure or output parsing error."""


def _load_prompt(name: str) -> str:
    return (_PROMPTS_DIR / f"{name}.md").read_text(encoding="utf-8")


def _strip_code_fence(text: str) -> str:
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    return m.group(1) if m else text.strip()


def _call_openai(client, model: str, prompt: str) -> str:
    response = client.chat.completions.create(
        model=model,
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )
    return response.choices[0].message.content


def _call_anthropic(client, model: str, prompt: str) -> str:
    response = client.messages.create(
        model=model,
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text


def _default_model(provider: Provider) -> str:
    env = os.environ.get("DIARY_LLM_MODEL")
    if env:
        return env
    return "gpt-4o-mini" if provider == "openai" else "claude-sonnet-4-6"


def _default_client(provider: Provider):
    if provider == "openai":
        from openai import OpenAI
        return OpenAI()
    elif provider == "anthropic":
        from anthropic import Anthropic
        return Anthropic()
    raise ValueError(f"Unknown provider: {provider}")


def generate_daily_content(
    saju: CompleteSajuData,
    target_date: _date,
    *,
    provider: Provider = "openai",
    client=None,
    model: Optional[str] = None,
) -> DailyContent:
    """Generate one day's content. Provider configurable (default: openai)."""
    if client is None:
        client = _default_client(provider)
    model = model or _default_model(provider)

    prompt = _load_prompt("daily").format(
        target_date=target_date.isoformat(),
        saju_string=saju.fullSajuString,
        saju_json=json.dumps(saju.model_dump(), ensure_ascii=False, indent=2),
    )

    try:
        if provider == "openai":
            text = _call_openai(client, model, prompt)
        elif provider == "anthropic":
            text = _call_anthropic(client, model, prompt)
        else:
            raise ValueError(f"Unknown provider: {provider}")
    except ContentGenerationError:
        raise
    except Exception as e:
        raise ContentGenerationError(f"{provider} API failed: {e}") from e

    json_str = _strip_code_fence(text)

    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ContentGenerationError(
            f"LLM output not JSON: {e}\n\n{json_str[:300]}"
        ) from e

    try:
        return DailyContent.model_validate(data)
    except Exception as e:
        raise ContentGenerationError(f"DailyContent schema violation: {e}") from e
