"""Content generation tests (mocked — no real API call)."""
from datetime import date
from unittest.mock import MagicMock

import pytest

from diary import SajuInput, calculate_saju
from diary.content import (
    ContentGenerationError,
    generate_daily_content,
)
from diary.models import DailyContent


@pytest.fixture
def sample_saju():
    return calculate_saju(SajuInput(
        year=1990, month=5, day=15, hour=14, gender="male",
    ))


def _mock_response(text: str):
    msg = MagicMock()
    msg.content = [MagicMock(text=text)]
    return msg


VALID_JSON = """```json
{
  "date": "2026-05-15",
  "daily_summary": "오늘은 전반적으로 평온하면서도 새로운 시작에 적합한 날입니다. 차분히 계획을 세우기 좋은 시간이 흐릅니다. 가족과의 시간이 의미 있을 수 있습니다.",
  "daily_focus": "장기적인 계획을 차분히 정리하고 가족과의 대화에 시간을 할애하세요.",
  "daily_caution": "성급한 결정은 피하고 감정적인 언행을 자제하는 것이 좋습니다.",
  "lucky_color": "청록색",
  "lucky_direction": "남동",
  "lucky_time": "오전 10-12시",
  "recommended_actions": ["산책 30분", "차 한 잔과 일기 쓰기", "가족에게 안부 전화"],
  "things_to_avoid": ["과식", "충동적 쇼핑"]
}
```"""


def test_generate_content_happy_path(sample_saju):
    client = MagicMock()
    client.messages.create.return_value = _mock_response(VALID_JSON)

    result = generate_daily_content(
        saju=sample_saju,
        target_date=date(2026, 5, 15),
        client=client,
        model="claude-sonnet-4-6",
    )

    assert isinstance(result, DailyContent)
    assert result.date == "2026-05-15"
    assert result.lucky_color == "청록색"
    assert len(result.recommended_actions) == 3
    client.messages.create.assert_called_once()


def test_generate_content_rejects_non_json(sample_saju):
    client = MagicMock()
    client.messages.create.return_value = _mock_response("죄송합니다, 생성할 수 없습니다.")

    with pytest.raises(ContentGenerationError, match="not JSON"):
        generate_daily_content(sample_saju, date(2026, 5, 15), client=client)


def test_generate_content_rejects_schema_violation(sample_saju):
    """Missing required field → schema error."""
    bad = '{"date": "2026-05-15", "daily_summary": "짧음"}'
    client = MagicMock()
    client.messages.create.return_value = _mock_response(bad)

    with pytest.raises(ContentGenerationError, match="schema"):
        generate_daily_content(sample_saju, date(2026, 5, 15), client=client)
