"""Generate 1 day's content via real API.

Usage:
    python samples/generate_sample.py                       # default: openai
    python samples/generate_sample.py --provider anthropic
"""
import argparse
import os
import sys
from datetime import date

from diary import SajuInput, calculate_saju, generate_daily_content


def main():
    p = argparse.ArgumentParser()
    p.add_argument(
        "--provider", choices=["openai", "anthropic"], default="openai"
    )
    p.add_argument("--model", default=None, help="override default model")
    p.add_argument("--date", default="2026-05-15", help="target date YYYY-MM-DD")
    args = p.parse_args()

    key_var = "OPENAI_API_KEY" if args.provider == "openai" else "ANTHROPIC_API_KEY"
    if not os.environ.get(key_var):
        sys.exit(f"{key_var} required")

    saju = calculate_saju(
        SajuInput(year=1990, month=5, day=15, hour=14, gender="male")
    )
    print(f"provider : {args.provider}")
    print(f"사주      : {saju.fullSajuString}\n")

    target = date.fromisoformat(args.date)
    content = generate_daily_content(
        saju=saju,
        target_date=target,
        provider=args.provider,
        model=args.model,
    )
    print(content.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
