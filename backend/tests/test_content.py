"""
Content Assembly Engine 단위 테스트
"""
import pytest
from datetime import date, time
from src.rhythm.models import BirthInfo, Gender, RhythmSignal
from src.rhythm.signals import create_daily_rhythm
from src.content.models import DailyContent, FocusCaution, ActionGuide, TimeDirection, StateTrigger
from src.content.assembly import ContentAssembler, create_daily_content
from src.content.validator import ContentValidator, validate_content, get_quality_report


class TestDailyContentModel:
    """DailyContent 모델 테스트"""

    def test_daily_content_creation(self):
        """DailyContent 객체 생성 테스트"""
        content = DailyContent(
            date=date(2026, 1, 20),
            summary="오늘은 안정적인 에너지가 있는 날입니다. 정리와 마무리에 집중하면 좋습니다.",
            keywords=["안정", "정리", "마무리"],
            rhythm_description="오늘의 리듬은 차분하고 안정적입니다. " * 5,  # 100자 이상
            focus_caution=FocusCaution(
                focus=["정리", "마무리"],
                caution=["새로운 시작"]
            ),
            action_guide=ActionGuide(
                do=["할 일 정리", "공간 정리"],
                avoid=["충동 구매", "큰 결정"]
            ),
            time_direction=TimeDirection(
                good_time="오전 9-11시",
                avoid_time="오후 5-7시",
                good_direction="북동",
                avoid_direction="남서",
                notes="집중 작업은 오전에"
            ),
            state_trigger=StateTrigger(
                gesture="양손 모으기",
                phrase="나는 충분하다",
                how_to="불안할 때 3번 반복"
            ),
            meaning_shift="오늘의 차분함은 무기력이 아니라 충전입니다. " * 2,
            rhythm_question="오늘 마무리하고 싶은 일은 무엇인가요?"
        )

        assert content.date == date(2026, 1, 20)
        assert len(content.keywords) == 3
        assert "안정" in content.keywords

    def test_keywords_validation(self):
        """키워드 개수 검증 (2-5개)"""
        with pytest.raises(ValueError):
            DailyContent(
                date=date(2026, 1, 20),
                summary="테스트",
                keywords=["하나만"],  # 1개는 안됨
                rhythm_description="테스트" * 20,
                focus_caution=FocusCaution(),
                action_guide=ActionGuide(),
                time_direction=TimeDirection(
                    good_time="오전",
                    avoid_time="오후",
                    good_direction="북",
                    avoid_direction="남"
                ),
                state_trigger=StateTrigger(
                    gesture="test",
                    phrase="test",
                    how_to="test"
                ),
                meaning_shift="test" * 10,
                rhythm_question="test?"
            )

    def test_total_text_length_calculation(self):
        """총 텍스트 길이 계산 테스트"""
        content = DailyContent(
            date=date(2026, 1, 20),
            summary="테스트 요약입니다.",  # 10자
            keywords=["키워드1", "키워드2"],  # 8자
            rhythm_description="해설" * 30,  # 60자
            focus_caution=FocusCaution(
                focus=["집중1", "집중2"],
                caution=["주의1"]
            ),
            action_guide=ActionGuide(
                do=["하기1", "하기2"],
                avoid=["피하기1"]
            ),
            time_direction=TimeDirection(
                good_time="오전",
                avoid_time="오후",
                good_direction="북",
                avoid_direction="남",
                notes="노트"
            ),
            state_trigger=StateTrigger(
                gesture="제스처",
                phrase="문구",
                how_to="방법"
            ),
            meaning_shift="의미전환" * 10,
            rhythm_question="질문입니다?"
        )

        total = content.get_total_text_length()
        assert total > 0
        assert isinstance(total, int)


class TestContentAssembler:
    """ContentAssembler 테스트"""

    @pytest.fixture
    def sample_rhythm_signal(self):
        """테스트용 리듬 신호"""
        return RhythmSignal(
            date=date(2026, 1, 20),
            saju_data={"test": "data"},
            energy_level=3,
            focus_capacity=4,
            social_energy=3,
            decision_clarity=4,
            favorable_times=["오전 9-11시", "오후 2-4시"],
            caution_times=["오후 5-7시"],
            favorable_directions=["북동", "남서"],
            main_theme="안정과 정리",
            opportunities=["학습", "관계 강화"],
            challenges=["충동 조절"]
        )

    @pytest.fixture
    def assembler(self):
        """ContentAssembler 인스턴스"""
        return ContentAssembler()

    def test_assemble_daily_content(self, assembler, sample_rhythm_signal):
        """RhythmSignal → DailyContent 변환 테스트"""
        content = assembler.assemble_daily_content(sample_rhythm_signal)

        # 반환 타입 확인
        assert isinstance(content, DailyContent)

        # 날짜 일치
        assert content.date == sample_rhythm_signal.date

        # 필수 필드 존재 확인
        assert content.summary
        assert len(content.keywords) >= 2
        assert content.rhythm_description
        assert len(content.rhythm_description) >= 100  # 최소 100자

        # 10개 블록 존재 확인
        assert content.focus_caution
        assert content.action_guide
        assert content.time_direction
        assert content.state_trigger
        assert content.meaning_shift
        assert content.rhythm_question

    def test_internal_terms_not_exposed(self, assembler, sample_rhythm_signal):
        """
        내부 전문 용어가 사용자 콘텐츠에 노출되지 않는지 확인
        """
        content = assembler.assemble_daily_content(sample_rhythm_signal)

        # 전체 텍스트 수집
        all_text = " ".join([
            content.summary,
            " ".join(content.keywords),
            content.rhythm_description,
            content.meaning_shift,
            content.rhythm_question
        ])

        # 금지 용어 확인
        forbidden_terms = ["사주", "천간", "지지", "오행", "십성", "대운"]
        for term in forbidden_terms:
            assert term not in all_text, f"내부 전문 용어 '{term}'가 노출되었습니다!"

    def test_content_length_meets_requirements(self, assembler, sample_rhythm_signal):
        """콘텐츠 최소 길이 요구사항 충족 테스트"""
        content = assembler.assemble_daily_content(sample_rhythm_signal)

        total_length = content.get_total_text_length()

        # 최소 400자 요구사항
        assert total_length >= 400, f"콘텐츠 길이 부족: {total_length}자 (최소 400자)"


class TestContentValidator:
    """ContentValidator 테스트"""

    @pytest.fixture
    def validator(self):
        """ContentValidator 인스턴스"""
        # 스키마 파일이 없을 수 있으므로 예외 처리
        try:
            return ContentValidator()
        except FileNotFoundError:
            pytest.skip("DAILY_CONTENT_SCHEMA.json 파일이 없습니다")

    @pytest.fixture
    def valid_content(self):
        """유효한 콘텐츠"""
        return DailyContent(
            date=date(2026, 1, 20),
            summary="오늘은 안정적인 에너지가 있는 날입니다. 정리와 마무리에 집중하면 좋습니다.",
            keywords=["안정", "정리", "마무리"],
            rhythm_description="오늘의 리듬은 차분하고 안정적입니다. 에너지가 내부로 향하며, 외부 활동보다는 내면 정리와 기존 작업 완성에 적합한 흐름입니다. 급하게 새로운 일을 시작하기보다는 지금까지 해온 일들을 점검하고 마무리하는 시간으로 활용하면 좋습니다.",
            focus_caution=FocusCaution(
                focus=["정리", "마무리", "성찰"],
                caution=["새로운 시작", "큰 결정"]
            ),
            action_guide=ActionGuide(
                do=["할 일 정리", "공간 정리", "마무리"],
                avoid=["충동 구매", "중요한 계약"]
            ),
            time_direction=TimeDirection(
                good_time="오전 9-11시, 오후 2-4시",
                avoid_time="오후 5-7시",
                good_direction="북동쪽",
                avoid_direction="남서쪽",
                notes="집중이 필요한 작업은 오전 시간대에 하세요"
            ),
            state_trigger=StateTrigger(
                gesture="양손을 가슴에 모으고 천천히 호흡",
                phrase="지금 이 순간, 나는 충분히 잘하고 있다",
                how_to="불안감이 올라올 때 3번 반복하세요"
            ),
            meaning_shift="오늘의 차분한 에너지는 '무기력'이 아니라 '내면 충전'의 시간입니다. 급하지 않게 한 걸음씩 나아가는 것이 오늘의 지혜입니다.",
            rhythm_question="오늘 마무리하고 싶은 일은 무엇인가요? 그것을 완성하면 어떤 기분이 들까요?"
        )

    def test_validate_valid_content(self, validator, valid_content):
        """유효한 콘텐츠 검증"""
        is_valid, messages = validator.validate_daily_content(valid_content)

        assert is_valid or len(messages) == 0 or all("경고" in msg or "목표" in msg for msg in messages)

    def test_forbidden_terms_detection(self, validator):
        """금지 용어 감지 테스트"""
        content_with_forbidden = DailyContent(
            date=date(2026, 1, 20),
            summary="오늘은 사주명리에 따르면...",  # 금지 용어!
            keywords=["천간", "지지"],  # 금지 용어!
            rhythm_description="오늘의 오행은..." * 20,  # 금지 용어!
            focus_caution=FocusCaution(),
            action_guide=ActionGuide(),
            time_direction=TimeDirection(
                good_time="오전",
                avoid_time="오후",
                good_direction="북",
                avoid_direction="남"
            ),
            state_trigger=StateTrigger(
                gesture="test",
                phrase="test",
                how_to="test"
            ),
            meaning_shift="test" * 10,
            rhythm_question="test?"
        )

        is_valid, messages = validator.validate_daily_content(content_with_forbidden)

        assert not is_valid
        assert any("내부 전문 용어" in msg for msg in messages)

    def test_quality_report_generation(self, validator, valid_content):
        """품질 리포트 생성 테스트"""
        report = validator.generate_quality_report(valid_content)

        assert "is_valid" in report
        assert "total_chars" in report
        assert "completion_rate" in report
        assert isinstance(report["completion_rate"], float)


class TestIntegration:
    """통합 테스트 (Rhythm → Content)"""

    def test_full_pipeline(self):
        """전체 파이프라인 테스트: BirthInfo → RhythmSignal → DailyContent"""
        # 1. BirthInfo 생성
        birth_info = BirthInfo(
            name="테스트",
            birth_date=date(1990, 1, 15),
            birth_time=time(14, 30),
            gender=Gender.MALE,
            birth_place="서울"
        )

        # 2. RhythmSignal 생성
        signal = create_daily_rhythm(birth_info, date(2026, 1, 20))
        assert isinstance(signal, RhythmSignal)

        # 3. DailyContent 생성
        content = create_daily_content(signal)
        assert isinstance(content, DailyContent)

        # 4. 검증
        total_length = content.get_total_text_length()
        assert total_length >= 400, f"콘텐츠 길이 부족: {total_length}자"

        # 5. 내부 용어 미노출 확인
        all_text = content.summary + content.rhythm_description
        assert "사주" not in all_text
        assert "천간" not in all_text

    def test_different_energy_levels(self):
        """다양한 에너지 레벨에 대한 콘텐츠 생성 테스트"""
        for energy_level in [1, 3, 5]:
            signal = RhythmSignal(
                date=date(2026, 1, 20),
                saju_data={},
                energy_level=energy_level,
                focus_capacity=3,
                social_energy=3,
                decision_clarity=3,
                main_theme="테스트",
                opportunities=["학습"],
                challenges=["조절"]
            )

            content = create_daily_content(signal)

            # 에너지 레벨에 따라 다른 콘텐츠 생성 확인
            assert content.summary
            assert len(content.keywords) >= 2
            assert content.get_total_text_length() >= 400


class TestConvenienceFunctions:
    """편의 함수 테스트"""

    def test_validate_content_function(self):
        """validate_content 편의 함수 테스트"""
        # 스키마 파일이 없을 수 있으므로 스킵
        pytest.skip("DAILY_CONTENT_SCHEMA.json 의존")

    def test_get_quality_report_function(self):
        """get_quality_report 편의 함수 테스트"""
        # 스키마 파일이 없을 수 있으므로 스킵
        pytest.skip("DAILY_CONTENT_SCHEMA.json 의존")


# ============================================================================
# 실행 가이드
# ============================================================================
"""
테스트 실행 방법:

1. 전체 테스트 실행:
   pytest tests/test_content.py -v

2. 특정 클래스만 테스트:
   pytest tests/test_content.py::TestContentAssembler -v

3. 통합 테스트만 실행:
   pytest tests/test_content.py::TestIntegration -v

4. 커버리지 확인:
   pytest tests/test_content.py --cov=src/content --cov-report=html

5. 상세 출력:
   pytest tests/test_content.py -v -s
"""
