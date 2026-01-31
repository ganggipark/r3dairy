"""
스키마 검증 테스트
DAILY_CONTENT_SCHEMA.json 준수 확인
"""
import pytest
import json
import datetime
from pathlib import Path
from jsonschema import validate, ValidationError

from src.rhythm.models import BirthInfo, Gender
from src.rhythm.saju import calculate_saju, analyze_daily_fortune
from src.content.assembly import assemble_daily_content
from src.translation import translate_daily_content


class TestSchemaValidation:
    """스키마 검증 회귀 테스트"""

    @pytest.fixture
    def schema(self):
        """DAILY_CONTENT_SCHEMA.json 로드"""
        schema_path = Path(__file__).parent.parent.parent.parent / "docs" / "content" / "DAILY_CONTENT_SCHEMA.json"

        if not schema_path.exists():
            pytest.skip(f"스키마 파일 없음: {schema_path}")

        with open(schema_path, "r", encoding="utf-8") as f:
            return json.load(f)

    @pytest.fixture
    def sample_content(self):
        """샘플 일간 콘텐츠 생성"""
        birth_info = BirthInfo(
            name="테스트",
            birth_date=datetime.date(1990, 5, 15),
            birth_time=datetime.time(14, 30),
            gender=Gender.MALE,
            birth_place="서울특별시"
        )
        target_date = datetime.date(2026, 1, 21)

        saju_result = calculate_saju(birth_info, target_date)
        daily_rhythm = analyze_daily_fortune(birth_info, target_date, saju_result)
        content = assemble_daily_content(target_date, saju_result, daily_rhythm)

        return content

    def test_schema_structure_compliance(self, sample_content, schema):
        """스키마 구조 준수 검증"""
        try:
            # JSONSchema 검증
            validate(instance=sample_content, schema=schema)
            print("[OK] 스키마 구조 검증 통과")

        except ValidationError as e:
            pytest.fail(f"스키마 검증 실패: {e.message}")

    def test_required_fields_present(self, sample_content):
        """필수 필드 존재 확인"""
        required_fields = [
            "summary",
            "keywords",
            "rhythm_description",
            "focus_caution",
            "action_guide",
            "time_direction",
            "state_trigger",
            "meaning_shift",
            "rhythm_question"
        ]

        missing_fields = []
        for field in required_fields:
            if field not in sample_content:
                missing_fields.append(field)

        assert len(missing_fields) == 0, f"필수 필드 누락: {missing_fields}"
        print("[OK] 필수 필드 존재 확인 통과")

    def test_field_types(self, sample_content):
        """필드 타입 검증"""
        # summary: string
        assert isinstance(sample_content["summary"], str), "summary 타입 오류"

        # keywords: list of strings
        assert isinstance(sample_content["keywords"], list), "keywords 타입 오류"
        assert all(isinstance(k, str) for k in sample_content["keywords"]), "keywords 항목 타입 오류"

        # rhythm_description: string
        assert isinstance(sample_content["rhythm_description"], str), "rhythm_description 타입 오류"

        # focus_caution: dict with 'focus' and 'caution' lists
        assert isinstance(sample_content["focus_caution"], dict), "focus_caution 타입 오류"
        assert "focus" in sample_content["focus_caution"], "focus 필드 누락"
        assert "caution" in sample_content["focus_caution"], "caution 필드 누락"
        assert isinstance(sample_content["focus_caution"]["focus"], list), "focus 타입 오류"
        assert isinstance(sample_content["focus_caution"]["caution"], list), "caution 타입 오류"

        # action_guide: dict with 'do' and 'avoid' lists
        assert isinstance(sample_content["action_guide"], dict), "action_guide 타입 오류"
        assert "do" in sample_content["action_guide"], "do 필드 누락"
        assert "avoid" in sample_content["action_guide"], "avoid 필드 누락"
        assert isinstance(sample_content["action_guide"]["do"], list), "do 타입 오류"
        assert isinstance(sample_content["action_guide"]["avoid"], list), "avoid 타입 오류"

        # time_direction: dict
        assert isinstance(sample_content["time_direction"], dict), "time_direction 타입 오류"

        # state_trigger: dict
        assert isinstance(sample_content["state_trigger"], dict), "state_trigger 타입 오류"

        # meaning_shift: string
        assert isinstance(sample_content["meaning_shift"], str), "meaning_shift 타입 오류"

        # rhythm_question: string
        assert isinstance(sample_content["rhythm_question"], str), "rhythm_question 타입 오류"

        print("[OK] 필드 타입 검증 통과")

    def test_field_length_requirements(self, sample_content):
        """필드 길이 요구사항 검증"""
        # summary: 최소 10자
        assert len(sample_content["summary"]) >= 10, f"summary 너무 짧음: {len(sample_content['summary'])}자"

        # keywords: 3-10개
        assert 3 <= len(sample_content["keywords"]) <= 10, \
            f"keywords 개수 이상: {len(sample_content['keywords'])}"

        # rhythm_description: 최소 50자
        assert len(sample_content["rhythm_description"]) >= 50, \
            f"rhythm_description 너무 짧음: {len(sample_content['rhythm_description'])}자"

        # focus/caution: 각각 최소 1개
        assert len(sample_content["focus_caution"]["focus"]) >= 1, "focus 항목 없음"
        assert len(sample_content["focus_caution"]["caution"]) >= 1, "caution 항목 없음"

        # do/avoid: 각각 최소 2개
        assert len(sample_content["action_guide"]["do"]) >= 2, "do 항목 부족"
        assert len(sample_content["action_guide"]["avoid"]) >= 2, "avoid 항목 부족"

        # meaning_shift: 최소 10자
        assert len(sample_content["meaning_shift"]) >= 10, \
            f"meaning_shift 너무 짧음: {len(sample_content['meaning_shift'])}자"

        # rhythm_question: 최소 5자
        assert len(sample_content["rhythm_question"]) >= 5, \
            f"rhythm_question 너무 짧음: {len(sample_content['rhythm_question'])}자"

        print("[OK] 필드 길이 요구사항 통과")

    def test_role_translated_content_schema_compliance(self, sample_content, schema):
        """역할별 변환 후에도 스키마 준수 확인"""
        roles = ["student", "office_worker", "freelancer"]

        for role in roles:
            translated = translate_daily_content(sample_content, role)

            try:
                validate(instance=translated, schema=schema)
                print(f"[OK] {role} 역할 변환 후 스키마 준수")

            except ValidationError as e:
                pytest.fail(f"{role} 역할 스키마 검증 실패: {e.message}")

    def test_no_empty_strings(self, sample_content):
        """빈 문자열 검증"""
        def check_empty_strings(data, path=""):
            if isinstance(data, dict):
                for key, value in data.items():
                    check_empty_strings(value, f"{path}.{key}" if path else key)
            elif isinstance(data, list):
                for i, item in enumerate(data):
                    check_empty_strings(item, f"{path}[{i}]")
            elif isinstance(data, str):
                assert len(data.strip()) > 0, f"빈 문자열 발견: {path}"

        check_empty_strings(sample_content)
        print("[OK] 빈 문자열 검증 통과")

    def test_consistent_date_format(self, sample_content):
        """날짜 형식 일관성 검증 (만약 date 필드가 있다면)"""
        if "date" in sample_content:
            date_str = sample_content["date"]
            # YYYY-MM-DD 형식 검증
            try:
                datetime.datetime.strptime(date_str, "%Y-%m-%d")
                print("[OK] 날짜 형식 검증 통과")
            except ValueError:
                pytest.fail(f"날짜 형식 오류: {date_str}")


class TestSchemaRegression:
    """스키마 변경 방지 회귀 테스트"""

    def test_schema_file_exists(self):
        """스키마 파일 존재 확인"""
        schema_path = Path(__file__).parent.parent.parent.parent / "docs" / "content" / "DAILY_CONTENT_SCHEMA.json"
        assert schema_path.exists(), f"스키마 파일 없음: {schema_path}"
        print("[OK] 스키마 파일 존재 확인")

    def test_schema_parseable(self):
        """스키마 파일 파싱 가능 확인"""
        schema_path = Path(__file__).parent.parent.parent.parent / "docs" / "content" / "DAILY_CONTENT_SCHEMA.json"

        if not schema_path.exists():
            pytest.skip(f"스키마 파일 없음: {schema_path}")

        try:
            with open(schema_path, "r", encoding="utf-8") as f:
                schema = json.load(f)

            assert isinstance(schema, dict), "스키마가 dict 타입이 아님"
            print("[OK] 스키마 파싱 가능 확인")

        except json.JSONDecodeError as e:
            pytest.fail(f"스키마 JSON 파싱 실패: {e}")

    def test_schema_has_required_definitions(self):
        """스키마에 필수 정의 포함 확인"""
        schema_path = Path(__file__).parent.parent.parent.parent / "docs" / "content" / "DAILY_CONTENT_SCHEMA.json"

        if not schema_path.exists():
            pytest.skip(f"스키마 파일 없음: {schema_path}")

        with open(schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)

        # 기본 JSONSchema 필드 확인
        assert "$schema" in schema or "type" in schema, "스키마 기본 구조 누락"

        print("[OK] 스키마 필수 정의 확인")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
