"""
Content Assembly Engine
RhythmSignal (내부 표현) → DailyContent (사용자 노출)

⚠️ 핵심 역할:
1. 내부 전문 용어를 일반 언어로 변환
2. 10개 블록 생성 (요약, 키워드, 해설, 집중/주의, Do/Avoid, 시간/방향, 트리거, 의미전환, 질문)
3. 최소 400-600자 콘텐츠 생성
4. 설명형 문단 포함 (카드 전용 요약 금지)
"""
from typing import List, Dict, Any
from ..rhythm.models import RhythmSignal, MonthlyRhythmSignal, YearlyRhythmSignal
from .models import (
    DailyContent,
    FocusCaution,
    ActionGuide,
    TimeDirection,
    StateTrigger,
    MonthlyContent,
    YearlyContent
)


class ContentAssembler:
    """콘텐츠 조립기 - 내부 신호를 사용자 콘텐츠로 변환"""

    def __init__(self):
        self.version = "1.0.0"

    def assemble_daily_content(self, signal: RhythmSignal) -> DailyContent:
        """
        RhythmSignal → DailyContent 변환

        Args:
            signal: 리듬 신호 (내부 표현, 전문 용어 포함)

        Returns:
            DailyContent: 사용자 노출 콘텐츠 (일반 언어)
        """
        # 1. 요약 생성
        summary = self._generate_summary(signal)

        # 2. 키워드 추출
        keywords = self._generate_keywords(signal)

        # 3. 리듬 해설 (설명형 문단)
        rhythm_description = self._generate_rhythm_description(signal)

        # 4. 집중/주의 포인트
        focus_caution = self._generate_focus_caution(signal)

        # 5. 행동 가이드 (Do/Avoid)
        action_guide = self._generate_action_guide(signal)

        # 6. 시간/방향
        time_direction = self._generate_time_direction(signal)

        # 7. 상태 트리거
        state_trigger = self._generate_state_trigger(signal)

        # 8. 의미 전환
        meaning_shift = self._generate_meaning_shift(signal)

        # 9. 리듬 질문
        rhythm_question = self._generate_rhythm_question(signal)

        # DailyContent 객체 생성
        content = DailyContent(
            date=signal.date,
            summary=summary,
            keywords=keywords,
            rhythm_description=rhythm_description,
            focus_caution=focus_caution,
            action_guide=action_guide,
            time_direction=time_direction,
            state_trigger=state_trigger,
            meaning_shift=meaning_shift,
            rhythm_question=rhythm_question
        )

        return content

    # ========================================================================
    # 블록 생성 함수
    # ========================================================================

    def _generate_summary(self, signal: RhythmSignal) -> str:
        """
        1. 요약 생성 (30-200자)

        내부 용어 → 사용자 용어:
        - "안정과 정리" → "오늘은 차분한 에너지가 흐르는 날"
        """
        # 에너지 레벨에 따른 기본 톤
        if signal.energy_level >= 4:
            energy_desc = "활기찬 에너지가 흐르는"
        elif signal.energy_level >= 3:
            energy_desc = "안정적인 에너지가 있는"
        else:
            energy_desc = "차분한 에너지가 흐르는"

        # 주요 테마 변환 (내부 표현 → 사용자 언어)
        theme = self._translate_theme(signal.main_theme)

        summary = f"오늘은 {energy_desc} 날입니다. {theme}에 집중하면 좋습니다."

        # 기회 요소 추가
        if signal.opportunities:
            opportunity = self._translate_term(signal.opportunities[0])
            summary += f" {opportunity}의 기회가 있습니다."

        return summary

    def _generate_keywords(self, signal: RhythmSignal) -> List[str]:
        """
        2. 키워드 추출 (2-5개)

        내부 표현에서 사용자 친화적 키워드 생성
        """
        keywords = []

        # 에너지 레벨 기반 키워드
        if signal.energy_level >= 4:
            keywords.append("활력")
        elif signal.energy_level >= 3:
            keywords.append("안정")
        else:
            keywords.append("차분")

        # 집중력 기반 키워드
        if signal.focus_capacity >= 4:
            keywords.append("집중")

        # 기회/도전 요소에서 키워드 추출
        for opp in signal.opportunities[:2]:
            translated = self._translate_term(opp)
            if translated not in keywords:
                keywords.append(translated)

        # 2-5개 범위로 조정
        return keywords[:5] if len(keywords) >= 2 else keywords + ["흐름", "리듬"]

    def _generate_rhythm_description(self, signal: RhythmSignal) -> str:
        """
        3. 리듬 해설 (100-500자, 설명형 문단)

        ⚠️ 중요: 카드 전용 요약 금지, 설명형 문단 필수
        """
        desc_parts = []

        # 전체 흐름 설명
        desc_parts.append(
            f"오늘의 리듬은 {self._get_energy_description(signal.energy_level)}입니다. "
        )

        # 에너지 방향 설명
        if signal.energy_level >= 4:
            desc_parts.append(
                "외부로 향하는 에너지가 강해 활동적인 일이나 사람들과의 교류에 적합합니다. "
            )
        elif signal.energy_level >= 3:
            desc_parts.append(
                "에너지가 균형을 이루어 계획적인 실행과 조율에 좋은 흐름입니다. "
            )
        else:
            desc_parts.append(
                "에너지가 내부로 향하며, 정리나 내면 성찰에 적합한 흐름입니다. "
            )

        # 집중력 설명
        if signal.focus_capacity >= 4:
            desc_parts.append(
                "집중력이 높아 중요한 작업이나 학습에 몰입하기 좋습니다. "
            )
        elif signal.focus_capacity >= 2:
            desc_parts.append(
                "집중력은 보통 수준이므로, 짧은 단위로 작업을 나누어 진행하세요. "
            )
        else:
            desc_parts.append(
                "집중이 쉽게 흐트러질 수 있으니, 단순하고 반복적인 작업부터 시작하세요. "
            )

        # 주요 테마 설명
        theme_explanation = self._explain_theme(signal.main_theme)
        desc_parts.append(theme_explanation)

        # 결합
        description = "".join(desc_parts)

        # 최소 100자 보장
        if len(description) < 100:
            description += " 오늘의 리듬을 이해하고 그에 맞춰 하루를 계획하면, 더 편안하고 효율적인 시간을 보낼 수 있습니다."

        return description

    def _generate_focus_caution(self, signal: RhythmSignal) -> FocusCaution:
        """4. 집중/주의 포인트"""
        focus = []
        caution = []

        # 기회 요소 → 집중 포인트
        for opp in signal.opportunities:
            translated = self._translate_term(opp)
            focus.append(translated)

        # 도전 요소 → 주의 포인트
        for challenge in signal.challenges:
            translated = self._translate_term(challenge)
            caution.append(f"{translated} 주의")

        # 에너지 레벨 기반 추가
        if signal.energy_level >= 4:
            focus.append("활동적인 일")
        else:
            focus.append("정리 및 마무리")
            caution.append("새로운 시작")

        return FocusCaution(focus=focus, caution=caution)

    def _generate_action_guide(self, signal: RhythmSignal) -> ActionGuide:
        """5. 행동 가이드 (Do/Avoid)"""
        do = []
        avoid = []

        # 에너지 레벨 기반
        if signal.energy_level >= 4:
            do.extend(["활발한 교류", "새로운 시도", "외출"])
            avoid.extend(["혼자 고립", "미루기"])
        elif signal.energy_level >= 3:
            do.extend(["계획 실행", "조율", "정리"])
            avoid.extend(["과도한 약속", "무리한 일정"])
        else:
            do.extend(["내면 성찰", "휴식", "마무리"])
            avoid.extend(["큰 결정", "중요한 계약", "충동 행동"])

        # 집중력 기반
        if signal.focus_capacity >= 4:
            do.append("중요한 작업 우선")
        else:
            do.append("단순 작업부터 시작")
            avoid.append("복잡한 의사결정")

        return ActionGuide(do=do, avoid=avoid)

    def _generate_time_direction(self, signal: RhythmSignal) -> TimeDirection:
        """6. 시간/방향 정보"""
        # 유리한 시간 (내부 표현 → 사용자 언어)
        good_times = signal.favorable_times if signal.favorable_times else ["오전 9-12시"]
        good_time = ", ".join(good_times)

        # 주의 시간
        caution_times = signal.caution_times if signal.caution_times else ["오후 늦은 시간"]
        avoid_time = ", ".join(caution_times)

        # 방향 (내부 표현 그대로 사용 가능)
        good_directions = signal.favorable_directions if signal.favorable_directions else ["북쪽", "동쪽"]
        good_direction = ", ".join(good_directions)
        avoid_direction = "정해진 방향 없음"

        notes = f"집중이 필요한 작업은 {good_times[0] if good_times else '오전'} 시간대에 하세요."

        return TimeDirection(
            good_time=good_time,
            avoid_time=avoid_time,
            good_direction=good_direction,
            avoid_direction=avoid_direction,
            notes=notes
        )

    def _generate_state_trigger(self, signal: RhythmSignal) -> StateTrigger:
        """7. 상태 트리거 (페이스 조절 기법)"""
        # 에너지/감정 상태에 따라 다른 트리거 제공
        if signal.energy_level >= 4:
            gesture = "양손을 위로 올려 스트레칭"
            phrase = "지금 내 에너지는 충분하다"
            how_to = "과도한 흥분을 느낄 때 천천히 3번 반복하세요"
        elif signal.energy_level >= 2:
            gesture = "양손을 가슴에 모으고 천천히 호흡"
            phrase = "지금 이 순간, 나는 충분히 잘하고 있다"
            how_to = "불안감이 올라올 때 3번 반복하세요"
        else:
            gesture = "발을 땅에 단단히 딛고 서기"
            phrase = "나는 내 페이스로 나아간다"
            how_to = "무기력감을 느낄 때 실천하세요"

        return StateTrigger(gesture=gesture, phrase=phrase, how_to=how_to)

    def _generate_meaning_shift(self, signal: RhythmSignal) -> str:
        """8. 의미 전환 (50-300자)"""
        # 에너지 레벨에 따른 재해석
        if signal.energy_level >= 4:
            return (
                "오늘의 높은 에너지는 '조급함'이 아니라 '추진력'입니다. "
                "많은 일을 해내고 싶은 마음을 긍정적으로 활용하되, "
                "과도한 약속이나 무리는 피하세요."
            )
        elif signal.energy_level >= 2:
            return (
                "오늘의 안정적인 에너지는 '평범함'이 아니라 '균형'입니다. "
                "급하게 밀어붙이지 않고도 차근차근 나아갈 수 있는 날입니다."
            )
        else:
            return (
                "오늘의 차분한 에너지는 '무기력'이 아니라 '내면 충전'의 시간입니다. "
                "급하지 않게 한 걸음씩 나아가는 것이 오늘의 지혜입니다."
            )

    def _generate_rhythm_question(self, signal: RhythmSignal) -> str:
        """9. 리듬 질문 (20-150자)"""
        # 에너지와 집중력에 따른 질문
        if signal.energy_level >= 4:
            return "오늘의 높은 에너지를 어떤 일에 쓰고 싶나요? 그것을 하면 어떤 기분이 들까요?"
        elif signal.focus_capacity >= 4:
            return "오늘 집중해서 완성하고 싶은 한 가지는 무엇인가요?"
        else:
            return "오늘은 어떤 작은 일을 마무리하고 싶나요? 그것을 완성하면 어떤 기분이 들까요?"

    # ========================================================================
    # 내부 용어 → 사용자 용어 변환 헬퍼 함수
    # ========================================================================

    def _translate_theme(self, internal_theme: str) -> str:
        """주요 테마 번역"""
        theme_map = {
            "안정과 정리": "정리와 마무리",
            "확장과 도전": "새로운 시도",
            "내면과 휴식": "휴식과 성찰",
            "관계와 소통": "사람들과의 교류",
            "집중과 실행": "계획 실행"
        }
        return theme_map.get(internal_theme, "균형과 조화")

    def _translate_term(self, internal_term: str) -> str:
        """개별 용어 번역"""
        term_map = {
            "관계 강화": "관계",
            "학습": "공부",
            "충동 조절": "감정 조절",
            "결정": "선택",
            "정리": "마무리",
            "휴식": "쉬기",
            "창작": "만들기"
        }
        return term_map.get(internal_term, internal_term)

    def _get_energy_description(self, level: int) -> str:
        """에너지 레벨 설명"""
        if level >= 4:
            return "활기차고 역동적"
        elif level >= 3:
            return "안정적이고 균형잡힌"
        elif level >= 2:
            return "차분하고 온화한"
        else:
            return "조용하고 내면적인"

    def _explain_theme(self, theme: str) -> str:
        """테마 상세 설명"""
        explanations = {
            "안정과 정리": "기존 작업을 마무리하고 정리하는 데 적합한 흐름입니다. 새로운 시작보다는 지금까지 해온 일들을 점검하고 완성하는 시간으로 활용하세요.",
            "확장과 도전": "새로운 것을 시도하고 확장하는 데 유리한 날입니다. 평소 망설였던 일에 도전해보세요.",
            "내면과 휴식": "외부 활동보다는 내면을 돌아보고 충전하는 시간이 필요합니다.",
            "관계와 소통": "사람들과의 교류와 소통이 잘 풀리는 날입니다.",
            "집중과 실행": "계획한 일을 착실히 실행하기 좋은 흐름입니다."
        }
        return explanations.get(theme, "오늘의 리듬에 맞춰 하루를 보내세요.")

    # ========================================================================
    # 월간/연간 콘텐츠 조립
    # ========================================================================

    def assemble_monthly_content(self, signal: MonthlyRhythmSignal) -> MonthlyContent:
        """월간 리듬 신호 → 월간 콘텐츠"""
        theme = f"{signal.year}년 {signal.month}월은 {signal.main_theme}입니다. " \
                f"{signal.energy_trend}의 흐름이 예상됩니다."

        priorities = signal.focus_areas[:3] if len(signal.focus_areas) >= 3 else signal.focus_areas + ["균형 유지"]

        return MonthlyContent(
            year=signal.year,
            month=signal.month,
            theme=theme,
            priorities=priorities,
            calendar_keywords={}  # TODO: 날짜별 키워드 생성
        )

    def assemble_yearly_content(self, signal: YearlyRhythmSignal) -> YearlyContent:
        """연간 리듬 신호 → 연간 콘텐츠"""
        summary = f"{signal.year}년은 {signal.main_theme}의 해입니다. " \
                  f"주요 키워드는 {', '.join(signal.keywords)}입니다."

        return YearlyContent(
            year=signal.year,
            summary=summary,
            keywords=signal.keywords,
            monthly_themes=signal.monthly_summary or {},
            growth_focus=signal.growth_areas
        )


# ============================================================================
# 편의 함수
# ============================================================================

def create_daily_content(signal: RhythmSignal) -> DailyContent:
    """
    편의 함수: RhythmSignal → DailyContent

    Usage:
        from src.rhythm.signals import create_daily_rhythm
        from src.content.assembly import create_daily_content

        signal = create_daily_rhythm(birth_info, date.today())
        content = create_daily_content(signal)
    """
    assembler = ContentAssembler()
    return assembler.assemble_daily_content(signal)
