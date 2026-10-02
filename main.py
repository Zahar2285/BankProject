from datetime import datetime

from src.processing import filter_by_state, sort_by_date
from src.readers import read_csv, read_excel
from src.search import process_bank_search
from src.utils import load_transactions


DATA_PATHS = {
    "1": "data/operations.json",
    "2": "data/transactions.csv",
    "3": "data/transactions_excel.xlsx",
}

AVAILABLE_STATUSES = {"EXECUTED", "CANCELED", "PENDING"}


def _load_data(file_type: str) -> list[dict]:
    """Загружает операции из выбранного файла."""
    path = DATA_PATHS[file_type]

    if file_type == "1":
        return load_transactions(path)

    if file_type == "2":
        return read_csv(path)

    return read_excel(path)


def _normalize_transaction(transaction: dict) -> dict:
    """Приводит операцию к единому формату."""
    if "operationAmount" in transaction:
        return transaction

    return {
        **transaction,
        "operationAmount": {
            "amount": transaction.get(
                "Сумма операции",
                transaction.get("amount", 0),
            ),
            "currency": {
                "code": transaction.get(
                    "Валюта операции",
                    transaction.get("currency_code", "RUB"),
                )
            },
        },
    }


def _is_yes(value: str) -> bool:
    """Проверяет положительный ответ пользователя."""
    return value.strip().lower() in {"да", "д", "yes", "y"}


def _is_ruble(transaction: dict) -> bool:
    """Проверяет, является ли операция рублевой."""
    operation_amount = transaction.get("operationAmount", {})
    currency = operation_amount.get("currency", {})

    if currency.get("code") == "RUB":
        return True

    return transaction.get(
        "Валюта операции",
        transaction.get("currency_code"),
    ) == "RUB"


def _format_amount(transaction: dict) -> str:
    """Формирует строку с суммой и валютой."""
    operation_amount = transaction.get("operationAmount", {})

    amount = operation_amount.get("amount")
    currency = operation_amount.get("currency", {}).get("code")

    if amount is None:
        amount = transaction.get(
            "Сумма операции",
            transaction.get("amount", 0),
        )
        currency = transaction.get(
            "Валюта операции",
            transaction.get("currency_code", ""),
        )

    return f"{amount} {currency}".strip()


def _format_transaction(transaction: dict) -> str:
    """Формирует строку для вывода операции."""
    date_value = transaction.get(
        "Дата операции",
        transaction.get("date", ""),
    )

    try:
        date = datetime.strptime(
            str(date_value),
            "%d.%m.%Y %H:%M:%S",
        ).strftime("%d.%m.%Y")
    except ValueError:
        date = str(date_value)

    description = transaction.get(
        "Описание",
        transaction.get("description", ""),
    )

    lines = [
        f"{date} {description}",
        f"Сумма: {_format_amount(transaction)}",
    ]

    return "\n".join(lines)


def _print_transactions(transactions: list[dict]) -> None:
    """Выводит найденные операции."""
    if not transactions:
        print(
            "Программа: Не найдено ни одной транзакции, "
            "подходящей под ваши условия фильтрации"
        )
        return

    print("Программа: Распечатываю итоговый список транзакций...")
    print(
        f"\nПрограмма: Всего банковских операций "
        f"в выборке: {len(transactions)}"
    )

    for transaction in transactions:
        print(f"\n{_format_transaction(transaction)}")


def _run_console() -> None:
    """Запускает консольную часть программы."""
    print(
        "Программа: Привет! Добро пожаловать "
        "в программу работы с банковскими транзакциями."
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
            "выполнить фильтрацию. "
            "Доступные статусы: EXECUTED, CANCELED, PENDING"
        )

        status = input().strip().upper()

        if status in AVAILABLE_STATUSES:
            break

        print(
            f'Программа: Статус операции "{status}" недоступен.'
        )

    transactions = filter_by_state(transactions, status)

    print(
        f'Программа: Операции отфильтрованы '
        f'по статусу "{status}"'
    )

    answer = input(
        "Программа: Отсортировать операции по дате? Да/Нет\n"
    )

    if _is_yes(answer):
        order = input(
            "Программа: Отсортировать по возрастанию "
            "или по убыванию?\n"
        ).strip().lower()

        transactions = sort_by_date(
            transactions,
            reverse=order != "по возрастанию",
        )

    answer = input(
        "Программа: Выводить только рублевые транзакции? Да/Нет\n"
    )

    if _is_yes(answer):
        transactions = [
            transaction
            for transaction in transactions
            if _is_ruble(transaction)
        ]

    answer = input(
        "Программа: Отфильтровать транзакции "
        "по слову в описании? Да/Нет\n"
    )

    if _is_yes(answer):
        search = input(
            "Программа: Введите строку для поиска:\n"
        ).strip()

        transactions = process_bank_search(
            transactions,
            search,
        )

    _print_transactions(transactions)


def main() -> None:
    """Точка входа в программу."""
    _run_console()


if __name__ == "__main__":
    main()
