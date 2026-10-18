import logging

import pytest


@pytest.fixture(autouse=True)
def disable_logging():
    """Отключение логирования во время тестов."""
    logging.disable(logging.CRITICAL)
    yield
    logging.disable(logging.NOTSET)


@pytest.fixture
def valid_csv(tmp_path):
    """Создание временного CSV-файл с валидными данными."""
    path = tmp_path / "test_valide.csv"
    path.write_text(
        "timestamp,level,source,message\n"
        "2026-10-18T11:45:22-02:00,INFO,api,ILOVETHISLABA\n"
        "2008-09-17T20:34:05+06:07,CRITICAL,db,\n",
        encoding="utf-8"
    )
    return path


@pytest.fixture
def valid_jsonl(tmp_path):
    """Создание временного JSONL-файла с валидными данными."""
    path = tmp_path / "test_valide.jsonl"
    path.write_text(
        '{"timestamp": "2222-11-01T12:09:58+00:00", '
        '"level": "WARNING", "source": "worker", "message": ""}\n'
        '{"timestamp": "2020-10-06T10:01:56+01:00", '
        '"level": "ERROR", "source": "web", "message": "lololo"}\n'
        '{"timestamp": "1029-07-05T10:03:56+02:00", '
        '"level": "INFO", "source": "api", "message": ""}\n',
        encoding="utf-8"
    )
    return path


