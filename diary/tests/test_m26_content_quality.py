"""M26: 콘텐츠 품질 — 조사/영문/일진 자연어."""
import pytest
from diary.content import (
    _josa_iga, _josa_eulreul, _josa_eunneun, _josa_wagwa,
    _sanitize_english, _compute_ilji_relation,
)


@pytest.mark.parametrize("word,expected", [
    ("화", "가"), ("금", "이"), ("목", "이"), ("토", "가"), ("수", "가"),
    ("인", "이"), ("진", "이"), ("오", "가"), ("미", "가"),
    ("자", "가"), ("축", "이"), ("해", "가"),
])
def test_josa_iga(word, expected):
    assert _josa_iga(word) == expected


@pytest.mark.parametrize("word,expected", [
    ("화", "를"), ("금", "을"), ("목", "을"), ("토", "를"), ("수", "를"),
])
def test_josa_eulreul(word, expected):
    assert _josa_eulreul(word) == expected


def test_ilji_no_josa_error():
    """일진 결과에 '화이/금를/수은' 없음."""
    r = _compute_ilji_relation("병", "오", "경", "신")
    text = " ".join(r["relations"])
    assert "화이" not in text
    assert "금를" not in text
    assert "수은" not in text


def test_ilji_japoo_chong():
    """병오 vs 병자 → 자오충."""
    r = _compute_ilji_relation("병", "오", "병", "자")
    text = " ".join(r["relations"])
    assert "충" in text


@pytest.mark.parametrize("text,forbidden", [
    ("time-blocking 기법", "time-blocking"),
    ("Implementation Intention 활용", "implementation"),
    ("Deep Work 시간", "deep work"),
    ("body scan을", "body scan"),
])
def test_sanitize_removes_english(text, forbidden):
    out = _sanitize_english(text)
    assert forbidden.lower() not in out.lower()


def test_sanitize_replaces_korean():
    out = _sanitize_english("time-blocking 30분")
    assert "시간 구획 관리" in out


def test_sanitize_parenthetical():
    out = _sanitize_english("몰입 작업 (Deep Work)")
    assert "Deep Work" not in out


def test_sanitize_pure_korean_unchanged():
    text = "오늘은 차분히 사고에 집중하세요."
    assert _sanitize_english(text) == text
