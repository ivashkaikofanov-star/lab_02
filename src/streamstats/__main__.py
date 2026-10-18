"""Точка входа CLI streamstats."""

import argparse


def build_parser() -> argparse.ArgumentParser:
    """
    Создание и настройка парсера аргументов командной строки.

    Returns:
        argparse.ArgumentParser: Настроенный объект парсера
            с подкомандой analyze и фильтрами.
    """
    epilog_text = ""
    with open("parser_epilog.txt", "r", encoding = "utf-8") as file:
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
        help = "Путь для сохранения 2 отчётов (CSV и JSON), созданных в программе"
    )
    analyze_parser.add_argument("--skip-invalid", action="store_true")
    analyze_parser.add_argument("--from", dest = "from_time")
    analyze_parser.add_argument("--to", dest = "to_time")
    analyze_parser.add_argument(
        "--level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        nargs = "+"
    )
    analyze_parser.add_argument("--source", nargs = "+")
    return parser
