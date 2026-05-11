"""Batch CLI: N customers from CSV → N PDFs.

CSV required columns: customer_id, name, year, month, day, hour, gender
CSV optional columns: minute, lunar, leap_month, birth_place
"""
from __future__ import annotations
import argparse
import csv
import re
import sys
from datetime import date
from pathlib import Path

from .models import SajuInput
from .pipeline import PipelineProgress, generate_diary


REQUIRED_FIELDS = ["customer_id", "name", "year", "month", "day", "hour", "gender"]


def _sanitize_filename(s: str) -> str:
    """Allow alphanumeric + underscore + Korean only."""
    cleaned = re.sub(r"[^\w가-힣]+", "_", s).strip("_")
    return cleaned or "unnamed"


def _truthy(v: str) -> bool:
    return str(v).strip().lower() in ("true", "1", "yes", "y", "t")


def parse_csv(csv_path: Path) -> list[dict]:
    """Parse customer CSV; validates required fields."""
    with open(csv_path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        missing = [f for f in REQUIRED_FIELDS if f not in fieldnames]
        if missing:
            raise ValueError(f"CSV missing required columns: {missing}")
        rows = [dict(row) for row in reader if any(v.strip() for v in row.values())]
    if not rows:
        raise ValueError("CSV has no data rows")
    return rows


def row_to_birth(row: dict) -> SajuInput:
    return SajuInput(
        year=int(row["year"]),
        month=int(row["month"]),
        day=int(row["day"]),
        hour=int(row["hour"]),
        minute=int(row.get("minute") or 0),
        gender=row["gender"].strip().lower(),
        isLunar=_truthy(row.get("lunar", "")),
        isLeapMonth=_truthy(row.get("leap_month", "")),
        birthPlace=(row.get("birth_place") or "서울").strip(),
    )


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="diary-batch",
        description="CSV로 N명 고객 일괄 다이어리 생성",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("--customers", type=Path, required=True,
                   help="CSV 파일 (required: customer_id,name,year,month,day,hour,gender)")
    p.add_argument("--start", required=True, help="시작일 YYYY-MM-DD")
    p.add_argument("--days", type=int, default=7)
    p.add_argument("--output-dir", type=Path, default=Path("output/batch"))
    p.add_argument("--provider", default="deepinfra",
                   choices=["deepinfra", "openai", "anthropic"])
    p.add_argument("--model", default=None)
    p.add_argument("--concurrency", type=int, default=5, help="고객 1명 내부 day 병렬도")
    p.add_argument("--max-retries", type=int, default=3)
    p.add_argument("--cache-dir", default=".cache/content")
    p.add_argument("--target-hour", type=int, default=12)
    p.add_argument("--continue-on-error", action="store_true",
                   help="1명 실패해도 다음 고객 진행")
    p.add_argument("--quiet", action="store_true")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        rows = parse_csv(args.customers)
    except (FileNotFoundError, ValueError) as e:
        print(f"CSV error: {e}", file=sys.stderr)
        return 2

    try:
        start_date = date.fromisoformat(args.start)
    except ValueError:
        print(f"--start invalid: {args.start}", file=sys.stderr)
        return 2

    args.output_dir.mkdir(parents=True, exist_ok=True)
    print(f"고객 수: {len(rows)}명 | 기간: {args.start} +{args.days}일")
    print(f"출력: {args.output_dir.resolve()}\n")

    summary: list[dict] = []

    for i, row in enumerate(rows, 1):
        cust_id = row["customer_id"].strip()
        name = row["name"].strip()
        output_path = args.output_dir / f"{cust_id}_{_sanitize_filename(name)}.pdf"

        print(f"[{i}/{len(rows)}] {cust_id} {name}")

        try:
            birth = row_to_birth(row)
        except (ValueError, KeyError) as e:
            print(f"  row parse error: {e}\n")
            summary.append({"id": cust_id, "name": name, "status": "csv_error", "error": str(e)})
            if not args.continue_on_error:
                return 1
            continue

        def _progress(p: PipelineProgress) -> None:
            if not args.quiet and p.stage in ("content", "cache_hit", "render"):
                print(f"    [{p.day:3d}/{p.total}] {p.target_date} - {p.stage}")

        try:
            result = generate_diary(
                birth=birth,
                start_date=start_date,
                days=args.days,
                output_path=output_path,
                provider=args.provider,
                model=args.model,
                target_hour=args.target_hour,
                cache_dir=args.cache_dir,
                concurrency=args.concurrency,
                max_retries=args.max_retries,
                progress=_progress,
                customer_name=name,
                title=f"{name}님의 다이어리",
            )
            summary.append({
                "id": cust_id, "name": name, "status": "ok",
                "succeeded": result.succeeded, "failed": result.failed,
                "output": str(result.output_path),
                "size": result.output_path.stat().st_size,
            })
            print(f"  {result.succeeded}/{result.total_days} days "
                  f"({result.output_path.stat().st_size:,} bytes)\n")
        except Exception as e:
            print(f"  pipeline error: {e}\n")
            summary.append({"id": cust_id, "name": name, "status": "error", "error": str(e)})
            if not args.continue_on_error:
                return 1

    ok = sum(1 for s in summary if s["status"] == "ok")
    err = len(summary) - ok
    print("=" * 50)
    print(f"전체 {len(summary)}명: 성공 {ok} / 실패 {err}")
    if err:
        print("\n실패 고객:")
        for s in summary:
            if s["status"] != "ok":
                msg = s.get("error", s["status"])[:80]
                print(f"  - {s['id']} {s['name']}: {msg}")

    return 0 if err == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
