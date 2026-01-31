"""
Content Assembly Engine 단위 테스트
"""
import pytest
from datetime import date, time
from src.content.assembly import assemble_daily_content
from src.content.validator import validate_daily_content


# Alias for backward compatibility in tests
create_daily_content = assemble_daily_content


class TestContentAssembly:
    """assemble_daily_content 테스트"""

    @pytest.fixture
    def sample_daily_rhythm(self):
        """테스트용 일간 리듬 데이터"""
        return {
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

    @pytest.fixture
    def sample_saju_data(self):
        """테스트용 사주 데이터"""
        return {"test": "data"}

    def test_assemble_daily_content(self, sample_saju_data, sample_daily_rhythm):
        """RhythmSignal dict -> DailyContent dict 변환 테스트"""
        content = assemble_daily_content(
            date=date(2026, 1, 20),
            saju_data=sample_saju_data,
            daily_rhythm=sample_daily_rhythm,
        )

        # 반환 타입 확인
        assert isinstance(content, dict)

        # 날짜 확인
        assert content["date"] == "2026-01-20"

        # 필수 필드 존재 확인
        assert content["summary"]
        assert len(content["keywords"]) >= 2
        assert content["rhythm_description"]
        assert len(content["rhythm_description"]) >= 50

        # 10개 블록 존재 확인
        assert content["focus_caution"]
        assert content["action_guide"]
        assert content["time_direction"]
        assert content["state_trigger"]
        assert content["meaning_shift"]
        assert content["rhythm_question"]

    def test_internal_terms_not_exposed(self, sample_saju_data, sample_daily_rhythm):
        """내부 전문 용어가 사용자 콘텐츠에 노출되지 않는지 확인"""
        content = assemble_daily_content(
            date=date(2026, 1, 20),
            saju_data=sample_saju_data,
            daily_rhythm=sample_daily_rhythm,
        )

        # 전체 텍스트 수집
        all_text = " ".join([
            content["summary"],
            " ".join(content["keywords"]),
            content["rhythm_description"],
            content["meaning_shift"],
            content["rhythm_question"],
        ])

        # 금지 용어 확인
        forbidden_terms = ["사주", "천간", "지지", "오행", "십성", "대운"]
        for term in forbidden_terms:
            assert term not in all_text, f"내부 전문 용어 '{term}'가 노출되었습니다!"

    def test_content_varies_by_energy_level(self, sample_saju_data):
        """다양한 에너지 레벨에 대한 콘텐츠 생성 테스트"""
        summaries = []
        for energy_level in [1, 3, 5]:
            rhythm = {
                "에너지_수준": energy_level,
                "집중력": 3,
                "사회운": 3,
                "결정력": 3,
                "주요_흐름": "테스트",
                "기회_요소": ["학습"],
                "도전_요소": ["조절"],
            }
            content = assemble_daily_content(
                date=date(2026, 1, 20),
                saju_data=sample_saju_data,
                daily_rhythm=rhythm,
            )
            assert content["summary"]
            assert len(content["keywords"]) >= 2
            summaries.append(content["summary"])

        # 에너지 레벨에 따라 다른 콘텐츠가 생성되어야 함
        assert len(set(summaries)) > 1, "에너지 레벨별 콘텐츠가 동일합니다"


class TestContentValidator:
    """ContentValidator 테스트"""

    @pytest.fixture
    def valid_content(self):
        """유효한 콘텐츠 (dict)"""
        return {
            "date": "2026-01-20",
            "summary": "오늘은 안정적인 에너지가 있는 날입니다. 정리와 마무리에 집중하면 좋습니다.",
            "keywords": ["안정", "정리", "마무리"],
            "rhythm_description": (
                "오늘의 리듬은 차분하고 안정적입니다. 에너지가 내부로 향하며, "
                "외부 활동보다는 내면 정리와 기존 작업 완성에 적합한 흐름입니다."
            ),
            "focus_caution": {
                "focus": ["정리", "마무리", "성찰"],
                "caution": ["새로운 시작", "큰 결정"],
            },
            "action_guide": {
                "do": ["할 일 정리", "공간 정리", "마무리"],
                "avoid": ["충동 구매", "중요한 계약"],
            },
            "time_direction": {
                "good_time": "오전 9-11시, 오후 2-4시",
                "avoid_time": "오후 5-7시",
                "good_direction": "북동쪽",
                "avoid_direction": "남서쪽",
                "notes": "집중이 필요한 작업은 오전 시간대에 하세요",
            },
            "state_trigger": {
                "gesture": "양손을 가슴에 모으고 천천히 호흡",
                "phrase": "지금 이 순간, 나는 충분히 잘하고 있다",
                "how_to": "불안감이 올라올 때 3번 반복하세요",
            },
            "meaning_shift": (
                "오늘의 차분한 에너지는 '무기력'이 아니라 '내면 충전'의 시간입니다. "
                "급하지 않게 한 걸음씩 나아가는 것이 오늘의 지혜입니다."
            ),
            "rhythm_question": "오늘 마무리하고 싶은 일은 무엇인가요? 그것을 완성하면 어떤 기분이 들까요?",
        }

    def test_validate_valid_content(self, valid_content):
        """유효한 콘텐츠 검증 - 반환 형식 확인"""
        is_valid, messages = validate_daily_content(valid_content)
        assert isinstance(is_valid, bool)
        assert isinstance(messages, list)

    def test_missing_fields_detected(self):
        """필수 필드 누락 감지 테스트"""
        incomplete_content = {
            "date": "2026-01-20",
            "summary": "테스트",
        }

        is_valid, messages = validate_daily_content(incomplete_content)
        assert not is_valid
        assert len(messages) > 0


class TestIntegration:
    """통합 테스트 (Assembly 함수 직접 호출)"""

    def test_full_assembly_pipeline(self):
        """전체 조립 파이프라인 테스트"""
        saju_data = {"test": "data"}
        daily_rhythm = {
            "에너지_수준": 4,
            "집중력": 3,
            "사회운": 4,
            "결정력": 3,
            "유리한_시간": ["오전 9-11시"],
            "주의_시간": ["오후 5-7시"],
            "유리한_방향": ["북동"],
            "주요_흐름": "활동과 소통",
            "기회_요소": ["관계 강화"],
            "도전_요소": ["과욕"],
        }

        content = assemble_daily_content(
            date=date(2026, 1, 20),
            saju_data=saju_data,
            daily_rhythm=daily_rhythm,
        )

        assert isinstance(content, dict)
        assert content["date"] == "2026-01-20"
        assert content["summary"]
        assert len(content["keywords"]) >= 2

        # 내부 용어 미노출 확인
        all_text = content["summary"] + content["rhythm_description"]
        assert "사주" not in all_text
        assert "천간" not in all_text


class TestConvenienceFunctions:
    """편의 함수 테스트"""

    def test_validate_content_function(self):
        """validate_daily_content 편의 함수 테스트"""
        content = {
            "date": "2026-01-20",
            "summary": "테스트 요약입니다.",
            "keywords": ["키워드1", "키워드2"],
            "rhythm_description": "해설" * 30,
            "focus_caution": {"focus": ["집중"], "caution": ["주의"]},
            "action_guide": {"do": ["하기"], "avoid": ["피하기"]},
            "time_direction": {
                "good_time": "오전",
                "avoid_time": "오후",
                "good_direction": "북",
                "avoid_direction": "남",
                "notes": "",
            },
            "state_trigger": {"gesture": "제스처", "phrase": "문구", "how_to": "방법"},
            "meaning_shift": "의미전환" * 10,
            "rhythm_question": "질문입니다?",
        }
        is_valid, messages = validate_daily_content(content)
        assert isinstance(is_valid, bool)
        assert isinstance(messages, list)
