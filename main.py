"""CLI-утилита «Сводка по городу»."""

import argparse
import json
import sys

from exceptions import (
    CityNotFoundError,
    CurrencyNotFoundError,
    ExternalServiceError,
    InvalidResponseError,
)
from processing.service import build_city_summary

EXIT_OK = 0
EXIT_ARGS = 2
EXIT_NOT_FOUND = 3
EXIT_SERVICE = 4


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="city_summary",
        description="Сводка по городу: погода и курс валюты к рублю.",
    )
    parser.add_argument(
        "--city",
        required=True,
        help="Название города (например, Moscow)",
    )
    parser.add_argument(
        "--currency",
        default="USD",
        help="ISO-код валюты (по умолчанию USD)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Вывести сводку в формате JSON",
    )
    return parser.parse_args(argv)


def format_summary(summary: dict) -> str:
    weather = summary["weather"]
    rates = summary["rates"]

    warm = "да" if weather["warm_clothes"] else "нет"
    expensive = "да" if rates["expensive"] else "нет"

    return (
        f"Город: {summary['city']}\n"
        f"Погода: {weather['temp_c']}°C, {weather['description']}\n"
        f"Тёплая одежда: {warm}\n"
        f"{rates['currency']}→RUB: {rates['rate_to_rub']}\n"
        f"Дорогой курс: {expensive}"
    )


def format_summary_json(summary: dict) -> str:
    return json.dumps(summary, indent=2, ensure_ascii=False)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    try:
        summary = build_city_summary(args.city, args.currency)
    except (CityNotFoundError, CurrencyNotFoundError) as exc:
        print(f"Ошибка: {exc}", file=sys.stderr)
        return EXIT_NOT_FOUND
    except (ExternalServiceError, InvalidResponseError) as exc:
        print(f"Ошибка сервиса: {exc}", file=sys.stderr)
        return EXIT_SERVICE

    if args.json:
        print(format_summary_json(summary))
    else:
        print(format_summary(summary))
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())

