"""
Character Count Optimizer for Page Layout

Optimizes content block character counts to ensure proper A5 page layout.
Validates per-block and total page character counts against configurable targets.
"""

from typing import Dict, Any, List, Tuple, Optional


# Per-block character count targets for A5 left page
# Target: ~1000 chars total (fits A5 left page with 10pt font, ~45 chars/line, ~50 lines)
BLOCK_CHAR_TARGETS = {
    "summary": {"min": 30, "max": 80, "target": 50},
    "keywords": {"min": 15, "max": 50, "target": 30},  # comma-separated
    "rhythm_description": {"min": 200, "max": 400, "target": 300},
    "focus_caution": {"min": 60, "max": 150, "target": 100},
    "action_guide": {"min": 80, "max": 200, "target": 140},
    "time_direction": {"min": 60, "max": 150, "target": 100},
    "state_trigger": {"min": 40, "max": 120, "target": 80},
    "meaning_shift": {"min": 80, "max": 250, "target": 160},
    "rhythm_question": {"min": 20, "max": 60, "target": 40},
}

# Total left page character count target
TOTAL_LEFT_PAGE_TARGET = {"min": 400, "max": 1200, "target": 1000}


class CharOptimizer:
    """Character count optimizer for page layout validation."""

    @staticmethod
    def validate_block(block_type: str, text: str) -> Tuple[bool, int, Dict[str, int]]:
        """
        Validate character count for a single content block.

        Args:
            block_type: Type of content block (e.g., "summary", "rhythm_description")
            text: The text content to validate

        Returns:
            Tuple of (is_valid, actual_count, target_range)
            - is_valid: True if character count is within min/max range
            - actual_count: Actual character count
            - target_range: Dict with min/max/target values for this block type
        """
        if block_type not in BLOCK_CHAR_TARGETS:
            # Unknown block type - return True to avoid blocking
            return True, len(text), {"min": 0, "max": 999999, "target": 0}

        actual_count = len(text)
        target_range = BLOCK_CHAR_TARGETS[block_type]

        is_valid = target_range["min"] <= actual_count <= target_range["max"]

        return is_valid, actual_count, target_range

    @staticmethod
    def validate_page(content: Dict[str, Any]) -> Tuple[bool, int, List[Dict[str, Any]]]:
        """
        Validate total character count for entire left page.

        Args:
            content: Daily content dictionary with all blocks

        Returns:
            Tuple of (is_valid, total_chars, issues_list)
            - is_valid: True if total character count is within min/max range
            - total_chars: Total character count for left page
            - issues_list: List of validation issues (if any)
        """
        issues = []
        total_chars = 0

        # Validate each block
        block_mappings = {
            "summary": "summary",
            "keywords": "keywords",
            "rhythm_description": "rhythm_description",
            "focus_caution": "focus_caution",
            "action_guide": "action_guide",
            "time_direction": "time_direction",
            "state_trigger": "state_trigger",
            "meaning_shift": "meaning_shift",
            "rhythm_question": "rhythm_question",
        }

        for block_type, content_key in block_mappings.items():
            if content_key not in content:
                issues.append({
                    "block": block_type,
                    "issue": "missing_block",
                    "message": f"블록 '{block_type}'이(가) 누락되었습니다"
                })
                continue

            # Calculate character count based on content type
            block_content = content[content_key]
            block_chars = CharOptimizer._calculate_block_chars(block_content)

            # Validate block
            is_valid, actual_count, target_range = CharOptimizer.validate_block(
                block_type, "x" * block_chars  # Use dummy string of correct length
            )

            if not is_valid:
                issues.append({
                    "block": block_type,
                    "issue": "char_count_out_of_range",
                    "actual": actual_count,
                    "min": target_range["min"],
                    "max": target_range["max"],
                    "target": target_range["target"],
                    "message": f"블록 '{block_type}': {actual_count}자 (목표: {target_range['min']}-{target_range['max']}자)"
                })

            total_chars += block_chars

        # Validate total page count
        page_target = TOTAL_LEFT_PAGE_TARGET
        page_valid = page_target["min"] <= total_chars <= page_target["max"]

        if not page_valid:
            issues.append({
                "block": "total_page",
                "issue": "total_char_count_out_of_range",
                "actual": total_chars,
                "min": page_target["min"],
                "max": page_target["max"],
                "target": page_target["target"],
                "message": f"전체 페이지: {total_chars}자 (목표: {page_target['min']}-{page_target['max']}자)"
            })

        is_valid = len(issues) == 0
        return is_valid, total_chars, issues

    @staticmethod
    def _calculate_block_chars(content: Any) -> int:
        """
        Calculate character count for various content types.

        Args:
            content: Content can be str, list, or dict

        Returns:
            Total character count
        """
        if isinstance(content, str):
            return len(content)
        elif isinstance(content, list):
            # For lists (e.g., keywords), sum all string lengths
            total = 0
            for item in content:
                if isinstance(item, str):
                    total += len(item)
            return total
        elif isinstance(content, dict):
            # For dicts (e.g., focus_caution, action_guide), sum all values
            total = 0
            for value in content.values():
                if isinstance(value, str):
                    total += len(value)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, str):
                            total += len(item)
            return total
        else:
            return 0

    @staticmethod
    def suggest_adjustment(block_type: str, current_len: int) -> str:
        """
        Suggest adjustment for a block that's out of range.

        Args:
            block_type: Type of content block
            current_len: Current character count

        Returns:
            Suggestion message in Korean
        """
        if block_type not in BLOCK_CHAR_TARGETS:
            return "알 수 없는 블록 타입입니다."

        target_range = BLOCK_CHAR_TARGETS[block_type]
        target = target_range["target"]
        min_val = target_range["min"]
        max_val = target_range["max"]

        if current_len < min_val:
            shortage = min_val - current_len
            return f"'{block_type}' 블록이 {shortage}자 부족합니다. 최소 {min_val}자 필요 (목표: {target}자)"
        elif current_len > max_val:
            excess = current_len - max_val
            return f"'{block_type}' 블록이 {excess}자 초과합니다. 최대 {max_val}자 (목표: {target}자)"
        else:
            diff = abs(current_len - target)
            if diff > target * 0.2:  # More than 20% away from target
                if current_len < target:
                    return f"'{block_type}' 블록을 {target - current_len}자 더 추가하면 목표({target}자)에 가까워집니다."
                else:
                    return f"'{block_type}' 블록을 {current_len - target}자 줄이면 목표({target}자)에 가까워집니다."
            else:
                return f"'{block_type}' 블록이 목표 범위 내에 있습니다."

    @staticmethod
    def get_block_target(block_type: str) -> Optional[Dict[str, int]]:
        """
        Get target character count range for a block type.

        Args:
            block_type: Type of content block

        Returns:
            Dict with min/max/target values, or None if block type not found
        """
        return BLOCK_CHAR_TARGETS.get(block_type)

    @staticmethod
    def get_page_target() -> Dict[str, int]:
        """
        Get target character count range for total page.

        Returns:
            Dict with min/max/target values
        """
        return TOTAL_LEFT_PAGE_TARGET.copy()
