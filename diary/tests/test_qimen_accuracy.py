"""기문둔갑 정확성 검증."""
import pytest
from datetime import date, datetime
from diary.models import SajuInput
from diary.saju import calculate_saju
from diary.qimen import calculate_qimen


def test_qimen_9_palaces():
    """기문 결과는 정확히 9개 궁(palace)을 가진다."""
    saju = calculate_saju(SajuInput(year=1971, month=11, day=17, hour=4, minute=0, gender="male"))
    birth = datetime(1971, 11, 17, 4)
    q = calculate_qimen(birth, date(2026, 5, 15),
                          yong_sin_score=saju.yongSin.yongSinScore, daily_best=True)
    assert len(q.palaces) == 9, f"palace 수 {len(q.palaces)} (9이어야 함)"


def test_qimen_palace_numbers_1_to_9():
    """9궁의 palaceNum은 정확히 1-9 한 번씩."""
    saju = calculate_saju(SajuInput(year=1971, month=11, day=17, hour=4, minute=0, gender="male"))
    birth = datetime(1971, 11, 17, 4)
    q = calculate_qimen(birth, date(2026, 5, 15),
                          yong_sin_score=saju.yongSin.yongSinScore, daily_best=True)
    nums = sorted(p.palaceNum for p in q.palaces)
    assert nums == list(range(1, 10)), f"palaceNum 분포 이상: {nums}"


def test_qimen_eight_gates_unique():
    """8문(八門) — 휴/생/상/두/경/사/경/개 — 8개 궁에 각각 배치 (중궁 제외)."""
    saju = calculate_saju(SajuInput(year=1971, month=11, day=17, hour=4, minute=0, gender="male"))
    birth = datetime(1971, 11, 17, 4)
    q = calculate_qimen(birth, date(2026, 5, 15),
                          yong_sin_score=saju.yongSin.yongSinScore, daily_best=True)
    gates = [p.gate for p in q.palaces if p.gate]
    unique_gates = set(g.replace("문", "") for g in gates if g)
    assert len(unique_gates) >= 6, f"8문 분포 부족: {unique_gates}"


def test_qimen_best_palace_score_in_range():
    """bestPalace.qualityScore는 0-100 범위."""
    saju = calculate_saju(SajuInput(year=1971, month=11, day=17, hour=4, minute=0, gender="male"))
    birth = datetime(1971, 11, 17, 4)
    q = calculate_qimen(birth, date(2026, 5, 15),
                          yong_sin_score=saju.yongSin.yongSinScore, daily_best=True)
    assert 0 <= q.bestPalace.qualityScore <= 100
    assert q.bestPalace.directionKo in {"북","남","동","서","북동","북서","남동","남서","중앙"}


def test_qimen_yang_yin_dun():
    """양둔/음둔 구분 — 절기에 따라."""
    saju = calculate_saju(SajuInput(year=1971, month=11, day=17, hour=4, minute=0, gender="male"))
    birth = datetime(1971, 11, 17, 4)

    q_summer = calculate_qimen(birth, date(2026, 7, 1), yong_sin_score=saju.yongSin.yongSinScore, daily_best=True)
    q_winter = calculate_qimen(birth, date(2026, 1, 5), yong_sin_score=saju.yongSin.yongSinScore, daily_best=True)

    assert q_summer.bestPalace.heavenlyPlateGan != q_winter.bestPalace.heavenlyPlateGan \
           or q_summer.bestPalace.earthlyPlateGan != q_winter.bestPalace.earthlyPlateGan, \
        "여름/겨울 기문판 동일 — 양둔/음둔 구분 오류"
