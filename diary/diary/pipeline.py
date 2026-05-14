"""End-to-end pipeline with concurrent per-day processing.

Stages: saju (1x) → qimen + LLM content (Nx in parallel) → render (1x).
Concurrency: ThreadPoolExecutor (I/O bound: subprocess + HTTP).
"""
from __future__ import annotations
import hashlib
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Callable, Literal, Optional

from .content import generate_daily_content
from .models import DailyContent, SajuInput
from .qimen import calculate_qimen
from .render import render_diary
from .retry import with_retry
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


def _format_birth(birth: SajuInput) -> str:
    """Format birth info for cover: '1990년 5월 15일 14시 (음력)'."""
    base = f"{birth.year}년 {birth.month}월 {birth.day}일 {birth.hour}시"
    if birth.isLunar:
        base += " (음력 윤월)" if birth.isLeapMonth else " (음력)"
    return base


def generate_diary(
    birth: SajuInput,
    start_date: date,
    days: int,
    output_path: Path | str,
    *,
    concurrency: int = 5,
    provider: str = "deepinfra",
    model: Optional[str] = None,
    target_hour: int = 12,
    cache_dir: Optional[Path | str] = ".cache/content",
    skip_failed: bool = True,
    progress: Optional[Callable[[PipelineProgress], None]] = None,
    title: str = "내 다이어리",
    max_retries: int = 3,
    include_cover: bool = True,
    include_month_dividers: bool = True,
    customer_name: str | None = None,
    subtitle: str | None = None,
    page_size: str = "A5",
    day_start_hour: int = 7,
    day_end_hour: int = 23,
    web_output: Path | str | None = None,
) -> PipelineResult:
    """End-to-end: 1 customer + N days → 1 PDF.

    Per-day work (qimen + LLM) runs in a ThreadPoolExecutor with `concurrency`
    workers. Render is sequential after all days complete.
    """
    output_path = Path(output_path)
    cache_dir = Path(cache_dir) if cache_dir else None
    cust_id = _customer_id(birth)

    if progress:
        progress(PipelineProgress(0, days, start_date, "saju"))
    saju = calculate_saju(birth)
    birth_dt = datetime(birth.year, birth.month, birth.day, birth.hour, birth.minute)

    dates = [start_date + timedelta(days=i) for i in range(days)]

    progress_lock = threading.Lock()
    completed = [0]

    def _emit(stage: Stage, target: date) -> None:
        """Emit progress. qimen is stage-transition (no count); others = day done."""
        if not progress:
            return
        if stage == "qimen":
            with progress_lock:
                n = completed[0]
            progress(PipelineProgress(n, days, target, stage))
            return
        with progress_lock:
            completed[0] += 1
            n = completed[0]
        progress(PipelineProgress(n, days, target, stage))

    results: dict[date, DailyContent] = {}
    missing: list[date] = []
    cache_hits = 0

    if cache_dir:
        for target in dates:
            cached = _cache_get(cache_dir, cust_id, target)
            if cached is not None:
                results[target] = cached
                cache_hits += 1
                _emit("cache_hit", target)
            else:
                missing.append(target)
    else:
        missing = list(dates)

    def _work_day(target: date) -> tuple[date, DailyContent | BaseException]:
        try:
            _emit("qimen", target)
            qimen = calculate_qimen(
                birth_dt, target, target_hour=target_hour,
                yong_sin_score=(saju.yongSin.yongSinScore if saju.yongSin else None),
                daily_best=True,  # M22: 12시진 중 최고 점수 시진 자동 선택
            )
            content = with_retry(
                lambda: generate_daily_content(
                    saju=saju, qimen=qimen, target_date=target,
                    provider=provider, model=model,
                ),
                max_attempts=max_retries,
            )
            if cache_dir:
                _cache_put(cache_dir, cust_id, target, content)
            _emit("content", target)
            return target, content
        except BaseException as e:
            return target, e

    errors: list[dict] = []

    if missing:
        with ThreadPoolExecutor(max_workers=concurrency) as ex:
            futures = {ex.submit(_work_day, d): d for d in missing}
            for fut in as_completed(futures):
                target, outcome = fut.result()
                if isinstance(outcome, BaseException):
                    errors.append({"date": target.isoformat(), "error": str(outcome)})
                    if not skip_failed:
                        for other in futures:
                            other.cancel()
                        raise outcome
                else:
                    results[target] = outcome

    if not results:
        raise RuntimeError(
            f"All {days} days failed. First error: {errors[0] if errors else 'unknown'}"
        )

    if progress:
        progress(PipelineProgress(days, days, start_date, "render"))
    contents = [results[d] for d in dates if d in results]
    period = f"{contents[0].date} — {contents[-1].date}" if contents else None
    render_diary(
        contents, output_path,
        title=title,
        subtitle=subtitle,
        customer_name=customer_name,
        customer_birth=_format_birth(birth),
        period=period,
        include_cover=include_cover,
        include_month_dividers=include_month_dividers,
        page_size=page_size,
        day_start_hour=day_start_hour,
        day_end_hour=day_end_hour,
    )

    if web_output:
        from .customer import customer_id as _cid
        from .web import render_web
        cust_id = _cid(birth, length=20)
        render_web(
            contents,
            Path(web_output) / cust_id,
            customer_id=cust_id,
            customer_name=customer_name,
            customer_birth=_format_birth(birth),
            day_start_hour=day_start_hour,
            day_end_hour=day_end_hour,
        )

    return PipelineResult(
        output_path=output_path,
        total_days=days,
        succeeded=len(contents),
        failed=len(errors),
        errors=errors,
        cache_hits=cache_hits,
    )
