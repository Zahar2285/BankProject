import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler(
    "logs/masks.log",
    mode="w",
    encoding="utf-8",
)

file_formatter = logging.Formatter(
    "%(asctime)s %(name)s %(levelname)s %(message)s"
)

file_handler.setFormatter(file_formatter)

if not logger.handlers:
    logger.addHandler(file_handler)

def get_mask_card_number(card_number: str) -> str:
    logger.debug("Начало маскирования номера карты")

    if len(card_number) != 16:
        logger.error("Неверная длина номера карты: %s", card_number)
        raise ValueError("Некорректный номер карты")

    result = (
        f"{card_number[:4]} "
        f"{card_number[4:6]}** **** "
        f"{card_number[-4:]}"
    )

    logger.info("Номер карты успешно замаскирован")

    return result

def get_mask_account(account: str) -> str:
    logger.debug("Начало маскирования счета")

    if len(account) < 4:
        logger.error("Некорректный номер счета: %s", account)
        raise ValueError("Некорректный номер счета")

    result = "**" + account[-4:]

    logger.info("Счет успешно замаскирован")

    return result
