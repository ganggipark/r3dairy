"""
Content Assembly Engine 테스트

리듬 신호를 사용자 노출 콘텐츠로 변환하는 기능을 테스트합니다.
"""
import datetime
from src.rhythm.models import BirthInfo, Gender
from src.rhythm.saju import (
    calculate_saju,
    analyze_daily_fortune,
    analyze_monthly_rhythm,
    analyze_yearly_rhythm
)
from src.content.assembly import (
    assemble_daily_content,
    assemble_monthly_content,
    assemble_yearly_content
)
from src.content.validator import (
    validate_daily_content,
    validate_monthly_content,
    validate_yearly_content
)
import json


def test_daily_content_assembly():
    """일간 콘텐츠 조립 테스트"""
    print("=" * 60)
    print("일간 콘텐츠 조립 테스트")
    print("=" * 60)

    # 1. 리듬 분석
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

        # 2. 콘텐츠 조립
        print("\n[단계 1] 콘텐츠 조립 중...")
        daily_content = assemble_daily_content(target_date, saju_result, daily_rhythm)

        # 3. 스키마 검증
        print("[단계 2] 스키마 검증 중...")
        is_valid, errors = validate_daily_content(daily_content)

        if is_valid:
            print("[OK] 스키마 검증 통과!")
        else:
            print(f"[ERROR] 스키마 검증 실패: {len(errors)}개 오류")
            for error in errors:
                print(f"  - {error}")
            return False

        # 4. 콘텐츠 출력
        print("\n[단계 3] 생성된 콘텐츠:")
        print(f"\n날짜: {daily_content['date']}")
        print(f"\n요약: {daily_content['summary']}")
        print(f"\n키워드: {', '.join(daily_content['keywords'])}")
        print(f"\n리듬 해설 ({len(daily_content['rhythm_description'])}자):")
        print(f"  {daily_content['rhythm_description']}")

        print(f"\n집중 포인트:")
        for item in daily_content['focus_caution']['focus']:
            print(f"  - {item}")

        print(f"\n주의 포인트:")
        for item in daily_content['focus_caution']['caution']:
            print(f"  - {item}")

        print(f"\nDo 가이드:")
        for item in daily_content['action_guide']['do']:
            print(f"  + {item}")

        print(f"\nAvoid 가이드:")
        for item in daily_content['action_guide']['avoid']:
            print(f"  - {item}")

        print(f"\n시간/방향 정보:")
        td = daily_content['time_direction']
        print(f"  유리한 시간: {td['good_time']}")
        print(f"  주의 시간: {td['avoid_time']}")
        print(f"  유리한 방향: {td['good_direction']}")
        print(f"  노트: {td['notes']}")

        print(f"\n상태 트리거:")
        st = daily_content['state_trigger']
        print(f"  동작: {st['gesture']}")
        print(f"  문구: {st['phrase']}")
        print(f"  방법: {st['how_to']}")

        print(f"\n의미 전환 ({len(daily_content['meaning_shift'])}자):")
        print(f"  {daily_content['meaning_shift']}")

        print(f"\n리듬 질문:")
        print(f"  {daily_content['rhythm_question']}")

        # 5. 총 글자 수 확인
        from src.content.validator import _calculate_left_page_length
        total_chars = _calculate_left_page_length(daily_content)
        print(f"\n[OK] 좌측 페이지 총 글자 수: {total_chars}자")

        print("\n[OK] 일간 콘텐츠 조립 성공!")
        return True

    except Exception as e:
        print(f"\n[ERROR] 일간 콘텐츠 조립 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_monthly_content_assembly():
    """월간 콘텐츠 조립 테스트"""
    print("\n\n" + "=" * 60)
    print("월간 콘텐츠 조립 테스트")
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

        print("\n[단계 1] 월간 콘텐츠 조립 중...")
        monthly_content = assemble_monthly_content(year, month, monthly_rhythm)

        print("[단계 2] 스키마 검증 중...")
        is_valid, errors = validate_monthly_content(monthly_content)

        if is_valid:
            print("[OK] 스키마 검증 통과!")
        else:
            print(f"[ERROR] 스키마 검증 실패: {errors}")
            return False

        print("\n[단계 3] 생성된 월간 콘텐츠:")
        print(f"년월: {monthly_content['year_month']}")
        print(f"테마: {monthly_content['theme']}")
        print(f"우선순위: {', '.join(monthly_content['priorities'])}")
        print(f"일별 에너지 데이터: {len(monthly_content['calendar_data'])}일")

        print("\n[OK] 월간 콘텐츠 조립 성공!")
        return True

    except Exception as e:
        print(f"\n[ERROR] 월간 콘텐츠 조립 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_yearly_content_assembly():
    """연간 콘텐츠 조립 테스트"""
    print("\n\n" + "=" * 60)
    print("연간 콘텐츠 조립 테스트")
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

        print("\n[단계 1] 연간 콘텐츠 조립 중...")
        yearly_content = assemble_yearly_content(year, yearly_rhythm)

        print("[단계 2] 스키마 검증 중...")
        is_valid, errors = validate_yearly_content(yearly_content)

        if is_valid:
            print("[OK] 스키마 검증 통과!")
        else:
            print(f"[ERROR] 스키마 검증 실패: {errors}")
            return False

        print("\n[단계 3] 생성된 연간 콘텐츠:")
        print(f"년도: {yearly_content['year']}")
        print(f"테마: {yearly_content['theme']}")
        print(f"전체 흐름: {yearly_content['flow_summary']}")
        print(f"월별 신호: {len(yearly_content['monthly_signals'])}개월")

        print("\n[OK] 연간 콘텐츠 조립 성공!")
        return True

    except Exception as e:
        print(f"\n[ERROR] 연간 콘텐츠 조립 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("Content Assembly Engine 통합 테스트 시작\n")

    results = []
    results.append(test_daily_content_assembly())
    results.append(test_monthly_content_assembly())
    results.append(test_yearly_content_assembly())

    print("\n" + "=" * 60)
    if all(results):
        print("[OK] 모든 Content Assembly 테스트 통과!")
    else:
        print("[ERROR] 일부 테스트 실패")
    print("=" * 60)
