from datetime import datetime

import pytest

from streamstats.analysis import init_stats
from streamstats.errors import InvalidEventError, InvalidTimestampError
from streamstats.parsers import parse_jsonl


def test_parse_jsonl_valid(valid_jsonl):
    """Проверка, что валидный JSONL парсится полностью."""
    stats = init_stats()
    with open(valid_jsonl, "r", encoding="utf-8") as file:
        events = list(parse_jsonl(file, stats, False))
    assert len(events) == 3
    assert set(events[0].keys()) == {"timestamp", "level", "source", "message"}
    assert set(events[1].keys()) == {"timestamp", "level", "source", "message"}
    assert set(events[2].keys()) == {"timestamp", "level", "source", "message"}
    assert isinstance(events[0]["timestamp"], datetime)
    assert isinstance(events[1]["timestamp"], datetime)
    assert isinstance(events[2]["timestamp"], datetime)
    assert events[0]["level"] == "WARNING"
    assert events[0]["source"] == "worker"
    assert events[0]["message"] == ""
    assert events[1]["level"] == "ERROR"
    assert events[1]["source"] == "web"
    assert events[1]["message"] == "lololo"
    assert events[2]["level"] == "INFO"
    assert events[2]["source"] == "api"
    assert events[2]["message"] == ""


def test_parse_jsonl_invalid_json(tmp_path):
    """Проверка, что неверный JSON вызывает InvalidEventError."""
    bad_file = tmp_path / "bad.jsonl"
    bad_file.write_text(
        '{"timestamp": "1999-10-08T04:00:11+06:07", "level": "INFO", '
        '"source": "api", "message": ""}\n'
        '{"timestamp": "2026-02-06T07:01:23+05:02", "level": "CRITICAL", '
        '"source": "db", "message": "PUPUPU"\n'
        '{"timestamp": "2047-10-24T06:02:52+00:00", "level": "DEBUG", '
        '"source": "db", "message": ""}\n',
        encoding="utf-8"
    )
    stats = init_stats()
    with open(bad_file, "r", encoding="utf-8") as file:
        with pytest.raises(InvalidEventError) as error_check:
            list(parse_jsonl(file, stats, False))
        assert "В строке 2 неверный JSON" in str(error_check.value)


def test_parse_jsonl_invalid_timestamp(tmp_path):
    """Проверка, что неверный timestamp вызывает InvalidTimestampError."""
    bad_file = tmp_path / "bad_time.jsonl"
    bad_file.write_text(
        '{"timestamp": "19999999-10-08T04:00:11+06:07", "level": "INFO", '
        '"source": "api", "message": "infa"}\n',
        encoding="utf-8"
    )
    stats = init_stats()
    
    with open(bad_file, "r", encoding="utf-8") as file:
        with pytest.raises(InvalidTimestampError) as error_check:
            list(parse_jsonl(file, stats, False))
        assert "в неверном формате" in str(error_check.value)


def test_parse_jsonl_empty_file(tmp_path):
    """Проверка, что пустой файл возвращает 0 событий."""
    empty_file = tmp_path / "empty.jsonl"
    empty_file.write_text("", encoding="utf-8")
    stats = init_stats()
    with open(empty_file, "r", encoding="utf-8") as file:
        events = list(parse_jsonl(file, stats, False))
    assert len(events) == 0


def test_parse_jsonl_skip_invalid(tmp_path):
    """Проверяка, что с флагом skip_invalid битые строки пропускаются."""
    bad_file = tmp_path / "skip.jsonl"
    bad_file.write_text(
        '{"timestamp": "2026-10-06T10:00:00+00:00", "level": "INFO", '
        '"source": "db", "message": "Good_line_da)"}\n'
        '{"timestamp":aaaaaaaaaaT10}\n'
        '{"timestamp": "2026-10-06T10:02:00+00:00", "level": "ERROR", '
        '"source": "web", "message": ""}\n',
        encoding="utf-8"
    )
    stats = init_stats()
    with open(bad_file, "r", encoding="utf-8") as file:
        events = list(parse_jsonl(file, stats, True))
    assert len(events) == 2
    assert events[0]["source"] == "db"
    assert events[1]["source"] == "web"
    assert stats["skipped"] == 1