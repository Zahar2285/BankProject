import re

from collections import defaultdict
from math import ceil
from typing import Any


def simple_search(data: list[dict], search: str) -> list[dict]:
    """Ищет операции по категории или описанию."""
    search = search.lower()

    return list(
        filter(
            lambda transaction: (
                search in str(transaction.get("Категория", "")).lower()
                or search in str(transaction.get("Описание", "")).lower()
            ),
            data,
        )
    )


def search_phone_numbers(data: list[dict]) -> list[dict]:
    """Ищет операции, в описании которых есть номер телефона."""
    pattern = re.compile(
        r"(?:"
        r"\+7\s*\(\d{3}\)\s*\d{3}[-\s]\d{2}[-\s]\d{2}"
        r"|"
        r"\+7\s*\d{3}\s+\d{2}[-\s]\d{2}[-\s]\d{2}"
        r"|"
        r"8\d{10}"
        r")"
    )

    return list(
        filter(
            lambda transaction: pattern.search(
                str(transaction.get("Описание", ""))
            )
            is not None,
            data,
        )
    )


def search_person_transfers(data: list[dict]) -> list[dict]:
    """Ищет переводы физическим лицам."""
    pattern = re.compile(
        r"[А-ЯЁ][а-яё]+\s+[А-ЯЁ]\."
    )

    return list(
        filter(
            lambda transaction: (
                str(transaction.get("Категория", "")) == "Переводы"
                and pattern.search(
                    str(transaction.get("Описание", ""))
                )
                is not None
            ),
            data,
        )
    )


def cashback_categories(
    data: list[dict],
    year: int,
    month: int,
) -> dict[str, float]:
    """Возвращает сумму кешбэка по категориям за указанный месяц."""
    filtered_data = filter(
        lambda transaction: (
            transaction.get("Дата операции", "").startswith(
                f"{year:04d}-{month:02d}"
            )
            and transaction.get("Кэшбэк", 0) > 0
        ),
        data,
    )

    cashback_by_category: dict[str, float] = defaultdict(float)

    for transaction in filtered_data:
        category = str(transaction.get("Категория", "Без категории"))
        cashback = float(transaction.get("Кэшбэк", 0))
        cashback_by_category[category] += cashback

    return dict(
        sorted(
            cashback_by_category.items(),
            key=lambda item: item[1],
            reverse=True,
        )
    )


def investment_bank(
    month: str,
    transactions: list[dict[str, Any]],
    limit: int,
) -> float:
    """Рассчитывает сумму, которую можно отложить в Инвесткопилку."""
    if limit <= 0:
        raise ValueError("Лимит должен быть больше нуля")

    month_transactions = filter(
        lambda transaction: (
            str(transaction.get("Дата операции", "")).startswith(month)
            and float(transaction.get("Сумма операции", 0)) < 0
        ),
        transactions,
    )

    savings = map(
        lambda transaction: (
            ceil(abs(float(transaction["Сумма операции"])) / limit) * limit
            - abs(float(transaction["Сумма операции"]))
        ),
        month_transactions,
    )

    return round(sum(savings), 2)
