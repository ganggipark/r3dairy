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
        key = os.environ.get("DEEPINFRA_API_KEY", "").strip()
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
    qimen_workday: QimenResult | None = None,
    today_pillar: tuple[str, str] | None = None,
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

    lucky_main = _compute_lucky(qimen)
    # M25: workday 항상 저장 (표시 단계에서 중복 회피)
    workday_extra: dict[str, object] = {}
    if qimen_workday is not None:
        lucky_wk = _compute_lucky(qimen_workday)
        workday_extra = {
            "lucky_color_workday": lucky_wk["lucky_color"],
            "lucky_direction_workday": lucky_wk["lucky_direction"],
            "lucky_time_workday": lucky_wk["lucky_time"],
            "hour_start_workday": qimen_workday.hourStart,
            "hour_end_workday": qimen_workday.hourEnd,
        }

    # M25: 일진통변 + 신살
    ilji_extra: dict[str, object] = {}
    if today_pillar is not None:
        today_gan, today_ji = today_pillar
        my_day = saju.fourPillars.day
        ilji_data = _compute_ilji_relation(my_day.gan, my_day.ji, today_gan, today_ji)
        sinsal_alerts = _extract_sinsal_alerts(my_day.gan, my_day.ji, today_ji)
        ilji_extra = {
            "ilji_pillar": ilji_data["today_pillar"],
            "ilji_relation": " ".join(ilji_data["relations"]) or None,
            "sinsal_alerts": sinsal_alerts,
        }

    return DailyContent(
        date=target_date.isoformat(),
        **lucky_main,
        **workday_extra,
        **ilji_extra,
        **narrative.model_dump(),
    )


# ===== M25: 일진통변 + 신살 데이터/함수 =====
_BRANCH_CHONG = frozenset({
    frozenset(("자","오")), frozenset(("축","미")), frozenset(("인","신")),
    frozenset(("묘","유")), frozenset(("진","술")), frozenset(("사","해")),
})
_BRANCH_YUKHAP = frozenset({
    frozenset(("자","축")), frozenset(("인","해")), frozenset(("묘","술")),
    frozenset(("진","유")), frozenset(("사","신")), frozenset(("오","미")),
})
_STEM_OHHAENG = {
    "갑":"목","을":"목","병":"화","정":"화","무":"토","기":"토",
    "경":"금","신":"금","임":"수","계":"수",
}
_SHENG = {"목":"화","화":"토","토":"금","금":"수","수":"목"}
_KE = {"목":"토","토":"수","수":"화","화":"금","금":"목"}

# 신살 — 명리 정통 규칙 (일간 기준 지지 매핑)
_CHEON_EUL_GUI_IN = {
    "갑": ("축","미"), "무": ("축","미"), "경": ("축","미"),
    "을": ("자","신"), "기": ("자","신"),
    "병": ("유","해"), "정": ("유","해"),
    "임": ("사","묘"), "계": ("사","묘"),
    "신": ("인","오"),
}
_MUN_CHANG = {
    "갑":"사","을":"오","병":"신","정":"유","무":"신",
    "기":"유","경":"해","신":"자","임":"인","계":"묘",
}
# 일지 三合국 → 도화/역마 지지
_SAMHAP_GROUPS = {
    frozenset(("신","자","진")): {"도화":"유","역마":"인"},
    frozenset(("인","오","술")): {"도화":"묘","역마":"신"},
    frozenset(("해","묘","미")): {"도화":"자","역마":"사"},
    frozenset(("사","유","축")): {"도화":"오","역마":"해"},
}


def _compute_ilji_relation(my_gan: str, my_ji: str,
                            today_gan: str, today_ji: str) -> dict:
    """본인 일주 vs 오늘 일주의 천간(생극)/지지(충합) 관계."""
    notes = []
    my_oh = _STEM_OHHAENG.get(my_gan, "")
    today_oh = _STEM_OHHAENG.get(today_gan, "")
    if my_oh and today_oh:
        if my_oh == today_oh:
            notes.append(f"천간 비견({today_oh}) — 협력과 경쟁이 동시에 작용")
        elif _SHENG.get(today_oh) == my_oh:
            notes.append(f"천간 인성({today_oh}→{my_oh}) — 도움과 배움의 기운")
        elif _SHENG.get(my_oh) == today_oh:
            notes.append(f"천간 식상({my_oh}→{today_oh}) — 표현과 활동의 날")
        elif _KE.get(today_oh) == my_oh:
            notes.append(f"천간 관성({today_oh}이 {my_oh}를 극) — 규율과 책임")
        elif _KE.get(my_oh) == today_oh:
            notes.append(f"천간 재성({my_oh}이 {today_oh}를 극) — 결과·성취")

    pair = frozenset((my_ji, today_ji))
    if my_ji == today_ji:
        notes.append(f"일지 {my_ji} 복음(伏吟) — 익숙함과 정체 사이")
    elif pair in _BRANCH_CHONG:
        notes.append(f"일지 {my_ji}{today_ji} 충(冲) — 변동과 결단의 날")
    elif pair in _BRANCH_YUKHAP:
        notes.append(f"일지 {my_ji}{today_ji} 합(合) — 협조와 결합")

    return {
        "today_pillar": f"{today_gan}{today_ji}",
        "my_pillar": f"{my_gan}{my_ji}",
        "relations": notes,
    }


def _extract_sinsal_alerts(my_gan: str, my_ji: str, today_ji: str) -> list[str]:
    """오늘 일지(today_ji)가 본인 일주 기준 신살 위치에 해당하면 발동 알림."""
    alerts = []
    if today_ji in _CHEON_EUL_GUI_IN.get(my_gan, ()):
        alerts.append("천을귀인 발동 — 귀인의 도움 가능")
    if today_ji == _MUN_CHANG.get(my_gan):
        alerts.append("문창귀인 발동 — 학습·시험·표현에 길")
    for group, sinsals in _SAMHAP_GROUPS.items():
        if my_ji in group:
            if today_ji == sinsals["도화"]:
                alerts.append("도화살 발동 — 인기·매력·인간관계 활성")
            if today_ji == sinsals["역마"]:
                alerts.append("역마살 발동 — 이동·변화·새 만남")
            break
    return alerts
