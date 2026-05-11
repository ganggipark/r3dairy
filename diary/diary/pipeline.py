"""End-to-end pipeline: birth + date range → PDF.

Stages: saju (1x) → qimen (Nx) → LLM content (Nx) → render (1x).
Features: file-based caching, failure isolation, progress callback.
"""
from __future__ import annotations
import hashlib
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Callable, Literal, Optional

from .content import generate_daily_content
from .models import DailyContent, SajuInput
from .qimen import calculate_qimen
from .render import render_diary
from .saju import calculate_saju

Stage = Literal["saju", "qimen", "content", "render", "cache_hit"]


@dataclass
class PipelineProgress:
    day: int
    total: int
    target_date: date
    stage: Stage


@dataclass
class PipelineResult:
    output_path: Path
    total_days: int
    succeeded: int
    failed: int
    errors: list[dict]
    cache_hits: int


def _customer_id(birth: SajuInput) -> str:
    """Stable 12-char ID for cache namespacing."""
    s = (
        f"{birth.year}-{birth.month}-{birth.day}T{birth.hour}:{birth.minute}_"
        f"{birth.gender}_lunar{birth.isLunar}_leap{birth.isLeapMonth}_"
        f"{birth.birthPlace}_true{birth.useTrueSolarTime}"
    )
    return hashlib.sha256(s.encode()).hexdigest()[:12]


def _cache_path(cache_dir: Path, cust_id: str, target: date) -> Path:
    return cache_dir / cust_id / f"{target.isoformat()}.json"


def _cache_get(cache_dir: Path, cust_id: str, target: date) -> Optional[DailyContent]:
    p = _cache_path(cache_dir, cust_id, target)
    if not p.exists():
        return None
    try:
        return DailyContent.model_validate_json(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def _cache_put(cache_dir: Path, cust_id: str, target: date, content: DailyContent) -> None:
    p = _cache_path(cache_dir, cust_id, target)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content.model_dump_json(indent=2), encoding="utf-8")


def generate_diary(
    birth: SajuInput,
    start_date: date,
    days: int,
    output_path: Path | str,
    *,
    provider: str = "deepinfra",
    model: Optional[str] = None,
    target_hour: int = 12,
    cache_dir: Optional[Path | str] = ".cache/content",
    skip_failed: bool = True,
    progress: Optional[Callable[[PipelineProgress], None]] = None,
    title: str = "내 다이어리",
) -> PipelineResult:
    """End-to-end: 1 customer + N days → 1 PDF."""
    output_path = Path(output_path)
    cache_dir = Path(cache_dir) if cache_dir else None
    cust_id = _customer_id(birth)

    if progress:
        progress(PipelineProgress(0, days, start_date, "saju"))
    saju = calculate_saju(birth)

    birth_dt = datetime(birth.year, birth.month, birth.day, birth.hour, birth.minute)

    contents: list[DailyContent] = []
    errors: list[dict] = []
    cache_hits = 0

    for i in range(days):
        target = start_date + timedelta(days=i)
        idx = i + 1

        try:
            if cache_dir:
                cached = _cache_get(cache_dir, cust_id, target)
                if cached:
                    if progress:
                        progress(PipelineProgress(idx, days, target, "cache_hit"))
                    contents.append(cached)
                    cache_hits += 1
                    continue

            if progress:
                progress(PipelineProgress(idx, days, target, "qimen"))
            qimen = calculate_qimen(birth_dt, target, target_hour=target_hour)

            if progress:
                progress(PipelineProgress(idx, days, target, "content"))
            content = generate_daily_content(
                saju=saju, qimen=qimen, target_date=target,
                provider=provider, model=model,
            )

            if cache_dir:
                _cache_put(cache_dir, cust_id, target, content)

            contents.append(content)
        except Exception as e:
            errors.append({"date": target.isoformat(), "error": str(e)})
            if not skip_failed:
                raise

    if not contents:
        raise RuntimeError(
            f"All {days} days failed. First error: {errors[0] if errors else 'unknown'}"
        )

    if progress:
        progress(PipelineProgress(days, days, start_date, "render"))
    render_diary(contents, output_path, title=title)

    return PipelineResult(
        output_path=output_path,
        total_days=days,
        succeeded=len(contents),
        failed=len(errors),
        errors=errors,
        cache_hits=cache_hits,
    )
