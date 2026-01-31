"""
Tests for Character Count Optimizer

Tests character count validation for content blocks and page layout.
"""

import pytest
from src.content.char_optimizer import CharOptimizer, BLOCK_CHAR_TARGETS, TOTAL_LEFT_PAGE_TARGET


class TestCharOptimizer:
    """Test CharOptimizer validation methods."""

    def test_validate_block_within_range(self):
        """Test validation passes when character count is within range."""
        # summary target: min=30, max=80, target=50
        text = "오늘은 매우 활기찬 에너지와 균형의 흐름이 함께하는 날입니다."  # ~35 chars
        is_valid, actual_count, target_range = CharOptimizer.validate_block("summary", text)

        assert is_valid is True
        assert actual_count == len(text)
        assert target_range == BLOCK_CHAR_TARGETS["summary"]

    def test_validate_block_too_short(self):
        """Test validation fails when text is too short."""
        # summary min=30
        text = "짧은 요약"  # ~5 chars
        is_valid, actual_count, target_range = CharOptimizer.validate_block("summary", text)

        assert is_valid is False
        assert actual_count < target_range["min"]

    def test_validate_block_too_long(self):
        """Test validation fails when text is too long."""
        # summary max=80
        text = "매우 긴 요약입니다. " * 10  # Much longer than 80
        is_valid, actual_count, target_range = CharOptimizer.validate_block("summary", text)

        assert is_valid is False
        assert actual_count > target_range["max"]

    def test_validate_block_unknown_type(self):
        """Test validation passes for unknown block type."""
        text = "알 수 없는 블록 타입"
        is_valid, actual_count, target_range = CharOptimizer.validate_block("unknown_block", text)

        assert is_valid is True  # Unknown blocks should not block validation
        assert actual_count == len(text)

    def test_validate_page_all_blocks_valid(self):
        """Test full page validation when all blocks are valid."""
        content = {
            "summary": "오늘은 매우 활기찬 에너지와 균형의 흐름이 함께하는 날입니다.",  # ~35
            "keywords": ["집중", "균형", "성장", "휴식"],  # ~12
            "rhythm_description": "오늘의 리듬은 균형을 중심으로 흐릅니다. " * 10,  # ~250
            "focus_caution": {
                "focus": ["집중 시간 확보", "중요한 결정"],
                "caution": ["과도한 긴장", "무리한 일정"]
            },  # ~48
            "action_guide": {
                "do": ["아침에 계획 세우기", "중요한 일 먼저 처리", "충분한 휴식"],
                "avoid": ["밤샘 작업", "갑작스런 결정"]
            },  # ~60
            "time_direction": {
                "good_time": "오전 9-11시",
                "avoid_time": "오후 5-7시",
                "good_direction": "북동쪽",
                "avoid_direction": "반대쪽",
                "notes": "집중이 필요한 활동은 좋은 시간대에 하세요."
            },  # ~60
            "state_trigger": {
                "gesture": "양손을 가슴에 대고 천천히 호흡하세요",
                "phrase": "지금 이 순간, 나는 충분히 잘하고 있습니다",
                "how_to": "긴장되거나 불안할 때 이 동작을 3번 반복하세요"
            },  # ~72
            "meaning_shift": "오늘은 균형 잡힌 에너지가 흐르는 날입니다. " * 5,  # ~125
            "rhythm_question": "오늘 가장 중요한 한 가지는 무엇인가요?"  # ~25
        }

        is_valid, total_chars, issues = CharOptimizer.validate_page(content)

        # Should be valid if total is within 400-1200 range
        assert total_chars >= TOTAL_LEFT_PAGE_TARGET["min"]
        assert total_chars <= TOTAL_LEFT_PAGE_TARGET["max"]

    def test_validate_page_missing_block(self):
        """Test validation detects missing blocks."""
        content = {
            "summary": "오늘은 매우 활기찬 에너지와 균형의 흐름이 함께하는 날입니다.",
            # Missing other required blocks
        }

        is_valid, total_chars, issues = CharOptimizer.validate_page(content)

        assert is_valid is False
        assert len(issues) > 0
        # Should have issues for missing blocks
        missing_issues = [i for i in issues if i.get("issue") == "missing_block"]
        assert len(missing_issues) > 0

    def test_validate_page_total_too_short(self):
        """Test validation detects when total page is too short."""
        content = {
            "summary": "짧은 요약",
            "keywords": ["키워드"],
            "rhythm_description": "짧은 설명",
            "focus_caution": {"focus": ["집중"], "caution": ["주의"]},
            "action_guide": {"do": ["하기"], "avoid": ["피하기"]},
            "time_direction": {
                "good_time": "오전",
                "avoid_time": "오후",
                "good_direction": "북",
                "avoid_direction": "남",
                "notes": "노트"
            },
            "state_trigger": {
                "gesture": "동작",
                "phrase": "문구",
                "how_to": "방법"
            },
            "meaning_shift": "의미",
            "rhythm_question": "질문?"
        }

        is_valid, total_chars, issues = CharOptimizer.validate_page(content)

        assert is_valid is False
        assert total_chars < TOTAL_LEFT_PAGE_TARGET["min"]
        # Should have issue for total page being too short
        total_issues = [i for i in issues if i.get("block") == "total_page"]
        assert len(total_issues) > 0

    def test_calculate_block_chars_string(self):
        """Test character calculation for string content."""
        text = "테스트 문자열"
        chars = CharOptimizer._calculate_block_chars(text)
        assert chars == len(text)

    def test_calculate_block_chars_list(self):
        """Test character calculation for list content."""
        keywords = ["키워드1", "키워드2", "키워드3"]
        chars = CharOptimizer._calculate_block_chars(keywords)
        expected = sum(len(k) for k in keywords)
        assert chars == expected

    def test_calculate_block_chars_dict(self):
        """Test character calculation for dict content."""
        focus_caution = {
            "focus": ["집중1", "집중2"],
            "caution": ["주의1", "주의2"]
        }
        chars = CharOptimizer._calculate_block_chars(focus_caution)
        expected = len("집중1") + len("집중2") + len("주의1") + len("주의2")
        assert chars == expected

    def test_suggest_adjustment_too_short(self):
        """Test adjustment suggestion for short content."""
        suggestion = CharOptimizer.suggest_adjustment("summary", 20)
        assert "부족" in suggestion
        assert "30" in suggestion  # min for summary

    def test_suggest_adjustment_too_long(self):
        """Test adjustment suggestion for long content."""
        suggestion = CharOptimizer.suggest_adjustment("summary", 100)
        assert "초과" in suggestion
        assert "80" in suggestion  # max for summary

    def test_suggest_adjustment_near_target(self):
        """Test adjustment suggestion when near target."""
        suggestion = CharOptimizer.suggest_adjustment("summary", 50)
        assert "목표 범위" in suggestion

    def test_suggest_adjustment_unknown_block(self):
        """Test adjustment suggestion for unknown block type."""
        suggestion = CharOptimizer.suggest_adjustment("unknown", 100)
        assert "알 수 없는" in suggestion

    def test_get_block_target(self):
        """Test getting target range for block type."""
        target = CharOptimizer.get_block_target("summary")
        assert target is not None
        assert "min" in target
        assert "max" in target
        assert "target" in target

        unknown = CharOptimizer.get_block_target("unknown")
        assert unknown is None

    def test_get_page_target(self):
        """Test getting total page target range."""
        target = CharOptimizer.get_page_target()
        assert target is not None
        assert target["min"] == 400
        assert target["max"] == 1200
        assert target["target"] == 1000


class TestBlockCharTargets:
    """Test BLOCK_CHAR_TARGETS configuration."""

    def test_all_blocks_have_targets(self):
        """Test all required blocks have character targets defined."""
        required_blocks = [
            "summary",
            "keywords",
            "rhythm_description",
            "focus_caution",
            "action_guide",
            "time_direction",
            "state_trigger",
            "meaning_shift",
            "rhythm_question",
        ]

        for block in required_blocks:
            assert block in BLOCK_CHAR_TARGETS
            target = BLOCK_CHAR_TARGETS[block]
            assert "min" in target
            assert "max" in target
            assert "target" in target
            assert target["min"] <= target["target"] <= target["max"]

    def test_total_targets_sum_reasonable(self):
        """Test that sum of all block targets is reasonable."""
        total_target = sum(t["target"] for t in BLOCK_CHAR_TARGETS.values())
        # Should be close to page target (1000)
        assert 800 <= total_target <= 1200

    def test_page_target_configured(self):
        """Test total page target is configured correctly."""
        assert TOTAL_LEFT_PAGE_TARGET["min"] == 400
        assert TOTAL_LEFT_PAGE_TARGET["max"] == 1200
        assert TOTAL_LEFT_PAGE_TARGET["target"] == 1000
