"""Парсеры CSV и JSONL: преобразование строк файла в словари."""
import csv
import json
import logging
from datetime import datetime

from streamstats.errors import (
    InvalidEventError,
    InvalidTimestampError,
    StreamStatsError,
)

logger = logging.getLogger(__name__)


def make_event(raw_dictionary, line_number):
    """
    Валидация одной строки файла, полученной в виде словаря.

    Args:
        raw_dictionary: Сырой словарь (непроверенный ещё на корректность).
        line_number: Номер строки в файле, на которой он был расположен.

    Returns:
        dict: Словарь события с ключами timestamp, level, source, message.

    Raises:
        InvalidTimestampError: Если в строке отсутствует временная метка
            или она неправильно записана.
        InvalidEventError: Если отсутствует какое-либо событие из списка:
            [level, source, message] или если содержимое данного события
            передано неверно.
    """
    invalid_keys = []
    for key in raw_dictionary:
        if key not in ("timestamp", "level", "source", "message"):
            invalid_keys.append(key)
    if invalid_keys:
        raise InvalidEventError(
            f"В строке {line_number} получены "
            f"недопустимые поля: {invalid_keys}"
        )
    timestamp = raw_dictionary.get("timestamp")
    if not timestamp:
        raise InvalidTimestampError(
            f"В строке {line_number} отсутствует timestamp"
        )
    else:
        try:
            timestamp = datetime.fromisoformat(timestamp)
        except (ValueError, TypeError):
            raise InvalidTimestampError(
                f"В строке {line_number} timestamp записан в неверном формате"
            )
    level = raw_dictionary.get("level")
    if not level:
        raise InvalidEventError(
            f"В строке {line_number} отсутствует level"
        )
    if level not in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"):
        raise InvalidEventError(
            f"В строке {line_number} недопустимый level: '{level}'"
        )
    source = raw_dictionary.get("source")
    if not source:
        raise InvalidEventError(
            f"В строке {line_number} отсутствует source"
        )
    message = raw_dictionary.get("message")
    if message is None:
        raise InvalidEventError(
            f"В строке {line_number} нет ключа message"
        )
    dictionary = {
        "timestamp": timestamp,
        "level": level,
        "source": source,
        "message": message
    }
    return dictionary


def parse_csv(file_csv, stats, skip_invalid):
    """
    Преобразование CSV-файла в генератор, который при
    каждом обращении будет выдавать словарь из новой строки,
    где ключи — имена колонок из заголовка, а значения — данные из строки.

    Args:
        file_csv: Открытый файл csv.
        stats: Отчёт, чтобы была возможность добавить число пропущенных строк.
        skip_invalid: Наличие флага --skip-invalid, введённого пользователем.
            Может принимать два значения: True, False.

    Yields:
        dict: Строчка в файле, превращённая в проверенный функцией
            make_event словарь.

    Raises:
        InvalidEventError: Пустая строка или неподходящий разделитель строк.
        StreamStatsError: Проброс ошибок из make_event при skip_invalid=False.
    """
    reader = None
    for separator in ",;\t":
        file_csv.seek(0)
        raw_reader = csv.DictReader(file_csv, delimiter=separator)
        if not raw_reader.fieldnames:
            return
        if set(raw_reader.fieldnames) == {
            "timestamp", "level", "source", "message"
        }:
            reader = raw_reader
            break
    if not reader:
        raise InvalidEventError("В файле разделитель строк не входит"
            "в стандартный перечень"
        )
    for line_number, raw_dictionary in enumerate(reader, 2):
        if all(not value for value in raw_dictionary.values()):
            if skip_invalid:
                stats["skipped"] += 1
                logger.warning(f"Строка {line_number} пропущена")
                continue
            raise InvalidEventError(f"Строка {line_number} пустая")
        try:
            dictionary = make_event(raw_dictionary, line_number)
            yield dictionary
        except StreamStatsError as e:
            if skip_invalid:
                stats["skipped"] += 1
                logger.warning(e)
                continue
            raise


def parse_jsonl(file_jsonl, stats, skip_invalid):
    """
    Преобразование каждой строки JSONL-файла в отдельный словарь.

    Args:
        file_jsonl: Открытый файл jsonl.
        stats: Отчёт, чтобы была возможность добавить число пропущенных строк.
        skip_invalid: Наличие флага --skip-invalid, введённого пользователем.
            Может принимать два значения: True, False.

    Yields:
        dict: Строчка в файле, превращённая в проверенный функцией
            make_event словарь.

    Raises:
        InvalidEventError: Пустая строка или неверный JSON в строке.
        StreamStatsError: Проброс ошибок из make_event при skip_invalid=False.
    """
    for line_number, line in enumerate(file_jsonl, 1):
        if not line.strip():
            if skip_invalid:
                stats["skipped"] += 1
                logger.warning(f"Строка {line_number} пропущена")
                continue
            raise InvalidEventError(f"Строка {line_number} пустая")
        try:
            raw_dictionary = json.loads(line)
        except json.JSONDecodeError as e:
            if skip_invalid:
                stats["skipped"] += 1
                logger.warning(f"В строке {line_number} неверный JSON: {e}")
                continue
            raise InvalidEventError(
                f"В строке {line_number} неверный JSON: {e}") from e
        try:
            dictionary = make_event(raw_dictionary, line_number)
            yield dictionary
        except StreamStatsError as e:
            if skip_invalid:
                stats["skipped"] += 1
                logger.warning(e)
                continue
            raise