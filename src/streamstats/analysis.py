"""Управление статистикой файла."""
def init_stats() -> dict:
    """
    Создание статистики по файлу.

    Returns:
        stats: Новая статистика (пока не заполненная).
    """
    stats = {
        "total": 0,
        "by_level": {
            "DEBUG": 0,
            "INFO": 0,
            "WARNING": 0,
            "ERROR": 0,
            "CRITICAL": 0
        },
        "by_source": {},
        "first_timestamp": None,
        "last_timestamp": None,
        "skipped": 0,
    }
    return stats


def update_stat(dictionary: dict, stats: dict) -> dict:
    """
    Обновление статистики при прочтении новой строки файла.
    
    Args:
        dictionary: Строка в файле, преобразованная в словарь.
            Учитывая её события, мы будем обновлять статистику.
        stats: Текущая статистика по файлу.
    
    Returns:
        stats: Обновлённая статистика по файлу.
    """
    stats["total"] += 1
    stats["by_level"][dictionary["level"]] += 1
    source = dictionary["source"]
    if source not in stats["by_source"]:
        stats["by_source"][source] = {"total": 0, "error": 0}
    stats["by_source"][source]["total"] += 1
    if dictionary["level"] in ("ERROR", "CRITICAL"):
        stats["by_source"][source]["error"] += 1
    event_time = dictionary["timestamp"]
    if stats["first_timestamp"] is None:
        stats["first_timestamp"] = event_time
        stats["last_timestamp"] = event_time
    elif event_time < stats["first_timestamp"]:
        stats["first_timestamp"] = event_time
    elif event_time > stats["last_timestamp"]:
        stats["last_timestamp"] = event_time
    return stats