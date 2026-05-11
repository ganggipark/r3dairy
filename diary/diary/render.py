"""PDF rendering via WeasyPrint + Jinja2.

Layout: A5 portrait, 1 day = 2 pages (좌측 가이드 + 우측 작성공간).
"""
from __future__ import annotations
from pathlib import Path
from typing import Iterable

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


def render_diary(
    contents: Iterable[DailyContent],
    output_path: Path | str,
    *,
    title: str = "내 다이어리",
) -> Path:
    """Render N days as PDF. Each day = 2 pages (left guide + right writing)."""
    env = Environment(
        loader=FileSystemLoader(_TEMPLATES_DIR),
        autoescape=select_autoescape(["html"]),
    )
    env.filters["color_hex"] = color_to_hex

    html_str = env.get_template("diary.html").render(
        title=title,
        days=list(contents),
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
