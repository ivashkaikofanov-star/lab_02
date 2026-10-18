"""Точка входа CLI streamstats."""
import argparse
import logging
import os
import sys
from collections.abc import Iterator
from datetime import datetime

from streamstats.analysis import init_stats, update_stat
from streamstats.errors import CLIConfigurationError, StreamStatsError
from streamstats.parsers import PARSER_REPOSITORY
from streamstats.report import build_report, report_csv, report_json


def build_parser() -> argparse.ArgumentParser:
    """
    Создание и настройка парсера аргументов командной строки.

    Returns:
        argparse.ArgumentParser: Настроенный объект парсера
            с подкомандой analyze и фильтрами.
    """
    epilog_text = ""
    with open("parser_epilog.txt", "r", encoding="utf-8") as file:
        for line in file:
            epilog_text += line
    parser = argparse.ArgumentParser(
        prog="streamstats",
        description="Потоковый анализатор файлов CSV и JSONL.",
        epilog=epilog_text,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    analyze_parser = subparsers.add_parser(
        "analyze", help="Проанализировать файл и вывести статистику"
    )
    analyze_parser.add_argument(
        "inputs",
        nargs="+",
        help="Пути к входным файлам (CSV или JSONL)"
    )
    analyze_parser.add_argument(
        "--format", required=True, nargs="+", choices=["csv", "jsonl"]
    )
    analyze_parser.add_argument(
        "--output",
        help="Путь для сохранения 2 отчётов (CSV и JSON)"
    )
    analyze_parser.add_argument("--skip-invalid", action="store_true")
    analyze_parser.add_argument("--from", dest="from_time")
    analyze_parser.add_argument("--to", dest="to_time")
    analyze_parser.add_argument(
        "--level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        nargs="+"
    )
    analyze_parser.add_argument("--source", nargs="+")
    return parser


def apply_filters(
        dictionary: Iterator[dict], args: argparse.Namespace
    ) -> Iterator[dict]:
    """
    Фильтрация событий по времени, уровню и источнику.

    Args:
        dictionary: Генератор событий (словарей) из парсера.
        args: Объект с аргументами командной строки.

    Yields:
        event: Словарь после фильтрации.

    Raises:
        CLIConfigurationError: Неверный формат времени для --from или --to.
    """
    if args.from_time:
        try:
            timestamp_from_time = datetime.fromisoformat(args.from_time)
        except ValueError:
            raise CLIConfigurationError(
                f"Неверный формат времени для --from: {args.from_time}"
            )
    if args.to_time:
        try:
            timestamp_to_time = datetime.fromisoformat(args.to_time)
        except ValueError:
            raise CLIConfigurationError(
                f"Неверный формат времени для --to: {args.to_time}"
            )
    for event in dictionary:
        if args.from_time and event["timestamp"] < timestamp_from_time:
            continue
        if args.to_time and event["timestamp"] > timestamp_to_time:
            continue
        if args.level and event["level"] not in args.level:
            continue
        if args.source and event["source"] not in args.source:
            continue
        yield event


def run_analyze(args: argparse.ArgumentParser) -> None:
    """
    Обработка файлов, сбор статистики и сохранение отчётов.

    Args:
        args: Объект с аргументами командной строки.

    Raises:
        CLIConfigurationError: Файл уже существует или 
            неверное количество форматов или несоответствие формата файла.
    """
    if args.output:
        output_csv = args.output.replace(".json", ".csv")
        if os.path.exists(output_csv):
            raise CLIConfigurationError(f"Файл {output_csv} уже существует")
        if os.path.exists(args.output):
            raise CLIConfigurationError(f"Файл {args.output} уже существует")
    if len(args.format) != 1 and len(args.format) != len(args.inputs):
        raise CLIConfigurationError("Неверное количество форматов")
    if len(args.format) == len(args.inputs):
        file_formats = args.format
    else:
        file_formats = [args.format[0]] * len(args.inputs)
    stats = init_stats()
    for file_path, file_format in zip(args.inputs, file_formats):
        with open(file_path, "r", encoding="utf-8") as file:
            first_line = ""
            for line in file:
                if line.strip():
                    first_line = line.strip()
                    break
            if first_line:
                if file_format == "jsonl" and first_line[0] != "{":
                    raise CLIConfigurationError(
                        f"Файл {file_path} не соответствует формату jsonl"
                    )
                if file_format == "csv" and first_line[0] == "{":
                    raise CLIConfigurationError(
                        f"Файл {file_path} не соответствует формату csv"
                    )
            file.seek(0)
            parser_func = PARSER_REPOSITORY[file_format]
            dictionary = parser_func(file, stats, args.skip_invalid)
            for filtered_events in apply_filters(dictionary, args):
                stats = update_stat(filtered_events, stats)
    report = build_report(stats)
    if args.output:
        report_csv(report, args.output.replace(".json", ".csv"))
        report_json(report, args.output)
    else:
        report_csv(report, None)
        report_json(report, None)


def main() -> int:
    """
    Точка входа программы.

    Returns:
        int: Код завершения программы(0 или 2).
    """
    parser = build_parser()
    args = parser.parse_args()
    logging.basicConfig(
        level=logging.WARNING,
        format="%(levelname)s: %(message)s"
    )
    try:
        run_analyze(args)
        return 0
    except StreamStatsError as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())