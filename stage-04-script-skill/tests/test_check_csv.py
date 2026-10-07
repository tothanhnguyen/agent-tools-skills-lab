"""csv-quality script: thống kê fixture, lỗi input/schema/parse exit 1, lỗi dữ liệu exit 0."""

import json
import os
import subprocess
import sys

import pytest

import paths

SCRIPT = paths.FIXTURES_DIR / "skills" / "csv-quality" / "scripts" / "check_csv.py"


def cli(*args):
    return subprocess.run([sys.executable, str(SCRIPT), *map(str, args)], capture_output=True,
                          text=True, encoding="utf-8", env={**os.environ, "PYTHONUTF8": "1"}, timeout=10)


def run(path, max_hours=8):
    return cli("--input", path, "--max-hours", max_hours)


def write_csv(tmp_path, text):
    path = tmp_path / "t.csv"
    path.write_text(text, encoding="utf-8")
    return path


def test_fixture_statistics():
    result = run(paths.FIXTURES_DIR / "data" / "tasks.csv")
    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    assert data["row_count"] == 6
    assert data["missing_owner_count"] == 1
    assert data["invalid_hours_count"] == 1
    assert data["duplicate_id_count"] == 1
    assert data["duplicate_ids"] == ["T02"]
    assert [(i["line"], i["column"], i["type"]) for i in data["issues"]] == [
        (4, "owner", "missing_owner"),
        (5, "hours", "invalid_hours"),
        (6, "task_id", "duplicate_id"),
    ]
    assert "total_hours" not in data


@pytest.mark.parametrize("hours", ["NaN", "nan", "Infinity", "-inf", "-1", ""])
def test_non_finite_negative_or_empty_hours_rejected(tmp_path, hours):
    data = json.loads(run(write_csv(tmp_path, f"task_id,owner,hours\nT01,Lan,{hours}\n")).stdout)
    assert data["invalid_hours_count"] == 1
    assert data["issues"][0]["line"] == 2


def test_clean_data_exit_0_without_issues(tmp_path):
    result = run(write_csv(tmp_path, "task_id,owner,hours\nT01,Lan,4\nT02,Minh,2.5\n"))
    assert result.returncode == 0
    assert json.loads(result.stdout)["issues"] == []


def test_missing_file_exit_1(tmp_path):
    result = run(tmp_path / "khong-co.csv")
    assert result.returncode == 1
    assert result.stdout == ""
    assert "Không đọc được file" in result.stderr


def test_missing_column_exit_1(tmp_path):
    result = run(write_csv(tmp_path, "task_id,owner\nT01,Lan\n"))
    assert result.returncode == 1
    assert "Thiếu cột bắt buộc: hours" in result.stderr


def test_parse_error_exit_1(tmp_path):
    result = run(write_csv(tmp_path, 'task_id,owner,hours\nT01,"La"n,4\n'))
    assert result.returncode == 1
    assert "Lỗi parse CSV" in result.stderr


def test_script_does_not_modify_input():
    source = paths.FIXTURES_DIR / "data" / "tasks.csv"
    before = source.read_bytes()
    run(source)
    assert source.read_bytes() == before


def test_workload_totals_exclusions_and_strict_threshold(tmp_path):
    path = write_csv(tmp_path, "task_id,owner,hours\nT01,Lan,4\nT02,Lan,5\nT03,Minh,3\nT04,Minh,abc\nT02,Lan,5\nT05,,2\n")
    before = path.read_bytes()
    low, equal = (json.loads(run(path, threshold).stdout) for threshold in (8, 9))
    assert low["hours_by_owner"] == equal["hours_by_owner"] == {"Lan": 9, "Minh": 3}
    assert low["overloaded_owners"] == [{"owner": "Lan", "total_hours": 9}]
    assert equal["overloaded_owners"] == []
    assert low["excluded_rows"] == equal["excluded_rows"] == [
        {"line": 5, "task_id": "T04", "reasons": ["invalid_hours"]},
        {"line": 6, "task_id": "T02", "reasons": ["duplicate_id"]},
        {"line": 7, "task_id": "T05", "reasons": ["missing_owner"]},
    ]
    assert low["row_count"] == 6
    assert (low["missing_owner_count"], low["invalid_hours_count"], low["duplicate_id_count"]) == (1, 1, 1)
    assert low["max_hours"] == 8 and equal["max_hours"] == 9
    assert path.read_bytes() == before


def test_first_invalid_id_is_reserved_and_valid_duplicate_never_replaces_it(tmp_path):
    path = write_csv(tmp_path, "task_id,owner,hours\nE01,Lan,abc\nE01,Lan,5\nE02,Minh,0\n")
    result = run(path, 0)
    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    assert data["hours_by_owner"] == {"Minh": 0}
    assert data["overloaded_owners"] == []
    assert data["excluded_rows"] == [
        {"line": 2, "task_id": "E01", "reasons": ["invalid_hours"]},
        {"line": 3, "task_id": "E01", "reasons": ["duplicate_id"]},
    ]
    assert data["duplicate_ids"] == ["E01"]


def test_all_reasons_once_per_row_and_quality_counts_include_rejected_rows(tmp_path):
    path = write_csv(tmp_path, "task_id,owner,hours\n,,abc,extra\nT01,,NaN,extra\nT01,,-2,extra\n")
    data = json.loads(run(path, 0).stdout)
    assert data["hours_by_owner"] == {} and data["overloaded_owners"] == []
    assert data["excluded_rows"] == [
        {"line": 2, "task_id": None, "reasons": ["wrong_field_count", "missing_task_id", "missing_owner", "invalid_hours"]},
        {"line": 3, "task_id": "T01", "reasons": ["wrong_field_count", "missing_owner", "invalid_hours"]},
        {"line": 4, "task_id": "T01", "reasons": ["wrong_field_count", "duplicate_id", "missing_owner", "invalid_hours"]},
    ]
    assert data["row_count"] == data["missing_owner_count"] == data["invalid_hours_count"] == 3
    assert data["duplicate_id_count"] == 1


def test_trim_case_sensitive_owners_blank_rows_and_sorted_overloads(tmp_path):
    path = write_csv(tmp_path, "task_id,owner,hours\n T01 , Lan , 0.5 \n T01 , Lan , 1 \nT02,lan,1\n\n , , \nT03,An,2\nT04,Lan,0\n")
    data = json.loads(run(path, 0).stdout)
    assert data["hours_by_owner"] == {"An": 2, "Lan": 0.5, "lan": 1}
    assert [o["owner"] for o in data["overloaded_owners"]] == ["An", "Lan", "lan"]
    assert data["row_count"] == 5
    assert data["excluded_rows"] == [{"line": 3, "task_id": "T01", "reasons": ["duplicate_id"]}]


@pytest.mark.parametrize("threshold", ["abc", "NaN", "inf", "-1", ""])
def test_invalid_threshold_is_cli_error(tmp_path, threshold):
    result = run(write_csv(tmp_path, "task_id,owner,hours\nA,X,1\n"), threshold)
    assert result.returncode != 0 and result.stdout == ""
    assert "--max-hours" in result.stderr


def test_missing_threshold_is_cli_error(tmp_path):
    result = cli("--input", write_csv(tmp_path, "task_id,owner,hours\nA,X,1\n"))
    assert result.returncode != 0 and result.stdout == ""
    assert "--max-hours" in result.stderr


def test_column_order_and_extra_header_columns_are_preserved(tmp_path):
    data = json.loads(run(write_csv(tmp_path, "owner,note,hours,task_id\nLan,ok,2.5,T01\n"), 2.5).stdout)
    assert data["hours_by_owner"] == {"Lan": 2.5} and not data["overloaded_owners"]
    assert data["excluded_rows"] == []


def test_invalid_utf8_preserves_input_failure_contract(tmp_path):
    path = tmp_path / "bad.csv"
    path.write_bytes(b"task_id,owner,hours\nA,\xff,1\n")
    result = run(path)
    assert result.returncode == 1 and result.stdout == ""
    assert "UTF-8" in result.stderr
