"""
Rhythm Analysis Engine 단위 테스트
"""
import pytest
from datetime import date, time
from src.rhythm.models import BirthInfo, Gender, RhythmSignal
from src.rhythm.signals import (
    RhythmAnalyzer,
    create_daily_rhythm,
    create_monthly_rhythm,
    create_yearly_rhythm
)
from src.rhythm.saju import calculate_saju


class TestBirthInfo:
    """BirthInfo 모델 테스트"""

    def test_birth_info_creation(self):
        """BirthInfo 객체 생성 테스트"""
        birth_info = BirthInfo(
            name="홍길동",
            birth_date=date(1990, 1, 15),
            birth_time=time(14, 30),
            gender=Gender.MALE,
            birth_place="서울",
            birth_place_lat=37.5665,
            birth_place_lng=126.9780
        )

        assert birth_info.name == "홍길동"
        assert birth_info.birth_date == date(1990, 1, 15)
        assert birth_info.birth_time == time(14, 30)
        assert birth_info.gender == Gender.MALE
        assert birth_info.birth_place == "서울"

    def test_birth_info_without_coordinates(self):
        """좌표 없이 BirthInfo 생성"""
        birth_info = BirthInfo(
            name="김철수",
            birth_date=date(1995, 5, 20),
            birth_time=time(10, 0),
            gender=Gender.MALE,
            birth_place="부산"
        )

        assert birth_info.birth_place_lat is None
        assert birth_info.birth_place_lng is None


class TestRhythmSignal:
    """RhythmSignal 모델 테스트"""

    def test_rhythm_signal_creation(self):
        """RhythmSignal 객체 생성 테스트"""
        signal = RhythmSignal(
            date=date(2026, 1, 20),
            saju_data={"test": "data"},
            energy_level=4,
            focus_capacity=3,
            social_energy=5,
            decision_clarity=4,
            favorable_times=["오전 9-11시"],
            caution_times=["오후 5-7시"],
            favorable_directions=["북동"],
            main_theme="안정과 정리",
            opportunities=["학습"],
            challenges=["충동 조절"]
        )

        assert signal.date == date(2026, 1, 20)
        assert signal.energy_level == 4
        assert signal.focus_capacity == 3
        assert "오전 9-11시" in signal.favorable_times

    def test_rhythm_signal_energy_validation(self):
        """에너지 레벨 검증 (1-5 범위)"""
        with pytest.raises(Exception):  # Pydantic ValidationError
            RhythmSignal(
                date=date(2026, 1, 20),
                saju_data={},
                energy_level=6,  # 범위 초과
                focus_capacity=3,
                social_energy=5,
                decision_clarity=4,
                main_theme="test"
            )


class TestSajuCalculation:
    """사주명리 계산 테스트"""

    def test_calculate_saju(self):
        """사주 계산 함수 테스트"""
        birth_info = BirthInfo(
            name="홍길동",
            birth_date=date(1990, 1, 15),
            birth_time=time(14, 30),
            gender=Gender.MALE,
            birth_place="서울"
        )

        saju_result = calculate_saju(birth_info, date(2026, 1, 20))

        # 결과 구조 검증
        assert "사주" in saju_result
        assert "년주" in saju_result["사주"]
        assert "월주" in saju_result["사주"]
        assert "일주" in saju_result["사주"]
        assert "시주" in saju_result["사주"]

        # 천간, 지지 존재 확인
        assert "천간" in saju_result["사주"]["년주"]
        assert "지지" in saju_result["사주"]["년주"]


class TestRhythmAnalyzer:
    """RhythmAnalyzer 테스트"""

    @pytest.fixture
    def sample_birth_info(self):
        """테스트용 출생 정보"""
        return BirthInfo(
            name="테스트",
            birth_date=date(1990, 1, 15),
            birth_time=time(14, 30),
            gender=Gender.MALE,
            birth_place="서울"
        )

    @pytest.fixture
    def analyzer(self):
        """RhythmAnalyzer 인스턴스"""
        return RhythmAnalyzer()

    def test_generate_daily_signal(self, analyzer, sample_birth_info):
        """일간 리듬 신호 생성 테스트"""
        target_date = date(2026, 1, 20)
        signal = analyzer.generate_daily_signal(sample_birth_info, target_date)

        # 반환 타입 확인
        assert isinstance(signal, RhythmSignal)

        # 필수 필드 확인
        assert signal.date == target_date
        assert 1 <= signal.energy_level <= 5
        assert 1 <= signal.focus_capacity <= 5
        assert 1 <= signal.social_energy <= 5
        assert 1 <= signal.decision_clarity <= 5
        assert signal.main_theme is not None
        assert isinstance(signal.favorable_times, list)
        assert isinstance(signal.opportunities, list)

    def test_generate_monthly_signal(self, analyzer, sample_birth_info):
        """월간 리듬 신호 생성 테스트"""
        signal = analyzer.generate_monthly_signal(sample_birth_info, 2026, 1)

        assert signal.year == 2026
        assert signal.month == 1
        assert signal.main_theme is not None
        assert isinstance(signal.focus_areas, list)
        assert isinstance(signal.caution_areas, list)

    def test_generate_yearly_signal(self, analyzer, sample_birth_info):
        """연간 리듬 신호 생성 테스트"""
        signal = analyzer.generate_yearly_signal(sample_birth_info, 2026)

        assert signal.year == 2026
        assert signal.main_theme is not None
        assert isinstance(signal.keywords, list)
        assert isinstance(signal.growth_areas, list)


class TestConvenienceFunctions:
    """편의 함수 테스트"""

    @pytest.fixture
    def sample_birth_info(self):
        return BirthInfo(
            name="테스트",
            birth_date=date(1990, 1, 15),
            birth_time=time(14, 30),
            gender=Gender.MALE,
            birth_place="서울"
        )

    def test_create_daily_rhythm(self, sample_birth_info):
        """create_daily_rhythm 편의 함수 테스트"""
        signal = create_daily_rhythm(sample_birth_info, date(2026, 1, 20))

        assert isinstance(signal, RhythmSignal)
        assert signal.date == date(2026, 1, 20)

    def test_create_monthly_rhythm(self, sample_birth_info):
        """create_monthly_rhythm 편의 함수 테스트"""
        signal = create_monthly_rhythm(sample_birth_info, 2026, 1)

        assert signal.year == 2026
        assert signal.month == 1

    def test_create_yearly_rhythm(self, sample_birth_info):
        """create_yearly_rhythm 편의 함수 테스트"""
        signal = create_yearly_rhythm(sample_birth_info, 2026)

        assert signal.year == 2026


class TestInternalTerminology:
    """내부 용어 사용 테스트 (사용자 노출 금지 검증)"""

    def test_saju_data_not_exposed_to_user(self):
        """
        사주 데이터에 내부 전문 용어가 포함되어 있는지 확인
        ⚠️ 이 데이터는 사용자에게 직접 노출하면 안 됩니다!
        """
        birth_info = BirthInfo(
            name="테스트",
            birth_date=date(1990, 1, 15),
            birth_time=time(14, 30),
            gender=Gender.MALE,
            birth_place="서울"
        )

        signal = create_daily_rhythm(birth_info, date(2026, 1, 20))

        # saju_data에 내부 용어가 포함되어 있음을 확인
        assert "사주" in signal.saju_data or "천간" in str(signal.saju_data)

        # RhythmSignal은 내부 표현이므로 전문 용어 사용 가능
        # Content Assembly Engine에서 일반 언어로 변환해야 함
        assert signal.main_theme is not None


class TestEdgeCases:
    """경계값 테스트"""

    def test_leap_year_date(self):
        """윤년 날짜 테스트"""
        birth_info = BirthInfo(
            name="윤년생",
            birth_date=date(2000, 2, 29),  # 윤년
            birth_time=time(12, 0),
            gender=Gender.FEMALE,
            birth_place="서울"
        )

        signal = create_daily_rhythm(birth_info, date(2026, 1, 20))
        assert signal is not None

    def test_midnight_birth_time(self):
        """자정 출생 시간 테스트"""
        birth_info = BirthInfo(
            name="자정생",
            birth_date=date(1990, 1, 1),
            birth_time=time(0, 0),
            gender=Gender.MALE,
            birth_place="서울"
        )

        signal = create_daily_rhythm(birth_info, date(2026, 1, 20))
        assert signal is not None

    def test_year_end_date(self):
        """연말 날짜 테스트"""
        birth_info = BirthInfo(
            name="연말생",
            birth_date=date(1995, 12, 31),
            birth_time=time(23, 59),
            gender=Gender.FEMALE,
            birth_place="제주"
        )

        signal = create_daily_rhythm(birth_info, date(2026, 12, 31))
        assert signal is not None
        assert signal.date == date(2026, 12, 31)


# ============================================================================
# 실행 가이드
# ============================================================================
"""
테스트 실행 방법:

1. 전체 테스트 실행:
   pytest tests/test_rhythm.py -v

2. 특정 클래스만 테스트:
   pytest tests/test_rhythm.py::TestRhythmAnalyzer -v

3. 특정 테스트만 실행:
   pytest tests/test_rhythm.py::TestRhythmAnalyzer::test_generate_daily_signal -v

4. 커버리지 확인:
   pytest tests/test_rhythm.py --cov=src/rhythm --cov-report=html

5. 상세 출력:
   pytest tests/test_rhythm.py -v -s
"""
