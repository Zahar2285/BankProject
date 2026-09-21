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

def search_phone_numbers(data: list[dict]) -> list[dict]:
    """Ищет операции, в описании которых есть номер телефона."""
    pattern = re.compile(r"\+7\s?\d{3}\s?\d{2}[-\s]?\d{2}[-\s]?\d{2}")

    result = []

    for transaction in data:
        description = str(transaction.get("Описание", ""))

        if pattern.search(description):
            result.append(transaction)

    return result
