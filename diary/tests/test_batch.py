"""Batch CLI tests (CSV parsing + main with mocked pipeline)."""
from pathlib import Path
from unittest.mock import patch

import pytest

from diary.batch import (
    _sanitize_filename,
    _truthy,
    build_parser,
    main,
    parse_csv,
    row_to_birth,
)


def _write_csv(tmp_path: Path, content: str) -> Path:
    p = tmp_path / "customers.csv"
    p.write_text(content, encoding="utf-8")
    return p


VALID_CSV = """customer_id,name,year,month,day,hour,gender
A001,홍길동,1990,5,15,14,male
A002,김영희,1992,8,20,9,female
"""


def test_parse_csv_valid(tmp_path):
    p = _write_csv(tmp_path, VALID_CSV)
    rows = parse_csv(p)
    assert len(rows) == 2
    assert rows[0]["customer_id"] == "A001"
    assert rows[0]["name"] == "홍길동"


def test_parse_csv_missing_column(tmp_path):
    p = _write_csv(tmp_path, "customer_id,name,year,month,day,hour\nA001,홍,1990,5,15,14\n")
    with pytest.raises(ValueError, match="missing required columns"):
        parse_csv(p)


def test_parse_csv_empty(tmp_path):
    p = _write_csv(tmp_path, "customer_id,name,year,month,day,hour,gender\n")
    with pytest.raises(ValueError, match="no data rows"):
        parse_csv(p)


def test_parse_csv_skips_blank_rows(tmp_path):
    csv = VALID_CSV + ",,,,,,\n"
    p = _write_csv(tmp_path, csv)
    rows = parse_csv(p)
    assert len(rows) == 2


def test_row_to_birth_minimal():
    row = {
        "customer_id": "A001", "name": "홍길동",
        "year": "1990", "month": "5", "day": "15",
        "hour": "14", "gender": "male",
    }
    birth = row_to_birth(row)
    assert birth.year == 1990
    assert birth.gender == "male"
    assert birth.minute == 0
    assert birth.isLunar is False
    assert birth.birthPlace == "서울"


def test_row_to_birth_full():
    row = {
        "customer_id": "A001", "name": "홍",
        "year": "1990", "month": "5", "day": "15", "hour": "14",
        "gender": "Female", "minute": "30", "lunar": "true",
        "leap_month": "false", "birth_place": "부산",
    }
    birth = row_to_birth(row)
    assert birth.minute == 30
    assert birth.gender == "female"
    assert birth.isLunar is True
    assert birth.birthPlace == "부산"


def test_sanitize_filename():
    assert _sanitize_filename("홍길동") == "홍길동"
    assert _sanitize_filename("hong/길동") == "hong_길동"
    assert _sanitize_filename("a b c") == "a_b_c"
    assert _sanitize_filename("***") == "unnamed"
    assert _sanitize_filename("name@2024!") == "name_2024"


def test_truthy():
    for v in ("true", "True", "1", "yes", "Y"):
        assert _truthy(v)
    for v in ("false", "0", "no", ""):
        assert not _truthy(v)


def test_parser_help():
    parser = build_parser()
    assert parser.prog == "diary-batch"


def test_main_with_mocked_pipeline(tmp_path):
    """main() iterates customers, calls generate_diary per row."""
    from diary.pipeline import PipelineResult

    csv_path = _write_csv(tmp_path, VALID_CSV)
    output_dir = tmp_path / "out"
    captured = []

    def fake_generate(**kwargs):
        captured.append(kwargs)
        out = kwargs["output_path"]
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(b"%PDF-1.4\n" + b"x" * 500)
        return PipelineResult(
            output_path=out, total_days=kwargs["days"],
            succeeded=kwargs["days"], failed=0, errors=[], cache_hits=0,
        )

    with patch("diary.batch.generate_diary", side_effect=fake_generate):
        rc = main([
            "--customers", str(csv_path),
            "--start", "2026-05-15", "--days", "3",
            "--output-dir", str(output_dir),
            "--quiet",
        ])

    assert rc == 0
    assert len(captured) == 2
    assert captured[0]["birth"].year == 1990
    assert captured[1]["birth"].gender == "female"
    assert (output_dir / "A001_홍길동.pdf").exists()
    assert (output_dir / "A002_김영희.pdf").exists()


def test_main_continues_on_error(tmp_path):
    """--continue-on-error: 1명 실패해도 다음 고객 진행."""
    from diary.pipeline import PipelineResult

    csv_path = _write_csv(tmp_path, VALID_CSV)
    output_dir = tmp_path / "out"
    call_count = [0]

    def flaky_generate(**kwargs):
        call_count[0] += 1
        if call_count[0] == 1:
            raise RuntimeError("simulated failure")
        out = kwargs["output_path"]
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(b"%PDF-1.4\n" + b"x" * 500)
        return PipelineResult(
            output_path=out, total_days=kwargs["days"],
            succeeded=kwargs["days"], failed=0, errors=[], cache_hits=0,
        )

    with patch("diary.batch.generate_diary", side_effect=flaky_generate):
        rc = main([
            "--customers", str(csv_path),
            "--start", "2026-05-15", "--days", "3",
            "--output-dir", str(output_dir),
            "--continue-on-error", "--quiet",
        ])

    assert rc == 1
    assert call_count[0] == 2


def test_main_invalid_csv_path(tmp_path):
    rc = main([
        "--customers", str(tmp_path / "nonexistent.csv"),
        "--start", "2026-05-15",
        "--output-dir", str(tmp_path / "out"),
    ])
    assert rc == 2
