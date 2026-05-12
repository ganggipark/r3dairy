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
            f"{d.month}월 {d.day}일은 분석적 사고와 패턴 인식에 유리한 환경입니다. "
            "복잡한 의사결정을 단계별로 분해해 처리하면 효율이 높아지며, 직관적 판단보다 "
            "데이터에 기반한 선택이 안정적 결과를 가져옵니다. 관계에서는 명확한 의도 표명이 "
            "신뢰를 강화하고, 외부 자극을 줄이는 환경 설계가 집중력을 보존합니다."
        ),
        daily_focus=(
            "작은 목표 하나에 집중하고, 그것을 마무리하세요. 완료하면 다음 단계를 "
            "자연스럽게 이끌어내는 흐름이 생깁니다. 단계별 분해가 효율의 핵심입니다."
        ),
        daily_caution=(
            "조급함과 무리한 약속을 피하시고, 휴식의 시간을 확보하세요. 거절하는 용기는 "
            "장기적 신뢰를 강화하며, 충분한 회복이 다음 날의 생산성을 결정합니다."
        ),
        mindfulness=(
            "오늘의 감정 흐름을 emotional labeling 기법으로 다루어 보세요. 짜증·불안·"
            "기대 같은 막연한 단어 대신 구체적으로 명명하면 편도체 활성이 약화되어 즉각적 "
            "반응이 줄어듭니다. 신경과학 연구에 따르면 이 단순한 명명 과정만으로도 효과가 "
            "크니, 하루 한 번 실천해 보세요."
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
