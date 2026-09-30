import json
import os
from datetime import datetime
from typing import TypedDict

import pandas as pd
import requests
from dotenv import load_dotenv

from src.processing import filter_by_state, sort_by_date
from src.readers import read_csv, read_excel
from src.search import process_bank_search
from src.utils import load_operations, load_transactions
from src.widget import get_date, mask_account_card


load_dotenv()


DATA_PATHS = {
    "1": "data/operations.json",
    "2": "data/transactions.csv",
    "3": "data/transactions_excel.xlsx",
}

AVAILABLE_STATUSES = {"EXECUTED", "CANCELED", "PENDING"}


class CardInfo(TypedDict):
    """Данные карты для главной страницы."""

    last_digits: str
    total_spent: float
    cashback: float


def _load_data(file_type: str) -> list[dict]:
    """Загружает операции из выбранного типа файла."""
    path = DATA_PATHS[file_type]

    if file_type == "1":
        return load_transactions(path)

    if file_type == "2":
        return read_csv(path)

    return read_excel(path)


def _normalize_transaction(transaction: dict) -> dict:
    """Приводит данные CSV/XLSX к структуре JSON-транзакции."""
    if "operationAmount" in transaction:
        return transaction

    return {
        **transaction,
        "operationAmount": {
            "amount": transaction.get("amount", 0),
            "currency": {
                "name": transaction.get("currency_name", ""),
                "code": transaction.get("currency_code", ""),
            },
        },
    }


def _is_yes(answer: str) -> bool:
    """Проверяет положительный ответ пользователя."""
    return answer.strip().lower() in {"да", "yes", "y"}


def _is_ruble(transaction: dict) -> bool:
    """Проверяет, является ли транзакция рублевой."""
    if "operationAmount" in transaction:
        currency = transaction.get("operationAmount", {}).get(
            "currency", {}
        )
        return str(currency.get("code", "")) == "RUB"

    return str(transaction.get("currency_code", "")) == "RUB"


def _format_amount(transaction: dict) -> str:
    """Возвращает сумму операции с кодом валюты."""
    operation_amount = transaction.get("operationAmount", {})

    amount = operation_amount.get("amount")
    currency = operation_amount.get("currency", {}).get("code")

    if amount is None:
        amount = transaction.get("amount", 0)
        currency = transaction.get("currency_code", "")

    return f"{amount} {currency}".strip()


def _format_transaction(transaction: dict) -> str:
    """Форматирует одну банковскую операцию для вывода в консоль."""
    date = get_date(str(transaction["date"]))
    description = transaction.get("description", "")

    lines = [f"{date} {description}"]

    source = transaction.get("from")
    destination = transaction.get("to")

    if source and destination:
        masked_source = mask_account_card(str(source))
        masked_destination = mask_account_card(str(destination))
        lines.append(f"{masked_source} -> {masked_destination}")

    elif destination:
        lines.append(mask_account_card(str(destination)))

    elif source:
        lines.append(mask_account_card(str(source)))

    lines.append(f"Сумма: {_format_amount(transaction)}")

    return "\n".join(lines)


def _print_transactions(transactions: list[dict]) -> None:
    """Выводит итоговый список банковских операций."""
    if not transactions:
        print(
            "Программа: Не найдено ни одной транзакции, подходящей "
            "под ваши условия фильтрации"
        )
        return

    print("Программа: Распечатываю итоговый список транзакций...")
    print(
        f"\nПрограмма: Всего банковских операций в выборке: "
        f"{len(transactions)}"
    )

    for transaction in transactions:
        print(f"\n{_format_transaction(transaction)}")


# ----------------------------------------------------------------------
# ГЛАВНАЯ СТРАНИЦА
# ----------------------------------------------------------------------


def load_user_settings() -> dict[str, list[str]]:
    """Загружает пользовательские настройки валют и акций."""
    try:
        with open("user_settings.json", encoding="utf-8") as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {
            "user_currencies": [],
            "user_stocks": [],
        }

    return {
        "user_currencies": list(data.get("user_currencies", [])),
        "user_stocks": list(data.get("user_stocks", [])),
    }


def get_stock_prices() -> list[dict[str, float | str]]:
    """Возвращает текущие цены акций из настроек."""
    settings = load_user_settings()
    stocks = settings["user_stocks"]
    api_key = os.getenv("STOCK_API_KEY")

    result: list[dict[str, float | str]] = []

    if not api_key:
        return result

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

            data = response.json()
            quote = data.get("Global Quote", {})
            price_value = quote.get("05. price")

            if price_value is None:
                continue

            price = float(price_value)

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


def get_currency_rates() -> list[dict[str, float | str]]:
    """Возвращает курсы валют из настроек."""
    settings = load_user_settings()
    currencies = settings["user_currencies"]

    result: list[dict[str, float | str]] = []

    if not currencies:
        return result

    try:
        response = requests.get(
            "https://api.exchangerate-api.com/v4/latest/RUB",
            timeout=10,
        )

        response.raise_for_status()

        data = response.json()
        rates = data.get("rates", {})

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


def _parse_operation_date(value: object) -> datetime | None:
    """Преобразует дату операции в datetime."""
    if value is None:
        return None

    if pd.isna(value):
        return None

    if isinstance(value, datetime):
        return value

    text = str(value).strip()

    formats = (
        "%d.%m.%Y %H:%M:%S",
        "%d.%m.%Y",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
    )

    for date_format in formats:
        try:
            return datetime.strptime(text, date_format)
        except ValueError:
            continue

    try:
        return pd.to_datetime(text).to_pydatetime()
    except (ValueError, TypeError):
        return None


def _get_amount(transaction: dict) -> float:
    """Возвращает сумму операции как число."""
    value = transaction.get("Сумма операции", 0)

    try:
        if pd.isna(value):
            return 0.0
    except TypeError:
        pass

    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _get_category(transaction: dict) -> str:
    """Возвращает категорию операции."""
    value = transaction.get("Категория", "")

    try:
        if pd.isna(value):
            return ""
    except TypeError:
        pass

    return str(value).strip()


def _get_description(transaction: dict) -> str:
    """Возвращает описание операции."""
    value = transaction.get("Описание", "")

    try:
        if pd.isna(value):
            return ""
    except TypeError:
        pass

    return str(value).strip()


def _get_period_data(
    data: list[dict],
    current_datetime: datetime,
) -> list[dict]:
    """Возвращает операции с начала месяца по указанную дату."""
    start_of_month = current_datetime.replace(
        day=1,
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )

    result: list[dict] = []

    for transaction in data:
        transaction_date = _parse_operation_date(
            transaction.get("Дата операции")
        )

        if transaction_date is None:
            continue

        if start_of_month <= transaction_date <= current_datetime:
            result.append(transaction)

    return result


def _get_greeting(hour: int) -> str:
    """Возвращает приветствие в зависимости от времени."""
    if 6 <= hour < 12:
        return "Доброе утро"

    if 12 <= hour < 18:
        return "Добрый день"

    if 18 <= hour < 23:
        return "Добрый вечер"

    return "Доброй ночи"


def _build_cards(period_data: list[dict]) -> list[CardInfo]:
    """Формирует информацию по картам."""
    cards: dict[str, CardInfo] = {}

    for transaction in period_data:
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
        card["total_spent"] = round(
            float(card["total_spent"]),
            2,
        )
        card["cashback"] = round(
            card["total_spent"] / 100,
            2,
        )

    return list(cards.values())


def _build_top_transactions(
    period_data: list[dict],
) -> list[dict]:
    """Формирует топ-5 транзакций по сумме."""
    top_transactions = sorted(
        period_data,
        key=lambda transaction: abs(_get_amount(transaction)),
        reverse=True,
    )[:5]

    result: list[dict] = []

    for transaction in top_transactions:
        transaction_date = _parse_operation_date(
            transaction.get("Дата операции")
        )

        formatted_date = ""

        if transaction_date is not None:
            formatted_date = transaction_date.strftime("%d.%m.%Y")

        result.append(
            {
                "date": formatted_date,
                "amount": _get_amount(transaction),
                "category": _get_category(transaction),
                "description": _get_description(transaction),
            }
        )

    return result


def _build_expenses(period_data: list[dict]) -> dict:
    """Формирует блок расходов."""
    expenses = [
        transaction
        for transaction in period_data
        if _get_amount(transaction) < 0
    ]

    total_amount = sum(
        abs(_get_amount(transaction))
        for transaction in expenses
    )

    category_totals: dict[str, float] = {}

    transfers_amount = 0.0
    cash_amount = 0.0

    for transaction in expenses:
        amount = abs(_get_amount(transaction))
        category = _get_category(transaction).lower()

        if "перевод" in category:
            transfers_amount += amount
            continue

        if (
            "наличн" in category
            or "банкомат" in category
            or "снятие" in category
        ):
            cash_amount += amount
            continue

        category_name = _get_category(transaction)

        if not category_name:
            category_name = "Без категории"

        category_totals[category_name] = (
            category_totals.get(category_name, 0.0) + amount
        )

    sorted_categories = sorted(
        category_totals.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    top_categories = sorted_categories[:7]
    other_amount = sum(
        amount for _, amount in sorted_categories[7:]
    )

    main_categories = [
        {
            "category": category,
            "amount": round(amount),
        }
        for category, amount in top_categories
    ]

    if other_amount > 0:
        main_categories.append(
            {
                "category": "Остальное",
                "amount": round(other_amount),
            }
        )

    transfers_and_cash = []

    if cash_amount > 0:
        transfers_and_cash.append(
            {
                "category": "Наличные",
                "amount": round(cash_amount),
            }
        )

    if transfers_amount > 0:
        transfers_and_cash.append(
            {
                "category": "Переводы",
                "amount": round(transfers_amount),
            }
        )

    return {
        "total_amount": round(total_amount),
        "main": main_categories,
        "transfers_and_cash": transfers_and_cash,
    }


def _build_income(period_data: list[dict]) -> dict:
    """Формирует блок поступлений."""
    income = [
        transaction
        for transaction in period_data
        if _get_amount(transaction) > 0
    ]

    total_amount = sum(
        _get_amount(transaction)
        for transaction in income
    )

    category_totals: dict[str, float] = {}

    for transaction in income:
        category = _get_category(transaction)

        if not category:
            category = "Без категории"

        category_totals[category] = (
            category_totals.get(category, 0.0)
            + _get_amount(transaction)
        )

    sorted_categories = sorted(
        category_totals.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    main_categories = [
        {
            "category": category,
            "amount": round(amount),
        }
        for category, amount in sorted_categories[:7]
    ]

    return {
        "total_amount": round(total_amount),
        "main": main_categories,
    }


def show_main_page(
    data: list[dict],
    date_time: str,
) -> dict:
    """
    Формирует JSON-данные для главной страницы.

    Диапазон данных:
    с первого дня месяца по указанную дату включительно.
    """
    current_datetime = datetime.strptime(
        date_time,
        "%Y-%m-%d %H:%M:%S",
    )

    period_data = _get_period_data(
        data,
        current_datetime,
    )

    greeting = _get_greeting(current_datetime.hour)

    cards = _build_cards(period_data)

    top_transactions = _build_top_transactions(
        period_data
    )

    expenses = _build_expenses(period_data)

    income = _build_income(period_data)

    return {
        "greeting": greeting,
        "cards": cards,
        "expenses": expenses,
        "income": income,
        "top_transactions": top_transactions,
        "currency_rates": get_currency_rates(),
        "stock_prices": get_stock_prices(),
    }


def run_main_page() -> None:
    """Запускает формирование главной страницы."""
    data = load_operations("data/operations.xlsx")

    result = show_main_page(
        data,
        "2018-04-07 23:59:59",
    )

    print(
        json.dumps(
            result,
            ensure_ascii=False,
            indent=2,
        )
    )


# ----------------------------------------------------------------------
# КОНСОЛЬНОЕ ПРИЛОЖЕНИЕ
# ----------------------------------------------------------------------


def main() -> None:
    """Запускает консольный интерфейс программы."""
    print(
        "Программа: Привет! Добро пожаловать в программу работы "
        "с банковскими транзакциями."
    )

    print("Выберите необходимый пункт меню:")
    print("1. Получить информацию о транзакциях из JSON-файла")
    print("2. Получить информацию о транзакциях из CSV-файла")
    print("3. Получить информацию о транзакциях из XLSX-файла")

    file_type = input().strip()

    while file_type not in DATA_PATHS:
        print(
            "Программа: Некорректный пункт меню. "
            "Выберите 1, 2 или 3."
        )
        file_type = input().strip()

    file_names = {
        "1": "JSON",
        "2": "CSV",
        "3": "XLSX",
    }

    print(
        f"Программа: Для обработки выбран "
        f"{file_names[file_type]}-файл."
    )

    transactions = [
        _normalize_transaction(item)
        for item in _load_data(file_type)
    ]

    while True:
        print(
            "Программа: Введите статус, по которому необходимо "
            "выполнить фильтрацию. Доступные для фильтровки "
            "статусы: EXECUTED, CANCELED, PENDING"
        )

        status = input().strip().upper()

        if status in AVAILABLE_STATUSES:
            break

        print(
            f'Программа: Статус операции "{status}" недоступен.'
        )

    transactions = filter_by_state(
        transactions,
        status,
    )

    print(
        f'Программа: Операции отфильтрованы '
        f'по статусу "{status}"'
    )

    if _is_yes(
        input(
            "Программа: Отсортировать операции по дате? Да/Нет\n"
        )
    ):
        order = input(
            "Программа: Отсортировать по возрастанию "
            "или по убыванию?\n"
        ).strip().lower()

        transactions = sort_by_date(
            transactions,
            reverse=order != "по возрастанию",
        )

    if _is_yes(
        input(
            "Программа: Выводить только рублевые "
            "транзакции? Да/Нет\n"
        )
    ):
        transactions = [
            transaction
            for transaction in transactions
            if _is_ruble(transaction)
        ]

    if _is_yes(
        input(
            "Программа: Отфильтровать список транзакций "
            "по определенному слову в описании? Да/Нет\n"
        )
    ):
        search = input(
            "Программа: Введите поисковую строку:\n"
        ).strip()

        transactions = process_bank_search(
            transactions,
            search,
        )

    _print_transactions(transactions)


if __name__ == "__main__":
    main()
