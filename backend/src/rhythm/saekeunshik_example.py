"""
색은식(五運六氣) 계산 예시 스크립트

실행 방법:
    python -m src.rhythm.saekeunshik_example
"""

from datetime import date
from typing import Dict, Any


def create_mock_saju_data() -> Dict[str, Any]:
    """
    목(Mock) 사주 데이터 생성
    실제로는 saju.calculate_saju()의 결과를 사용
    """
    return {
        "사주": {
            "년주": {"천간": "辛", "지지": "亥", "간지": "辛亥"},
            "월주": {"천간": "己", "지지": "亥", "간지": "己亥"},
            "일주": {"천간": "丙", "지지": "寅", "간지": "丙寅"},
            "시주": {"천간": "戊", "지지": "辰", "간지": "戊辰"},
        },
        "오행": {"목": 2, "화": 2, "토": 3, "금": 2, "수": 2},
        "십성": {"비견": 1, "겁재": 0, "식신": 2, "상관": 1},
        "격국": {
            "일간": "丙",
            "일간오행": "화",
            "강약": "중화",
            "계절": "겨울",
        },
        "용신": {
            "용신": ["목", "화"],
            "기신": ["금", "수"],
        },
        "에너지_수준": 4,
        "집중력": 3,
        "사회운": 4,
    }


def example_basic_calculation():
    """기본 계산 예시"""
    print("=" * 70)
    print("예시 1: 기본 오운육기 계산")
    print("=" * 70)

    from .saekeunshik import (
        calculate_five_movements,
        calculate_six_qi,
    )

    birth_year = 1971
    target_date = date(2026, 1, 31)

    # 오운 계산
    print(f"\n분석 날짜: {target_date}")
    print(f"출생 년도: {birth_year}")

    five_movements = calculate_five_movements(birth_year, target_date)
    print(f"\n【오운(五運)】")
    print(f"  년운: {five_movements['year_movement']} (천간: {five_movements['year_stem']})")
    print(f"  월운: {five_movements['month_movement']} (천간: {five_movements['month_stem']})")
    print(f"  일운: {five_movements['day_movement']} (천간: {five_movements['day_stem']})")

    # 육기 계산
    six_qi = calculate_six_qi(birth_year, target_date)
    print(f"\n【육기(六氣)】")
    print(f"  사천(司天): {six_qi['sicheon']} - 상반기 주도 기운")
    print(f"  재천(在泉): {six_qi['jaecheon']} - 하반기 주도 기운")
    print(f"  주기(主氣): {six_qi['dominant_qi']} - 현재 월 기본 기운")
    print(f"  기운 단계: {six_qi['qi_phase']}")


def example_health_signals():
    """건강 신호 생성 예시"""
    print("\n\n" + "=" * 70)
    print("예시 2: 건강 신호 생성")
    print("=" * 70)

    from .saekeunshik import (
        calculate_five_movements,
        calculate_six_qi,
        generate_health_signals,
    )

    birth_year = 1971
    target_date = date(2026, 1, 31)

    five_movements = calculate_five_movements(birth_year, target_date)
    six_qi = calculate_six_qi(birth_year, target_date)
    health = generate_health_signals(five_movements, six_qi, target_date)

    print(f"\n분석 날짜: {target_date}")
    print(f"\n【건강 신호】")
    print(f"  에너지 균형: {health['energy_balance']}")
    print(f"  취약 장부: {', '.join(health['vulnerable_organs'])}")
    print(f"  권장 음식: {', '.join(health['favorable_foods'])}")
    print(f"  주의 활동: {', '.join(health['caution_activities'])}")
    print(f"  권장 휴식: {', '.join(health['recommended_rest_times'])}")
    print(f"  계절 특성: {health['seasonal_nature']} ({health['season_context']})")


def example_integration():
    """energy.json 통합 예시"""
    print("\n\n" + "=" * 70)
    print("예시 3: 기존 에너지 데이터 통합")
    print("=" * 70)

    from .saekeunshik import integrate_with_energy_json

    birth_year = 1971
    target_date = date(2026, 1, 31)

    # 기존 에너지 데이터
    energy_data = create_mock_saju_data()

    print(f"\n분석 날짜: {target_date}")
    print(f"\n【통합 전 데이터 구조】")
    print(f"  키 목록: {', '.join(energy_data.keys())}")

    # 색은식 데이터 통합
    result = integrate_with_energy_json(energy_data, birth_year, target_date)

    print(f"\n【통합 후 데이터 구조】")
    print(f"  키 목록: {', '.join(result.keys())}")
    print(f"\n【색은식 섹션】")
    saekeunshik = result["saekeunshik"]
    print(f"  오운: {saekeunshik['five_movements']['day_movement']}")
    print(f"  육기: {saekeunshik['six_qi']['dominant_qi']}")
    print(f"  건강 균형: {saekeunshik['health_signals']['energy_balance']}")
    print(f"  계산 날짜: {saekeunshik['calculation_date']}")


def example_summary():
    """종합 요약 예시"""
    print("\n\n" + "=" * 70)
    print("예시 4: 색은식 종합 요약")
    print("=" * 70)

    from .saekeunshik import analyze_saekeunshik_summary

    birth_year = 1971
    target_date = date(2026, 1, 31)

    summary = analyze_saekeunshik_summary(birth_year, target_date)

    print(f"\n【종합 요약 리포트】")
    print(f"  날짜: {summary['date']}")
    print(f"\n  오운 요약:")
    print(f"    {summary['five_movements_summary']}")
    print(f"\n  육기 요약:")
    print(f"    {summary['six_qi_summary']}")
    print(f"\n  건강 조언:")
    print(f"    {summary['health_advice']}")
    print(f"\n  에너지 균형: {summary['energy_balance']}")


def example_monthly_batch():
    """월간 배치 분석 예시"""
    print("\n\n" + "=" * 70)
    print("예시 5: 월간 배치 분석 (2026년 1월)")
    print("=" * 70)

    import calendar
    from .saekeunshik import analyze_saekeunshik_summary

    birth_year = 1971
    year = 2026
    month = 1

    days_in_month = calendar.monthrange(year, month)[1]

    print(f"\n【2026년 1월 일간 리듬 요약】")
    print("-" * 70)
    print(f"{'날짜':<12} {'일운':<10} {'주기':<15} {'균형':<8}")
    print("-" * 70)

    for day in range(1, min(8, days_in_month + 1)):  # 첫 주만 출력
        target_date = date(year, month, day)
        summary = analyze_saekeunshik_summary(birth_year, target_date)

        # 간단한 표시
        date_str = summary["date"]
        movement = summary["five_movements_summary"].split(" - ")[0]
        qi = summary["six_qi_summary"].split(" - ")[0]
        balance = summary["energy_balance"]

        print(f"{date_str:<12} {movement:<10} {qi:<15} {balance:<8}")

    print("-" * 70)
    print(f"(총 {days_in_month}일 중 첫 7일만 표시)")


def example_seasonal_comparison():
    """계절별 비교 예시"""
    print("\n\n" + "=" * 70)
    print("예시 6: 계절별 오운육기 비교")
    print("=" * 70)

    from .saekeunshik import analyze_saekeunshik_summary

    birth_year = 1971

    seasons = [
        ("봄", date(2026, 3, 21)),
        ("여름", date(2026, 6, 21)),
        ("가을", date(2026, 9, 21)),
        ("겨울", date(2026, 12, 21)),
    ]

    print(f"\n【2026년 계절별 리듬 비교】")
    print("-" * 70)

    for season_name, season_date in seasons:
        summary = analyze_saekeunshik_summary(birth_year, season_date)

        print(f"\n■ {season_name} ({summary['date']})")
        print(f"  오운: {summary['five_movements_summary']}")
        print(f"  육기: {summary['six_qi_summary']}")
        print(f"  균형: {summary['energy_balance']}")

        # 건강 신호 상세
        detailed = summary["detailed_data"]["health_signals"]
        print(f"  취약: {', '.join(detailed['vulnerable_organs'])}")
        print(f"  권장: {', '.join(detailed['favorable_foods'][:2])}")


def main():
    """전체 예시 실행"""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "     색은식(五運六氣) 계산 모듈 - 사용 예시          ".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "=" * 68 + "╝")

    try:
        example_basic_calculation()
        example_health_signals()
        example_integration()
        example_summary()
        example_monthly_batch()
        example_seasonal_comparison()

        print("\n\n" + "=" * 70)
        print("모든 예시 실행 완료!")
        print("=" * 70)
        print("\n자세한 사용법은 SAEKEUNSHIK_USAGE.md를 참조하세요.\n")

    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        print("\n참고: 이 예시는 사주 계산 엔진이 필요합니다.")
        print("      독립 테스트는 test_saekeunshik_standalone.py를 실행하세요.\n")


if __name__ == "__main__":
    main()
