"""
PDF Generator 테스트 스크립트
"""
import sys
import os
from pathlib import Path
import datetime

# pdf-generator 디렉토리를 PYTHONPATH에 추가
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from generator import PDFGenerator


def test_daily_pdf():
    """일간 PDF 생성 테스트"""
    print("=" * 60)
    print("일간 PDF 생성 테스트")
    print("=" * 60)

    # 샘플 일간 콘텐츠 (실제 assemble_daily_content 출력 형식)
    sample_daily_content = {
        "date": "2026-01-21",
        "summary": "오늘은 안정적인 에너지가 흐르는 날입니다. 균형잡힌 리듬 속에서 계획적인 실행과 조율에 좋은 흐름이 형성되어 있습니다.",
        "keywords": ["균형", "집중", "학습", "관계", "소통"],
        "rhythm_description": "오늘의 흐름은 안정적입니다. 에너지가 균형을 이루어 계획적인 실행과 조율에 좋은 흐름입니다. 무리하게 욕심내기보다는 현재 가진 것들을 차분히 다듬고 정리하는 시간으로 활용하면 좋습니다.",
        "focus_caution": {
            "focus": [
                "중요한 작업에 대한 깊은 집중",
                "관계 형성과 네트워킹",
                "장기 계획 수립"
            ],
            "caution": [
                "과도한 욕심이나 조급함",
                "불필요한 갈등 유발"
            ]
        },
        "action_guide": {
            "do": [
                "일상 업무를 차분히 처리하기",
                "계획 점검 및 정리",
                "중요한 사람과의 대화 시간 갖기"
            ],
            "avoid": [
                "충동적 선택",
                "불필요한 갈등",
                "과도한 멀티태스킹"
            ]
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
            "phrase": "지금 이대로 충분하다",
            "how_to": "평온한 에너지 속에서 양손을 앞으로 펴고 좌우 균형을 느껴보세요."
        },
        "meaning_shift": "평범한 하루라는 느낌은 오히려 안정의 증거입니다. 특별한 사건이 없다는 것은 조화로운 흐름 속에 있다는 의미입니다.",
        "rhythm_question": "오늘 하루 동안 가장 소중하게 여기고 싶은 순간은 무엇인가요?"
    }

    # PDF Generator 초기화
    generator = PDFGenerator()

    # 출력 경로 설정
    output_dir = Path(__file__).parent / "test_output"
    output_dir.mkdir(exist_ok=True)

    # 역할별 PDF 생성 테스트
    roles = [None, "student", "office_worker", "freelancer"]
    role_names = {
        None: "중립",
        "student": "학생",
        "office_worker": "직장인",
        "freelancer": "프리랜서"
    }

    for role in roles:
        role_name = role_names[role]
        filename = f"daily_2026-01-21_{role or 'neutral'}.pdf"
        output_path = str(output_dir / filename)

        print(f"\n[{role_name}] PDF 생성 중...")
        try:
            result_path = generator.generate_daily_pdf(
                content=sample_daily_content,
                output_path=output_path,
                role=role
            )
            print(f"  ✅ 성공: {result_path}")

            # 파일 크기 확인
            file_size = os.path.getsize(result_path)
            print(f"  파일 크기: {file_size:,} bytes")

        except Exception as e:
            print(f"  ❌ 실패: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 60)
    print(f"테스트 완료! 출력 디렉토리: {output_dir}")
    print("=" * 60)


def test_monthly_pdf():
    """월간 PDF 생성 테스트 (기본 구조만)"""
    print("\n" + "=" * 60)
    print("월간 PDF 생성 테스트 (기본 템플릿)")
    print("=" * 60)

    # 월간 콘텐츠는 아직 미정의 상태 (Phase 3 예정)
    sample_monthly_content = {}

    generator = PDFGenerator()
    output_dir = Path(__file__).parent / "test_output"
    output_path = str(output_dir / "monthly_2026-01.pdf")

    print(f"\n월간 PDF 생성 중...")
    try:
        result_path = generator.generate_monthly_pdf(
            year=2026,
            month=1,
            content=sample_monthly_content,
            output_path=output_path
        )
        print(f"  ✅ 성공: {result_path}")

        file_size = os.path.getsize(result_path)
        print(f"  파일 크기: {file_size:,} bytes")

    except Exception as e:
        print(f"  ❌ 실패: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 60)
    print("월간 PDF 테스트 완료")
    print("=" * 60)


if __name__ == "__main__":
    print("PDF Generator 통합 테스트 시작\n")

    # 일간 PDF 테스트
    test_daily_pdf()

    # 월간 PDF 테스트
    test_monthly_pdf()

    print("\n모든 PDF 생성 테스트 완료!")
