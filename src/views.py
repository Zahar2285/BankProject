import json
import os
from datetime import datetime, timedelta
from typing import Any

import requests
from dotenv import load_dotenv

load_dotenv()


def load_user_settings() -> dict[str, list[str]]:
    """Загружает настройки валют и акций."""
    with open("user_settings.json", encoding="utf-8") as file:
        settings = json.load(file)

    return {
        "user_currencies": settings.get("user_currencies", []),
        "user_stocks": settings.get("user_stocks", []),
    }


def _parse_date(date_value: Any) -> datetime | None:
    """Преобразует дату операции в datetime."""
    if isinstance(date_value, datetime):
        return date_value

    if date_value is None:
        return None

    value = str(date_value)

    formats = (
        "%d.%m.%Y %H:%M:%S",
        "%d.%m.%Y",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
    )

    for date_format in formats:
        try:
            return datetime.strptime(value, date_format)
        except ValueError:
            continue

    return None


def _get_amount(transaction: dict) -> float:
    """Возвращает сумму операции."""
    value = transaction.get("Сумма операции", 0)

    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _get_category(transaction: dict) -> str:
    """Возвращает категорию операции."""
    value = transaction.get("Категория", "")

    if value is None:
        return ""

    return str(value)


def _get_description(transaction: dict) -> str:
    """Возвращает описание операции."""
    value = transaction.get("Описание", "")

    if value is None:
        return ""

    return str(value)


def _get_period_data(
    data: list[dict],
    current_datetime: datetime,
    start_date: datetime | None = None,
) -> list[dict]:
    """Возвращает операции за заданный период."""
    if start_date is None:
        start_date = current_datetime.replace(
            day=1,
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )

    return [
        transaction
        for transaction in data
        if (
            transaction_date := _parse_date(
                transaction.get("Дата операции")
            )
        )
        is not None
        and start_date <= transaction_date <= current_datetime
    ]


def _get_greeting(hour: int) -> str:
    if 5 <= hour < 12:
        return "Доброе утро"
    if 12 <= hour < 18:
        return "Добрый день"
    if 18 <= hour < 23:
        return "Добрый вечер"
    return "Доброй ночи"


def _build_cards(data: list[dict]) -> list[dict[str, Any]]:
    """Формирует информацию по банковским картам."""
    cards: dict[str, dict[str, Any]] = {}

    for transaction in data:
        card_number = transaction.get("Номер карты")

        if not card_number or str(card_number) == "nan":
            continue

        last_digits = str(card_number)[-4:]
        amount = _get_amount(transaction)

        if last_digits not in cards:
            cards[last_digits] = {
                "last_digits": last_digits,
                "total_spent": 0.0,
                "cashback": 0.0,
            }

        if amount < 0:
            cards[last_digits]["total_spent"] += abs(amount)

    for card in cards.values():
        total_spent = round(float(card["total_spent"]), 2)
        card["total_spent"] = total_spent
        card["cashback"] = round(total_spent / 100, 2)

    return list(cards.values())


def _build_top_transactions(data: list[dict]) -> list[dict]:
    """Формирует топ-5 операций по сумме."""
    top_transactions = sorted(
        data,
        key=lambda transaction: abs(_get_amount(transaction)),
        reverse=True,
    )[:5]

    result = []

    for transaction in top_transactions:
        transaction_date = _parse_date(
            transaction.get("Дата операции")
        )

        result.append(
            {
                "date": (
                    transaction_date.strftime("%d.%m.%Y")
                    if transaction_date
                    else ""
                ),
                "amount": _get_amount(transaction),
                "category": _get_category(transaction),
                "description": _get_description(transaction),
            }
        )

    return result


def _build_expenses(data: list[dict]) -> dict[str, Any]:
    """Формирует блок расходов."""
    expenses: dict[str, float] = {}

    for transaction in data:
        amount = _get_amount(transaction)

        if amount >= 0:
            continue

        category = _get_category(transaction)

        if not category:
            category = "Без категории"

        expenses[category] = (
            expenses.get(category, 0.0) + abs(amount)
        )

    total_amount = sum(expenses.values())

    transfers_and_cash: dict[str, float] = {}
    main_expenses: dict[str, float] = {}

    for category, amount in expenses.items():
        category_lower = category.lower()

        if "перевод" in category_lower:
            transfers_and_cash["Переводы"] = (
                transfers_and_cash.get("Переводы", 0.0) + amount
            )
        elif (
            "налич" in category_lower
            or "банкомат" in category_lower
            or "снятие" in category_lower
        ):
            transfers_and_cash["Наличные"] = (
                transfers_and_cash.get("Наличные", 0.0) + amount
            )
        else:
            main_expenses[category] = amount

    sorted_expenses = sorted(
        main_expenses.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    top_seven = sorted_expenses[:7]
    other_amount = sum(
        amount for _, amount in sorted_expenses[7:]
    )

    main = [
        {
            "category": category,
            "amount": round(amount),
        }
        for category, amount in top_seven
    ]

    if other_amount:
        main.append(
            {
                "category": "Остальное",
                "amount": round(other_amount),
            }
        )

    transfers = [
        {
            "category": category,
            "amount": round(amount),
        }
        for category, amount in sorted(
            transfers_and_cash.items(),
            key=lambda item: item[1],
            reverse=True,
        )
    ]

    return {
        "total_amount": round(total_amount),
        "main": main,
        "transfers_and_cash": transfers,
    }


def _build_income(data: list[dict]) -> dict[str, Any]:
    """Формирует блок поступлений."""
    income: dict[str, float] = {}

    for transaction in data:
        amount = _get_amount(transaction)

        if amount <= 0:
            continue

        category = _get_category(transaction)

        if not category:
            category = "Без категории"

        income[category] = income.get(category, 0.0) + amount

    sorted_income = sorted(
        income.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    return {
        "total_amount": round(sum(income.values())),
        "main": [
            {
                "category": category,
                "amount": round(amount),
            }
            for category, amount in sorted_income
        ],
    }


def get_currency_rates() -> list[dict[str, Any]]:
    """Получает курсы валют из API."""
    settings = load_user_settings()
    currencies = settings["user_currencies"]

    result: list[dict[str, Any]] = []

    try:
        response = requests.get(
            "https://api.exchangerate-api.com/v4/latest/RUB",
            timeout=10,
        )
        response.raise_for_status()
        rates = response.json().get("rates", {})
    except (
        requests.RequestException,
        ValueError,
        TypeError,
    ):
        return result

    for currency in currencies:
        try:
            rate = float(rates[currency])

            if rate <= 0:
                continue

            result.append(
                {
                    "currency": currency,
                    "rate": round(1 / rate, 2),
                }
            )
        except (KeyError, TypeError, ValueError, ZeroDivisionError):
            continue

    return result


def get_stock_prices() -> list[dict[str, Any]]:
    """Получает цены акций из API Alpha Vantage."""
    settings = load_user_settings()
    stocks = settings["user_stocks"]

    api_key = os.getenv("API_KEY")

    if not api_key:
        return []

    result = []

    for stock in stocks:
        try:
            response = requests.get(
                "https://www.alphavantage.co/query",
                params={
                    "function": "GLOBAL_QUOTE",
                    "symbol": stock,
                    "apikey": api_key,
                },
                timeout=10,
            )
            response.raise_for_status()

            quote = response.json().get("Global Quote", {})
            price = float(quote.get("05. price", 0))

            if price <= 0:
                continue

            result.append(
                {
                    "stock": stock,
                    "price": round(price, 2),
                }
            )
        except (
            requests.RequestException,
            ValueError,
            TypeError,
        ):
            continue

    return result


def show_main_page(
    data: list[dict],
    date_time: str,
) -> dict[str, Any]:
    """Формирует JSON главной страницы."""
    current_datetime = datetime.strptime(
        date_time,
        "%Y-%m-%d %H:%M:%S",
    )

    period_data = _get_period_data(
        data,
        current_datetime,
    )

    return {
        "greeting": _get_greeting(current_datetime.hour),
        "cards": _build_cards(period_data),
        "top_transactions": _build_top_transactions(period_data),
        "currency_rates": get_currency_rates(),
        "stock_prices": get_stock_prices(),
    }


def _get_events_period(
    current_datetime: datetime,
    period: str,
) -> tuple[datetime, datetime]:
    """Определяет начало и конец периода страницы События."""
    period = period.upper()

    if period == "W":
        start_date = (
            current_datetime
            - timedelta(days=current_datetime.weekday())
        ).replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )
        return start_date, current_datetime

    if period == "M":
        start_date = current_datetime.replace(
            day=1,
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )
        return start_date, current_datetime

    if period == "Y":
        start_date = current_datetime.replace(
            month=1,
            day=1,
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )
        return start_date, current_datetime

    if period == "ALL":
        return datetime.min, current_datetime

    start_date = current_datetime.replace(
        day=1,
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )

    return start_date, current_datetime


def show_events_page(
    data: list[dict],
    date_time: str,
    period: str = "M",
) -> dict[str, Any]:
    """Формирует JSON страницы События."""
    current_datetime = datetime.strptime(
        date_time,
        "%Y-%m-%d %H:%M:%S",
    )

    start_date, end_date = _get_events_period(
        current_datetime,
        period,
    )

    period_data = _get_period_data(
        data,
        current_datetime=end_date,
        start_date=start_date,
    )

    return {
        "expenses": _build_expenses(period_data),
        "income": _build_income(period_data),
        "currency_rates": get_currency_rates(),
        "stock_prices": get_stock_prices(),
    }


def run_main_page(data: list[dict]) -> dict[str, Any]:
    """Запускает формирование главной страницы."""
    date_time = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    return show_main_page(data, date_time)


def run_events_page(
    data: list[dict],
    period: str = "M",
) -> dict[str, Any]:
    """Запускает формирование страницы События."""
    date_time = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    return show_events_page(
        data,
        date_time,
        period,
    )
