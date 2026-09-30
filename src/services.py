import re


def simple_search(data: list[dict], search: str) -> list[dict]:
    """Ищет операции по категории или описанию."""
    search = search.lower()

    return list(
        filter(
            lambda transaction: (
                search in str(transaction.get("Категория", "")).lower()
                or search in str(transaction.get("Описание", "")).lower()
            ),
            data,
        )
    )


def search_phone_numbers(data: list[dict]) -> list[dict]:
    """Ищет операции, в описании которых есть номер телефона."""
    pattern = re.compile(
        r"(?:"
        r"\+7\s*\(\d{3}\)\s*\d{3}[-\s]\d{2}[-\s]\d{2}"
        r"|"
        r"\+7\s*\d{3}\s+\d{2}[-\s]\d{2}[-\s]\d{2}"
        r"|"
        r"8\d{10}"
        r")"
    )

    return list(
        filter(
            lambda transaction: pattern.search(
                str(transaction.get("Описание", ""))
            )
            is not None,
            data,
        )
    )


def search_person_transfers(data: list[dict]) -> list[dict]:
    """Ищет переводы физическим лицам."""
    pattern = re.compile(
        r"[А-ЯЁ][а-яё]+\s+[А-ЯЁ]\."
    )

    return list(
        filter(
            lambda transaction: (
                str(transaction.get("Категория", "")) == "Переводы"
                and pattern.search(
                    str(transaction.get("Описание", ""))
                )
                is not None
            ),
            data,
        )
    )
