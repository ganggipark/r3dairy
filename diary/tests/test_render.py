"""PDF rendering smoke tests (mock DailyContent)."""
from diary import DailyContent, color_to_hex, render_diary


def _mock_day(date_str: str = "2026-05-15", color: str = "은백색") -> DailyContent:
    return DailyContent(
        date=date_str,
        lucky_color=color,
        lucky_direction="서",
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
            "work": "복잡한 의사결정을 오전에 처리. 단계별 분해 후 우선순위화.",
            "relations": "표면 대화보다 의도 표명이 신뢰를 강화합니다.",
            "health": "외부 자극 줄이는 환경 설계. 알림 차단·짧은 호흡 휴식.",
            "finance": "지출 결정은 24시간 보류 후 재검토하세요.",
        },
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


def test_pretendard_font_files_present():
    """3 weights committed to repo with sane file sizes."""
    from diary.render import _STATIC_DIR
    fonts_dir = _STATIC_DIR / "fonts"
    for weight in ("Regular", "SemiBold", "Bold"):
        font_file = fonts_dir / f"Pretendard-{weight}.woff2"
        assert font_file.exists(), f"missing: {font_file}"
        assert font_file.stat().st_size > 10_000, f"suspicious size: {font_file}"


def test_pdf_embeds_pretendard(tmp_path):
    """PDF font dictionary contains a Pretendard entry.

    pypdf inspects the actual /Font resources (compressed in PDF streams),
    so we don't rely on raw byte search through compressed content.
    Without @font-face the PDF falls back to system fonts (Malgun Gothic
    on Windows). With FontConfiguration wiring, Pretendard is loaded,
    subset, and embedded.
    """
    from pypdf import PdfReader

    output = tmp_path / "embedded.pdf"
    render_diary([_mock_day()], output)

    reader = PdfReader(str(output))
    fonts: set[str] = set()
    for page in reader.pages:
        font_dict = page.get("/Resources", {}).get("/Font", {})
        if hasattr(font_dict, "keys"):
            for fk in font_dict.keys():
                obj = font_dict[fk].get_object() if hasattr(font_dict[fk], "get_object") else font_dict[fk]
                basefont = str(obj.get("/BaseFont", ""))
                fonts.add(basefont)

    assert any("Pretendard" in f for f in fonts), (
        f"Pretendard not in PDF /Font resources. Found: {fonts}"
    )


def test_ofl_license_bundled():
    """OFL license must be distributed with the font (OFL §5)."""
    from diary.render import _STATIC_DIR
    ofl = _STATIC_DIR / "fonts" / "OFL.txt"
    assert ofl.exists()
    content = ofl.read_text(encoding="utf-8")
    assert "SIL OPEN FONT LICENSE" in content.upper()


from diary.render import _parse_korean_hour, parse_lucky_hours


def test_parse_korean_hour_morning():
    assert _parse_korean_hour("오전 9시") == 9
    assert _parse_korean_hour("오전 12시") == 0


def test_parse_korean_hour_afternoon():
    assert _parse_korean_hour("오후 1시") == 13
    assert _parse_korean_hour("오후 11시") == 23
    assert _parse_korean_hour("오후 12시") == 12


def test_parse_korean_hour_special():
    assert _parse_korean_hour("정오") == 12
    assert _parse_korean_hour("자정") == 0


def test_parse_korean_hour_invalid():
    assert _parse_korean_hour("garbage") is None
    assert _parse_korean_hour("") is None


def test_parse_lucky_hours_morning_range():
    assert parse_lucky_hours("오전 9시–오전 11시") == {9, 10, 11}


def test_parse_lucky_hours_crosses_noon():
    assert parse_lucky_hours("오전 11시–오후 1시") == {11, 12, 13}


def test_parse_lucky_hours_midnight_crossing():
    assert parse_lucky_hours("오후 11시–오전 1시") == {23, 0, 1}


def test_parse_lucky_hours_invalid():
    assert parse_lucky_hours("garbage") == set()
    assert parse_lucky_hours("") == set()


def test_render_a4(tmp_path):
    output = tmp_path / "a4.pdf"
    result = render_diary([_mock_day()], output, page_size="A4")
    assert result.exists()
    assert result.stat().st_size > 3000


def test_render_a6(tmp_path):
    output = tmp_path / "a6.pdf"
    result = render_diary([_mock_day()], output, page_size="A6")
    assert result.exists()


def test_render_invalid_page_size(tmp_path):
    import pytest
    with pytest.raises(ValueError, match="Unknown page_size"):
        render_diary([_mock_day()], tmp_path / "bad.pdf", page_size="A99")


def test_render_invalid_hour_range(tmp_path):
    import pytest
    with pytest.raises(ValueError, match="day_end_hour must be"):
        render_diary([_mock_day()], tmp_path / "bad.pdf",
                     day_start_hour=20, day_end_hour=5)


def test_pdf_contains_time_labels(tmp_path):
    """우측 페이지에 시간 라벨이 들어가는지."""
    output = tmp_path / "grid.pdf"
    render_diary([_mock_day()], output, day_start_hour=7, day_end_hour=10)

    content = output.read_bytes()
    assert content[:4] == b"%PDF"
