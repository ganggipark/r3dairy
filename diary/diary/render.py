"""PDF rendering via WeasyPrint + Jinja2.

Layout: A5 portrait.
- Optional cover (2 pages: title + intro)
- Optional monthly dividers (2 pages each: month label + goals space)
- Daily pages (2 pages: left guide + right writing)
"""
from __future__ import annotations
from pathlib import Path
from typing import Iterable, Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import CSS, HTML

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


def color_to_hex(name: str) -> str:
    return _COLOR_TO_HEX.get(name, "#999999")


def _enrich_entries(contents: list[DailyContent], with_month_dividers: bool) -> list[dict]:
    """Annotate days with month-start flag for template iteration."""
    entries = []
    prev_month: Optional[str] = None
    for day in contents:
        current_month = day.date[:7]
        starts_new_month = with_month_dividers and current_month != prev_month
        entries.append({
            "day": day,
            "starts_new_month": starts_new_month,
            "month_label": f"{int(day.date[5:7])}월",
            "year_label": day.date[:4],
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
    period: Optional[str] = None,
    include_cover: bool = False,
    include_month_dividers: bool = False,
) -> Path:
    """Render mixed-layout PDF.

    Existing callers (Iterable[DailyContent]) keep working — cover/dividers
    are off by default. Pipeline (generate_diary) turns them on.
    """
    contents_list = list(contents)
    entries = _enrich_entries(contents_list, include_month_dividers)

    env = Environment(
        loader=FileSystemLoader(_TEMPLATES_DIR),
        autoescape=select_autoescape(["html"]),
    )
    env.filters["color_hex"] = color_to_hex

    html_str = env.get_template("diary.html").render(
        title=title,
        subtitle=subtitle,
        customer_name=customer_name,
        period=period,
        include_cover=include_cover,
        entries=entries,
    )

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    css = _STATIC_DIR / "styles.css"
    stylesheets = [CSS(filename=str(css))] if css.exists() else None

    HTML(string=html_str, base_url=str(_TEMPLATES_DIR)).write_pdf(
        target=str(output_path),
        stylesheets=stylesheets,
    )
    return output_path
