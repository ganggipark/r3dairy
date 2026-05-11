"""Generate 1 day of real content via Anthropic API.

Requires: ANTHROPIC_API_KEY env var.
Usage:    python diary/samples/generate_sample.py
"""
import os
import sys
from datetime import date

from diary import SajuInput, calculate_saju, generate_daily_content


def main():
    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("ANTHROPIC_API_KEY 환경변수가 필요합니다.")

    saju = calculate_saju(SajuInput(
        year=1990, month=5, day=15, hour=14, gender="male",
    ))
    print(f"사주: {saju.fullSajuString}\n")

    content = generate_daily_content(saju=saju, target_date=date(2026, 5, 15))
    print(content.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
