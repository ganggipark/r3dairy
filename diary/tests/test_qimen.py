"""E2E smoke: qimen subprocess to qimen-cli.js."""
from datetime import date, datetime

import pytest

from diary import calculate_qimen
from diary.models import QimenResult


def test_calculate_qimen_smoke():
    birth = datetime(1990, 5, 15, 14, 0)
    result = calculate_qimen(birth, date(2026, 5, 15), target_hour=12)

    assert isinstance(result, QimenResult)
    assert len(result.palaces) == 9
    assert result.bestPalace.qualityScore >= result.avoidPalace.qualityScore
    assert 0 <= result.hourStart <= 23
    assert 0 <= result.hourEnd <= 23
    assert result.userGuidance
    assert result.overallQuality in {"excellent", "good", "neutral", "bad"}


def test_palaces_have_directions():
    birth = datetime(1990, 5, 15, 14, 0)
    result = calculate_qimen(birth, date(2026, 5, 15), target_hour=12)

    for p in result.palaces:
        assert p.directionKo, f"palace {p.palaceNum} missing directionKo"
        assert p.gate
        assert p.star


def test_invalid_hour_raises():
    birth = datetime(1990, 5, 15, 14, 0)
    with pytest.raises(ValueError, match="target_hour"):
        calculate_qimen(birth, date(2026, 5, 15), target_hour=24)
