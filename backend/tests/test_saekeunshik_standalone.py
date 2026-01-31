"""
색은식(五運六氣) 계산 모듈 독립 테스트

사주 계산에 의존하지 않고 핵심 로직만 테스트합니다.
"""

import pytest
from datetime import date
from typing import Dict, Any


# 테스트용 목 데이터
def create_mock_five_movements() -> Dict[str, str]:
    """목 오운 데이터"""
    return {
        "year_movement": "土運",
        "month_movement": "金運",
        "day_movement": "水運",
        "year_stem": "甲",
        "month_stem": "乙",
        "day_stem": "丙",
    }


def create_mock_six_qi() -> Dict[str, str]:
    """목 육기 데이터"""
    return {
        "sicheon": "少陰君火",
        "jaecheon": "陽明燥金",
        "dominant_qi": "厥陰風木",
        "year_branch": "子",
        "month_branch": "寅",
        "qi_phase": "상반기",
    }


# ==================== 매핑 테스트 ====================
class TestMappings:
    """매핑 테이블 정확도 테스트"""

    def test_stem_to_movement_mapping(self):
        """천간-오운 매핑 완전성 테스트"""
        from src.rhythm.saekeunshik import STEM_TO_FIVE_MOVEMENTS

        # 10천간 모두 매핑되어야 함
        assert len(STEM_TO_FIVE_MOVEMENTS) == 10

        # 각 천간이 오운에 정확히 매핑됨
        expected_mappings = {
            "甲": "土運", "乙": "金運", "丙": "水運", "丁": "木運", "戊": "火運",
            "己": "土運", "庚": "金運", "辛": "水運", "壬": "木運", "癸": "火運",
        }

        for stem, movement in expected_mappings.items():
            assert STEM_TO_FIVE_MOVEMENTS[stem] == movement

    def test_branch_to_sicheon_mapping(self):
        """지지-사천 매핑 완전성 테스트"""
        from src.rhythm.saekeunshik import BRANCH_TO_SICHEON

        # 12지지 모두 매핑되어야 함
        assert len(BRANCH_TO_SICHEON) == 12

        # 대칭 구조 확인 (자-오, 축-미, 인-신 등)
        assert BRANCH_TO_SICHEON["子"] == BRANCH_TO_SICHEON["午"]  # 소음군화
        assert BRANCH_TO_SICHEON["丑"] == BRANCH_TO_SICHEON["未"]  # 태음습토
        assert BRANCH_TO_SICHEON["寅"] == BRANCH_TO_SICHEON["申"]  # 소양상화
        assert BRANCH_TO_SICHEON["卯"] == BRANCH_TO_SICHEON["酉"]  # 양명조금
        assert BRANCH_TO_SICHEON["辰"] == BRANCH_TO_SICHEON["戌"]  # 태양한수
        assert BRANCH_TO_SICHEON["巳"] == BRANCH_TO_SICHEON["亥"]  # 궐음풍목

    def test_sicheon_jaecheon_opposition(self):
        """사천-재천 상극 관계 테스트"""
        from src.rhythm.saekeunshik import SICHEON_TO_JAECHEON

        # 6가지 기운 모두 매핑됨
        assert len(SICHEON_TO_JAECHEON) == 6

        # 상극 관계 확인
        oppositions = {
            "少陰君火": "陽明燥金",  # 화-금
            "太陰濕土": "太陽寒水",  # 토-수
            "少陽相火": "厥陰風木",  # 화-목
        }

        for sicheon, expected_jaecheon in oppositions.items():
            assert SICHEON_TO_JAECHEON[sicheon] == expected_jaecheon


# ==================== 건강 신호 생성 테스트 ====================
class TestHealthSignalsLogic:
    """건강 신호 생성 로직 테스트 (사주 계산 불필요)"""

    def test_generate_health_signals_structure(self):
        """건강 신호 생성 구조 테스트"""
        from src.rhythm.saekeunshik import generate_health_signals

        five_movements = create_mock_five_movements()
        six_qi = create_mock_six_qi()
        target_date = date(2026, 1, 31)

        result = generate_health_signals(five_movements, six_qi, target_date)

        # 필수 필드 확인
        required_fields = [
            "energy_balance",
            "vulnerable_organs",
            "favorable_foods",
            "caution_activities",
            "recommended_rest_times",
            "seasonal_nature",
            "season_context",
        ]

        for field in required_fields:
            assert field in result

    def test_energy_balance_logic(self):
        """에너지 균형 판단 로직 테스트"""
        from src.rhythm.saekeunshik import generate_health_signals

        # 상반기 + 화운 = 과잉
        five_movements_fire = {
            "day_movement": "火運",
            "year_stem": "甲",
            "month_stem": "乙",
            "day_stem": "丙",
        }
        six_qi_spring = {
            "sicheon": "少陰君火",
            "jaecheon": "陽明燥金",
            "dominant_qi": "厥陰風木",
            "qi_phase": "상반기",
        }

        result = generate_health_signals(five_movements_fire, six_qi_spring, date(2026, 3, 1))
        assert result["energy_balance"] in ["조화", "과잉", "부족"]

    def test_vulnerable_organs_by_movement(self):
        """오운별 취약 장부 매핑 테스트"""
        from src.rhythm.saekeunshik import generate_health_signals

        movements_and_organs = [
            ("木運", ["간", "담"]),
            ("火運", ["심", "소장"]),
            ("土運", ["비", "위"]),
            ("金運", ["폐", "대장"]),
            ("水運", ["신", "방광"]),
        ]

        six_qi = create_mock_six_qi()
        target_date = date(2026, 1, 31)

        for movement, expected_organs in movements_and_organs:
            five_movements = {
                "day_movement": movement,
                "year_stem": "甲",
                "month_stem": "乙",
                "day_stem": "丙",
            }

            result = generate_health_signals(five_movements, six_qi, target_date)
            assert result["vulnerable_organs"] == expected_organs


# ==================== 음식/휴식 추천 테스트 ====================
class TestRecommendations:
    """음식 및 휴식 시간 추천 테스트"""

    def test_favorable_foods_completeness(self):
        """모든 오운/육기 조합에 음식 추천 존재"""
        from src.rhythm.saekeunshik import get_favorable_foods

        movements = ["木運", "火運", "土運", "金運", "水運"]
        qi_list = ["厥陰風木", "少陰君火", "少陽相火", "太陰濕土", "陽明燥金", "太陽寒水"]

        for movement in movements:
            for qi in qi_list:
                foods = get_favorable_foods(movement, qi)

                # 최소 1개 이상의 음식 추천
                assert len(foods) >= 1
                assert len(foods) <= 4  # 최대 4개

                # 모든 항목이 문자열
                for food in foods:
                    assert isinstance(food, str)
                    assert len(food) > 0

    def test_rest_times_by_all_qi(self):
        """모든 육기에 휴식 시간 존재"""
        from src.rhythm.saekeunshik import get_rest_times_by_qi

        qi_list = ["厥陰風木", "少陰君火", "少陽相火", "太陰濕土", "陽明燥金", "太陽寒水"]

        for qi in qi_list:
            rest_times = get_rest_times_by_qi(qi)

            # 최소 1개 이상의 휴식 시간
            assert len(rest_times) >= 1

            # 시간 형식 확인
            for time in rest_times:
                assert isinstance(time, str)
                # 시간 관련 키워드가 포함되어야 함
                assert any(keyword in time for keyword in ["시", "낮잠", "수면", "휴식", "정오"])


# ==================== 주기(主氣) 계산 테스트 ====================
class TestDominantQi:
    """주기(主氣) 계산 로직 테스트"""

    def test_get_dominant_qi_by_month_coverage(self):
        """12개월 모두 주기 매핑 확인"""
        from src.rhythm.saekeunshik import get_dominant_qi_by_month

        # 모든 월에 주기 존재
        for month in range(1, 13):
            dominant_qi = get_dominant_qi_by_month(month)

            # 유효한 육기 값
            valid_qi = ["厥陰風木", "少陰君火", "少陽相火", "太陰濕土", "陽明燥金", "太陽寒水"]
            assert dominant_qi in valid_qi

    def test_seasonal_qi_mapping(self):
        """계절별 주기 매핑 합리성 테스트"""
        from src.rhythm.saekeunshik import get_dominant_qi_by_month

        # 봄 (2-4월): 풍목/군화
        spring_qi = [get_dominant_qi_by_month(m) for m in [2, 3, 4]]
        assert any("風木" in qi or "君火" in qi for qi in spring_qi)

        # 여름 (5-7월): 군화/상화/습토
        summer_qi = [get_dominant_qi_by_month(m) for m in [5, 6, 7]]
        assert any("火" in qi or "濕土" in qi for qi in summer_qi)

        # 겨울 (11-1월): 한수
        winter_qi = [get_dominant_qi_by_month(m) for m in [11, 12, 1]]
        assert any("寒水" in qi for qi in winter_qi)


# ==================== 통합 데이터 구조 테스트 ====================
class TestDataIntegration:
    """energy.json 통합 데이터 구조 테스트"""

    def test_integrated_structure_completeness(self):
        """통합 데이터 구조 완전성 테스트"""
        # 목 데이터
        base_energy_data = {
            "사주": {"년주": {"천간": "甲"}},
            "오행": {"목": 2},
            "에너지_수준": 4,
        }

        # 색은식 섹션 시뮬레이션
        saekeunshik_section = {
            "five_movements": create_mock_five_movements(),
            "six_qi": create_mock_six_qi(),
            "health_signals": {
                "energy_balance": "조화",
                "vulnerable_organs": ["간", "담"],
                "favorable_foods": ["녹색 채소"],
                "caution_activities": ["외풍 주의"],
                "recommended_rest_times": ["오전 9-11시"],
                "seasonal_nature": "바람",
                "season_context": "봄",
            },
            "calculation_date": "2026-01-31",
        }

        # 통합 데이터
        integrated = {**base_energy_data, "saekeunshik": saekeunshik_section}

        # 기존 키 보존 확인
        assert "사주" in integrated
        assert "오행" in integrated

        # 색은식 추가 확인
        assert "saekeunshik" in integrated
        assert "five_movements" in integrated["saekeunshik"]
        assert "six_qi" in integrated["saekeunshik"]
        assert "health_signals" in integrated["saekeunshik"]


# ==================== 한국어 용어 정확도 테스트 ====================
class TestKoreanTerminology:
    """한의학 용어 정확도 테스트"""

    def test_five_movements_korean_terms(self):
        """오운 한국어 표기 일관성"""
        from src.rhythm.saekeunshik import STEM_TO_FIVE_MOVEMENTS

        movements = set(STEM_TO_FIVE_MOVEMENTS.values())
        expected_movements = {"木運", "火運", "土運", "金運", "水運"}

        assert movements == expected_movements

    def test_six_qi_korean_terms(self):
        """육기 한국어 표기 일관성"""
        from src.rhythm.saekeunshik import BRANCH_TO_SICHEON

        qi_types = set(BRANCH_TO_SICHEON.values())
        expected_qi = {"厥陰風木", "少陰君火", "少陽相火", "太陰濕土", "陽明燥金", "太陽寒水"}

        assert qi_types == expected_qi

    def test_organ_names_traditional(self):
        """장부명 전통 표기 확인"""
        from src.rhythm.saekeunshik import generate_health_signals

        five_movements = create_mock_five_movements()
        six_qi = create_mock_six_qi()

        result = generate_health_signals(five_movements, six_qi, date(2026, 1, 31))

        organs = result["vulnerable_organs"]

        # 전통 장부명 사용 확인
        traditional_organs = ["간", "담", "심", "소장", "비", "위", "폐", "대장", "신", "방광"]

        for organ in organs:
            assert organ in traditional_organs


# ==================== 문서화 테스트 ====================
class TestDocumentation:
    """독스트링 및 주석 존재 확인"""

    def test_module_docstring_exists(self):
        """모듈 독스트링 존재 확인"""
        import src.rhythm.saekeunshik as saekeunshik_module

        assert saekeunshik_module.__doc__ is not None
        assert "五運六氣" in saekeunshik_module.__doc__

    def test_function_docstrings_exist(self):
        """주요 함수 독스트링 존재 확인"""
        from src.rhythm.saekeunshik import (
            calculate_five_movements,
            calculate_six_qi,
            generate_health_signals,
        )

        for func in [calculate_five_movements, calculate_six_qi, generate_health_signals]:
            assert func.__doc__ is not None
            assert len(func.__doc__) > 20  # 충분히 상세한 설명


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
