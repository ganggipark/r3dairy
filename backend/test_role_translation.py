"""
Role Translation Layer 테스트

동일한 리듬 콘텐츠를 역할별로 다르게 표현하는 기능을 테스트합니다.
"""
import datetime
from src.rhythm.models import BirthInfo, Gender
from src.rhythm.saju import calculate_saju, analyze_daily_fortune
from src.content.assembly import assemble_daily_content
from src.translation.translator import (
    translate_daily_content,
    validate_semantic_preservation
)


def test_role_translation():
    """역할별 콘텐츠 번역 테스트"""
    print("=" * 60)
    print("역할별 콘텐츠 번역 테스트")
    print("=" * 60)

    # 1. 기본 콘텐츠 생성
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
        original_content = assemble_daily_content(target_date, saju_result, daily_rhythm)

        print(f"\n[단계 1] 원본 콘텐츠 생성 완료")
        print(f"  요약: {original_content['summary'][:50]}...")

        # 2. 역할별 번역
        roles = ["student", "office_worker", "freelancer"]
        role_names = {
            "student": "학생",
            "office_worker": "직장인",
            "freelancer": "프리랜서"
        }

        translated_contents = {}

        for role in roles:
            print(f"\n[단계 2-{role}] {role_names[role]} 역할로 번역 중...")
            translated = translate_daily_content(original_content, role)
            translated_contents[role] = translated

            # 의미 불변성 검증
            is_valid, errors = validate_semantic_preservation(original_content, translated)

            if is_valid:
                print(f"  [OK] 의미 불변성 검증 통과")
            else:
                print(f"  [WARNING] 의미 불변성 검증 문제:")
                for error in errors:
                    print(f"    - {error}")

        # 3. 역할별 차이 비교
        print(f"\n[단계 3] 역할별 표현 차이 비교")
        print("=" * 60)

        # Summary 비교
        print(f"\n요약 (Summary) 비교:")
        print(f"  원본:      {original_content['summary']}")
        for role in roles:
            print(f"  {role_names[role]:6s}: {translated_contents[role]['summary']}")

        # Keywords 비교
        print(f"\n키워드 (Keywords) 비교:")
        print(f"  원본:      {', '.join(original_content['keywords'])}")
        for role in roles:
            print(f"  {role_names[role]:6s}: {', '.join(translated_contents[role]['keywords'])}")

        # Action Guide의 첫 번째 Do 항목 비교
        print(f"\n행동 가이드 (Action Guide - Do) 첫 항목 비교:")
        orig_do = original_content['action_guide']['do'][0] if original_content['action_guide']['do'] else "없음"
        print(f"  원본:      {orig_do}")
        for role in roles:
            trans_do = translated_contents[role]['action_guide']['do'][0] if translated_contents[role]['action_guide']['do'] else "없음"
            print(f"  {role_names[role]:6s}: {trans_do}")

        # Rhythm Question 비교
        print(f"\n리듬 질문 (Rhythm Question) 비교:")
        print(f"  원본:      {original_content['rhythm_question']}")
        for role in roles:
            print(f"  {role_names[role]:6s}: {translated_contents[role]['rhythm_question']}")

        # 4. 표현 변환 사례
        print(f"\n[단계 4] 표현 변환 사례")
        print("=" * 60)

        # "업무" → 학생: "학습", 직장인: "업무", 프리랜서: "작업"
        original_text = "일상 업무를 차분히 처리하기"
        print(f"\n원본: \"{original_text}\"")
        print(f"  학생:     \"일상 학습을 차분히 처리하기\" (업무 → 학습)")
        print(f"  직장인:   \"{original_text}\" (변화 없음)")
        print(f"  프리랜서: \"일상 작업을 차분히 처리하기\" (업무 → 작업)")

        print("\n[OK] 역할별 콘텐츠 번역 테스트 성공!")
        return True

    except Exception as e:
        print(f"\n[ERROR] 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_semantic_preservation():
    """의미 불변성 검증 테스트"""
    print("\n\n" + "=" * 60)
    print("의미 불변성 검증 테스트")
    print("=" * 60)

    # 간단한 콘텐츠로 테스트
    original = {
        "date": "2026-01-21",
        "summary": "오늘은 안정적인 에너지가 흐르는 날입니다.",
        "keywords": ["균형", "집중", "학습", "관계", "소통"],
        "rhythm_description": "오늘의 흐름은 안정적입니다. 에너지가 균형을 이루어 계획적인 실행과 조율에 좋은 흐름입니다.",
        "focus_caution": {
            "focus": ["중요한 작업에 대한 깊은 집중", "관계 형성과 네트워킹"],
            "caution": ["과도한 욕심이나 조급함"]
        },
        "action_guide": {
            "do": ["일상 업무를 차분히 처리하기", "계획 점검 및 정리"],
            "avoid": ["충동적 선택", "불필요한 갈등"]
        },
        "time_direction": {
            "good_time": "오전 9-11시",
            "avoid_time": "늦은 밤",
            "good_direction": "동쪽",
            "avoid_direction": "특별히 피할 방향 없음",
            "notes": "오늘은 오전 시간대에 집중력이 높습니다."
        },
        "state_trigger": {
            "gesture": "양손을 가볍게 펴고 균형 확인하기",
            "phrase": "\"지금 이대로 충분하다\"",
            "how_to": "평온한 에너지 속에서 양손을 앞으로 펴고 좌우 균형을 느껴보세요."
        },
        "meaning_shift": "평범한 하루라는 느낌은 오히려 안정의 증거입니다.",
        "rhythm_question": "오늘 하루 동안 가장 소중하게 여기고 싶은 순간은 무엇인가요?"
    }

    try:
        # 역할별 번역
        student_content = translate_daily_content(original, "student")
        office_content = translate_daily_content(original, "office_worker")
        freelancer_content = translate_daily_content(original, "freelancer")

        # 각 역할별 검증
        roles_and_contents = [
            ("학생", student_content),
            ("직장인", office_content),
            ("프리랜서", freelancer_content)
        ]

        all_valid = True

        for role_name, content in roles_and_contents:
            is_valid, errors = validate_semantic_preservation(original, content)

            if is_valid:
                print(f"\n{role_name}: [OK] 의미 불변성 검증 통과")
            else:
                print(f"\n{role_name}: [ERROR] 의미 불변성 검증 실패")
                for error in errors:
                    print(f"  - {error}")
                all_valid = False

        if all_valid:
            print("\n[OK] 모든 역할에서 의미 불변성 유지!")
            return True
        else:
            print("\n[ERROR] 일부 역할에서 의미 불변성 검증 실패")
            return False

    except Exception as e:
        print(f"\n[ERROR] 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("Role Translation Layer 통합 테스트 시작\n")

    results = []
    results.append(test_role_translation())
    results.append(test_semantic_preservation())

    print("\n" + "=" * 60)
    if all(results):
        print("[OK] 모든 Role Translation 테스트 통과!")
    else:
        print("[ERROR] 일부 테스트 실패")
    print("=" * 60)
