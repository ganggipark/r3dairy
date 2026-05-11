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


def _openai_mock(text):
    client = MagicMock()
    msg = MagicMock()
    msg.message.content = text
    client.chat.completions.create.return_value = MagicMock(choices=[msg])
    return client


def _anthropic_mock(text):
    client = MagicMock()
    client.messages.create.return_value = MagicMock(
        content=[MagicMock(text=text)]
    )
    return client


def test_openai_happy_path(sample_saju):
    result = generate_daily_content(
        saju=sample_saju,
        target_date=date(2026, 5, 15),
        provider="openai",
        client=_openai_mock(VALID_JSON),
        model="gpt-4o-mini",
    )
    assert isinstance(result, DailyContent)
    assert result.lucky_color == "청록색"


def test_anthropic_happy_path(sample_saju):
    result = generate_daily_content(
        saju=sample_saju,
        target_date=date(2026, 5, 15),
        provider="anthropic",
        client=_anthropic_mock(VALID_JSON),
        model="claude-sonnet-4-6",
    )
    assert result.lucky_color == "청록색"


def test_rejects_non_json(sample_saju):
    with pytest.raises(ContentGenerationError, match="not JSON"):
        generate_daily_content(
            sample_saju,
            date(2026, 5, 15),
            provider="openai",
            client=_openai_mock("죄송합니다, 생성 불가."),
        )


def test_rejects_schema_violation(sample_saju):
    bad = '{"date": "2026-05-15", "daily_summary": "짧음"}'
    with pytest.raises(ContentGenerationError, match="schema"):
        generate_daily_content(
            sample_saju,
            date(2026, 5, 15),
            provider="openai",
            client=_openai_mock(bad),
        )
