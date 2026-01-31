"""
색은식(五運六氣) 계산 모듈 테스트

테스트 대상:
1. calculate_five_movements() - 오운 계산
2. calculate_six_qi() - 육기 계산
3. integrate_with_energy_json() - energy.json 통합
4. generate_health_signals() - 건강 신호 생성
5. analyze_saekeunshik_summary() - 종합 요약
"""

import pytest
from datetime import date, time
from src.rhythm.saekeunshik import (
    calculate_five_movements,
    calculate_six_qi,
    integrate_with_energy_json,
    generate_health_signals,
    analyze_saekeunshik_summary,
    get_favorable_foods,
    get_rest_times_by_qi,
    STEM_TO_FIVE_MOVEMENTS,
    BRANCH_TO_SICHEON,
)


# ==================== 테스트 데이터 ====================
@pytest.fixture
def test_birth_year():
    """테스트용 출생 년도 (1971년)"""
    return 1971


@pytest.fixture
def test_target_date():
    """테스트용 분석 날짜 (2026년 1월 31일)"""
    return date(2026, 1, 31)


@pytest.fixture
def sample_energy_data():
    """테스트용 energy.json 데이터"""
    return {
        "사주": {
            "년주": {"천간": "甲", "지지": "子"},
            "월주": {"천간": "丙", "지지": "寅"},
            "일주": {"천간": "戊", "지지": "辰"},
            "시주": {"천간": "庚", "지지": "午"},
        },
        "오행": {"목": 2, "화": 1, "토": 3, "금": 2, "수": 1},
        "에너지_수준": 4,
        "집중력": 3,
        "사회운": 5,
    }


# ==================== 오운 계산 테스트 ====================
class TestFiveMovements:
    """오운(五運) 계산 테스트"""

    def test_calculate_five_movements_basic(self, test_birth_year, test_target_date):
        """기본 오운 계산 테스트"""
        result = calculate_five_movements(test_birth_year, test_target_date)

        # 필수 필드 확인
        assert "year_movement" in result
        assert "month_movement" in result
        assert "day_movement" in result
        assert "year_stem" in result
        assert "month_stem" in result
        assert "day_stem" in result

        # 오운 값 유효성 확인
        valid_movements = ["木運", "火運", "土運", "金運", "水運"]
        assert result["year_movement"] in valid_movements
        assert result["month_movement"] in valid_movements
        assert result["day_movement"] in valid_movements

    def test_five_movements_stem_mapping(self):
        """천간-오운 매핑 정확도 테스트"""
        # 전체 10천간 매핑 확인
        assert STEM_TO_FIVE_MOVEMENTS["甲"] == "土運"
        assert STEM_TO_FIVE_MOVEMENTS["乙"] == "金運"
        assert STEM_TO_FIVE_MOVEMENTS["丙"] == "水運"
        assert STEM_TO_FIVE_MOVEMENTS["丁"] == "木運"
        assert STEM_TO_FIVE_MOVEMENTS["戊"] == "火運"
        assert STEM_TO_FIVE_MOVEMENTS["己"] == "土運"
        assert STEM_TO_FIVE_MOVEMENTS["庚"] == "金運"
        assert STEM_TO_FIVE_MOVEMENTS["辛"] == "水運"
        assert STEM_TO_FIVE_MOVEMENTS["壬"] == "木運"
        assert STEM_TO_FIVE_MOVEMENTS["癸"] == "火運"

    def test_five_movements_different_dates(self, test_birth_year):
        """다양한 날짜에서 오운 계산 일관성 테스트"""
        dates = [
            date(2026, 1, 1),   # 신년
            date(2026, 6, 15),  # 여름
            date(2026, 12, 31), # 연말
        ]

        for test_date in dates:
            result = calculate_five_movements(test_birth_year, test_date)
            assert result["day_movement"] in ["木運", "火運", "土運", "金運", "水運"]


# ==================== 육기 계산 테스트 ====================
class TestSixQi:
    """육기(六氣) 계산 테스트"""

    def test_calculate_six_qi_basic(self, test_birth_year, test_target_date):
        """기본 육기 계산 테스트"""
        result = calculate_six_qi(test_birth_year, test_target_date)

        # 필수 필드 확인
        assert "sicheon" in result
        assert "jaecheon" in result
        assert "dominant_qi" in result
        assert "year_branch" in result
        assert "month_branch" in result
        assert "qi_phase" in result

        # 육기 값 유효성 확인
        valid_qi = ["厥陰風木", "少陰君火", "少陽相火", "太陰濕土", "陽明燥金", "太陽寒水"]
        assert result["sicheon"] in valid_qi
        assert result["jaecheon"] in valid_qi
        assert result["dominant_qi"] in valid_qi

    def test_sicheon_branch_mapping(self):
        """지지-사천 매핑 정확도 테스트"""
        assert BRANCH_TO_SICHEON["子"] == "少陰君火"
        assert BRANCH_TO_SICHEON["丑"] == "太陰濕土"
        assert BRANCH_TO_SICHEON["寅"] == "少陽相火"
        assert BRANCH_TO_SICHEON["卯"] == "陽明燥金"
        assert BRANCH_TO_SICHEON["辰"] == "太陽寒水"
        assert BRANCH_TO_SICHEON["巳"] == "厥陰風木"

    def test_qi_phase_detection(self, test_birth_year):
        """상반기/하반기 구분 테스트"""
        # 상반기
        result_spring = calculate_six_qi(test_birth_year, date(2026, 3, 1))
        assert result_spring["qi_phase"] == "상반기"

        # 하반기
        result_fall = calculate_six_qi(test_birth_year, date(2026, 9, 1))
        assert result_fall["qi_phase"] == "하반기"

    def test_dominant_qi_by_month(self, test_birth_year):
        """월별 주기(主氣) 계산 테스트"""
        # 2월 (입춘~춘분): 궐음풍목
        result_feb = calculate_six_qi(test_birth_year, date(2026, 2, 15))
        assert result_feb["dominant_qi"] in ["厥陰風木", "少陰君火"]

        # 7월 (대서~추분): 태음습토
        result_july = calculate_six_qi(test_birth_year, date(2026, 7, 15))
        assert result_july["dominant_qi"] in ["少陽相火", "太陰濕土"]


# ==================== 건강 신호 생성 테스트 ====================
class TestHealthSignals:
    """건강 신호 생성 테스트"""

    def test_generate_health_signals_basic(self, test_birth_year, test_target_date):
        """기본 건강 신호 생성 테스트"""
        five_movements = calculate_five_movements(test_birth_year, test_target_date)
        six_qi = calculate_six_qi(test_birth_year, test_target_date)

        result = generate_health_signals(five_movements, six_qi, test_target_date)

        # 필수 필드 확인
        assert "energy_balance" in result
        assert "vulnerable_organs" in result
        assert "favorable_foods" in result
        assert "caution_activities" in result
        assert "recommended_rest_times" in result
        assert "seasonal_nature" in result

        # 에너지 균형 값 확인
        assert result["energy_balance"] in ["조화", "과잉", "부족"]

        # 장부 목록 확인
        assert len(result["vulnerable_organs"]) >= 1

        # 음식/활동 목록 확인
        assert len(result["favorable_foods"]) >= 1
        assert len(result["caution_activities"]) >= 1

    def test_favorable_foods_by_movement(self):
        """오운별 권장 음식 테스트"""
        foods_wood = get_favorable_foods("木運", "厥陰風木")
        assert "녹색 채소" in foods_wood

        foods_fire = get_favorable_foods("火運", "少陰君火")
        assert "붉은 과일" in foods_fire

        foods_earth = get_favorable_foods("土運", "太陰濕土")
        assert "곡물" in foods_earth

    def test_rest_times_by_qi(self):
        """육기별 휴식 시간 테스트"""
        rest_spring = get_rest_times_by_qi("厥陰風木")
        assert len(rest_spring) >= 1
        assert any("시" in time for time in rest_spring)


# ==================== energy.json 통합 테스트 ====================
class TestIntegration:
    """energy.json 통합 테스트"""

    def test_integrate_with_energy_json(
        self,
        sample_energy_data,
        test_birth_year,
        test_target_date
    ):
        """energy.json에 색은식 데이터 통합 테스트"""
        result = integrate_with_energy_json(
            sample_energy_data,
            test_birth_year,
            test_target_date
        )

        # 기존 데이터 보존 확인
        assert "사주" in result
        assert "오행" in result
        assert "에너지_수준" in result

        # 색은식 필드 추가 확인
        assert "saekeunshik" in result

        saekeunshik = result["saekeunshik"]
        assert "five_movements" in saekeunshik
        assert "six_qi" in saekeunshik
        assert "health_signals" in saekeunshik
        assert "calculation_date" in saekeunshik

        # 계산 날짜 확인
        assert saekeunshik["calculation_date"] == test_target_date.isoformat()

    def test_integration_preserves_structure(self, sample_energy_data, test_birth_year, test_target_date):
        """통합 시 기존 구조 보존 테스트"""
        original_keys = set(sample_energy_data.keys())

        result = integrate_with_energy_json(
            sample_energy_data,
            test_birth_year,
            test_target_date
        )

        # 기존 키는 모두 보존되어야 함
        for key in original_keys:
            assert key in result

        # 새 키 추가 확인
        assert "saekeunshik" in result


# ==================== 종합 분석 테스트 ====================
class TestSummary:
    """종합 분석 요약 테스트"""

    def test_analyze_saekeunshik_summary(self, test_birth_year, test_target_date):
        """색은식 종합 분석 요약 테스트"""
        result = analyze_saekeunshik_summary(test_birth_year, test_target_date)

        # 필수 필드 확인
        assert "date" in result
        assert "five_movements_summary" in result
        assert "six_qi_summary" in result
        assert "health_advice" in result
        assert "energy_balance" in result
        assert "detailed_data" in result

        # 날짜 확인
        assert result["date"] == test_target_date.isoformat()

        # 요약 문구 유효성 확인
        assert len(result["five_movements_summary"]) > 0
        assert len(result["six_qi_summary"]) > 0
        assert len(result["health_advice"]) > 10

        # 상세 데이터 존재 확인
        detailed = result["detailed_data"]
        assert "five_movements" in detailed
        assert "six_qi" in detailed
        assert "health_signals" in detailed

    def test_summary_different_seasons(self, test_birth_year):
        """계절별 종합 분석 일관성 테스트"""
        seasons = [
            date(2026, 3, 21),   # 봄
            date(2026, 6, 21),   # 여름
            date(2026, 9, 21),   # 가을
            date(2026, 12, 21),  # 겨울
        ]

        for season_date in seasons:
            result = analyze_saekeunshik_summary(test_birth_year, season_date)

            # 기본 구조 확인
            assert "date" in result
            assert "health_advice" in result
            assert result["energy_balance"] in ["조화", "과잉", "부족"]


# ==================== 엣지 케이스 테스트 ====================
class TestEdgeCases:
    """엣지 케이스 테스트"""

    def test_leap_year_handling(self, test_birth_year):
        """윤년 처리 테스트"""
        leap_date = date(2024, 2, 29)  # 윤년
        result = calculate_five_movements(test_birth_year, leap_date)

        assert "day_movement" in result
        assert result["day_movement"] in ["木運", "火運", "土運", "金運", "水運"]

    def test_year_boundary_dates(self, test_birth_year):
        """년 경계 날짜 테스트"""
        new_year = date(2026, 1, 1)
        year_end = date(2026, 12, 31)

        result_new = calculate_six_qi(test_birth_year, new_year)
        result_end = calculate_six_qi(test_birth_year, year_end)

        # 둘 다 정상 계산되어야 함
        assert "dominant_qi" in result_new
        assert "dominant_qi" in result_end

    def test_ancient_birth_year(self):
        """오래된 출생 년도 처리 테스트"""
        ancient_year = 1900
        result = calculate_five_movements(ancient_year, date(2026, 1, 1))

        # 정상 계산되어야 함
        assert "year_movement" in result

    def test_future_date(self, test_birth_year):
        """미래 날짜 처리 테스트"""
        future_date = date(2030, 12, 31)
        result = analyze_saekeunshik_summary(test_birth_year, future_date)

        # 정상 분석되어야 함
        assert "date" in result
        assert result["date"] == future_date.isoformat()


# ==================== 성능 테스트 ====================
class TestPerformance:
    """성능 테스트"""

    def test_bulk_calculation_performance(self, test_birth_year):
        """대량 계산 성능 테스트"""
        import time

        # 100일치 계산
        dates = [date(2026, 1, day) for day in range(1, 32)]  # 1월 전체

        start_time = time.time()

        for test_date in dates:
            calculate_five_movements(test_birth_year, test_date)
            calculate_six_qi(test_birth_year, test_date)

        elapsed = time.time() - start_time

        # 1월 전체 (31일) 계산이 10초 이내에 완료되어야 함
        assert elapsed < 10.0, f"성능 저하: {elapsed}초 소요 (예상: < 10초)"


# ==================== 통합 시나리오 테스트 ====================
class TestIntegrationScenarios:
    """실제 사용 시나리오 테스트"""

    def test_full_daily_analysis_workflow(self, test_birth_year, test_target_date, sample_energy_data):
        """일간 분석 전체 워크플로우 테스트"""
        # 1. 오운 계산
        five_movements = calculate_five_movements(test_birth_year, test_target_date)
        assert "day_movement" in five_movements

        # 2. 육기 계산
        six_qi = calculate_six_qi(test_birth_year, test_target_date)
        assert "dominant_qi" in six_qi

        # 3. 건강 신호 생성
        health_signals = generate_health_signals(five_movements, six_qi, test_target_date)
        assert "vulnerable_organs" in health_signals

        # 4. energy.json 통합
        result = integrate_with_energy_json(sample_energy_data, test_birth_year, test_target_date)
        assert "saekeunshik" in result

        # 5. 종합 요약
        summary = analyze_saekeunshik_summary(test_birth_year, test_target_date)
        assert "health_advice" in summary

        # 전체 파이프라인 성공
        assert True

    def test_monthly_batch_analysis(self, test_birth_year):
        """월간 배치 분석 시나리오"""
        import calendar

        year = 2026
        month = 1
        days_in_month = calendar.monthrange(year, month)[1]

        results = []

        for day in range(1, days_in_month + 1):
            target_date = date(year, month, day)
            summary = analyze_saekeunshik_summary(test_birth_year, target_date)
            results.append(summary)

        # 전체 월 분석 성공
        assert len(results) == days_in_month

        # 각 결과 유효성 확인
        for result in results:
            assert "health_advice" in result
            assert "energy_balance" in result
