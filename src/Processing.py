from typing import Any


def filter_by_state(
    operations: list[dict[str, Any]],
    state: str = "EXECUTED",
) -> list[dict[str, Any]]:
    """
    Фильтрует список операций по статусу.

    Args:
        operations: Список словарей с операциями.
        state: Статус для фильтрации.

    Returns:
        Новый список операций с указанным статусом.
    """
    return [operation for operation in operations
            if operation.get("state") == state]


def sort_by_date(
    operations: list[dict[str, Any]],
    reverse: bool = True,
) -> list[dict[str, Any]]:
    """
    Сортирует операции по дате.

    Args:
        operations: Список словарей с операциями.
        reverse: Порядок сортировки.
                 True — по убыванию,
                 False — по возрастанию.

    Returns:
        Отсортированный список операций.
    """
    return sorted(
        operations,
        key=lambda operation: operation["date"],
        reverse=reverse,
    )