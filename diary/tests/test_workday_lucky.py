"""M24: dual lucky time — daily best + workday best."""
from datetime import date, datetime
import pytest

from diary.models import SajuInput
from diary.saju import calculate_saju
from diary.qimen import calculate_qimen


@pytest.fixture
def park_junsoo():
    return SajuInput(year=1971, month=11, day=17, hour=4, minute=0, gender="male")


def test_workday_range_returns_in_range(park_junsoo):
    """workday_range=(7,23) 내 시진을 반환."""
    saju = calculate_saju(park_junsoo)
    birth = datetime(1971, 11, 17, 4)
    q = calculate_qimen(birth, date(2026, 5, 15),
                          yong_sin_score=saju.yongSin.yongSinScore,
                          workday_range=(7, 23))
    assert 7 <= q.hourStart <= 23
    assert 7 <= q.hourEnd <= 23


def test_workday_differs_from_daily_best(park_junsoo):
    """박준수 5/15는 daily best=새벽 3-5시, workday best는 07-23 내."""
    saju = calculate_saju(park_junsoo)
    birth = datetime(1971, 11, 17, 4)

    daily = calculate_qimen(birth, date(2026, 5, 15),
                              yong_sin_score=saju.yongSin.yongSinScore,
                              daily_best=True)
    workday = calculate_qimen(birth, date(2026, 5, 15),
                                yong_sin_score=saju.yongSin.yongSinScore,
                                workday_range=(7, 23))

    if daily.hourStart < 7:
        assert workday.hourStart >= 7, f"workday {workday.hourStart} 일과 시간 밖"


def test_workday_best_score_le_daily_best(park_junsoo):
    """workday best 점수 <= daily best (전체에서 최고가 daily)."""
    saju = calculate_saju(park_junsoo)
    birth = datetime(1971, 11, 17, 4)
    daily = calculate_qimen(birth, date(2026, 5, 15),
                              yong_sin_score=saju.yongSin.yongSinScore, daily_best=True)
    workday = calculate_qimen(birth, date(2026, 5, 15),
                                yong_sin_score=saju.yongSin.yongSinScore,
                                workday_range=(7, 23))
    assert workday.bestPalace.qualityScore <= daily.bestPalace.qualityScore


def test_pipeline_workday_in_daily_content():
    """DailyContent에 workday 필드 채움 가능."""
    from diary.models import DailyContent
    dc = DailyContent(
        date="2026-05-15",
        lucky_color="청록색", lucky_direction="동", lucky_time="오전 3시–5시",
        lucky_color_workday="황금색", lucky_direction_workday="남",
        lucky_time_workday="오전 11시–오후 1시",
        hour_start_workday=11, hour_end_workday=13,
        daily_summary="x"*100, daily_focus="x"*60, daily_caution="x"*60,
        mindfulness="x"*100, right_page_hint="x"*8,
        recommended_actions=["a"*5, "b"*5, "c"*5],
        things_to_avoid=["x"*3, "y"*3],
    )
    assert dc.lucky_time_workday == "오전 11시–오후 1시"
    assert dc.hour_start_workday == 11


def test_workday_fallback_when_no_in_range_match(park_junsoo):
    """workday_range를 매우 좁히면 폴백으로 전체 best 반환."""
    saju = calculate_saju(park_junsoo)
    birth = datetime(1971, 11, 17, 4)
    q = calculate_qimen(birth, date(2026, 5, 15),
                          yong_sin_score=saju.yongSin.yongSinScore,
                          workday_range=(2, 4))
    assert q.bestPalace is not None
