"""PDF rendering via WeasyPrint + Jinja2.

Features:
- Configurable page size (A4/A5/A6/B5/B6) with proper margins
- Right-page hourly time grid with lucky-hour highlighting
- Cover + month dividers (optional)
- Pretendard embedded fonts
"""
from __future__ import annotations
import re
from pathlib import Path
from typing import Iterable, Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import CSS, HTML
from weasyprint.text.fonts import FontConfiguration

from .models import DailyContent

_TEMPLATES_DIR = Path(__file__).parent / "templates"
_STATIC_DIR = Path(__file__).parent / "static"

_COLOR_TO_HEX = {
    "청록색": "#4FB89F",
    "주황색": "#E89B5C",
    "황금색": "#D4A848",
    "은백색": "#C8C8CC",
    "감청색": "#2E4A7F",
}

PAGE_SIZES = {
    "A4": ("A4", (20, 18, 22, 18)),
    "A5": ("A5", (14, 13, 16, 13)),
    "A6": ("A6", (10, 9, 12, 9)),
    "B5": ("B5", (16, 14, 18, 14)),
    "B6": ("B6", (12, 11, 14, 11)),
}


def color_to_hex(name: str) -> str:
    return _COLOR_TO_HEX.get(name, "#999999")


def _parse_korean_hour(text: str) -> int | None:
    """'오전 11시' / '오후 1시' / '정오' / '자정' → 24h int. None on fail."""
    text = text.strip()
    if "정오" in text:
        return 12
    if "자정" in text:
        return 0
    m = re.search(r"(오전|오후)\s*(\d{1,2})\s*시?", text)
    if not m:
        return None
    period, num_s = m.groups()
    num = int(num_s)
    if not (1 <= num <= 12):
        return None
    if period == "오전":
        return 0 if num == 12 else num
    return 12 if num == 12 else (num + 12) % 24


def parse_lucky_hours(lucky_time: str) -> set[int]:
    """'오전 11시–오후 1시' → {11, 12, 13}. Handles midnight crossing."""
    if not lucky_time:
        return set()
    parts = re.split(r"\s*[–—~\-]\s*", lucky_time, maxsplit=1)
    if len(parts) != 2:
        return set()
    start = _parse_korean_hour(parts[0])
    end = _parse_korean_hour(parts[1])
    if start is None or end is None:
        return set()
    if end >= start:
        return set(range(start, end + 1))
    return set(range(start, 24)) | set(range(0, end + 1))


def _enrich_entries(
    contents: list[DailyContent],
    with_month_dividers: bool,
    day_start_hour: int,
    day_end_hour: int,
) -> list[dict]:
    """Annotate days with month-start flag + hourly time lines."""
    entries = []
    prev_month: Optional[str] = None
    for day in contents:
        current_month = day.date[:7]
        starts_new_month = with_month_dividers and current_month != prev_month
        lucky_hours = parse_lucky_hours(day.lucky_time)
        time_lines = [
            {
                "hour": h,
                "label": f"{h:02d}:00",
                "is_lucky": h in lucky_hours,
            }
            for h in range(day_start_hour, day_end_hour + 1)
        ]
        entries.append({
            "day": day,
            "starts_new_month": starts_new_month,
            "month_label": f"{int(day.date[5:7])}월",
            "year_label": day.date[:4],
            "time_lines": time_lines,
        })
        prev_month = current_month
    return entries


def render_diary(
    contents: Iterable[DailyContent],
    output_path: Path | str,
    *,
    title: str = "내 다이어리",
    subtitle: Optional[str] = None,
    customer_name: Optional[str] = None,
    customer_birth: Optional[str] = None,
    period: Optional[str] = None,
    include_cover: bool = False,
    include_month_dividers: bool = False,
    page_size: str = "A5",
    day_start_hour: int = 7,
    day_end_hour: int = 23,
) -> Path:
    """Render PDF. page_size ∈ A4/A5/A6/B5/B6. Time grid: day_start_hour..day_end_hour."""
    if page_size not in PAGE_SIZES:
        raise ValueError(
            f"Unknown page_size: {page_size!r}. Use one of: {list(PAGE_SIZES)}"
        )
    if not (0 <= day_start_hour <= 23 and 0 <= day_end_hour <= 23):
        raise ValueError("day_start_hour/day_end_hour must be 0..23")
    if day_end_hour < day_start_hour:
        raise ValueError("day_end_hour must be >= day_start_hour")

    contents_list = list(contents)
    entries = _enrich_entries(
        contents_list, include_month_dividers,
        day_start_hour, day_end_hour,
    )

    env = Environment(
        loader=FileSystemLoader(_TEMPLATES_DIR),
        autoescape=select_autoescape(["html"]),
    )
    env.filters["color_hex"] = color_to_hex

    html_str = env.get_template("diary.html").render(
        title=title,
        subtitle=subtitle,
        customer_name=customer_name,
        customer_birth=customer_birth,
        period=period,
        include_cover=include_cover,
        entries=entries,
    )

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    size_kw, (mt, mr, mb, ml) = PAGE_SIZES[page_size]
    page_css = f"@page {{ size: {size_kw}; margin: {mt}mm {mr}mm {mb}mm {ml}mm; }}"

    font_config = FontConfiguration()
    css = _STATIC_DIR / "styles.css"
    stylesheets = []
    if css.exists():
        stylesheets.append(CSS(filename=str(css), font_config=font_config))
    stylesheets.append(CSS(string=page_css, font_config=font_config))

    HTML(string=html_str, base_url=str(_TEMPLATES_DIR)).write_pdf(
        target=str(output_path),
        stylesheets=stylesheets,
        font_config=font_config,
    )
    return output_path
