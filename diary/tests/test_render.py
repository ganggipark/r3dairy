"""PDF rendering smoke tests (mock DailyContent)."""
from diary import DailyContent, color_to_hex, render_diary


def _mock_day(date_str: str = "2026-05-15", color: str = "은백색") -> DailyContent:
    return DailyContent(
        date=date_str,
        lucky_color=color,
        lucky_direction="서",
        lucky_time="오전 11시–오후 1시",
        daily_summary=(
            "오늘은 마음이 안정되어 차분히 생각을 정리하기 좋은 하루입니다. "
            "가까운 사람들과의 대화가 의미 있게 다가올 수 있습니다. "
            "혼자만의 시간도 충분히 누리세요."
        ),
        daily_focus="장기 계획을 차분히 점검하고 가족과의 대화에 시간을 내세요.",
        daily_caution="성급한 결정은 피하고 감정적 언행을 자제하는 것이 좋습니다.",
        mindfulness=(
            "잠시 멈춰 깊은 숨을 들이마시고 천천히 내쉬어 보세요. "
            "떠오르는 감정을 판단 없이 받아들이는 연습이 오늘의 평온을 지켜줍니다. "
            "자신에게 친절한 한마디를 건네 보세요."
        ),
        right_page_hint="오늘도 한 걸음, 충분히 잘하고 있어요.",
        recommended_actions=["산책 30분", "차 한 잔과 일기", "가족 안부 전화"],
        things_to_avoid=["과식", "충동적 쇼핑"],
    )


def test_render_single_day(tmp_path):
    output = tmp_path / "single.pdf"
    result = render_diary([_mock_day()], output)
    assert result.exists()
    assert result.stat().st_size > 3000
    with open(result, "rb") as f:
        assert f.read(4) == b"%PDF"


def test_render_seven_days(tmp_path):
    days = [
        _mock_day(
            date_str=f"2026-05-{15+i:02d}",
            color=["은백색", "청록색", "주황색", "황금색", "감청색"][i % 5],
        )
        for i in range(7)
    ]
    output = tmp_path / "week.pdf"
    result = render_diary(days, output)
    assert result.exists()
    assert result.stat().st_size > 10000


def test_color_to_hex_known():
    assert color_to_hex("은백색") == "#C8C8CC"
    assert color_to_hex("청록색") == "#4FB89F"


def test_color_to_hex_unknown_returns_fallback():
    assert color_to_hex("미지의색") == "#999999"


def _multi_month_days() -> list:
    """5/30, 5/31, 6/1, 6/2 — 2 months."""
    return [
        _mock_day(date_str="2026-05-30", color="청록색"),
        _mock_day(date_str="2026-05-31", color="주황색"),
        _mock_day(date_str="2026-06-01", color="황금색"),
        _mock_day(date_str="2026-06-02", color="감청색"),
    ]


def test_render_with_cover(tmp_path):
    output = tmp_path / "cover.pdf"
    result = render_diary(
        [_mock_day()],
        output,
        include_cover=True,
        customer_name="홍길동",
        period="2026-05-15 — 2027-05-14",
    )
    assert result.exists()
    assert result.stat().st_size > 5000


def test_render_with_month_dividers(tmp_path):
    output = tmp_path / "dividers.pdf"
    result = render_diary(
        _multi_month_days(),
        output,
        include_month_dividers=True,
    )
    assert result.exists()
    assert result.stat().st_size > 8000


def test_render_full_book(tmp_path):
    """cover + dividers + days 모두."""
    output = tmp_path / "book.pdf"
    result = render_diary(
        _multi_month_days(),
        output,
        title="내 다이어리",
        customer_name="홍길동",
        period="2026-05-30 — 2026-06-02",
        include_cover=True,
        include_month_dividers=True,
    )
    assert result.exists()
    with open(result, "rb") as f:
        assert f.read(4) == b"%PDF"


def test_render_default_no_cover_back_compat(tmp_path):
    """Default render_diary call should still work (no cover/dividers)."""
    output = tmp_path / "plain.pdf"
    result = render_diary([_mock_day()], output)
    assert result.exists()
