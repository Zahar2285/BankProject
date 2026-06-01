from src.masks import get_mask_account, get_mask_card_number

def mask_account_card(data: str) -> str:
    parts = data.split()

    if len(parts) < 2:
        raise ValueError("Некорректный формат данных")

    number = parts[-1]
    name = " ".join(parts[:-1])

    if name.lower() == "счет":
        return f"{name} {get_mask_account(number)}"

    return f"{name} {get_mask_card_number(number)}"