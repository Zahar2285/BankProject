def simple_search(data: list[dict], search: str) -> list[dict]:
    """Ищет операции по категории или описанию."""
    search = search.lower()

    result = []

    for transaction in data:
        category = str(transaction.get("Категория", "")).lower()
        description = str(transaction.get("Описание", "")).lower()

        if search in category or search in description:
            result.append(transaction)

    return result