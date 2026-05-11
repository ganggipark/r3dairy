"""Render a 7-day sample PDF using mock DailyContent (no API)."""
from pathlib import Path

from diary import DailyContent, render_diary


def _mock(date_str: str, color: str, direction: str, time_str: str) -> DailyContent:
    return DailyContent(
        date=date_str,
        lucky_color=color,
        lucky_direction=direction,
        lucky_time=time_str,
        daily_summary=(
            "오늘은 새로운 시작에 적합한 안정된 기운이 흐릅니다. "
            "차분히 한 걸음씩 나아가는 하루가 되겠습니다. "
            "주변 사람들과의 따뜻한 대화가 마음을 풍요롭게 해줄 거예요."
        ),
        daily_focus="작은 목표 하나를 정해 끝까지 마무리해 보세요. 성취감이 큰 힘이 됩니다.",
        daily_caution="조급함은 피하시고, 무리한 약속은 다음으로 미루는 것이 좋습니다.",
        mindfulness=(
            "오늘 한 번, 자신에게 따뜻한 말을 건네는 시간을 가져보세요. "
            "지금 이 순간의 호흡에 잠시 머물러도 좋습니다. "
            "완벽하지 않아도 괜찮다는 사실을 기억해 주세요."
        ),
        right_page_hint="오늘도 한 걸음, 충분히 잘하고 있어요.",
        recommended_actions=["산책 20분", "감사한 일 3가지 적기", "차 한 잔의 여유"],
        things_to_avoid=["과식", "충동 구매"],
    )


WEEK = [
    ("2026-05-15", "은백색", "서", "오전 11시–오후 1시"),
    ("2026-05-16", "청록색", "동", "오전 5시–7시"),
    ("2026-05-17", "주황색", "남", "오전 11시–오후 1시"),
    ("2026-05-18", "황금색", "중앙", "오후 1시–3시"),
    ("2026-05-19", "감청색", "북", "오후 11시–오전 1시"),
    ("2026-05-20", "청록색", "동남", "오전 7시–9시"),
    ("2026-05-21", "은백색", "서북", "오후 7시–9시"),
]


def main():
    days = [_mock(*row) for row in WEEK]
    output = Path("output/sample_week.pdf")
    result = render_diary(days, output, title="7일 샘플 다이어리")
    print(f"PDF 생성: {result.resolve()}")
    print(f"  크기: {result.stat().st_size:,} bytes")
    print(f"  페이지: {len(days) * 2}장 (1일 = 2페이지)")


if __name__ == "__main__":
    main()
