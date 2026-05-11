"""Content generation tests (mocked)."""
from datetime import date, datetime
from unittest.mock import MagicMock

import pytest

from diary import SajuInput, calculate_qimen, calculate_saju
from diary.content import (
    ContentGenerationError,
    _derive_lucky_color,
    _format_lucky_time,
    generate_daily_content,
)
from diary.models import DailyContent


@pytest.fixture(scope="module")
def sample_saju():
    return calculate_saju(
        SajuInput(year=1990, month=5, day=15, hour=14, gender="male")
    )


@pytest.fixture(scope="module")
def sample_qimen():
    return calculate_qimen(
        datetime(1990, 5, 15, 14, 0), date(2026, 5, 15), target_hour=12
    )


VALID_NARRATIVE = """```json
{
  "daily_summary": "오늘은 마음이 안정되어 차분히 생각을 정리하기 좋은 하루입니다. 가까운 사람들과의 대화가 의미 있게 다가올 수 있습니다.",
  "daily_focus": "장기 계획을 차분히 점검하고 가족과의 대화에 시간을 내세요.",
  "daily_caution": "성급한 결정은 피하고 감정적 언행을 자제하는 것이 좋습니다.",
  "mindfulness": "잠시 멈춰 깊은 숨을 들이마시고 천천히 내쉬어 보세요. 떠오르는 감정을 판단 없이 받아들이는 연습이 오늘의 평온을 지켜줍니다. 자신에게 친절한 한마디를 건네 보세요.",
  "right_page_hint": "오늘도 한 걸음, 충분히 잘하고 있어요.",
  "recommended_actions": ["산책 30분", "차 한 잔과 일기", "가족 안부 전화"],
  "things_to_avoid": ["과식", "충동적 쇼핑"]
}
```"""


def _oai_mock(text):
    c = MagicMock()
    msg = MagicMock()
    msg.message.content = text
    c.chat.completions.create.return_value = MagicMock(choices=[msg])
    return c


def _ant_mock(text):
    c = MagicMock()
    c.messages.create.return_value = MagicMock(content=[MagicMock(text=text)])
    return c


@pytest.mark.parametrize(
    "provider,mock_fn,model",
    [
        ("openai", _oai_mock, "gpt-4o-mini"),
        ("deepinfra", _oai_mock, "Qwen/Qwen3-235B-A22B-Instruct-2507"),
        ("anthropic", _ant_mock, "claude-sonnet-4-6"),
    ],
)
def test_happy_path_all_providers(sample_saju, sample_qimen, provider, mock_fn, model):
    result = generate_daily_content(
        saju=sample_saju,
        qimen=sample_qimen,
        target_date=date(2026, 5, 15),
        provider=provider,
        client=mock_fn(VALID_NARRATIVE),
        model=model,
    )
    assert isinstance(result, DailyContent)
    assert result.date == "2026-05-15"
    assert result.mindfulness
    assert result.right_page_hint


def test_lucky_values_come_from_qimen(sample_saju, sample_qimen):
    """lucky_*는 LLM이 아닌 qimen에서 결정론적으로."""
    result = generate_daily_content(
        sample_saju,
        sample_qimen,
        date(2026, 5, 15),
        provider="deepinfra",
        client=_oai_mock(VALID_NARRATIVE),
    )
    assert result.lucky_direction == sample_qimen.bestPalace.directionKo
    assert str(sample_qimen.hourStart) in result.lucky_time
    assert result.lucky_color in {"청록색", "주황색", "황금색", "은백색", "감청색"}


def test_rejects_non_json(sample_saju, sample_qimen):
    with pytest.raises(ContentGenerationError, match="not JSON"):
        generate_daily_content(
            sample_saju,
            sample_qimen,
            date(2026, 5, 15),
            provider="deepinfra",
            client=_oai_mock("죄송합니다."),
        )


def test_rejects_narrative_missing_field(sample_saju, sample_qimen):
    bad = '{"daily_summary": "짧음"}'
    with pytest.raises(ContentGenerationError, match="Narrative"):
        generate_daily_content(
            sample_saju,
            sample_qimen,
            date(2026, 5, 15),
            provider="deepinfra",
            client=_oai_mock(bad),
        )


def test_format_lucky_time():
    assert _format_lucky_time(8, 10) == "오전 8시–10시"
    assert _format_lucky_time(13, 15) == "오후 1시–3시"
    assert _format_lucky_time(11, 13) == "오전 11시–오후 1시"
    assert _format_lucky_time(23, 1) == "오후 11시–오전 1시"


def test_derive_lucky_color_from_gan():
    from diary.models import QimenPalace, QimenResult

    def _build(gan):
        palace = QimenPalace(
            palaceNum=7, directionKo="서", directionEn="W",
            gate="開門", star="天蓬", deity="太陰",
            earthlyPlateGan="갑", heavenlyPlateGan=gan, qualityScore=80,
        )
        return QimenResult(
            hourStart=11, hourEnd=13, hourBranch="午",
            palaces=[palace] * 9, bestPalace=palace, avoidPalace=palace,
            overallQuality="good", userGuidance="test",
        )

    assert _derive_lucky_color(_build("경")) == "은백색"
    assert _derive_lucky_color(_build("甲")) == "청록색"
    assert _derive_lucky_color(_build("丙")) == "주황색"
    assert _derive_lucky_color(_build("기")) == "황금색"
    assert _derive_lucky_color(_build("壬")) == "감청색"
