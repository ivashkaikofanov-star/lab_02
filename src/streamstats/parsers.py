from datetime import datetime

from streamstats.errors import InvalidEventError, InvalidTimestampError


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