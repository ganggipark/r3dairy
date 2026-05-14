"""M23: parse_lucky_hours 회귀 테스트 — M22 이후 발생한 모든 시진 패턴."""
import pytest
from diary.render import parse_lucky_hours, _parse_korean_hour


@pytest.mark.parametrize("text,expected", [
    ("오전 11시–오후 1시", {11, 12, 13}),
    ("오후 11시–오전 1시", {0, 1, 23}),  # 자정 걸침
    ("오후 1시–3시", {13, 14, 15}),
    ("오전 7시–9시", {7, 8, 9}),
    ("오전 9시–11시", {9, 10, 11}),
    ("오후 3시–5시", {15, 16, 17}),
    ("오전 3시–5시", {3, 4, 5}),
    ("오후 5시–7시", {17, 18, 19}),
    ("오후 7시–9시", {19, 20, 21}),
    ("오후 9시–11시", {21, 22, 23}),
])
def test_parse_all_12_sijins(text, expected):
    """12시진 전체 패턴 round-trip."""
    assert parse_lucky_hours(text) == expected, f"'{text}' 파싱 실패"


def test_round_trip_all_12_sijins():
    """_format_lucky_time → parse_lucky_hours 라운드트립."""
    from diary.content import _format_lucky_time
    sijin_starts = [23, 1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21]
    for s in sijin_starts:
        e = (s + 2) % 24
        label = _format_lucky_time(s, e)
        hours = parse_lucky_hours(label)
        if e >= s:
            assert hours == set(range(s, e + 1)), \
                f"라운드트립 실패: ({s},{e}) → '{label}' → {hours}"
        else:
            assert hours == set(range(s, 24)) | set(range(0, e + 1))
