"""Daily content generation: qimen-driven lucky_* + LLM narrative."""
from __future__ import annotations
import json
import os
import re
from datetime import date as _date
from pathlib import Path
from typing import Literal, Optional

from .models import CompleteSajuData, DailyContent, QimenResult, _LLMNarrative

_PROMPTS_DIR = Path(__file__).parent / "prompts"

Provider = Literal["openai", "anthropic", "deepinfra"]

_DEFAULT_MODELS = {
    "openai": "gpt-4o-mini",
    "anthropic": "claude-sonnet-4-6",
    "deepinfra": "Qwen/Qwen3-235B-A22B-Instruct-2507",
}

DEEPINFRA_BASE_URL = "https://api.deepinfra.com/v1/openai"


_GAN_TO_ELEMENT = {
    "갑": "목", "甲": "목", "을": "목", "乙": "목",
    "병": "화", "丙": "화", "정": "화", "丁": "화",
    "무": "토", "戊": "토", "기": "토", "己": "토",
    "경": "금", "庚": "금", "신": "금", "辛": "금",
    "임": "수", "壬": "수", "계": "수", "癸": "수",
}

_ELEMENT_TO_COLOR = {
    "목": "청록색",
    "화": "주황색",
    "토": "황금색",
    "금": "은백색",
    "수": "감청색",
}


class ContentGenerationError(RuntimeError):
    pass


def _load_prompt(name: str) -> str:
    return (_PROMPTS_DIR / f"{name}.md").read_text(encoding="utf-8")


def _strip_code_fence(text: str) -> str:
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    return m.group(1) if m else text.strip()


def _derive_lucky_color(qimen: QimenResult) -> str:
    """bestPalace의 heavenly plate gan -> 오행 -> 색."""
    gan = qimen.bestPalace.heavenlyPlateGan
    element = _GAN_TO_ELEMENT.get(gan, "토")
    return _ELEMENT_TO_COLOR[element]


def _format_lucky_time(hour_start: int, hour_end: int) -> str:
    """8,10 -> '오전 8시–10시'; 13,15 -> '오후 1시–3시'; 11,13 -> '오전 11시–오후 1시'."""
    def _label(h: int) -> tuple[str, int]:
        h = h % 24
        if h == 0:
            return "오전", 12
        if h < 12:
            return "오전", h
        if h == 12:
            return "오후", 12
        return "오후", h - 12

    s_period, s_h = _label(hour_start)
    e_period, e_h = _label(hour_end)
    if s_period == e_period:
        return f"{s_period} {s_h}시–{e_h}시"
    return f"{s_period} {s_h}시–{e_period} {e_h}시"


def _compute_lucky(qimen: QimenResult) -> dict:
    return {
        "lucky_color": _derive_lucky_color(qimen),
        "lucky_direction": qimen.bestPalace.directionKo,
        "lucky_time": _format_lucky_time(qimen.hourStart, qimen.hourEnd),
    }


def _format_qimen_context(qimen: QimenResult) -> str:
    bp = qimen.bestPalace
    ap = qimen.avoidPalace
    return (
        f"오늘 기운: {qimen.overallQuality}\n"
        f"좋은 방위: {bp.directionKo} ({bp.gate}/{bp.star}/{bp.deity}, score {bp.qualityScore})\n"
        f"좋은 시간: {qimen.hourStart}시–{qimen.hourEnd}시 ({qimen.hourBranch}시)\n"
        f"피할 방위: {ap.directionKo} (score {ap.qualityScore})\n"
        f"안내: {qimen.userGuidance}"
    )


def _call_openai_compat(client, model: str, prompt: str, *, json_mode: bool) -> str:
    kwargs = {
        "model": model,
        "max_tokens": 2048,
        "messages": [{"role": "user", "content": prompt}],
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
    response = client.chat.completions.create(**kwargs)
    return response.choices[0].message.content


def _call_anthropic(client, model: str, prompt: str) -> str:
    response = client.messages.create(
        model=model,
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text


def _default_client(provider: Provider):
    if provider == "openai":
        from openai import OpenAI
        return OpenAI()
    if provider == "anthropic":
        from anthropic import Anthropic
        return Anthropic()
    if provider == "deepinfra":
        from openai import OpenAI
        key = os.environ.get("DEEPINFRA_API_KEY")
        if not key:
            raise ContentGenerationError("DEEPINFRA_API_KEY required")
        return OpenAI(api_key=key, base_url=DEEPINFRA_BASE_URL)
    raise ValueError(f"Unknown provider: {provider}")


def _default_model(provider: Provider) -> str:
    return os.environ.get("DIARY_LLM_MODEL") or _DEFAULT_MODELS[provider]


def generate_daily_content(
    saju: CompleteSajuData,
    qimen: QimenResult,
    target_date: _date,
    *,
    provider: Provider = "deepinfra",
    client=None,
    model: Optional[str] = None,
) -> DailyContent:
    """Generate 1일치 콘텐츠. lucky_*는 qimen 결정론, narrative는 LLM."""
    if client is None:
        client = _default_client(provider)
    model = model or _default_model(provider)

    prompt = _load_prompt("daily").format(
        target_date=target_date.isoformat(),
        saju_string=saju.fullSajuString,
        qimen_context=_format_qimen_context(qimen),
    )

    try:
        if provider == "openai":
            text = _call_openai_compat(client, model, prompt, json_mode=True)
        elif provider == "deepinfra":
            text = _call_openai_compat(client, model, prompt, json_mode=False)
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
        narrative = _LLMNarrative.model_validate(data)
    except Exception as e:
        raise ContentGenerationError(f"Narrative schema violation: {e}") from e

    return DailyContent(
        date=target_date.isoformat(),
        **_compute_lucky(qimen),
        **narrative.model_dump(),
    )
