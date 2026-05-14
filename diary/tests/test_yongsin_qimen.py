"""M21: 사주 용신 기반 기문 개인화 검증."""
from datetime import date, datetime
import pytest

from diary.models import SajuInput
from diary.saju import calculate_saju
from diary.qimen import calculate_qimen


@pytest.fixture
def park_junsoo():
    return SajuInput(year=1971, month=11, day=17, hour=4, minute=0, gender="male")


@pytest.fixture
def other_customer():
    return SajuInput(year=1985, month=6, day=15, hour=14, minute=0, gender="female")


def test_yongsin_in_saju_output(park_junsoo):
    saju = calculate_saju(park_junsoo)
    assert saju.yongSin is not None
    assert isinstance(saju.yongSin.yongSinScore, dict)
    assert len(saju.yongSin.yongSinScore) > 0


def test_different_customers_different_yongsin(park_junsoo, other_customer):
    s1 = calculate_saju(park_junsoo)
    s2 = calculate_saju(other_customer)
    assert s1.yongSin.yongSinScore != s2.yongSin.yongSinScore


def test_different_customers_different_best_palace(park_junsoo, other_customer):
    """🎯 핵심 검증: 같은 날짜라도 다른 사주는 다른 bestPalace."""
    target = date(2026, 5, 15)
    s1 = calculate_saju(park_junsoo)
    s2 = calculate_saju(other_customer)
    birth1 = datetime(park_junsoo.year, park_junsoo.month, park_junsoo.day, park_junsoo.hour)
    birth2 = datetime(other_customer.year, other_customer.month, other_customer.day, other_customer.hour)

    q1 = calculate_qimen(birth1, target, target_hour=12,
                          yong_sin_score=s1.yongSin.yongSinScore)
    q2 = calculate_qimen(birth2, target, target_hour=12,
                          yong_sin_score=s2.yongSin.yongSinScore)

    diff = (q1.bestPalace.palaceNum != q2.bestPalace.palaceNum
            or q1.bestPalace.directionKo != q2.bestPalace.directionKo
            or q1.bestPalace.heavenlyPlateGan != q2.bestPalace.heavenlyPlateGan)
    assert diff, (
        f"M21 fix 실패 — 다른 사주 같은 bestPalace:\n"
        f"  박준수: palace={q1.bestPalace.palaceNum}, "
        f"dir={q1.bestPalace.directionKo}, gan={q1.bestPalace.heavenlyPlateGan}\n"
        f"  타고객: palace={q2.bestPalace.palaceNum}, "
        f"dir={q2.bestPalace.directionKo}, gan={q2.bestPalace.heavenlyPlateGan}"
    )


def test_no_yongsin_falls_back(park_junsoo):
    """하위호환: yong_sin_score=None이면 기존 동작."""
    birth = datetime(park_junsoo.year, park_junsoo.month, park_junsoo.day, park_junsoo.hour)
    q = calculate_qimen(birth, date(2026, 5, 15), target_hour=12, yong_sin_score=None)
    assert 0 <= q.bestPalace.qualityScore <= 100
