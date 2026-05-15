"""M26.2: sanitize 중복 제거 + 의문형 보정."""
import pytest
from diary.content import _sanitize_english, _ensure_question_form


def test_sanitize_no_korean_duplication():
    """'urge surfing(충동 관찰)' → '충동 관찰' (괄호 영문 제거 우선)."""
    out = _sanitize_english("urge surfing(충동 관찰) 기법")
    assert out.count("충동 관찰") == 1, f"중복: {out}"


def test_sanitize_parenthetical_removed_first():
    """괄호 영문이 영문 치환보다 먼저 제거됨."""
    out = _sanitize_english("몰입 작업 (Deep Work)을 권장")
    assert "Deep Work" not in out
    assert out.count("몰입 작업") == 1


def test_sanitize_korean_paren_duplicate():
    """이미 한글로 중복된 'X(X)' 패턴도 정리."""
    out = _sanitize_english("마음챙김(마음챙김) 연습")
    assert out.count("마음챙김") == 1


@pytest.mark.parametrize("text,expected_endswith", [
    ("어떻게 활용하셨는지 돌아보세요.", "?"),
    ("오늘 어떤 결정을 미루셨나요?", "?"),
    ("자기 자비를 발휘하셨나요?", "?"),
    ("성장의 기회를 찾으셨다.", "?"),
    ("외부의 기대와 내 진짜 선택 사이 어디에 있었나요?", "?"),
])
def test_ensure_question_form_endings(text, expected_endswith):
    out = _ensure_question_form(text)
    assert out.endswith(expected_endswith), f"'{text}' → '{out}'"


def test_ensure_question_form_preserves_content():
    """원본 의미 보존."""
    text = "오늘 어떤 결정을 미루며 에너지를 보존하셨나요?"
    assert _ensure_question_form(text) == text


def test_ensure_question_form_command_to_question():
    """돌아보세요 → 어떠셨나요?"""
    out = _ensure_question_form("인시의 몰입 시간을 돌아보세요.")
    assert "?" in out
    assert "돌아보세요" not in out
