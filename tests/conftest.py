import logging

import pytest


@pytest.fixture(autouse=True)
def disable_logging():
    """Отключает логирование во время тестов."""
    logging.disable(logging.CRITICAL)
    yield
    logging.disable(logging.NOTSET)


@pytest.fixture
def valid_csv(tmp_path):
    """Создает временный CSV-файл с валидными данными."""
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
    """Создает временный JSONL-файл с валидными данными."""
    path = tmp_path / "test_valide.jsonl"
    path.write_text(
        '{"timestamp": "2222-11-01T12:09:58+00:00", '
        '"level": "WARNING", "source": "worker", "message": ""}\n'
        '{"timestamp": "2020-11-06T10:01:56+01:00", '
        '"level": "ERROR", "source": "web", "message": "lololo"}\n',
        encoding="utf-8"
    )


