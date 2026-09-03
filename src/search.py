import re
from collections import Counter


def process_bank_search(data: list[dict], search: str) -> list[dict]:
    """Возвращает транзакции с искомой строкой в описании.

    Поиск выполняется без учета регистра.
    """
    pattern = re.compile(re.escape(search), re.IGNORECASE)

    return [
        transaction
        for transaction in data
        if pattern.search(str(transaction.get("description", "")))
    ]


def process_bank_operations(
    data: list[dict], categories: list[str]
) -> dict[str, int]:
    """Подсчитывает количество операций для заданных категорий."""
    descriptions = [
        str(transaction.get("description", ""))
        for transaction in data
    ]

    counter = Counter(descriptions)

    return {
        category: counter.get(category, 0)
        for category in categories
    }