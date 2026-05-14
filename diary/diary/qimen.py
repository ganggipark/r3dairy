"""Subprocess client for the TypeScript qimen calculator."""
from __future__ import annotations
import json
import subprocess
from datetime import date as _date, datetime

from .models import QimenResult
from .saju import _resolve_saju_engine_dir


class QimenEngineError(RuntimeError):
    """qimen-cli.js failure or output parse error."""


def calculate_qimen(
    birth_datetime: datetime,
    target_date: _date,
    target_hour: int = 12,
    yong_sin_score: dict[str, float] | None = None,
) -> QimenResult:
    """Call qimen-cli.js for a specific date and hour.

    Args:
        birth_datetime: customer's birth (date + time)
        target_date: the day to compute qimen for
        target_hour: hour 0-23 (default 12 = 오시, typical daily snapshot)
    """
    if not (0 <= target_hour <= 23):
        raise ValueError(f"target_hour must be 0-23, got {target_hour}")

    engine_dir = _resolve_saju_engine_dir()
    cli_path = engine_dir / "qimen-cli.js"
    if not cli_path.exists():
        raise QimenEngineError(f"qimen-cli.js not found at {cli_path}")

    payload = json.dumps({
        "birthDate": birth_datetime.isoformat(),
        "targetDate": target_date.isoformat(),
        "targetHour": target_hour,
        "yongSinScore": yong_sin_score,
    })

    try:
        proc = subprocess.run(
            ["node", "qimen-cli.js"],
            cwd=str(engine_dir),
            input=payload,
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8",
        )
    except FileNotFoundError as e:
        raise QimenEngineError(
            "node executable not found on PATH — install Node.js"
        ) from e
    except subprocess.CalledProcessError as e:
        raise QimenEngineError(
            f"qimen-cli exit {e.returncode}: {e.stderr.strip()}"
        ) from e

    try:
        raw = json.loads(proc.stdout)
    except json.JSONDecodeError as e:
        raise QimenEngineError(f"qimen output not JSON: {e}") from e

    return QimenResult.model_validate(raw)
