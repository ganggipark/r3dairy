"""Content generation tests (mocked — no real API)."""
from datetime import date
from unittest.mock import MagicMock

import pytest

from diary import SajuInput, calculate_saju
from diary.content import ContentGenerationError, generate_daily_content
from diary.models import DailyContent


@pytest.fixture
def sample_saju():
    return calculate_saju(
        SajuInput(year=1990, month=5, day=15, hour=14, gender="male")
    )


VALID_JSON = """```json
{
  "date": "2026-05-15",
  "daily_summary": "오늘은 전반적으로 평온하면서도 새로운 시작에 적합한 날입니다. 차분히 계획을 세우기 좋은 시간이 흐릅니다.",
  "daily_focus": "장기적인 계획을 차분히 정리하고 가족과의 대화에 시간을 할애하세요.",
  "daily_caution": "성급한 결정은 피하고 감정적인 언행을 자제하는 것이 좋습니다.",
  "lucky_color": "청록색",
  "lucky_direction": "남동",
  "lucky_time": "오전 10-12시",
  "recommended_actions": ["산책 30분", "차 한 잔과 일기", "가족 안부 전화"],
  "things_to_avoid": ["과식", "충동적 쇼핑"]
}
```"""


def _oai_mock(text):
    """Mock for openai/deepinfra (both use OpenAI SDK shape)."""
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
def test_happy_path_all_providers(sample_saju, provider, mock_fn, model):
    result = generate_daily_content(
        saju=sample_saju,
        target_date=date(2026, 5, 15),
        provider=provider,
        client=mock_fn(VALID_JSON),
        model=model,
    )
    assert isinstance(result, DailyContent)
    assert result.lucky_color == "청록색"


def test_rejects_non_json(sample_saju):
    with pytest.raises(ContentGenerationError, match="not JSON"):
        generate_daily_content(
            sample_saju,
            date(2026, 5, 15),
            provider="deepinfra",
            client=_oai_mock("죄송합니다, 생성 불가."),
        )


def test_rejects_schema_violation(sample_saju):
    bad = '{"date": "2026-05-15", "daily_summary": "짧음"}'
    with pytest.raises(ContentGenerationError, match="schema"):
        generate_daily_content(
            sample_saju,
            date(2026, 5, 15),
            provider="deepinfra",
            client=_oai_mock(bad),
        )
