from datetime import datetime
from typing import TypedDict

import pandas as pd
import requests
import json
import os

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
        currency = transaction.get("operationAmount", {}).get("currency", {})
        return str(currency.get("code", "")) == "RUB"

    return str(transaction.get("currency_code", "")) == "RUB"


def _format_amount(transaction: dict) -> str:
    """Возвращает сумму операции с кодом валюты."""
    amount = transaction.get("operationAmount", {}).get("amount")
    currency = (
        transaction.get("operationAmount", {})
        .get("currency", {})
        .get("code")
    )

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


class CardInfo(TypedDict):
    """Данные карты для главной страницы."""

    last_digits: str
    total_spent: float
    cashback: float


def load_user_settings() -> dict[str, list[str]]:
    """Загружает пользовательские настройки."""
    with open("user_settings.json", encoding="utf-8") as file:
        data = json.load(file)

    return {
        "user_currencies": list(data["user_currencies"]),
        "user_stocks": list(data["user_stocks"]),
    }


def get_stock_prices() -> list[dict[str, float | str]]:
    """Возвращает текущие цены акций."""
    settings = load_user_settings()
    stocks = settings["user_stocks"]
    api_key = os.getenv("STOCK_API_KEY")
    result: list[dict[str, float | str]] = []

    for stock in stocks:
        response = requests.get(
            "https://www.alphavantage.co/query",
            params={
                "function": "GLOBAL_QUOTE",
                "symbol": stock,
                "apikey": api_key,
            },
            timeout=10,
        )
        data = response.json()

        price = float(data["Global Quote"]["05. price"])
        result.append(
            {
                "stock": stock,
                "price": round(price, 2),
            }
        )

    return result


def get_currency_rates() -> list[dict[str, float | str]]:
    """Возвращает курсы валют."""
    settings = load_user_settings()
    currencies = settings["user_currencies"]
    result = []

    for currency in currencies:
        response = requests.get(
            "https://api.exchangerate-api.com/v4/latest/RUB",
            timeout=10,
        )
        data = response.json()
        rate = data["rates"][currency]

        result.append(
            {
                "currency": currency,
                "rate": round(1 / rate, 2),
            }
        )

    return result


def show_main_page(data: list[dict]) -> dict:
    """Формирует данные для главной страницы."""
    current_datetime = datetime.now()
    current_hour = current_datetime.hour

    if 6 <= current_hour < 12:
        greeting = "Доброе утро"
    elif 12 <= current_hour < 18:
        greeting = "Добрый день"
    elif 18 <= current_hour < 23:
        greeting = "Добрый вечер"
    else:
        greeting = "Доброй ночи"

    cards: dict[str, CardInfo] = {}

    for transaction in data:
        card_number = transaction.get("Номер карты")

        if not card_number or str(card_number) == "nan":
            continue

        last_digits = str(card_number)[-4:]
        amount = transaction.get("Сумма операции", 0)

        if not isinstance(amount, (int, float)):
            continue

        if last_digits not in cards:
            cards[last_digits] = {
                "last_digits": last_digits,
                "total_spent": 0.0,
                "cashback": 0.0,
            }

        if amount < 0:
            cards[last_digits]["total_spent"] += abs(amount)

    for card in cards.values():
        card["total_spent"] = round(float(card["total_spent"]), 2)
        card["cashback"] = round(float(card["total_spent"]) / 100, 2)

    top_transactions = sorted(
        data,
        key=lambda transaction: abs(
            transaction.get("Сумма операции", 0)
        ),
        reverse=True,
    )[:5]

    transactions = []

    for transaction in top_transactions:
        date = str(transaction.get("Дата операции", ""))

        if date:
            date = datetime.strptime(
                date,
                "%d.%m.%Y %H:%M:%S",
            ).strftime("%d.%m.%Y")

        transactions.append(
            {
                "date": date,
                "amount": transaction.get("Сумма операции", 0),
                "category": (
                    ""
                    if pd.isna(transaction.get("Категория"))
                    else str(transaction.get("Категория"))
                ),
                "description": transaction.get("Описание", ""),
            }
        )

    return {
        "greeting": greeting,
        "cards": list(cards.values()),
        "top_transactions": transactions,
        "currency_rates": get_currency_rates(),
        "stock_prices": get_stock_prices(),
    }


def run_main_page() -> None:
    """Запускает главную страницу проекта."""
    data = load_operations("data/operations.xlsx")
    show_main_page(data)


def main() -> None:

    """Запускает консольный интерфейс программы.

    Пользователь выбирает источник данных и параметры выборки.
    """
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
        print("Программа: Некорректный пункт меню. Выберите 1, 2 или 3.")
        file_type = input().strip()

    file_names = {"1": "JSON", "2": "CSV", "3": "XLSX"}
    print(f"Программа: Для обработки выбран {file_names[file_type]}-файл.")
    transactions = [
        _normalize_transaction(item) for item in _load_data(file_type)
    ]

    while True:
        print(
            "Программа: Введите статус, по которому необходимо "
            "выполнить фильтрацию. Доступные для фильтровки статусы: "
            "EXECUTED, "
            "CANCELED, PENDING"
        )
        status = input().strip().upper()
        if status in AVAILABLE_STATUSES:
            break
        print(f'Программа: Статус операции "{status}" недоступен.')

    transactions = filter_by_state(transactions, status)
    print(f'Программа: Операции отфильтрованы по статусу "{status}"')

    if _is_yes(input("Программа: Отсортировать операции по дате? Да/Нет\n")):
        order = input(
            "Программа: Отсортировать по возрастанию или по "
            "убыванию?\n"
        ).strip().lower()
        transactions = sort_by_date(
            transactions, reverse=order != "по возрастанию"
        )

    if _is_yes(
        input("Программа: Выводить только рублевые транзакции? Да/Нет\n")
    ):
        transactions = [
            transaction for transaction in transactions if _is_ruble(transaction)
        ]

    if _is_yes(
        input(
            "Программа: Отфильтровать список транзакций по "
            "определенному слову в описании? Да/Нет\n"
        )
    ):
        search = input("Программа: Введите поисковую строку:\n").strip()
        transactions = process_bank_search(transactions, search)

    _print_transactions(transactions)


if __name__ == "__main__":
    main()
