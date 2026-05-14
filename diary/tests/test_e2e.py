import pytest

from diary import SajuInput, calculate_saju
from diary.saju import SajuEngineError


def test_e2e_subprocess_smoke():
    """Real node subprocess; no mocks. Verifies the I/O contract end-to-end."""
    result = calculate_saju(
        SajuInput(year=1990, month=5, day=15, hour=14, gender="male")
    )

    assert result.isComplete is True
    assert result.version
    assert result.fullSajuString
    assert len(result.fullSajuString.split()) == 4

    fp = result.fourPillars
    for pillar in (fp.year, fp.month, fp.day, fp.time):
        assert pillar.gan
        assert pillar.ji
        assert pillar.ganJi == pillar.gan + pillar.ji

    extra = result.model_extra or {}
    assert "ohHaeng" in extra
    assert "sipSung" in extra
    assert "gyeokGuk" in extra
    # M21: yongSin promoted from model_extra to explicit YongSinAnalysis field
    assert result.yongSin is not None
    assert result.yongSin.yongSinScore


def test_known_birthdate_pillars():
    """1990-05-15 14:00 male => pillars from prior verified output."""
    result = calculate_saju(
        SajuInput(year=1990, month=5, day=15, hour=14, gender="male")
    )
    assert result.fullSajuString == "경오 신사 경진 계미"
    assert result.fourPillars.year.ganJi == "경오"
    assert result.fourPillars.month.ganJi == "신사"
    assert result.fourPillars.day.ganJi == "경진"
    assert result.fourPillars.time.ganJi == "계미"


def test_env_override_redirects_engine_dir(tmp_path, monkeypatch):
    """SAJU_ENGINE_DIR env var must redirect the subprocess CWD; missing cli.js fails fast."""
    monkeypatch.setenv("SAJU_ENGINE_DIR", str(tmp_path))
    with pytest.raises(SajuEngineError, match="cli.js not found"):
        calculate_saju(
            SajuInput(year=1990, month=5, day=15, hour=14, gender="male")
        )
