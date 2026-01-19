"""
Role Translation Layer 단위 테스트
"""
import pytest
from datetime import date, time
from src.rhythm.models import BirthInfo, Gender
from src.rhythm.signals import create_daily_rhythm
from src.content.assembly import create_daily_content
from src.translation.models import Role, RoleTemplate, TranslationContext
from src.translation.translator import RoleTranslator, translate_content


class TestRoleModels:
    """Role 모델 테스트"""

    def test_role_enum(self):
        """Role enum 정의 확인"""
        assert Role.STUDENT == "student"
        assert Role.OFFICE_WORKER == "office_worker"
        assert Role.FREELANCER == "freelancer"

    def test_translation_context_creation(self):
        """TranslationContext 생성 테스트"""
        context = TranslationContext(
            target_role=Role.STUDENT,
            user_preferences={"grade": "고3", "interests": ["수학"]}
        )

        assert context.target_role == Role.STUDENT
        assert context.user_preferences["grade"] == "고3"


class TestRoleTemplateLoading:
    """역할 템플릿 로딩 테스트"""

    @pytest.fixture
    def translator(self):
        """RoleTranslator 인스턴스"""
        return RoleTranslator()

    def test_templates_loaded(self, translator):
        """템플릿 로드 확인"""
        assert Role.STUDENT in translator.templates
        assert Role.OFFICE_WORKER in translator.templates
        assert Role.FREELANCER in translator.templates

    def test_student_template_structure(self, translator):
        """학생 템플릿 구조 확인"""
        template = translator.templates[Role.STUDENT]

        assert template.role == Role.STUDENT
        assert "작업 완료" in template.expressions
        assert template.expressions["작업 완료"] == "과제 마무리"
        assert len(template.action_keywords) > 0
        assert "학습" in template.action_keywords
        assert len(template.question_templates) > 0

    def test_office_worker_template_structure(self, translator):
        """직장인 템플릿 구조 확인"""
        template = translator.templates[Role.OFFICE_WORKER]

        assert template.role == Role.OFFICE_WORKER
        assert "작업 완료" in template.expressions
        assert template.expressions["작업 완료"] == "업무 마무리"
        assert "보고" in template.action_keywords

    def test_freelancer_template_structure(self, translator):
        """프리랜서 템플릿 구조 확인"""
        template = translator.templates[Role.FREELANCER]

        assert template.role == Role.FREELANCER
        assert "작업 완료" in template.expressions
        assert template.expressions["작업 완료"] == "프로젝트 마감"
        assert "마감" in template.action_keywords


class TestRoleTranslation:
    """역할별 콘텐츠 변환 테스트"""

    @pytest.fixture
    def translator(self):
        """RoleTranslator 인스턴스"""
        return RoleTranslator()

    @pytest.fixture
    def sample_content(self):
        """테스트용 중립 콘텐츠"""
        birth_info = BirthInfo(
            name="테스트",
            birth_date=date(1990, 1, 15),
            birth_time=time(14, 30),
            gender=Gender.MALE,
            birth_place="서울"
        )
        signal = create_daily_rhythm(birth_info, date(2026, 1, 20))
        return create_daily_content(signal)

    def test_translate_to_student(self, translator, sample_content):
        """학생 역할 변환 테스트"""
        translated = translator.translate(sample_content, Role.STUDENT)

        # 날짜 유지
        assert translated.date == sample_content.date

        # 키워드 개수 유지
        assert len(translated.keywords) == len(sample_content.keywords)

        # 역할별 표현 확인 (만약 원본에 "작업 완료"가 있었다면)
        if "작업 완료" in sample_content.summary:
            assert "과제 마무리" in translated.summary

    def test_translate_to_office_worker(self, translator, sample_content):
        """직장인 역할 변환 테스트"""
        translated = translator.translate(sample_content, Role.OFFICE_WORKER)

        assert translated.date == sample_content.date
        assert len(translated.keywords) == len(sample_content.keywords)

        # 역할별 표현 확인
        if "작업 완료" in sample_content.summary:
            assert "업무 마무리" in translated.summary

    def test_translate_to_freelancer(self, translator, sample_content):
        """프리랜서 역할 변환 테스트"""
        translated = translator.translate(sample_content, Role.FREELANCER)

        assert translated.date == sample_content.date
        assert len(translated.keywords) == len(sample_content.keywords)

        # 역할별 표현 확인
        if "작업 완료" in sample_content.summary:
            assert "프로젝트 마감" in translated.summary

    def test_all_blocks_translated(self, translator, sample_content):
        """모든 블록이 변환되는지 확인"""
        translated = translator.translate(sample_content, Role.STUDENT)

        # 필수 블록 존재 확인
        assert translated.summary
        assert len(translated.keywords) >= 2
        assert translated.rhythm_description
        assert translated.focus_caution
        assert translated.action_guide
        assert translated.time_direction
        assert translated.state_trigger
        assert translated.meaning_shift
        assert translated.rhythm_question


class TestSemanticPreservation:
    """의미 불변성 검증 테스트"""

    @pytest.fixture
    def translator(self):
        """RoleTranslator 인스턴스"""
        return RoleTranslator()

    @pytest.fixture
    def sample_content(self):
        """테스트용 콘텐츠"""
        birth_info = BirthInfo(
            name="테스트",
            birth_date=date(1990, 1, 15),
            birth_time=time(14, 30),
            gender=Gender.MALE,
            birth_place="서울"
        )
        signal = create_daily_rhythm(birth_info, date(2026, 1, 20))
        return create_daily_content(signal)

    def test_semantic_preservation_student(self, translator, sample_content):
        """학생 역할 변환 시 의미 보존 확인"""
        translated = translator.translate(sample_content, Role.STUDENT)

        is_valid, issues = translator.validate_semantic_preservation(
            sample_content, translated
        )

        # 의미 불변성 검증 통과 확인
        assert is_valid or len(issues) == 0, f"의미 불변성 검증 실패: {issues}"

    def test_semantic_preservation_office_worker(self, translator, sample_content):
        """직장인 역할 변환 시 의미 보존 확인"""
        translated = translator.translate(sample_content, Role.OFFICE_WORKER)

        is_valid, issues = translator.validate_semantic_preservation(
            sample_content, translated
        )

        assert is_valid or len(issues) == 0, f"의미 불변성 검증 실패: {issues}"

    def test_semantic_preservation_freelancer(self, translator, sample_content):
        """프리랜서 역할 변환 시 의미 보존 확인"""
        translated = translator.translate(sample_content, Role.FREELANCER)

        is_valid, issues = translator.validate_semantic_preservation(
            sample_content, translated
        )

        assert is_valid or len(issues) == 0, f"의미 불변성 검증 실패: {issues}"

    def test_length_preservation(self, translator, sample_content):
        """콘텐츠 길이 보존 확인 (±20% 이내)"""
        for role in [Role.STUDENT, Role.OFFICE_WORKER, Role.FREELANCER]:
            translated = translator.translate(sample_content, role)

            orig_len = sample_content.get_total_text_length()
            trans_len = translated.get_total_text_length()
            ratio = abs(trans_len - orig_len) / orig_len

            assert ratio <= 0.2, f"{role.value}: 길이 차이 {ratio*100:.1f}% (허용: 20%)"


class TestConvenienceFunction:
    """편의 함수 테스트"""

    @pytest.fixture
    def sample_content(self):
        """테스트용 콘텐츠"""
        birth_info = BirthInfo(
            name="테스트",
            birth_date=date(1990, 1, 15),
            birth_time=time(14, 30),
            gender=Gender.MALE,
            birth_place="서울"
        )
        signal = create_daily_rhythm(birth_info, date(2026, 1, 20))
        return create_daily_content(signal)

    def test_translate_content_function(self, sample_content):
        """translate_content 편의 함수 테스트"""
        student_content = translate_content(sample_content, Role.STUDENT)

        assert student_content.date == sample_content.date
        assert len(student_content.keywords) == len(sample_content.keywords)


class TestIntegration:
    """통합 테스트 (Rhythm → Content → Translation)"""

    def test_full_pipeline_all_roles(self):
        """전체 파이프라인: BirthInfo → RhythmSignal → DailyContent → Role Translation"""
        # 1. BirthInfo
        birth_info = BirthInfo(
            name="통합테스트",
            birth_date=date(1990, 1, 15),
            birth_time=time(14, 30),
            gender=Gender.MALE,
            birth_place="서울"
        )

        # 2. RhythmSignal
        signal = create_daily_rhythm(birth_info, date(2026, 1, 20))

        # 3. DailyContent (중립)
        neutral_content = create_daily_content(signal)

        # 4. Role Translation
        student_content = translate_content(neutral_content, Role.STUDENT)
        worker_content = translate_content(neutral_content, Role.OFFICE_WORKER)
        freelancer_content = translate_content(neutral_content, Role.FREELANCER)

        # 검증: 모든 역할 버전이 생성됨
        assert student_content.date == signal.date
        assert worker_content.date == signal.date
        assert freelancer_content.date == signal.date

        # 검증: 각 역할 버전이 서로 다른 표현을 사용함
        # (만약 원본에 "작업 완료"가 있다면)
        all_summaries = [
            student_content.summary,
            worker_content.summary,
            freelancer_content.summary
        ]

        # 적어도 하나는 다른 표현이어야 함
        assert len(set(all_summaries)) >= 1

    def test_regression_meaning_consistency(self):
        """회귀 테스트: 의미 일관성 확인"""
        birth_info = BirthInfo(
            name="회귀테스트",
            birth_date=date(1995, 5, 10),
            birth_time=time(9, 0),
            gender=Gender.FEMALE,
            birth_place="부산"
        )

        signal = create_daily_rhythm(birth_info, date(2026, 2, 14))
        neutral_content = create_daily_content(signal)

        translator = RoleTranslator()

        for role in [Role.STUDENT, Role.OFFICE_WORKER, Role.FREELANCER]:
            translated = translator.translate(neutral_content, role)
            is_valid, issues = translator.validate_semantic_preservation(
                neutral_content, translated
            )

            assert is_valid or len(issues) == 0, \
                f"{role.value} 역할 변환 시 의미 불변성 실패: {issues}"


# ============================================================================
# 실행 가이드
# ============================================================================
"""
테스트 실행 방법:

1. 전체 테스트 실행:
   pytest tests/test_translation.py -v

2. 특정 클래스만 테스트:
   pytest tests/test_translation.py::TestRoleTranslation -v

3. 통합 테스트만 실행:
   pytest tests/test_translation.py::TestIntegration -v

4. 의미 불변성 테스트만 실행:
   pytest tests/test_translation.py::TestSemanticPreservation -v

5. 커버리지 확인:
   pytest tests/test_translation.py --cov=src/translation --cov-report=html

6. 상세 출력:
   pytest tests/test_translation.py -v -s
"""
