"""Generate 1 day content via real API. saju + qimen + LLM 통합."""
import argparse
import os
import sys
from datetime import date, datetime

from diary import (
    SajuInput,
    calculate_qimen,
    calculate_saju,
    generate_daily_content,
)


KEY_VARS = {
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "deepinfra": "DEEPINFRA_API_KEY",
}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--provider", choices=list(KEY_VARS), default="deepinfra")
    p.add_argument("--model", default=None)
    p.add_argument("--date", default="2026-05-15")
    args = p.parse_args()

    key_var = KEY_VARS[args.provider]
    if not os.environ.get(key_var):
        sys.exit(f"{key_var} required")

    birth = SajuInput(year=1990, month=5, day=15, hour=14, gender="male")
    target = date.fromisoformat(args.date)

    saju = calculate_saju(birth)
    qimen = calculate_qimen(
        datetime(birth.year, birth.month, birth.day, birth.hour, birth.minute),
        target,
        target_hour=12,
    )

    print(f"provider     : {args.provider}")
    print(f"사주         : {saju.fullSajuString}")
    print(
        f"기문 best    : 궁{qimen.bestPalace.palaceNum} "
        f"{qimen.bestPalace.directionKo} (score {qimen.bestPalace.qualityScore})"
    )
    print(f"기문 시간    : {qimen.hourStart}시-{qimen.hourEnd}시")
    print(f"전체 운      : {qimen.overallQuality}\n")

    content = generate_daily_content(
        saju=saju,
        qimen=qimen,
        target_date=target,
        provider=args.provider,
        model=args.model,
    )
    print(content.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
