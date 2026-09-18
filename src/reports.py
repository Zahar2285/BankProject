def spending_by_category(data: list[dict], category: str) -> float:
    """Считает общую сумму трат по указанной категории."""
    total = 0.0

    for transaction in data:
        if transaction.get("Категория") == category:
            amount = transaction.get("Сумма операции", 0)

            if amount < 0:
                total += abs(amount)

    return round(total, 2)