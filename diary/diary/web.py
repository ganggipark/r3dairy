"""Mobile/tablet companion app HTML rendering.

Reads same DailyContent objects as PDF render → static HTML files.
Output:
  <output_dir>/
    index.html        (오늘 redirect or 캘린더 fallback)
    calendar.html     (전체 날짜 리스트, 월별 그룹)
    YYYY-MM-DD.html   (일별 페이지, 모바일 최적)
    assets/styles.css
"""
from __future__ import annotations
import shutil
from datetime import date
from itertools import groupby
from pathlib import Path
from typing import Iterable

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .models import DailyContent
from .render import _enrich_entries, color_to_hex

_WEB_TEMPLATES = Path(__file__).parent / "templates" / "web"
_WEB_STATIC = Path(__file__).parent / "static" / "web"


def render_web(
    contents: Iterable[DailyContent],
    output_dir: Path | str,
    *,
    customer_id: str,
    customer_name: str | None = None,
    customer_birth: str | None = None,
    day_start_hour: int = 7,
    day_end_hour: int = 23,
) -> Path:
    """Generate static HTML companion for diary contents."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    contents_list = list(contents)
    if not contents_list:
        raise ValueError("contents is empty")

    # Copy static assets
    assets_dir = output_dir / "assets"
    assets_dir.mkdir(exist_ok=True)
    if _WEB_STATIC.exists():
        for f in _WEB_STATIC.iterdir():
            if f.is_file():
                shutil.copy(f, assets_dir / f.name)

    env = Environment(
        loader=FileSystemLoader(_WEB_TEMPLATES),
        autoescape=select_autoescape(["html"]),
    )
    env.filters["color_hex"] = color_to_hex

    entries = _enrich_entries(
        contents_list,
        with_month_dividers=False,
        day_start_hour=day_start_hour,
        day_end_hour=day_end_hour,
    )
    dates = [e["day"].date for e in entries]

    # Group entries by YYYY-MM for calendar
    entries_by_month = []
    for month, group in groupby(entries, key=lambda e: e["day"].date[:7]):
        entries_by_month.append((month, list(group)))

    common_ctx = {
        "customer_id": customer_id,
        "customer_name": customer_name,
        "customer_birth": customer_birth,
        "start_date": dates[0],
        "end_date": dates[-1],
    }

    # 1. index.html (JS redirect → today or calendar)
    (output_dir / "index.html").write_text(
        env.get_template("index.html").render(**common_ctx),
        encoding="utf-8",
    )

    # 2. calendar.html
    (output_dir / "calendar.html").write_text(
        env.get_template("calendar.html").render(
            entries_by_month=entries_by_month,
            **common_ctx,
        ),
        encoding="utf-8",
    )

    # 3. Per-day pages
    for i, entry in enumerate(entries):
        prev_date = dates[i - 1] if i > 0 else None
        next_date = dates[i + 1] if i < len(dates) - 1 else None
        (output_dir / f"{entry['day'].date}.html").write_text(
            env.get_template("day.html").render(
                entry=entry,
                prev_date=prev_date,
                next_date=next_date,
                **common_ctx,
            ),
            encoding="utf-8",
        )

    return output_dir
