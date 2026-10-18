import subprocess
import sys

from streamstats.__main__ import build_parser


def test_help_exit_code():
    """--help выводит справку и код 0."""
    result = subprocess.run(
        [sys.executable, "-m", "streamstats", "--help"],
        capture_output=True,
        text=True,
        check=False
    )
    assert result.returncode == 0
    assert "Потоковый анализатор файлов CSV и JSONL" in result.stdout
    assert result.stderr == ""


def test_invalid_format():
    """Неверный формат вызывает ошибку."""
    result = subprocess.run(
        [
            sys.executable, "-m", "streamstats",
            "analyze", "file.csv", "--format", "xml"
        ],
        capture_output=True,
        text=True,
        check=False
    )
    assert result.returncode == 2
    assert "invalid choice: 'xml'" in result.stderr


def test_absence_from():
    """Отсутствие --format вызывает ошибку."""
    result = subprocess.run(
        [sys.executable, "-m", "streamstats", "analyze", "file.csv"],
        capture_output=True,
        text=True,
        check=False
    )
    assert result.returncode == 2
    assert "required: --format" in result.stderr


def test_build_parser_valid_args():
    """build_parser правильно парсит валидные аргументы."""
    parser = build_parser()
    args = parser.parse_args([
        "analyze", "file1.csv", "file2.jsonl",
        "--format", "csv", "jsonl",
        "--skip-invalid"
    ])
    assert args.command == "analyze"
    assert args.inputs == ["file1.csv", "file2.jsonl"]
    assert args.format == ["csv", "jsonl"]
    assert args.skip_invalid is True
    assert args.output is None