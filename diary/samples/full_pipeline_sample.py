"""Full pipeline sample: birth + 7 days -> PDF via real LLM.

Usage:
    $env:DEEPINFRA_API_KEY = "..."
    python samples/full_pipeline_sample.py
"""
import os
import sys
from datetime import date
from pathlib import Path

from diary import SajuInput, generate_diary
from diary.pipeline import PipelineProgress


def main():
    if not os.environ.get("DEEPINFRA_API_KEY"):
        sys.exit("DEEPINFRA_API_KEY required")

    birth = SajuInput(year=1990, month=5, day=15, hour=14, gender="male")
    output = Path("output/full_week.pdf")

    def show(p: PipelineProgress):
        print(f"  [{p.day:3d}/{p.total}] {p.target_date} - {p.stage}")

    print(f"고객: {birth.year}-{birth.month}-{birth.day} {birth.hour}:00 {birth.gender}")
    print(f"기간: 2026-05-15 ~ 2026-05-21 (7일)")
    print(f"출력: {output}\n")

    result = generate_diary(
        birth=birth,
        start_date=date(2026, 5, 15),
        days=7,
        output_path=output,
        provider="deepinfra",
        cache_dir=".cache/content",
        progress=show,
    )

    print(f"\n완료")
    print(f"  성공: {result.succeeded}/{result.total_days}")
    print(f"  캐시 hit: {result.cache_hits}")
    print(f"  실패: {result.failed}")
    if result.errors:
        for e in result.errors:
            print(f"    - {e}")
    print(f"  출력: {result.output_path.resolve()}")
    print(f"  크기: {result.output_path.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
