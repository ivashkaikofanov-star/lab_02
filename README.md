# lab_02

Потоковый анализатор файлов: читает события из CSV и JSONL и создаёт статистический отчёт.

## Что умеет

* Читает входные файлы построчно (потоково), не загружая их целиком в память.
* Поддерживает два формата: CSV и JSONL.
* Валидирует обязательные поля события (`timestamp`, `level`, `source`, `message`).
* Считает общее число событий, количество по уровням и источникам.
* Находит первую и последнюю временную метку.
* Выводит top-5 источников ошибок уровня `ERROR`/`CRITICAL`.
* Поддерживает флаг `--skip-invalid` для пропуска битых строк.
* Сохраняет итоговый отчёт в JSON и CSV (при указании пути).
* Поддерживает ленивые фильтры по времени, уровню и источнику.

## Установка

```bash
pip install -e .
```

Если нужны тесты и линтер:

```bash
pip install -e ".[test,lint]"
```

## Как пользоваться

Обработка одного файла и вывод результата в консоль:

```bash
python -m streamstats analyze INPUT --format jsonl
# или
python -m streamstats analyze INPUT --format csv
```

Игнорирование битых строк:

```bash
python -m streamstats analyze INPUT --format csv --skip-invalid
```

Сохранение отчёта на диск (в форматах JSON и CSV):

```bash
python -m streamstats analyze INPUT --format csv --output REPORT.json
```

Обработка нескольких файлов с разными или одинаковыми форматами:

```bash
python -m streamstats analyze INPUT [INPUT ...] --format jsonl csv --output REPORT.json
# или (если формат у всех одинаковый)
python -m streamstats analyze INPUT [INPUT ...] --format csv --output REPORT.json
```

Ленивые фильтры (по времени, уровню, источнику):

```bash
python -m streamstats analyze INPUT --format csv --level INFO ERROR
python -m streamstats analyze INPUT --format csv --source api db
python -m streamstats analyze INPUT --format csv --from 2026-10-06T10:00:00 --to 2026-10-06T11:00:00
```

## Структура

lab_02/
  pyproject.toml
  README.md
  parser_epilog.txt      - текст для вывода в разделе --help
  src/streamstats/
    __init__.py
    __main__.py          - точка входа CLI
    parsers.py           - парсеры CSV и JSONL
    analysis.py          - ядро статистики
    report.py            - формирование JSON и CSV отчётов
    errors.py            - свои классы исключений
  tests/
    conftest.py          - общие фикстуры для тестов
    test_csv_parser.py   - тесты для CSV-парсера
    test_jsonl_parser.py - тесты для JSONL-парсера
    test_analysis.py     - тесты для подсчёта статистики
    test_cli.py          - тесты для проверки работы аргументов командной строки
    test_integration.py  - сквозные тесты (запуск программы целиком от начала до конца)

## Тесты

```bash
python -m pytest
```

## Проверка стиля

```bash
ruff check .
```

## Ошибки

Если что-то не так, программа выводит сообщение в поток ошибок (stderr) и завершается с кодом 2. Например:

```bash
python -m streamstats analyze file.csv --format xml
```

Выведет ошибку invalid choice: 'xml' и код возврата 2.
