"""Sample: 35-day book with cover + month divider (mock content, no API)."""
from datetime import date, timedelta
from pathlib import Path

from diary import DailyContent, render_diary


def _mock(d: date, color: str = "은백색") -> DailyContent:
    return DailyContent(
        date=d.isoformat(),
        lucky_color=color,
        lucky_direction="동",
        lucky_time="오전 7시–9시",
        daily_summary=(
            f"{d.month}월 {d.day}일은 안정된 흐름의 하루입니다. "
            "차분히 한 걸음씩 나아가세요. 주변과의 대화가 의미 있게 다가옵니다."
        ),
        daily_focus="작은 목표 하나에 집중하고, 그것을 마무리하세요.",
        daily_caution="조급함과 무리한 약속을 피하시고, 휴식의 시간을 확보하세요.",
        mindfulness=(
            "오늘 한 번, 자신에게 따뜻한 말을 건네는 시간을 가져보세요. "
            "지금 이 순간의 호흡에 잠시 머물러도 좋습니다. "
            "완벽하지 않아도 괜찮다는 사실을 기억해 주세요. "
            "마음의 평온은 작은 멈춤에서 시작됩니다."
        ),
        right_page_hint="오늘도 한 걸음, 충분히 잘하고 있어요.",
        recommended_actions=["산책 20분", "감사 3가지 적기", "차 한 잔"],
        things_to_avoid=["과식", "충동 구매"],
    )


def main():
    start = date(2026, 5, 30)
    days = [start + timedelta(days=i) for i in range(35)]
    colors = ["청록색", "주황색", "황금색", "은백색", "감청색"]
    contents = [_mock(d, colors[i % 5]) for i, d in enumerate(days)]

    output = Path("output/sample_book.pdf")
    result = render_diary(
        contents,
        output,
        title="내 다이어리",
        subtitle="사주 기반 365일 안내",
        customer_name="샘플 고객",
        period=f"{days[0]} — {days[-1]}",
        include_cover=True,
        include_month_dividers=True,
    )
    print(f"PDF: {result.resolve()}")
    print(f"  크기: {result.stat().st_size:,} bytes")
    print(f"  구성: 표지 2p + 월구분 3×2p + 일별 35×2p = ~78p")


if __name__ == "__main__":
    main()
