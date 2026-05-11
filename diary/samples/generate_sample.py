"""Generate 1 day content via real API.

Default: deepinfra (Qwen/Qwen3-235B-A22B-Instruct-2507)

Examples:
    python samples/generate_sample.py
    python samples/generate_sample.py --provider openai
    python samples/generate_sample.py --provider anthropic --date 2026-06-01
"""
import argparse
import os
import sys
from datetime import date

from diary import SajuInput, calculate_saju, generate_daily_content


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
