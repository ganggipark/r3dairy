"""M26.1: 시작 문구 안전성 + 페이지 fit."""
import pytest
from diary.content import _ensure_safe_opener, _FORBIDDEN_OPENERS


@pytest.mark.parametrize("text,should_be_modified", [
    ("충은 결단을 부른다.", True),
    ("극이 작동하는 날.", True),
    ("살이 든 날.", True),
    ("형이 겹친다.", True),
    ("천간에 인성이 두텁다.", False),
    ("병자 일주의 흐름이 펼쳐진다.", False),
    ("맑은 새벽처럼 부드러운 시작.", False),
])
def test_opener_safety(text, should_be_modified):
    """금지 단어로 시작 → prefix 부착, 안전 단어 → 변경 없음."""
    out = _ensure_safe_opener(text)
    if should_be_modified:
        assert out != text, f"'{text}'는 prefix 부착되어야 함"
        head = out[:15]
        for w in _FORBIDDEN_OPENERS:
            assert not head.startswith(w), f"여전히 '{w}'로 시작: {head}"
    else:
        assert out == text, f"'{text}'는 변경되면 안 됨"


def test_opener_empty():
    """빈 문자열 안전 처리."""
    assert _ensure_safe_opener("") == ""
    assert _ensure_safe_opener(None) is None


def test_opener_preserves_meaning():
    """prefix 부착 시 원래 내용 보존."""
    text = "충이 강하게 작동하는 날, 결단의 흐름이 펼쳐진다."
    out = _ensure_safe_opener(text)
    assert "결단의 흐름이 펼쳐진다" in out
    assert "충이 강하게 작동하는 날" in out
