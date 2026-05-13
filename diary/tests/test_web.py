"""Web HTML rendering tests."""
from datetime import date
from pathlib import Path

import pytest

from diary import DailyContent
from diary.web import render_web
from diary.customer import customer_id
from diary.models import SajuInput


def _mock_day(date_str: str = "2026-05-15") -> DailyContent:
    return DailyContent(
        date=date_str,
        lucky_color="청록색",
        lucky_direction="남",
        lucky_time="오전 11시–오후 1시",
        daily_summary=(
            "오늘은 분석적 사고와 패턴 인식에 유리한 환경입니다. 복잡한 의사결정을 "
            "단계별로 분해해 처리하면 효율이 높아지며, 직관적 판단보다 데이터에 "
            "기반한 선택이 안정적 결과를 가져옵니다. 관계에서는 명확한 의도 표명이 "
            "신뢰를 강화하고, 외부 자극을 줄이는 환경 설계가 집중력을 보존합니다."
        ),
        daily_focus=(
            "장기 계획을 차분히 점검하고 가족과의 대화에 시간을 내세요. 작은 목표 "
            "하나에 집중하는 것이 효율적이며, 완료하면 다음 단계를 자연스럽게 이끌어줍니다."
        ),
        daily_caution=(
            "성급한 결정은 피하고 감정적 언행을 자제하는 것이 좋습니다. 무리한 약속을 "
            "거절하는 용기는 장기적 신뢰를 강화하며, 휴식 시간을 충분히 확보하는 것이 중요합니다."
        ),
        mindfulness=(
            "오늘의 감정 흐름을 emotional labeling 기법으로 다루어 보세요. 짜증·불안·"
            "기대 같은 막연한 단어 대신 구체적으로 명명하면 편도체 활성이 약화되어 즉각적 "
            "반응이 줄어듭니다. 신경과학 연구에 따르면 이 단순한 명명 과정만으로도 효과가 "
            "크니, 하루 한 번 실천해 보세요."
        ),
        right_page_hint="오늘도 한 걸음, 충분히 잘하고 있어요.",
        recommended_actions=["산책 30분", "차 한 잔과 일기", "가족 안부 전화"],
        things_to_avoid=["과식", "충동적 쇼핑"],
        domain_advice={
            "work": "복잡한 의사결정을 오전에 처리하세요.",
            "relations": "신뢰 기반 대화에 가치를 두세요.",
            "health": "외부 자극 줄이는 환경 설계.",
            "finance": "지출은 24시간 보류 후 재검토.",
        },
    )


def test_render_web_creates_required_files(tmp_path):
    output = tmp_path / "out"
    render_web(
        [_mock_day("2026-05-15"), _mock_day("2026-05-16")],
        output,
        customer_id="abc123def456",
        customer_name="박준수",
    )
    assert (output / "index.html").exists()
    assert (output / "calendar.html").exists()
    assert (output / "2026-05-15.html").exists()
    assert (output / "2026-05-16.html").exists()
    assert (output / "assets" / "styles.css").exists()


def test_day_html_contains_customer_name(tmp_path):
    output = tmp_path / "out"
    render_web(
        [_mock_day("2026-05-15")],
        output,
        customer_id="t",
        customer_name="박준수",
    )
    html = (output / "2026-05-15.html").read_text(encoding="utf-8")
    assert "박준수" in html
    assert "오늘의 흐름" in html
    assert "오늘의 시간" in html
    assert "마음챙김" not in html or "mindfulness-quote" in html


def test_day_html_navigation_links(tmp_path):
    output = tmp_path / "out"
    contents = [_mock_day(f"2026-05-{15+i:02d}") for i in range(3)]
    render_web(contents, output, customer_id="t", customer_name="박준수")

    middle = (output / "2026-05-16.html").read_text(encoding="utf-8")
    assert "2026-05-15.html" in middle  # prev
    assert "2026-05-17.html" in middle  # next

    first = (output / "2026-05-15.html").read_text(encoding="utf-8")
    assert 'class="nav-btn disabled">‹' in first  # no prev

    last = (output / "2026-05-17.html").read_text(encoding="utf-8")
    assert 'class="nav-btn disabled">›' in last  # no next


def test_index_redirects_based_on_today(tmp_path):
    output = tmp_path / "out"
    render_web(
        [_mock_day("2026-05-15"), _mock_day("2026-05-16")],
        output,
        customer_id="t",
        customer_name="박준수",
    )
    index = (output / "index.html").read_text(encoding="utf-8")
    assert "2026-05-15" in index  # START
    assert "2026-05-16" in index  # END
    assert "calendar.html" in index  # fallback


def test_calendar_groups_by_month(tmp_path):
    output = tmp_path / "out"
    contents = [
        _mock_day("2026-05-30"),
        _mock_day("2026-05-31"),
        _mock_day("2026-06-01"),
        _mock_day("2026-06-02"),
    ]
    render_web(contents, output, customer_id="t", customer_name="박준수")
    cal = (output / "calendar.html").read_text(encoding="utf-8")
    assert "2026-05" in cal
    assert "2026-06" in cal
    for date_str in ["2026-05-30", "2026-05-31", "2026-06-01", "2026-06-02"]:
        assert f'{date_str}.html' in cal


def test_customer_id_20_chars():
    """20-char customer_id for web URL token."""
    birth = SajuInput(year=1990, month=5, day=15, hour=14, gender="male")
    assert len(customer_id(birth, length=12)) == 12  # cache (legacy)
    assert len(customer_id(birth, length=20)) == 20  # web token
    # Stability
    assert customer_id(birth, 20) == customer_id(birth, 20)
    # 20-char is prefix of 64-char hash
    assert customer_id(birth, 20).startswith(customer_id(birth, 12))


def test_customer_id_invalid_length():
    birth = SajuInput(year=1990, month=5, day=15, hour=14, gender="male")
    with pytest.raises(ValueError):
        customer_id(birth, length=4)
    with pytest.raises(ValueError):
        customer_id(birth, length=100)
