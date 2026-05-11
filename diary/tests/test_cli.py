"""CLI tests (subprocess + argparse smoke)."""
import subprocess
import sys
from datetime import date
from unittest.mock import patch

from diary.cli import build_parser, main
from diary.models import SajuInput


def test_help_exits_zero():
    result = subprocess.run(
        [sys.executable, "-m", "diary", "--help"],
        capture_output=True, text=True, timeout=10,
    )
    assert result.returncode == 0
    assert "--year" in result.stdout
    assert "--gender" in result.stdout
    assert "--start" in result.stdout


def test_no_args_exits_non_zero():
    result = subprocess.run(
        [sys.executable, "-m", "diary"],
        capture_output=True, text=True, timeout=10,
    )
    assert result.returncode != 0


def test_parser_constructs_correct_birth_input():
    parser = build_parser()
    args = parser.parse_args([
        "--year", "1990", "--month", "5", "--day", "15",
        "--hour", "14", "--gender", "male",
        "--start", "2026-05-15",
    ])
    assert args.year == 1990
    assert args.month == 5
    assert args.gender == "male"
    assert args.days == 7
    assert args.provider == "deepinfra"


def test_parser_invalid_start_date():
    rc = main([
        "--year", "1990", "--month", "5", "--day", "15",
        "--hour", "14", "--gender", "male",
        "--start", "not-a-date",
    ])
    assert rc == 2


def test_main_with_mocked_pipeline(tmp_path):
    captured = {}

    def fake_generate(**kwargs):
        captured.update(kwargs)
        from diary.pipeline import PipelineResult
        out = tmp_path / "fake.pdf"
        out.write_bytes(b"%PDF-1.4\n" + b"x" * 1000)
        return PipelineResult(
            output_path=out, total_days=kwargs["days"],
            succeeded=kwargs["days"], failed=0, errors=[], cache_hits=0,
        )

    with patch("diary.cli.generate_diary", side_effect=fake_generate):
        rc = main([
            "--year", "1990", "--month", "5", "--day", "15",
            "--hour", "14", "--gender", "male",
            "--start", "2026-05-15", "--days", "3",
            "--output", str(tmp_path / "out.pdf"),
            "--quiet",
        ])

    assert rc == 0
    assert isinstance(captured["birth"], SajuInput)
    assert captured["birth"].year == 1990
    assert captured["start_date"] == date(2026, 5, 15)
    assert captured["days"] == 3
