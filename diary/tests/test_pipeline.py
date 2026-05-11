"""Pipeline orchestration tests (LLM mocked; saju+qimen real subprocess)."""
from datetime import date
from unittest.mock import MagicMock

import pytest

from diary import SajuInput, generate_diary
from diary.pipeline import PipelineProgress, _customer_id


VALID_NARRATIVE = """```json
{
  "daily_summary": "오늘은 마음이 안정되어 차분히 생각을 정리하기 좋은 하루입니다. 가까운 사람들과의 대화가 의미 있게 다가올 수 있습니다.",
  "daily_focus": "장기 계획을 차분히 점검하고 가족과의 대화에 시간을 내세요.",
  "daily_caution": "성급한 결정은 피하고 감정적 언행을 자제하는 것이 좋습니다.",
  "mindfulness": "잠시 멈춰 깊은 숨을 들이마시고 천천히 내쉬어 보세요. 떠오르는 감정을 판단 없이 받아들이는 연습이 평온을 지켜줍니다. 자신에게 친절한 한마디를 건네 보세요.",
  "right_page_hint": "오늘도 한 걸음, 충분히 잘하고 있어요.",
  "recommended_actions": ["산책 30분", "차 한 잔과 일기", "가족 안부 전화"],
  "things_to_avoid": ["과식", "충동적 쇼핑"]
}
```"""


def _patch_llm(monkeypatch):
    from diary import content as content_module

    def fake_default_client(provider):
        c = MagicMock()
        msg = MagicMock()
        msg.message.content = VALID_NARRATIVE
        c.chat.completions.create.return_value = MagicMock(choices=[msg])
        c.messages.create.return_value = MagicMock(
            content=[MagicMock(text=VALID_NARRATIVE)]
        )
        return c

    monkeypatch.setattr(content_module, "_default_client", fake_default_client)


@pytest.fixture
def birth():
    return SajuInput(year=1990, month=5, day=15, hour=14, gender="male")


def test_generate_diary_3days(birth, tmp_path, monkeypatch):
    _patch_llm(monkeypatch)
    output = tmp_path / "test.pdf"
    cache = tmp_path / "cache"

    result = generate_diary(
        birth=birth, start_date=date(2026, 5, 15), days=3,
        output_path=output, cache_dir=cache,
    )

    assert result.succeeded == 3
    assert result.failed == 0
    assert result.cache_hits == 0
    assert result.output_path.exists()
    assert result.output_path.stat().st_size > 5000


def test_cache_hit_on_second_run(birth, tmp_path, monkeypatch):
    _patch_llm(monkeypatch)
    output1 = tmp_path / "first.pdf"
    output2 = tmp_path / "second.pdf"
    cache = tmp_path / "cache"

    r1 = generate_diary(birth, date(2026, 5, 15), 2, output1, cache_dir=cache)
    r2 = generate_diary(birth, date(2026, 5, 15), 2, output2, cache_dir=cache)

    assert r1.cache_hits == 0
    assert r2.cache_hits == 2
    assert r2.succeeded == 2


def test_progress_callback_fires(birth, tmp_path, monkeypatch):
    _patch_llm(monkeypatch)
    output = tmp_path / "p.pdf"
    events: list[PipelineProgress] = []

    generate_diary(
        birth, date(2026, 5, 15), 2, output,
        cache_dir=None,
        progress=lambda p: events.append(p),
    )

    stages = [e.stage for e in events]
    assert "saju" in stages
    assert "qimen" in stages
    assert "content" in stages
    assert "render" in stages


def test_customer_id_stable(birth):
    id1 = _customer_id(birth)
    id2 = _customer_id(birth)
    assert id1 == id2
    assert len(id1) == 12


def test_customer_id_differs_by_birth():
    a = SajuInput(year=1990, month=5, day=15, hour=14, gender="male")
    b = SajuInput(year=1990, month=5, day=15, hour=14, gender="female")
    assert _customer_id(a) != _customer_id(b)


def test_concurrent_execution_completes(birth, tmp_path, monkeypatch):
    """5일치를 concurrency=3으로 실행 → 모두 성공."""
    _patch_llm(monkeypatch)
    output = tmp_path / "concurrent.pdf"

    result = generate_diary(
        birth=birth, start_date=date(2026, 5, 15), days=5,
        output_path=output, cache_dir=tmp_path / "cache",
        concurrency=3,
    )

    assert result.succeeded == 5
    assert result.failed == 0
    assert result.output_path.exists()


def test_concurrent_preserves_date_order_in_pdf(birth, tmp_path, monkeypatch):
    """병렬 실행해도 PDF는 날짜 순서대로 렌더."""
    _patch_llm(monkeypatch)
    output = tmp_path / "ordered.pdf"
    captured_order: list = []

    from diary import render as render_module
    original_render = render_module.render_diary

    def spy_render(contents, output_path, **kwargs):
        captured_order.extend(c.date for c in contents)
        return original_render(contents, output_path, **kwargs)

    monkeypatch.setattr("diary.pipeline.render_diary", spy_render)

    generate_diary(
        birth=birth, start_date=date(2026, 5, 15), days=5,
        output_path=output, cache_dir=None,
        concurrency=3,
    )

    assert captured_order == [
        "2026-05-15", "2026-05-16", "2026-05-17", "2026-05-18", "2026-05-19",
    ]


def test_concurrent_with_partial_failure(birth, tmp_path, monkeypatch):
    """일부 날짜만 실패해도 나머지는 성공 + 렌더."""
    from diary import content as content_module

    call_count = [0]
    count_lock = __import__("threading").Lock()

    def flaky_client(provider):
        c = MagicMock()
        msg = MagicMock()
        msg.message.content = VALID_NARRATIVE

        def side_effect(*a, **kw):
            with count_lock:
                call_count[0] += 1
                n = call_count[0]
            if n == 2:
                raise RuntimeError("simulated LLM failure")
            return MagicMock(choices=[msg])

        c.chat.completions.create.side_effect = side_effect
        return c

    monkeypatch.setattr(content_module, "_default_client", flaky_client)

    output = tmp_path / "partial.pdf"
    result = generate_diary(
        birth=birth, start_date=date(2026, 5, 15), days=3,
        output_path=output, cache_dir=None,
        concurrency=2, skip_failed=True,
    )

    assert result.succeeded >= 1
    assert result.failed >= 1
    assert result.output_path.exists()
