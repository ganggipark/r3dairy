"""사주 계산 정확성 검증 — 표준 만세력 reference."""
import pytest
from diary.models import SajuInput
from diary.saju import calculate_saju


STANDARD_CASES = [
    {
        "name": "박준수",
        "input": SajuInput(year=1971, month=11, day=17, hour=4, minute=0, gender="male"),
        "expected_pillars": {
            "year": "신해",
            "month": "기해",
            "day": "병오",
            "time": "경인",
        },
    },
    {
        "name": "1985 case",
        "input": SajuInput(year=1985, month=6, day=15, hour=14, minute=0, gender="female"),
    },
]


def test_park_junsoo_pillars():
    """박준수 사주 4기둥이 만세력 표준과 일치."""
    case = STANDARD_CASES[0]
    saju = calculate_saju(case["input"])
    fp = saju.fourPillars
    expected = case["expected_pillars"]
    actual = {
        "year":  fp.year.gan + fp.year.ji,
        "month": fp.month.gan + fp.month.ji,
        "day":   fp.day.gan + fp.day.ji,
        "time":  fp.time.gan + fp.time.ji,
    }
    assert actual == expected, (
        f"\n박준수 사주 만세력 불일치:\n"
        f"  계산: {actual}\n"
        f"  표준: {expected}"
    )


def test_day_pillar_60_cycle():
    """일주는 60갑자 순환 — 60일 후 같은 일주."""
    base = SajuInput(year=2026, month=1, day=1, hour=12, minute=0, gender="male")
    s1 = calculate_saju(base)

    from datetime import date, timedelta
    later = date(2026, 1, 1) + timedelta(days=60)
    s2 = calculate_saju(SajuInput(
        year=later.year, month=later.month, day=later.day,
        hour=12, minute=0, gender="male"
    ))

    p1 = s1.fourPillars.day
    p2 = s2.fourPillars.day
    assert p1.gan == p2.gan and p1.ji == p2.ji, (
        f"60일 후 일주 다름 — 60갑자 순환 오류:\n"
        f"  Day 0: {p1.gan}{p1.ji}\n"
        f"  Day 60: {p2.gan}{p2.ji}"
    )


def test_day_pillar_sequential():
    """연속 5일의 일주가 60갑자 순서대로."""
    GAN = ['갑','을','병','정','무','기','경','신','임','계']
    JI  = ['자','축','인','묘','진','사','오','미','신','유','술','해']

    from datetime import date, timedelta
    base = date(2026, 5, 15)
    indices = []
    for i in range(5):
        d = base + timedelta(days=i)
        saju = calculate_saju(SajuInput(
            year=d.year, month=d.month, day=d.day, hour=12, minute=0, gender="male"
        ))
        gan_idx = GAN.index(saju.fourPillars.day.gan)
        ji_idx = JI.index(saju.fourPillars.day.ji)
        for cycle in range(60):
            if cycle % 10 == gan_idx and cycle % 12 == ji_idx:
                indices.append(cycle)
                break

    for i in range(1, len(indices)):
        diff = (indices[i] - indices[i-1]) % 60
        assert diff == 1, (
            f"일주 비순차 — Day {i-1}→{i}: 인덱스 차이 {diff}\n"
            f"  인덱스 시퀀스: {indices}"
        )


def test_hour_pillar_consistency():
    """시주는 일간(日干) + 시지(時支)로 결정 — 5호둔(五虎遁) 규칙."""
    base = {"year": 1971, "month": 11, "day": 17, "minute": 0, "gender": "male"}

    s_inhour = calculate_saju(SajuInput(**base, hour=4))
    s_oohour = calculate_saju(SajuInput(**base, hour=12))

    assert s_inhour.fourPillars.time.ji == "인", \
        f"04시는 寅시여야 하는데 {s_inhour.fourPillars.time.ji}"
    assert s_oohour.fourPillars.time.ji == "오", \
        f"12시는 午시여야 하는데 {s_oohour.fourPillars.time.ji}"
    assert s_inhour.fourPillars.time.gan + s_inhour.fourPillars.time.ji == "경인", \
        f"丙日 寅時 = 庚寅이어야 함, 실제: {s_inhour.fourPillars.time.gan}{s_inhour.fourPillars.time.ji}"


def test_yongsin_score_oh_haeng_keys():
    """yongSinScore는 5개 오행 키를 모두 가진다 (목/화/토/금/수)."""
    saju = calculate_saju(SajuInput(year=1971, month=11, day=17, hour=4, minute=0, gender="male"))
    score = saju.yongSin.yongSinScore
    expected_keys = {"목", "화", "토", "금", "수"}
    actual_keys = set(score.keys())
    han_keys = {"木", "火", "土", "金", "水"}
    assert expected_keys.issubset(actual_keys) or han_keys.issubset(actual_keys), \
        f"yongSinScore에 5개 오행 key 누락:\n  실제: {actual_keys}\n  기대: {expected_keys}"
    for k, v in score.items():
        assert 0 <= v <= 100, f"score[{k}]={v} 범위 초과"
