import json
import subprocess
import sys


def test_csv_and_jsonl_equivalence(tmp_path):
    """Эквивалентные CSV и JSONL дают одинаковую статистику."""
    csv_file = tmp_path / "data.csv"
    csv_file.write_text(
        "timestamp,level,source,message\n"
        "2006-11-24T20:08:09+00:00,INFO,api,\n"
        "2007-09-06T10:01:00+00:00,ERROR,db,\n",
        encoding="utf-8"
    )
    jsonl_file = tmp_path / "data.jsonl"
    jsonl_file.write_text(
        '{"timestamp": "2006-11-24T20:08:09+00:00", "level": "INFO", '
        '"source": "api", "message": ""}\n'
        '{"timestamp": "2007-09-06T10:01:00+00:00", "level": "ERROR", '
        '"source": "db", "message": ""}\n',
        encoding="utf-8"
    )
    csv_report_path = tmp_path / "report_csv.json"
    subprocess.run(
        [
            sys.executable, "-m", "streamstats", "analyze", str(csv_file),
            "--format", "csv", "--output", str(csv_report_path)
        ],
        capture_output=True,
        check=False
    )
    jsonl_report_path = tmp_path / "report_jsonl.json"
    subprocess.run(
        [
            sys.executable, "-m", "streamstats", "analyze", str(jsonl_file),
            "--format", "jsonl", "--output", str(jsonl_report_path)
        ],
        capture_output=True,
        check=False
    )
    with open(csv_report_path, "r", encoding="utf-8") as file:
        csv_report = json.load(file)
    with open(jsonl_report_path, "r", encoding="utf-8") as file:
        jsonl_report = json.load(file)
    assert csv_report == jsonl_report


def test_multiple_files(tmp_path):
    """Объединение статистики из нескольких файлов."""
    file1 = tmp_path / "file1.csv"
    file1.write_text(
        "timestamp,level,source,message\n"
        "2021-11-11T11:11:11+11:00,INFO,api,\n",
        encoding="utf-8"
    )
    file2 = tmp_path / "file2.jsonl"
    file2.write_text(
        '{"timestamp": "2020-07-02T04:03:13+07:00", "level": "ERROR", '
        '"source": "db", "message": ""}\n',
        encoding="utf-8"
    )
    report_path = tmp_path / "report_multi.json"
    subprocess.run(
        [
            sys.executable, "-m", "streamstats", "analyze",
            str(file1), str(file2),
            "--format", "csv", "jsonl",
            "--output", str(report_path)
        ],
        capture_output=True,
        check=False
    )
    with open(report_path, "r", encoding="utf-8") as file:
        report = json.load(file)
    assert report["total"] == 2
    assert report["by_source"]["api"]["total"] == 1
    assert report["by_source"]["db"]["total"] == 1


def test_empty_file(tmp_path):
    """Пустой файл создает нулевой отчет без падения."""
    empty_file = tmp_path / "empty.csv"
    empty_file.write_text("", encoding="utf-8")
    report_path = tmp_path / "report_empty.json"
    result = subprocess.run(
        [
            sys.executable, "-m", "streamstats", "analyze", str(empty_file),
            "--format", "csv", "--output", str(report_path)
        ],
        capture_output=True,
        check=False
    )
    assert result.returncode == 0
    with open(report_path, "r", encoding="utf-8") as file:
        report = json.load(file)
    assert report["total"] == 0
    assert report["skipped"] == 0


def test_skip_invalid(tmp_path):
    """Флаг --skip-invalid работает на уровне всей программы."""
    bad_file = tmp_path / "bad.csv"
    bad_file.write_text(
        "timestamp,level,source,message\n"
        "2026-10-06T10:00:00+00:00,INFO,api,Good\n"
        "2026-100-06T10:00:00+00:00,INFO,api,Bad\n",
        encoding="utf-8"
    )
    report_path = tmp_path / "report_skip.json"
    result = subprocess.run(
        [
            sys.executable, "-m", "streamstats", "analyze", str(bad_file),
            "--format", "csv", "--skip-invalid", "--output", str(report_path)
        ],
        capture_output=True,
        check=False
    )
    assert result.returncode == 0
    with open(report_path, "r", encoding="utf-8") as file:
        report = json.load(file)
    assert report["total"] == 1
    assert report["skipped"] == 1