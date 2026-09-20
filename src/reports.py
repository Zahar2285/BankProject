from datetime import datetime
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
def spending_by_category(data: list[dict], category: str) -> str:
    """Формирует отчёт о тратах по указанной категории."""
    total = 0.0

    for transaction in data:
        if transaction.get("Категория") == category:
            amount = transaction.get("Сумма операции", 0)

            if amount < 0:
                total += abs(amount)

    return f"Категория: {category}\nСумма трат: {round(total, 2)} руб."

@report("report_weekday.txt")
def spending_by_weekday(data: list[dict]) -> dict[str, float]:
    """Считает сумму трат по дням недели."""
    result = {}

    for transaction in data:
        amount = transaction.get("Сумма операции", 0)

        if amount >= 0:
            continue

        date = transaction.get("Дата операции")

        if not date:
            continue

        date = datetime.strptime(date, "%d.%m.%Y %H:%M:%S")
        weekday = date.strftime("%A")

        result[weekday] = result.get(weekday, 0) + abs(amount)

    return {
        day: round(total, 2)
        for day, total in result.items()
    }