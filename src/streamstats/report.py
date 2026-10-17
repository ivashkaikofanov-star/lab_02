"""Создание отчёта по файлу."""
import csv
import json
import os
import sys

from streamstats.errors import CLIConfigurationError


def build_report(stats: dict) -> dict:
    """
    Создание отчёта по данным статистики полученного файла.

    Args:
        stats: Статистика полученного файла в виде словаря.
    
    Returns:
        report: Отчёт в виде словаря, где указаны:
            общее количество валидных событий("total"), 
            количество событий по уровням логирования("by_level"),
            количество событий по источникам("by_source"),
            самая ранняя временная метка("first_timestamp"),
            самая поздняя временная метка("last_timestamp"),
            количество пропущенных строк("skipped"),
            топ-5 источников по количеству ошибок("top_errors").
    """
    start_time = (
        stats["first_timestamp"].isoformat()
        if stats["first_timestamp"] is not None else None
    )
    finish_time = (
        stats["last_timestamp"].isoformat()
        if stats["last_timestamp"] is not None else None
    )
    error_counts = []
    for source, counters in stats["by_source"].items():
        error_counts.append(
            {"source": source, "errors": counters["error"]}
        )
    top_5_errors = sorted(
        error_counts, key=lambda item: (-item["errors"], item["source"])
    )[:5]
    report = {
        "total": stats["total"],
        "by_level": stats["by_level"],
        "by_source": stats["by_source"],
        "first_timestamp": start_time,
        "last_timestamp": finish_time,
        "skipped": stats["skipped"],
        "top_errors": top_5_errors,
    }
    return report


def report_json(report: dict, path: str | None) -> None:
    """
    Запись отчёта в JSON-файл или вывод отчёта в JSON-формате в консоль.
    
    Args:
        report: Словарь с отчётом, который мы получили в функции
            build_report.
        path: Путь, по которому будет записан JSON-файл.
    
    Raises:
        CLIConfigurationError: Файл уже существует.
    """
    text = json.dumps(report, ensure_ascii=False, indent=2)
    if path is None:
        print(text)
        return
    if os.path.exists(path):
        raise CLIConfigurationError(f"Файл {path} уже существует")
    with open(path, "w", encoding = "utf-8") as f:
        f.write(text)


def write_csv(writer: csv.writer, report: dict) -> None:
    """
    Запись отчёта в CSV-формате.

    Args:
        writer: Объект для записи данных в CSV-формате.
        report: Словарь с отчётом.
    """
    writer.writerow(["Общая статистика"])
    writer.writerow(["total", "skipped", "first", "last"])
    writer.writerow([
        report["total"],
        report["skipped"],
        report["first_timestamp"],
        report["last_timestamp"],
    ])
    writer.writerow([])
    writer.writerow(["Информация об уровнях"])
    writer.writerow(["level", "count"])
    for level, count in report["by_level"].items():
        writer.writerow([level, count])
    writer.writerow([])
    writer.writerow(["Информация об источниках"])
    writer.writerow(["source", "total", "error"])
    for source, counters in report["by_source"].items():
        writer.writerow([source, counters["total"], counters["error"]])
    writer.writerow([])
    writer.writerow(["Топ-5 источников ошибок"])
    writer.writerow(["source", "errors"])
    for item in report["top_errors"]:
        writer.writerow([item["source"], item["errors"]])


def report_csv(report: dict, path: str | None) -> None:
    """
    Запись отчёта CSV-файл или вывод отчёта в CSV-формате в консоль.

    Args:
        report: Словарь с отчётом, который мы получили в функции
            build_report.
        path: Путь, по которому будет записан CSV-файл.

    Raises:
        CLIConfigurationError: Файл уже существует.
    """
    if path is None:
        writer = csv.writer(sys.stdout)
        write_csv(writer, report)
    else:
        if os.path.exists(path):
            raise CLIConfigurationError(f"Файл {path} уже существует")
        with open(path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            write_csv(writer, report)
