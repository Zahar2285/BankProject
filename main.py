from src.processing import filter_by_state, sort_by_date
from src.readers import read_csv, read_excel
from src.search import process_bank_search
from src.utils import load_transactions
from src.widget import get_date, mask_account_card

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
