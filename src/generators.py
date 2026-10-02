from collections.abc import Generator


def filter_by_currency(
    transactions: list[dict],
    currency: str,
) -> Generator[dict, None, None]:
    """
    Возвращает транзакции с указанной валютой.
    """
    for transaction in transactions:
        if (
            transaction["operationAmount"]["currency"]["code"]
            == currency
        ):
            yield transaction


def transaction_descriptions(
    transactions: list[dict],
) -> Generator[str, None, None]:
    """
    Последовательно возвращает описания операций.
    """
    for transaction in transactions:
        yield transaction["description"]


def card_number_generator(
    start: int,
    stop: int,
) -> Generator[str, None, None]:
    """
    Генерирует номера банковских карт в формате
    XXXX XXXX XXXX XXXX.
    """
    for number in range(start, stop + 1):
        card = f"{number:016d}"
        yield (
            f"{card[:4]} {card[4:8]} "
            f"{card[8:12]} {card[12:]}"
        )
