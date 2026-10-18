from datetime import datetime

import pytest

from streamstats.analysis import init_stats
from streamstats.errors import InvalidEventError, InvalidTimestampError
from streamstats.parsers import parse_csv


def test_parse_csv_valid(valid_csv):
    """Проверяет, что валидный CSV парсится полностью."""
    stats = init_stats()
    with open(valid_csv, "r", encoding="utf-8") as file:
        events = list(parse_csv(file, stats, False))
    assert len(events) == 2
    assert set(events[0].keys()) == {"timestamp", "level", "source", "message"}
    assert events[0]["level"] == "INFO"
    assert events[1]["level"] == "CRITICAL"
    assert events[0]["message"] == "ILOVETHISLABA"
    assert events[1]["message"] == ""
    assert isinstance(events[0]["timestamp"], datetime)
    assert isinstance(events[1]["timestamp"], datetime)
    assert events[0]["source"] == "api"
    assert events[1]["source"] == "db"


def test_parse_csv_invalid_timestamp(tmp_path):
    """Проверяет, что неверный timestamp вызывает ошибку."""
    bad_file = tmp_path / "bad_time.csv"
    bad_file.write_text(
        "timestamp,level,source,message\n"
        "jcdhjh,INFO,api,Started\n",
        encoding="utf-8"
    )
    stats = init_stats()
    with open(bad_file, "r", encoding="utf-8") as file:
        with pytest.raises(InvalidTimestampError) as error_check:
            list(parse_csv(file, stats, False))
        assert "в неверном формате" in str(error_check.value)


def test_parse_csv_invalid_level(tmp_path):
    """Проверяет, что неверный level вызывает ошибку."""
    bad_file = tmp_path / "bad_level.csv"
    bad_file.write_text(
        "timestamp,level,source,message\n"
        "2100-10-06T11:01:46+05:00,TRACE,api,Started\n"
        "2000-05-46T02:03:00+01:00,TELEGRAM,api,Started\n",
        encoding="utf-8"
    )
    stats = init_stats()
    with open(bad_file, "r", encoding="utf-8") as file:
        with pytest.raises(InvalidEventError) as error_check:
            list(parse_csv(file, stats, False))
        assert "недопустимый level" in str(error_check.value)


def test_parse_csv_empty_file(tmp_path):
    """Проверяет, что пустой файл возвращает пустой список (0 событий)."""
    empty_file = tmp_path / "empty.csv"
    empty_file.write_text("", encoding="utf-8")
    stats = init_stats()
    with open(empty_file, "r", encoding="utf-8") as file:
        events = list(parse_csv(file, stats, False))
    assert len(events) == 0


def test_parse_csv_skip_invalid(tmp_path):
    """Проверяет, что с флагом skip_invalid битые строки пропускаются."""
    bad_file = tmp_path / "skip.csv"
    bad_file.write_text(
        "timestamp,level,source,message\n"
        "1012-11-16T10:28:01+06:45,INFO,api,MAI\n"
        "ddddddd,INFO,apii,Bad line\n"
        "2025-08-09T10:24:10+11:05,DEBUG,api,\n",
        encoding="utf-8"
    )
    stats = init_stats()
    with open(bad_file, "r", encoding="utf-8") as file:
        events = list(parse_csv(file, stats, True))
    assert len(events) == 2
    assert events[0]["message"] == "MAI"
    assert stats["skipped"] == 1




