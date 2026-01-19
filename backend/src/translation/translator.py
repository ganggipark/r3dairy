"""
Role Translator
역할별 표현 변환 엔진
"""
import json
from pathlib import Path
from typing import Dict, List, Optional
from copy import deepcopy

from .models import Role, RoleTemplate, TranslationContext
from ..content.models import DailyContent, FocusCaution, ActionGuide, StateTrigger


class RoleTranslator:
    """역할별 콘텐츠 변환기"""

    def __init__(self, templates_dir: Optional[str] = None):
        """
        Args:
            templates_dir: 템플릿 JSON 파일 디렉토리 경로
        """
        if templates_dir is None:
            # 기본 경로: src/translation/templates/
            templates_dir = Path(__file__).parent / "templates"

        self.templates_dir = Path(templates_dir)
        self.templates: Dict[Role, RoleTemplate] = {}
        self._load_templates()

    def _load_templates(self):
        """템플릿 JSON 파일 로드"""
        for role in Role:
            template_path = self.templates_dir / f"{role.value}.json"
            if template_path.exists():
                with open(template_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.templates[role] = RoleTemplate(**data)
            else:
                raise FileNotFoundError(
                    f"Template not found for role '{role.value}': {template_path}"
                )

    def translate(
        self,
        content: DailyContent,
        target_role: Role,
        context: Optional[TranslationContext] = None
    ) -> DailyContent:
        """
        DailyContent를 역할에 맞게 변환

        Args:
            content: 원본 콘텐츠 (중립적 표현)
            target_role: 대상 역할
            context: 변환 컨텍스트 (선택)

        Returns:
            역할에 맞게 변환된 DailyContent
        """
        template = self.templates[target_role]

        # Deep copy to avoid modifying original
        translated = deepcopy(content)

        # 1. Summary 변환
        translated.summary = self._translate_text(
            translated.summary,
            template.expressions
        )

        # 2. Keywords 변환
        translated.keywords = [
            self._translate_text(kw, template.expressions)
            for kw in translated.keywords
        ]

        # 3. Rhythm Description 변환
        translated.rhythm_description = self._translate_text(
            translated.rhythm_description,
            template.expressions
        )

        # 4. Focus/Caution 변환
        translated.focus_caution = FocusCaution(
            focus=[
                self._translate_text(item, template.expressions)
                for item in translated.focus_caution.focus
            ],
            caution=[
                self._translate_text(item, template.expressions)
                for item in translated.focus_caution.caution
            ]
        )

        # 5. Action Guide 변환
        translated.action_guide = ActionGuide(
            do=[
                self._translate_text(item, template.expressions)
                for item in translated.action_guide.do
            ],
            avoid=[
                self._translate_text(item, template.expressions)
                for item in translated.action_guide.avoid
            ]
        )

        # 6. State Trigger는 역할별로 다르게 변환
        translated.state_trigger = self._translate_state_trigger(
            translated.state_trigger,
            template
        )

        # 7. Meaning Shift 변환
        translated.meaning_shift = self._translate_text(
            translated.meaning_shift,
            template.expressions
        )

        # 8. Rhythm Question 변환 (역할별 질문 템플릿 사용)
        translated.rhythm_question = self._translate_question(
            translated.rhythm_question,
            template
        )

        return translated

    def _translate_text(self, text: str, expression_map: Dict[str, str]) -> str:
        """
        텍스트 변환 (표현 매핑 적용)

        Args:
            text: 원본 텍스트
            expression_map: 표현 매핑 사전

        Returns:
            변환된 텍스트
        """
        translated = text
        for internal_expr, role_expr in expression_map.items():
            translated = translated.replace(internal_expr, role_expr)
        return translated

    def _translate_state_trigger(
        self,
        trigger: StateTrigger,
        template: RoleTemplate
    ) -> StateTrigger:
        """
        상태 트리거 변환 (역할별 표현 적용)

        Args:
            trigger: 원본 트리거
            template: 역할 템플릿

        Returns:
            변환된 트리거
        """
        return StateTrigger(
            gesture=self._translate_text(trigger.gesture, template.expressions),
            phrase=self._translate_text(trigger.phrase, template.expressions),
            how_to=self._translate_text(trigger.how_to, template.expressions)
        )

    def _translate_question(
        self,
        question: str,
        template: RoleTemplate
    ) -> str:
        """
        질문 변환 (역할별 질문 템플릿 활용)

        기존 질문이 역할에 잘 맞지 않으면 템플릿 질문으로 대체

        Args:
            question: 원본 질문
            template: 역할 템플릿

        Returns:
            변환된 질문
        """
        # 먼저 표현 매핑 적용
        translated = self._translate_text(question, template.expressions)

        # 역할별 핵심 키워드가 포함되어 있는지 확인
        has_role_context = any(
            keyword in translated
            for keyword in template.action_keywords[:3]  # 상위 3개 키워드
        )

        # 역할 맥락이 없으면 템플릿 질문 사용
        if not has_role_context and template.question_templates:
            # 원본 질문의 의도를 유지하면서 템플릿 질문 선택
            if "마무리" in question or "완료" in question:
                translated = template.question_templates[0]
            elif "목표" in question or "계획" in question:
                translated = template.question_templates[1]
            else:
                translated = template.question_templates[-1]  # 기본 질문

        return translated

    def validate_semantic_preservation(
        self,
        original: DailyContent,
        translated: DailyContent
    ) -> tuple[bool, List[str]]:
        """
        의미 불변성 검증

        원본과 번역본이 의미적으로 동일한지 확인

        Args:
            original: 원본 콘텐츠
            translated: 번역된 콘텐츠

        Returns:
            (검증 통과 여부, 차이점 메시지 리스트)
        """
        issues = []

        # 1. 날짜 동일 확인
        if original.date != translated.date:
            issues.append("날짜가 다릅니다")

        # 2. 키워드 개수 확인
        if len(original.keywords) != len(translated.keywords):
            issues.append(
                f"키워드 개수 불일치: {len(original.keywords)} vs {len(translated.keywords)}"
            )

        # 3. Focus/Caution 개수 확인
        if len(original.focus_caution.focus) != len(translated.focus_caution.focus):
            issues.append("집중 포인트 개수 불일치")
        if len(original.focus_caution.caution) != len(translated.focus_caution.caution):
            issues.append("주의 포인트 개수 불일치")

        # 4. Action Guide 개수 확인
        if len(original.action_guide.do) != len(translated.action_guide.do):
            issues.append("추천 행동 개수 불일치")
        if len(original.action_guide.avoid) != len(translated.action_guide.avoid):
            issues.append("피할 행동 개수 불일치")

        # 5. 콘텐츠 길이 비교 (±20% 이내여야 함)
        orig_len = original.get_total_text_length()
        trans_len = translated.get_total_text_length()
        ratio = abs(trans_len - orig_len) / orig_len

        if ratio > 0.2:
            issues.append(
                f"콘텐츠 길이 차이가 20%를 초과합니다: {orig_len} → {trans_len} ({ratio*100:.1f}%)"
            )

        # 6. 핵심 블록 존재 여부 확인
        if not translated.rhythm_description:
            issues.append("리듬 해설이 비어있습니다")
        if not translated.meaning_shift:
            issues.append("의미 전환이 비어있습니다")
        if not translated.rhythm_question:
            issues.append("리듬 질문이 비어있습니다")

        return (len(issues) == 0, issues)


def translate_content(
    content: DailyContent,
    target_role: Role,
    context: Optional[TranslationContext] = None
) -> DailyContent:
    """
    편의 함수: DailyContent를 역할에 맞게 변환

    Usage:
        from src.content.assembly import create_daily_content
        from src.translation import translate_content, Role

        # 중립적 콘텐츠 생성
        content = create_daily_content(rhythm_signal)

        # 역할별 변환
        student_content = translate_content(content, Role.STUDENT)
        worker_content = translate_content(content, Role.OFFICE_WORKER)
        freelancer_content = translate_content(content, Role.FREELANCER)
    """
    translator = RoleTranslator()
    return translator.translate(content, target_role, context)
