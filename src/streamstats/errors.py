"""Обработка ошибок с помощью классов."""

class StreamStatsError(Exception):
    """Главная ветка всех ошибок."""


class UnsupportedFormatError(StreamStatsError):
    """Неподдерживаемый формат."""


class InvalidEventError(StreamStatsError):
    """Неверное событие"""


class InvalidTimestampError(StreamStatsError):
    """Неверная временная метка."""


class CLIConfigurationError(StreamStatsError):
    """Ошибка конфигурации CLI."""


