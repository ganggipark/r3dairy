"""
Role Translation Layer 단위 테스트
"""
import pytest
from datetime import date, time
from src.content.assembly import assemble_daily_content
from src.translation.translator import (
    translate_daily_content,
    validate_semantic_preservation,
    ROLE_EXPRESSIONS,
)


def _make_sample_content():
    """테스트용 중립 콘텐츠 생성"""
    saju_data = {"test": "data"}
    daily_rhythm = {
        "에너지_수준": 3,
        "집중력": 4,
        "사회운": 3,
        "결정력": 4,
        "유리한_시간": ["오전 9-11시", "오후 2-4시"],
        "주의_시간": ["오후 5-7시"],
        "유리한_방향": ["북동", "남서"],
        "주요_흐름": "안정과 정리",
        "기회_요소": ["학습", "관계 강화"],
        "도전_요소": ["충동 조절"],
    }
    return assemble_daily_content(
        date=date(2026, 1, 20),
        saju_data=saju_data,
        daily_rhythm=daily_rhythm,
    )


class TestRoleExpressions:
    """Role expression mapping 테스트"""

    def test_student_expressions_exist(self):
        """학생 표현 매핑 확인"""
        assert "student" in ROLE_EXPRESSIONS
        student = ROLE_EXPRESSIONS["student"]
        assert "활동" in student
        assert student["활동"] == "공부"

    def test_office_worker_expressions_exist(self):
        """직장인 표현 매핑 확인"""
        assert "office_worker" in ROLE_EXPRESSIONS

    def test_freelancer_expressions_exist(self):
        """프리랜서 표현 매핑 확인"""
        assert "freelancer" in ROLE_EXPRESSIONS


class TestRoleTranslation:
    """역할별 콘텐츠 변환 테스트"""

    @pytest.fixture
    def sample_content(self):
        return _make_sample_content()

    def test_translate_to_student(self, sample_content):
        """학생 역할 변환 테스트"""
        translated = translate_daily_content(sample_content, "student")
        assert translated["date"] == sample_content["date"]
        assert len(translated["keywords"]) == len(sample_content["keywords"])

    def test_translate_to_office_worker(self, sample_content):
        """직장인 역할 변환 테스트"""
        translated = translate_daily_content(sample_content, "office_worker")
        assert translated["date"] == sample_content["date"]
        assert len(translated["keywords"]) == len(sample_content["keywords"])

    def test_translate_to_freelancer(self, sample_content):
        """프리랜서 역할 변환 테스트"""
        translated = translate_daily_content(sample_content, "freelancer")
        assert translated["date"] == sample_content["date"]
        assert len(translated["keywords"]) == len(sample_content["keywords"])

    def test_all_blocks_translated(self, sample_content):
        """모든 블록이 변환되는지 확인"""
        translated = translate_daily_content(sample_content, "student")

        assert translated["summary"]
        assert len(translated["keywords"]) >= 2
        assert translated["rhythm_description"]
        assert translated["focus_caution"]
        assert translated["action_guide"]
        assert translated["time_direction"]
        assert translated["state_trigger"]
        assert translated["meaning_shift"]
        assert translated["rhythm_question"]

    def test_unsupported_role_returns_original(self, sample_content):
        """지원하지 않는 역할은 원본 반환"""
        translated = translate_daily_content(sample_content, "unknown_role")
        assert translated == sample_content


class TestSemanticPreservation:
    """의미 불변성 검증 테스트"""

    @pytest.fixture
    def sample_content(self):
        return _make_sample_content()

    def test_semantic_preservation_student(self, sample_content):
        """학생 역할 변환 시 의미 보존 확인"""
        translated = translate_daily_content(sample_content, "student")
        is_valid, issues = validate_semantic_preservation(sample_content, translated)
        assert is_valid or len(issues) == 0, f"의미 불변성 검증 실패: {issues}"

    def test_semantic_preservation_office_worker(self, sample_content):
        """직장인 역할 변환 시 의미 보존 확인"""
        translated = translate_daily_content(sample_content, "office_worker")
        is_valid, issues = validate_semantic_preservation(sample_content, translated)
        assert is_valid or len(issues) == 0, f"의미 불변성 검증 실패: {issues}"

    def test_semantic_preservation_freelancer(self, sample_content):
        """프리랜서 역할 변환 시 의미 보존 확인"""
        translated = translate_daily_content(sample_content, "freelancer")
        is_valid, issues = validate_semantic_preservation(sample_content, translated)
        assert is_valid or len(issues) == 0, f"의미 불변성 검증 실패: {issues}"


class TestIntegration:
    """통합 테스트 (Assembly -> Translation)"""

    def test_full_pipeline_all_roles(self):
        """전체 파이프라인: Assembly -> Translation 모든 역할"""
        content = _make_sample_content()

        student_content = translate_daily_content(content, "student")
        worker_content = translate_daily_content(content, "office_worker")
        freelancer_content = translate_daily_content(content, "freelancer")

        # 모든 역할 버전이 생성됨
        assert student_content["date"] == content["date"]
        assert worker_content["date"] == content["date"]
        assert freelancer_content["date"] == content["date"]

    def test_regression_meaning_consistency(self):
        """회귀 테스트: 의미 일관성 확인"""
        content = _make_sample_content()

        for role in ["student", "office_worker", "freelancer"]:
            translated = translate_daily_content(content, role)
            is_valid, issues = validate_semantic_preservation(content, translated)
            assert is_valid or len(issues) == 0, \
                f"{role} 역할 변환 시 의미 불변성 실패: {issues}"
