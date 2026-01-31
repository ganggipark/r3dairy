"""
Base Translator - 역할별 번역기의 기본 클래스
"""
from abc import ABC, abstractmethod
from copy import deepcopy
from typing import Dict, List, Tuple, Any

from ..models import RoleAdaptationRules, TranslationContext, TranslationResult


class BaseTranslator(ABC):
    """역할별 콘텐츠 번역기 기본 클래스"""

    def __init__(self, role: str):
        self.role = role
        self.vocabulary = self._load_vocabulary()
        self.rules = self._load_rules()

    @abstractmethod
    def _load_vocabulary(self) -> Dict[str, str]:
        """역할별 어휘 매핑 로드"""
        pass

    @abstractmethod
    def _load_rules(self) -> RoleAdaptationRules:
        """역할별 적응 규칙 로드"""
        pass

    def translate_content_block(
        self,
        block_type: str,
        original_content: str,
        context: TranslationContext,
    ) -> Tuple[bool, str, List[str]]:
        """
        단일 콘텐츠 블록 번역.
        Returns (success, translated_text, issues)
        """
        issues: List[str] = []
        translated = self._apply_vocabulary_mapping(original_content)
        translated = self._adjust_tone(translated)

        # forbidden term check
        for term in self.rules.forbidden_terms:
            if term in translated:
                issues.append(f"금지 용어 발견: '{term}' in {block_type}")

        return (len(issues) == 0, translated, issues)

    def translate_daily_content(
        self,
        content: Dict[str, Any],
        context: TranslationContext,
    ) -> Tuple[bool, Dict[str, Any], List[str]]:
        """
        전체 일간 콘텐츠 번역.
        Returns (success, translated_content, issues)
        """
        translated = deepcopy(content)
        all_issues: List[str] = []
        expr_map = self.vocabulary

        # Text fields
        _text_fields = ["summary", "rhythm_description", "meaning_shift", "rhythm_question"]
        for field in _text_fields:
            if field in translated and isinstance(translated[field], str):
                ok, txt, issues = self.translate_content_block(field, translated[field], context)
                translated[field] = txt
                all_issues.extend(issues)

        # List-of-string fields in nested dicts
        _nested_list_fields = {
            "focus_caution": ["focus", "caution"],
            "action_guide": ["do", "avoid"],
        }
        for parent, children in _nested_list_fields.items():
            if parent in translated and isinstance(translated[parent], dict):
                for child in children:
                    if child in translated[parent]:
                        translated[parent][child] = [
                            self._apply_vocabulary_mapping(item)
                            for item in translated[parent][child]
                        ]

        # Keywords
        if "keywords" in translated and isinstance(translated["keywords"], list):
            translated["keywords"] = [
                self._apply_vocabulary_mapping(kw) for kw in translated["keywords"]
            ]

        # Time/direction notes
        if "time_direction" in translated and isinstance(translated["time_direction"], dict):
            if "notes" in translated["time_direction"]:
                translated["time_direction"]["notes"] = self._apply_vocabulary_mapping(
                    translated["time_direction"]["notes"]
                )

        # State trigger
        if "state_trigger" in translated and isinstance(translated["state_trigger"], dict):
            for key in ["gesture", "phrase", "how_to"]:
                if key in translated["state_trigger"]:
                    translated["state_trigger"][key] = self._apply_vocabulary_mapping(
                        translated["state_trigger"][key]
                    )

        # Lifestyle categories (10 categories) - translate explanation fields
        _lifestyle_categories = [
            "daily_health_sports", "daily_meal_nutrition", "daily_fashion_beauty",
            "daily_shopping_finance", "daily_living_space", "daily_routines",
            "digital_communication", "hobbies_creativity", "relationships_social",
            "seasonal_environment",
        ]
        for cat in _lifestyle_categories:
            if cat in translated and isinstance(translated[cat], dict):
                if "explanation" in translated[cat]:
                    translated[cat]["explanation"] = self._apply_vocabulary_mapping(
                        translated[cat]["explanation"]
                    )
                # Translate all list-of-string sub-fields
                for k, v in translated[cat].items():
                    if isinstance(v, list) and v and isinstance(v[0], str):
                        translated[cat][k] = [
                            self._apply_vocabulary_mapping(item) for item in v
                        ]

        # Forbidden term final sweep
        forbidden_issues = self._check_forbidden_terms(translated)
        all_issues.extend(forbidden_issues)

        success = len(all_issues) == 0
        return (success, translated, all_issues)

    def _apply_vocabulary_mapping(self, text: str) -> str:
        """어휘 매핑 적용 (긴 표현 우선)"""
        # Sort by length descending to avoid partial matches
        sorted_vocab = sorted(
            self.vocabulary.items(),
            key=lambda x: len(x[0]),
            reverse=True,
        )
        result = text
        for original, replacement in sorted_vocab:
            result = result.replace(original, replacement)
        return result

    def _adjust_tone(self, text: str) -> str:
        """톤 조정 (서브클래스에서 오버라이드 가능)"""
        return text

    def _check_forbidden_terms(self, content: Dict[str, Any]) -> List[str]:
        """금지 용어 검사"""
        issues: List[str] = []
        text_blob = _extract_all_text(content)
        for term in self.rules.forbidden_terms:
            if term in text_blob:
                issues.append(f"금지 용어 '{term}' 발견 (역할: {self.role})")
        return issues

    def validate_translation(
        self,
        original: Dict[str, Any],
        translated: Dict[str, Any],
    ) -> TranslationResult:
        """번역 품질 검증"""
        issues: List[str] = []

        # Structure check
        orig_keys = set(original.keys())
        trans_keys = set(translated.keys())
        missing = orig_keys - trans_keys
        if missing:
            issues.append(f"누락된 필드: {missing}")

        # Forbidden terms
        issues.extend(self._check_forbidden_terms(translated))

        # Length ratio check
        orig_len = len(_extract_all_text(original))
        trans_len = len(_extract_all_text(translated))
        if orig_len > 0:
            ratio = abs(trans_len - orig_len) / orig_len
            if ratio > 0.3:
                issues.append(
                    f"콘텐츠 길이 차이 {ratio*100:.1f}% (허용: 30%)"
                )

        score = max(0.0, 1.0 - len(issues) * 0.2)

        return TranslationResult(
            success=len(issues) == 0,
            translated_content=translated,
            semantic_preserved=len(issues) == 0,
            tone_matched=True,
            role_alignment_score=score,
            issues=issues,
            mapping_used=self.vocabulary,
        )


def _extract_all_text(content: Dict[str, Any]) -> str:
    """딕셔너리에서 모든 텍스트 추출"""
    parts: List[str] = []

    def _recurse(obj: Any) -> None:
        if isinstance(obj, str):
            parts.append(obj)
        elif isinstance(obj, list):
            for item in obj:
                _recurse(item)
        elif isinstance(obj, dict):
            for v in obj.values():
                _recurse(v)

    _recurse(content)
    return " ".join(parts)
