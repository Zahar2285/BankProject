from datetime import datetime

from src.masks import get_mask_card_number, get_mask_account


def mask_account_card(data: str) -> str:
    """Маскирует номер карты или счета."""

    parts = data.split()

    if len(parts) < 2:
        raise ValueError("Некорректный формат данных")

    name = " ".join(parts[:-1])
    number = parts[-1]

    if name.lower() == "счет":
        return f"{name} {get_mask_account(number)}"

    return f"{name} {get_mask_card_number(number)}"


def get_date(date_string: str) -> str:
    """Преобразует дату из ISO-формата в ДД.ММ.ГГГГ."""

    date_obj = datetime.fromisoformat(date_string)
    return date_obj.strftime("%d.%m.%Y")
