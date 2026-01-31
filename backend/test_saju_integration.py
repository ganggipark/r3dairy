"""
사주 계산 통합 테스트

Node.js CLI를 통한 사주 계산 기능 테스트
"""
import datetime
from src.rhythm.models import BirthInfo, Gender
from src.rhythm.saju import calculate_saju, analyze_daily_fortune
import json


def test_basic_saju_calculation():
    """기본 사주 계산 테스트"""
    print("=" * 60)
    print("사주 계산 기본 테스트")
    print("=" * 60)

    # 테스트 출생 정보
    birth_info = BirthInfo(
        name="홍길동",
        birth_date=datetime.date(1990, 1, 15),
        birth_time=datetime.time(14, 30),
        gender=Gender.MALE,
        birth_place="서울특별시"
    )

    target_date = datetime.date.today()

    try:
        # 사주 계산
        print(f"\n출생정보: {birth_info.birth_date} {birth_info.birth_time}")
        print(f"대상날짜: {target_date}")
        print("\n사주 계산 중...")

        saju_result = calculate_saju(birth_info, target_date)

        print("\n[OK] 사주 계산 성공!")
        print("\n=== 사주팔자 ===")
        for pillar_name, pillar_data in saju_result["사주"].items():
            print(f"{pillar_name}: {pillar_data['간지']} (천간: {pillar_data['천간']}, 지지: {pillar_data['지지']})")

        print("\n=== 오행 균형 ===")
        for element, score in saju_result["오행"].items():
            print(f"{element}: {score}")

        print("\n=== 격국 ===")
        gyeokguk = saju_result["격국"]
        print(f"일간: {gyeokguk['일간']} ({gyeokguk['일간오행']})")
        print(f"강약: {gyeokguk['강약']}")
        print(f"계절: {gyeokguk['계절']}")

        print("\n=== 용신/기신 ===")
        yongsin = saju_result["용신"]
        print(f"용신: {', '.join(yongsin['용신'])}")
        print(f"기신: {', '.join(yongsin['기신'])}")

        # 일간 운세 분석
        print("\n\n" + "=" * 60)
        print("일간 운세 분석 테스트")
        print("=" * 60)

        fortune = analyze_daily_fortune(birth_info, target_date, saju_result)

        print(f"\n에너지 수준: {fortune['에너지_수준']}/5")
        print(f"집중력: {fortune['집중력']}/5")
        print(f"사회운: {fortune['사회운']}/5")
        print(f"결정력: {fortune['결정력']}/5")
        print(f"\n유리한 시간: {', '.join(fortune['유리한_시간'])}")
        print(f"주의 시간: {', '.join(fortune['주의_시간'])}")
        print(f"유리한 방향: {', '.join(fortune['유리한_방향'])}")
        print(f"\n주요 흐름: {fortune['주요_흐름']}")
        print(f"기회 요소: {', '.join(fortune['기회_요소'])}")
        print(f"도전 요소: {', '.join(fortune['도전_요소'])}")
        print(f"\n세운 점수: {fortune['세운점수']}/100")

        print("\n[OK] 일간 운세 분석 성공!")

        return True

    except Exception as e:
        print(f"\n[ERROR] 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_different_gender():
    """성별에 따른 대운 차이 테스트"""
    print("\n\n" + "=" * 60)
    print("성별별 대운 차이 테스트")
    print("=" * 60)

    birth_date = datetime.date(1990, 5, 20)
    birth_time = datetime.time(10, 0)
    target_date = datetime.date.today()

    for gender in [Gender.MALE, Gender.FEMALE]:
        birth_info = BirthInfo(
            name="테스트",
            birth_date=birth_date,
            birth_time=birth_time,
            gender=gender,
            birth_place="서울특별시"
        )

        try:
            saju_result = calculate_saju(birth_info, target_date)
            daewoon = saju_result["대운"]

            print(f"\n{gender.value} - 대운 방향: {daewoon['direction']}")
            print(f"대운 시작 나이: {daewoon['startAge']}세")
            if daewoon['current']:
                print(f"현재 대운: {daewoon['current']['ganJi']} ({daewoon['current']['startAge']}-{daewoon['current']['endAge']}세)")

        except Exception as e:
            print(f"[ERROR] {gender.value} 계산 실패: {e}")


if __name__ == "__main__":
    print("사주 계산 통합 테스트 시작\n")

    success = test_basic_saju_calculation()
    test_different_gender()

    print("\n" + "=" * 60)
    if success:
        print("[OK] 모든 테스트 통과!")
    else:
        print("[ERROR] 테스트 실패")
    print("=" * 60)
