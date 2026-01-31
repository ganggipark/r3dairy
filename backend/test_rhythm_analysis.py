"""
Rhythm Analysis Engine 테스트

일간/월간/연간 리듬 분석 기능을 테스트합니다.
"""
import datetime
from src.rhythm.models import BirthInfo, Gender
from src.rhythm.saju import (
    calculate_saju,
    analyze_daily_fortune,
    analyze_monthly_rhythm,
    analyze_yearly_rhythm
)
import json


def test_daily_rhythm():
    """일간 리듬 분석 테스트"""
    print("=" * 60)
    print("일간 리듬 분석 테스트")
    print("=" * 60)

    birth_info = BirthInfo(
        name="테스트",
        birth_date=datetime.date(1990, 1, 15),
        birth_time=datetime.time(14, 30),
        gender=Gender.MALE,
        birth_place="서울특별시"
    )

    target_date = datetime.date(2026, 1, 21)

    try:
        saju_result = calculate_saju(birth_info, target_date)
        daily_rhythm = analyze_daily_fortune(birth_info, target_date, saju_result)

        print(f"\n대상 날짜: {target_date}")
        print(f"에너지 수준: {daily_rhythm['에너지_수준']}/5")
        print(f"집중력: {daily_rhythm['집중력']}/5")
        print(f"사회운: {daily_rhythm['사회운']}/5")
        print(f"결정력: {daily_rhythm['결정력']}/5")
        print(f"유리한 시간: {', '.join(daily_rhythm['유리한_시간'])}")
        print(f"주의 시간: {', '.join(daily_rhythm['주의_시간'])}")
        print(f"유리한 방향: {', '.join(daily_rhythm['유리한_방향'])}")

        print("\n[OK] 일간 리듬 분석 성공!")
        return True

    except Exception as e:
        print(f"\n[ERROR] 일간 리듬 분석 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_monthly_rhythm():
    """월간 리듬 분석 테스트"""
    print("\n\n" + "=" * 60)
    print("월간 리듬 분석 테스트")
    print("=" * 60)

    birth_info = BirthInfo(
        name="테스트",
        birth_date=datetime.date(1990, 1, 15),
        birth_time=datetime.time(14, 30),
        gender=Gender.MALE,
        birth_place="서울특별시"
    )

    target_date = datetime.date(2026, 1, 21)
    year = 2026
    month = 1

    try:
        saju_result = calculate_saju(birth_info, target_date)
        monthly_rhythm = analyze_monthly_rhythm(birth_info, year, month, saju_result)

        print(f"\n대상 기간: {monthly_rhythm['년월']}")
        print(f"주제: {monthly_rhythm['주제']}")
        print(f"우선순위:")
        for i, priority in enumerate(monthly_rhythm['우선순위'], 1):
            print(f"  {i}. {priority}")

        print(f"\n기회 요소: {', '.join(monthly_rhythm['기회_요소'])}")
        print(f"도전 요소: {', '.join(monthly_rhythm['도전_요소'])}")
        print(f"전체 흐름: {monthly_rhythm['전체_흐름']}")

        # 일별 에너지 샘플 (처음 7일)
        print(f"\n일별 에너지 (1-7일):")
        for day in range(1, 8):
            energy = monthly_rhythm['일별_에너지'].get(day, 3)
            print(f"  {day}일: {energy}/5")

        print("\n[OK] 월간 리듬 분석 성공!")
        return True

    except Exception as e:
        print(f"\n[ERROR] 월간 리듬 분석 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_yearly_rhythm():
    """연간 리듬 분석 테스트"""
    print("\n\n" + "=" * 60)
    print("연간 리듬 분석 테스트")
    print("=" * 60)

    birth_info = BirthInfo(
        name="테스트",
        birth_date=datetime.date(1990, 1, 15),
        birth_time=datetime.time(14, 30),
        gender=Gender.MALE,
        birth_place="서울특별시"
    )

    target_date = datetime.date(2026, 1, 21)
    year = 2026

    try:
        saju_result = calculate_saju(birth_info, target_date)
        yearly_rhythm = analyze_yearly_rhythm(birth_info, year, saju_result)

        print(f"\n대상 년도: {yearly_rhythm['년도']}")
        print(f"주제: {yearly_rhythm['주제']}")
        print(f"전체 흐름: {yearly_rhythm['전체_흐름']}")

        if yearly_rhythm['대운_정보']:
            daewoon = yearly_rhythm['대운_정보']
            print(f"\n현재 대운: {daewoon.get('ganJi')} ({daewoon.get('startAge')}-{daewoon.get('endAge')}세)")

        print(f"\n용신: {', '.join(yearly_rhythm['용신'])}")
        print(f"기신: {', '.join(yearly_rhythm['기신']) if yearly_rhythm['기신'] else '없음'}")

        print(f"\n핵심 과제:")
        for task in yearly_rhythm['핵심_과제']:
            print(f"  - {task}")

        # 월별 신호 샘플 (1-4월)
        print(f"\n월별 신호 (1-4월):")
        for month in range(1, 5):
            signal = yearly_rhythm['월별_신호'].get(month, {})
            print(f"  {month}월: {signal.get('테마')} (에너지: {signal.get('에너지')}/5)")

        print("\n[OK] 연간 리듬 분석 성공!")
        return True

    except Exception as e:
        print(f"\n[ERROR] 연간 리듬 분석 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("Rhythm Analysis Engine 통합 테스트 시작\n")

    results = []
    results.append(test_daily_rhythm())
    results.append(test_monthly_rhythm())
    results.append(test_yearly_rhythm())

    print("\n" + "=" * 60)
    if all(results):
        print("[OK] 모든 Rhythm Analysis 테스트 통과!")
    else:
        print("[ERROR] 일부 테스트 실패")
    print("=" * 60)
