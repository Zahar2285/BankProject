from functools import wraps
from typing import Any, Callable

from src.utils import load_operations


def report(filename: str = "report.txt") -> Callable:
    """Декоратор сохраняет результат отчёта в файл."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            result = func(*args, **kwargs)

            with open(filename, "w", encoding="utf-8") as file:
                file.write(str(result))

            return result

        return wrapper

    return decorator


@report()
def spending_by_category(data: list[dict], category: str) -> float:
    """Считает общую сумму трат по указанной категории."""
    total = 0.0

    for transaction in data:
        if transaction.get("Категория") == category:
            amount = transaction.get("Сумма операции", 0)

            if amount < 0:
                total += abs(amount)

    return round(total, 2)
