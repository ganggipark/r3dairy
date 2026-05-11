from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

from .models import CompleteSajuData, SajuInput

_DEFAULT_SAJU_ENGINE_DIR = (
    Path(__file__).resolve().parent.parent.parent / "saju-engine"
)


def _resolve_saju_engine_dir() -> Path:
    override = os.environ.get("SAJU_ENGINE_DIR")
    return Path(override).resolve() if override else _DEFAULT_SAJU_ENGINE_DIR


SAJU_ENGINE_DIR = _resolve_saju_engine_dir()


class SajuEngineError(RuntimeError):
    pass


def calculate_saju(birth: SajuInput) -> CompleteSajuData:
    engine_dir = _resolve_saju_engine_dir()
    cli_path = engine_dir / "cli.js"
    if not cli_path.exists():
        raise SajuEngineError(f"saju-engine cli.js not found at {cli_path}")

    payload = birth.model_dump_json()
    try:
        proc = subprocess.run(
            ["node", "cli.js"],
            cwd=str(engine_dir),
            input=payload,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=True,
        )
    except subprocess.CalledProcessError as e:
        raise SajuEngineError(
            f"saju-engine exited {e.returncode}: {e.stderr.strip()}"
        ) from e
    except FileNotFoundError as e:
        raise SajuEngineError(
            "node executable not found on PATH — install Node.js"
        ) from e

    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError as e:
        raise SajuEngineError(
            f"saju-engine output is not valid JSON: {e}"
        ) from e

    return CompleteSajuData.model_validate(data)
