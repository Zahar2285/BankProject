import json


def load_transactions(path: str) -> list[dict]:
    """
    Загружает список транзакций из JSON-файла.
    """

    try:
        with open(path, encoding="utf-8") as file:
            data = json.load(file)

            if isinstance(data, list):
                return data

            return []

    except (FileNotFoundError, json.JSONDecodeError):
        return []
