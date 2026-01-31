"""
통합 테스트: 전체 워크플로우
프로필 생성 → 리듬 분석 → 콘텐츠 생성 → 화면 표시
"""
import pytest
import datetime
from typing import Dict, Any

from src.rhythm.models import BirthInfo, Gender
from src.rhythm.saju import calculate_saju, analyze_daily_fortune, analyze_monthly_rhythm, analyze_yearly_rhythm
from src.content.assembly import assemble_daily_content, assemble_monthly_content, assemble_yearly_content
from src.translation import translate_daily_content, Role


class TestFullWorkflow:
    """전체 워크플로우 통합 테스트"""

    @pytest.fixture
    def sample_birth_info(self) -> BirthInfo:
        """샘플 프로필 데이터"""
        return BirthInfo(
            name="김철수",
            birth_date=datetime.date(1990, 5, 15),
            birth_time=datetime.time(14, 30),
            gender=Gender.MALE,
            birth_place="서울특별시"
        )

    @pytest.fixture
    def target_date(self) -> datetime.date:
        """테스트 대상 날짜"""
        return datetime.date(2026, 1, 21)

    def test_daily_workflow_neutral(self, sample_birth_info, target_date):
        """일간 워크플로우 - 중립 콘텐츠"""
        # 1. 사주 계산
        saju_result = calculate_saju(sample_birth_info, target_date)
        assert saju_result is not None
        # 사주 결과는 한글 키 또는 영어 키를 사용할 수 있음
        assert "사주" in saju_result or "pillars" in saju_result
        assert isinstance(saju_result, dict)

        # 2. 리듬 분석
        daily_rhythm = analyze_daily_fortune(sample_birth_info, target_date, saju_result)
        assert daily_rhythm is not None
        assert isinstance(daily_rhythm, dict)
        # 한글 키 또는 영어 키 사용 가능
        assert len(daily_rhythm) > 0, "리듬 분석 결과가 비어있음"

        # 3. 콘텐츠 생성
        daily_content = assemble_daily_content(target_date, saju_result, daily_rhythm)
        assert daily_content is not None

        # 4. 필수 블록 존재 확인
        required_fields = [
            "summary", "keywords", "rhythm_description",
            "focus_caution", "action_guide", "time_direction",
            "state_trigger", "meaning_shift", "rhythm_question"
        ]
        for field in required_fields:
            assert field in daily_content, f"필수 필드 누락: {field}"

        # 5. 좌측 페이지 최소 글자 수 확인 (400자 이상)
        total_text = (
            daily_content["summary"] +
            daily_content["rhythm_description"] +
            daily_content["meaning_shift"] +
            daily_content["rhythm_question"]
        )
        assert len(total_text) >= 400, f"좌측 페이지 글자 수 부족: {len(total_text)}자"

        # 6. 내부 용어 노출 확인 (사용자 노출 텍스트에 전문 용어 없어야 함)
        forbidden_terms = ["천간", "지지", "오행", "사주", "명리", "기문둔갑", "NLP"]
        for term in forbidden_terms:
            assert term not in daily_content["summary"], f"내부 용어 노출: {term}"
            assert term not in daily_content["rhythm_description"], f"내부 용어 노출: {term}"

        print(f"[OK] 일간 워크플로우(중립) 통과: {len(total_text)}자")

    def test_daily_workflow_with_roles(self, sample_birth_info, target_date):
        """일간 워크플로우 - 역할별 변환"""
        # 1-3. 사주 계산 → 리듬 분석 → 콘텐츠 생성
        saju_result = calculate_saju(sample_birth_info, target_date)
        daily_rhythm = analyze_daily_fortune(sample_birth_info, target_date, saju_result)
        original_content = assemble_daily_content(target_date, saju_result, daily_rhythm)

        # 4. 역할별 변환
        roles = ["student", "office_worker", "freelancer"]
        role_names = {
            "student": "학생",
            "office_worker": "직장인",
            "freelancer": "프리랜서"
        }

        translated_contents = {}

        for role in roles:
            # 역할별 번역
            translated = translate_daily_content(original_content, role)
            translated_contents[role] = translated

            # 기본 구조 유지 확인
            assert set(translated.keys()) == set(original_content.keys()), \
                f"{role_names[role]} 역할 번역 후 구조 변경"

            # 표현 차이 확인 (적어도 하나의 필드는 달라야 함)
            differences = 0
            for key in ["summary", "keywords", "action_guide"]:
                if str(translated[key]) != str(original_content[key]):
                    differences += 1

            assert differences > 0, f"{role_names[role]} 역할 번역이 원본과 동일함"

            print(f"[OK] {role_names[role]} 역할 변환 통과")

        # 5. 역할 간 차이 확인
        student_summary = translated_contents["student"]["summary"]
        office_summary = translated_contents["office_worker"]["summary"]

        # 학생과 직장인 표현이 달라야 함
        assert student_summary != office_summary, "역할별 표현 차이 없음"

        print("[OK] 역할별 워크플로우 통과")

    def test_monthly_workflow(self, sample_birth_info):
        """월간 워크플로우"""
        year = 2026
        month = 1

        # 1. 사주 계산
        target_date = datetime.date(year, month, 1)
        saju_result = calculate_saju(sample_birth_info, target_date)
        assert saju_result is not None

        # 2. 월간 리듬 분석
        monthly_rhythm = analyze_monthly_rhythm(sample_birth_info, year, month, saju_result)
        assert monthly_rhythm is not None

        # 3. 월간 콘텐츠 생성
        monthly_content = assemble_monthly_content(year, month, monthly_rhythm)
        assert monthly_content is not None

        # 4. 기본 구조 확인 (월간 콘텐츠는 Phase 3에서 정의)
        # 현재는 기본 구조만 확인
        assert isinstance(monthly_content, dict)

        print("[OK] 월간 워크플로우 통과")

    def test_yearly_workflow(self, sample_birth_info):
        """연간 워크플로우"""
        year = 2026

        # 1. 사주 계산
        target_date = datetime.date(year, 1, 1)
        saju_result = calculate_saju(sample_birth_info, target_date)
        assert saju_result is not None

        # 2. 연간 리듬 분석
        yearly_rhythm = analyze_yearly_rhythm(sample_birth_info, year, saju_result)
        assert yearly_rhythm is not None

        # 3. 연간 콘텐츠 생성
        yearly_content = assemble_yearly_content(year, yearly_rhythm)
        assert yearly_content is not None

        # 4. 기본 구조 확인
        assert isinstance(yearly_content, dict)

        print("[OK] 연간 워크플로우 통과")

    def test_content_length_requirements(self, sample_birth_info, target_date):
        """콘텐츠 길이 요구사항 검증"""
        # 콘텐츠 생성
        saju_result = calculate_saju(sample_birth_info, target_date)
        daily_rhythm = analyze_daily_fortune(sample_birth_info, target_date, saju_result)
        content = assemble_daily_content(target_date, saju_result, daily_rhythm)

        # 요약 최소 길이
        assert len(content["summary"]) >= 30, "요약이 너무 짧음"

        # 리듬 해설 최소 길이
        assert len(content["rhythm_description"]) >= 100, "리듬 해설이 너무 짧음"

        # 키워드 개수
        assert 3 <= len(content["keywords"]) <= 10, f"키워드 개수 이상: {len(content['keywords'])}"

        # Do/Avoid 각각 최소 2개
        assert len(content["action_guide"]["do"]) >= 2, "Do 항목이 너무 적음"
        assert len(content["action_guide"]["avoid"]) >= 2, "Avoid 항목이 너무 적음"

        # 질문 존재
        assert len(content["rhythm_question"]) > 0, "리듬 질문이 없음"

        print("[OK] 콘텐츠 길이 요구사항 통과")

    def test_no_internal_terms_in_user_content(self, sample_birth_info, target_date):
        """내부 용어 사용자 노출 금지 검증"""
        saju_result = calculate_saju(sample_birth_info, target_date)
        daily_rhythm = analyze_daily_fortune(sample_birth_info, target_date, saju_result)
        content = assemble_daily_content(target_date, saju_result, daily_rhythm)

        # 금지된 전문 용어
        forbidden_terms = [
            "천간", "지지", "오행", "사주", "명리", "기문둔갑",
            "NLP", "GPT", "AI", "알고리즘", "분석", "계산"
        ]

        # 사용자 노출 필드
        user_facing_fields = [
            content["summary"],
            content["rhythm_description"],
            " ".join(content["keywords"]),
            content["meaning_shift"],
            content["rhythm_question"]
        ]

        violations = []
        for field_text in user_facing_fields:
            for term in forbidden_terms:
                if term in field_text:
                    violations.append(f"'{term}' 발견: {field_text[:50]}...")

        assert len(violations) == 0, f"내부 용어 노출: {violations}"

        print("[OK] 내부 용어 노출 검증 통과")

    def test_role_translation_preserves_meaning(self, sample_birth_info, target_date):
        """역할 번역 의미 불변성 검증"""
        from src.translation.translator import validate_semantic_preservation

        # 원본 콘텐츠 생성
        saju_result = calculate_saju(sample_birth_info, target_date)
        daily_rhythm = analyze_daily_fortune(sample_birth_info, target_date, saju_result)
        original = assemble_daily_content(target_date, saju_result, daily_rhythm)

        # 역할별 번역 및 의미 불변성 검증
        roles = ["student", "office_worker", "freelancer"]

        for role in roles:
            translated = translate_daily_content(original, role)

            # 의미 불변성 검증
            is_valid, errors = validate_semantic_preservation(original, translated)

            assert is_valid, f"{role} 역할 번역 의미 불변성 실패: {errors}"

        print("[OK] 역할 번역 의미 불변성 통과")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
