"""M22: 일주(日柱) 전 시진 최적 탐색 — lucky_time이 실제로 변동되는지 검증."""
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


def _hour_window(qimen):
    return (qimen.hourStart, qimen.hourEnd)


def test_daily_best_different_customers_different_hour(park_junsoo, other_customer):
    """🎯 핵심: 7일 중 최소 1일은 두 고객의 best hour 또는 방향이 달라야.

    단일 날짜만 보면 두 고객 모두 100점 만점 palace가 여러 시진에 존재해
    reduce()의 첫-등장 선택으로 우연히 같아질 수 있음. 통계적으로 검증.
    """
    s1 = calculate_saju(park_junsoo)
    s2 = calculate_saju(other_customer)
    b1 = datetime(park_junsoo.year, park_junsoo.month, park_junsoo.day, park_junsoo.hour)
    b2 = datetime(other_customer.year, other_customer.month, other_customer.day, other_customer.hour)

    diff_days = 0
    samples = []
    for d in range(15, 22):  # 2026-05-15 ~ 21
        target = date(2026, 5, d)
        q1 = calculate_qimen(b1, target,
                              yong_sin_score=s1.yongSin.yongSinScore, daily_best=True)
        q2 = calculate_qimen(b2, target,
                              yong_sin_score=s2.yongSin.yongSinScore, daily_best=True)
        differs = (_hour_window(q1) != _hour_window(q2)
                   or q1.bestPalace.directionKo != q2.bestPalace.directionKo
                   or q1.bestPalace.heavenlyPlateGan != q2.bestPalace.heavenlyPlateGan)
        if differs:
            diff_days += 1
        samples.append((d, _hour_window(q1), q1.bestPalace.directionKo,
                        _hour_window(q2), q2.bestPalace.directionKo, differs))

    assert diff_days >= 1, (
        f"M22 fix 실패 — 7일 모두 lucky_* 동일 (개인화 안 됨):\n"
        + "\n".join(f"  {d}일: P1={t1}{dir1} P2={t2}{dir2} {'DIFF' if df else 'SAME'}"
                     for d, t1, dir1, t2, dir2, df in samples)
    )


def test_daily_best_varies_across_days(park_junsoo):
    """같은 고객의 7일 lucky_time이 매일 동일하면 안 됨."""
    saju = calculate_saju(park_junsoo)
    birth = datetime(park_junsoo.year, park_junsoo.month, park_junsoo.day, park_junsoo.hour)
    hours_seen = set()
    for d in range(15, 22):
        q = calculate_qimen(birth, date(2026, 5, d),
                             yong_sin_score=saju.yongSin.yongSinScore, daily_best=True)
        hours_seen.add(_hour_window(q))
    assert len(hours_seen) >= 2, (
        f"7일간 lucky_time이 단 1개({hours_seen}) — daily_best가 동작 안 함"
    )


def test_daily_best_fallback_without_yongsin(park_junsoo):
    """yongSin 없어도 동작."""
    birth = datetime(park_junsoo.year, park_junsoo.month, park_junsoo.day, park_junsoo.hour)
    q = calculate_qimen(birth, date(2026, 5, 15), daily_best=True, yong_sin_score=None)
    assert q.bestPalace is not None
    assert 0 <= q.bestPalace.qualityScore <= 100


def test_daily_best_vs_fixed_hour(park_junsoo):
    """daily_best=True가 daily_best=False(고정 12시)보다 점수가 같거나 높아야."""
    saju = calculate_saju(park_junsoo)
    birth = datetime(park_junsoo.year, park_junsoo.month, park_junsoo.day, park_junsoo.hour)
    fixed = calculate_qimen(birth, date(2026, 5, 15), target_hour=12,
                             yong_sin_score=saju.yongSin.yongSinScore, daily_best=False)
    best = calculate_qimen(birth, date(2026, 5, 15),
                            yong_sin_score=saju.yongSin.yongSinScore, daily_best=True)
    assert best.bestPalace.qualityScore >= fixed.bestPalace.qualityScore, (
        f"daily_best 점수({best.bestPalace.qualityScore}) < fixed({fixed.bestPalace.qualityScore})"
    )
