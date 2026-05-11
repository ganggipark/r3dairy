"""Command-line interface for diary generation."""
from __future__ import annotations
import argparse
import sys
from datetime import date

from .models import SajuInput
from .pipeline import PipelineProgress, generate_diary


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="diary",
        description="사주 + 기문 기반 인쇄용 다이어리 생성기",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    g_birth = p.add_argument_group("출생 정보 (모두 필수)")
    g_birth.add_argument("--year", type=int, required=True)
    g_birth.add_argument(
        "--month", type=int, required=True, choices=range(1, 13), metavar="1-12"
    )
    g_birth.add_argument(
        "--day", type=int, required=True, choices=range(1, 32), metavar="1-31"
    )
    g_birth.add_argument(
        "--hour", type=int, required=True, choices=range(0, 24), metavar="0-23"
    )
    g_birth.add_argument("--gender", required=True, choices=["male", "female"])
    g_birth.add_argument(
        "--minute", type=int, default=0, choices=range(0, 60), metavar="0-59"
    )
    g_birth.add_argument("--lunar", action="store_true", help="음력 입력")
    g_birth.add_argument("--leap-month", action="store_true", help="윤월")
    g_birth.add_argument("--birth-place", default="서울")
    g_birth.add_argument("--no-true-solar", action="store_true", help="진태양시 보정 끔")

    g_range = p.add_argument_group("기간")
    g_range.add_argument("--start", required=True, help="시작일 YYYY-MM-DD")
    g_range.add_argument("--days", type=int, default=7, help="일수")

    g_out = p.add_argument_group("출력")
    g_out.add_argument("--output", "-o", default="output/diary.pdf")
    g_out.add_argument("--title", default="내 다이어리")

    g_llm = p.add_argument_group("LLM")
    g_llm.add_argument(
        "--provider", default="deepinfra",
        choices=["deepinfra", "openai", "anthropic"],
    )
    g_llm.add_argument("--model", default=None, help="기본 모델 override")

    g_pipe = p.add_argument_group("파이프라인")
    g_pipe.add_argument("--cache-dir", default=".cache/content")
    g_pipe.add_argument("--no-cache", action="store_true")
    g_pipe.add_argument("--target-hour", type=int, default=12, help="일간 기문 기준 시")
    g_pipe.add_argument("--concurrency", type=int, default=5, help="병렬 워커 수")
    g_pipe.add_argument("--fail-fast", action="store_true", help="첫 실패 시 즉시 종료")
    g_pipe.add_argument("--quiet", action="store_true", help="진행률 숨김")

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        start_date = date.fromisoformat(args.start)
    except ValueError:
        print(
            f"--start invalid: {args.start} (expected YYYY-MM-DD)",
            file=sys.stderr,
        )
        return 2

    birth = SajuInput(
        year=args.year, month=args.month, day=args.day,
        hour=args.hour, minute=args.minute,
        gender=args.gender,
        isLunar=args.lunar, isLeapMonth=args.leap_month,
        useTrueSolarTime=not args.no_true_solar,
        birthPlace=args.birth_place,
    )

    cache = None if args.no_cache else args.cache_dir

    def on_progress(p: PipelineProgress) -> None:
        if not args.quiet:
            print(f"  [{p.day:3d}/{p.total}] {p.target_date} - {p.stage}")

    try:
        result = generate_diary(
            birth=birth,
            start_date=start_date,
            days=args.days,
            output_path=args.output,
            provider=args.provider,
            model=args.model,
            target_hour=args.target_hour,
            concurrency=args.concurrency,
            cache_dir=cache,
            skip_failed=not args.fail_fast,
            progress=on_progress,
            title=args.title,
        )
    except Exception as e:
        print(f"pipeline error: {e}", file=sys.stderr)
        return 1

    print(
        f"\n{result.succeeded}/{result.total_days} days "
        f"(cached: {result.cache_hits}, failed: {result.failed})"
    )

    if result.errors:
        for err in result.errors[:5]:
            print(f"  - {err['date']}: {err['error'][:80]}")
        if len(result.errors) > 5:
            print(f"  ... +{len(result.errors)-5} more")

    print(f"  Output: {result.output_path.resolve()}")
    print(f"  Size  : {result.output_path.stat().st_size:,} bytes")

    return 1 if result.failed > 0 and args.fail_fast else 0


if __name__ == "__main__":
    raise SystemExit(main())
